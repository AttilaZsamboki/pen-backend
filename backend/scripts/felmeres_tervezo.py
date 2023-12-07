import numpy as np
from ..utils.google_routes import Client
import os
from ..utils.logs import log
from ..models import Appointments
from ..models import MiniCrmAdatlapok, Routes, OpenSlots, Salesmen, Skills, UserSkills
from ..utils.utils import is_number, round_to_30
from datetime import datetime, timedelta, date as dt_date
from django.db.models import Q
from typing import List

## Todo: NE FELEJTSD EL ODAíRNI A VÉGÉRE A T-t!!!!!!!
gmaps = Client(key=os.environ.get("GOOGLE_MAPS_API_KE"))


class Generation:
    class Individual:
        class Chromosome:
            def __init__(self, dates, id=0, zip=None, date=None, felmero=None):
                self.id = id
                self.dates: List[datetime] = dates
                self.date: datetime = date
                self.zip = zip
                self.felmero: Salesmen = felmero

            def random_date(self):
                if self.dates:
                    if len(self.dates) == 1:
                        return self.dates[0]
                    return (
                        self.dates[np.random.randint(low=0, high=len(self.dates))]
                        if len(self.dates) != 0
                        else self.dates[0]
                    )
                return None

            def __str__(self):
                return str(self.__dict__)

        def __init__(self, outer_instance, data=None):
            self.data = [self.Chromosome(**i.__dict__) for i in data if i is not None]
            self.outer_instace: Generation = outer_instance

        def sort_route(self):
            def sort_key(x: Generation.Individual.Chromosome):
                if isinstance(x.date, dt_date):
                    return x.date
                else:
                    return datetime.min.date()

            self.data.sort(key=sort_key)

        def __str__(self):
            return str(self.data)

        def calculate_distance(self):
            distances = []
            for i in range(len(self.data)):
                origin = 0 if i == 0 else self.data[i - 1].zip
                dest = self.data[i].zip
                distance = self.outer_instace.matrix.filter(
                    Q(origin_zip=origin, dest_zip=dest)
                    | Q(origin_zip=dest, dest_zip=origin)
                )
                if distance.exists():
                    distances.append(distance.first().duration)

            return sum(distances)

        def calculate_fitness(self):
            if self.calculate_distance() == 0:
                return 0
            return 1 / self.calculate_distance()

        def print_route(self, print_starting_city=False):
            route = [
                (
                    i.id,
                    i.zip,
                    f"{i.date.month}-{i.date.day}",
                )
                if i.zip != self.outer_instace.start_city or print_starting_city
                else " - "
                for i in self.data
                if i.date != "*"
            ]

            print(route)

        def mutate(self):
            size = len(self.data)
            data = self.data.copy()
            while True:
                i = np.random.randint(0, size)
                if len(data[i].dates):
                    if len(data[i].dates) == 1:
                        if data[i].dates[0] == "*":
                            new_date = self.outer_instace.get_possible_dates(data[i])
                    new_date = self.data[i].random_date()
                    data[i].date = new_date
                    Generation.Individual(data=data, outer_instance=self).sort_route()
                    break
            return self.data

    def count_appointments_on_date(self, date, salesman: Salesmen):
        return len(
            [
                i
                for i in self.data
                if i.date != "*"
                and i.date.date() == date
                and i.felmero == salesman.name
            ]
        )

    def check_working_hours(
        self, date, felmero: Salesmen, plus_time=0, chromosome=None
    ) -> List[datetime]:
        jobs_on_day = [
            i
            for i in self.data
            if i.date != "*" and i.date.date() == date and felmero == i.felmero
        ]
        possible_hours = []
        if jobs_on_day:
            jobs_on_day.sort(key=lambda x: x.date)

            first_appointment = jobs_on_day[0]
            if not is_number(first_appointment.zip):
                return
            z = self.matrix.filter(
                Q(
                    origin_zip=self.start_city,
                    dest_zip=float(first_appointment.zip),
                )
                | Q(
                    origin_zip=float(first_appointment.zip),
                    dest_zip=self.start_city,
                )
            )
            if not z.exists():
                return

            z = z.first().duration
            a = datetime.combine(
                date, datetime.strptime(self.first_appointment, "%H:%M").time()
            ) - timedelta(seconds=z)

            last_appointment = jobs_on_day[-1]
            x = self.matrix.filter(
                Q(
                    origin_zip=chromosome.zip,
                    dest_zip=last_appointment.zip,
                )
                | Q(
                    origin_zip=last_appointment.zip,
                    dest_zip=chromosome.zip,
                )
            )
            if not x.exists():
                return

            x = x.first().duration
            y = self.get_time_home(chromosome)
            b = (
                last_appointment.date.replace(minute=0, second=0)
                + max(timedelta(minutes=plus_time), timedelta(seconds=x))
                + timedelta(minutes=2 * self.time_for_one_appointment)
                + timedelta(seconds=y)
            )

            if b - a < timedelta(hours=self.number_of_work_hours) and b > a:
                possible_hours += [
                    round_to_30(
                        last_appointment.date
                        + timedelta(minutes=self.time_for_one_appointment)
                        + max(timedelta(seconds=x), timedelta(minutes=plus_time))
                    )
                ] + self.check_working_hours(
                    date,
                    plus_time=plus_time + 30,
                    felmero=felmero,
                    chromosome=chromosome,
                )
            return list(set(possible_hours))
        else:
            plus_time = 0
            time_home = self.get_time_home(chromosome)
            while True:
                if timedelta(minutes=plus_time) + timedelta(
                    seconds=time_home
                ) * 2 < timedelta(hours=self.number_of_work_hours):
                    possible_hours.append(
                        datetime.combine(
                            date,
                            datetime.strptime(self.first_appointment, "%H:%M").time(),
                        )
                        + timedelta(minutes=plus_time)
                    )
                    plus_time += 30
                else:
                    break
            return possible_hours

    def get_time_home(self, chromosome: Individual.Chromosome):
        time_home = self.matrix.filter(
            Q(origin_zip=self.start_city, dest_zip=chromosome.zip)
            | Q(
                origin_zip=chromosome.zip,
                dest_zip=self.start_city,
            )
        )
        if not time_home.exists():
            return
        return time_home.first().duration

    def get_gap_appointment(
        self, chromosome: Individual.Chromosome, date: dt_date, felmero: Salesmen
    ):
        jobs_on_day = [
            self.Individual.Chromosome(
                felmero=felmero,
                zip=self.start_city,
                id="XXX",
                date=datetime.combine(date, datetime.min.time()),
                dates=[],
            )
        ] + [
            i
            for i in self.data
            if i.date != "*" and i.date.date() == date and i.felmero == felmero
        ]
        possible_hours = []
        if jobs_on_day:
            jobs_on_day.sort(key=lambda x: x.date)
            for i in range(len(jobs_on_day)):
                if i + 1 == len(jobs_on_day):
                    continue
                job = jobs_on_day[i]
                next_job = jobs_on_day[i + 1]
                if is_number(job.zip) and is_number(next_job.zip):
                    num_job_zip = float(job.zip)
                    num_next_job_zip = float(next_job.zip)
                    x = self.matrix.filter(
                        Q(
                            origin_zip=num_job_zip,
                            dest_zip=chromosome.zip,
                        )
                        | Q(
                            origin_zip=chromosome.zip,
                            dest_zip=num_job_zip,
                        )
                    )
                    y = self.matrix.filter(
                        Q(
                            origin_zip=chromosome.zip,
                            dest_zip=num_next_job_zip,
                        )
                        | Q(
                            origin_zip=num_next_job_zip,
                            dest_zip=chromosome.zip,
                        )
                    )
                    if not x.exists() or not y.exists():
                        continue
                    x = x.first().duration
                    y = y.first().duration

                    time_between_jobs = (
                        (next_job.date - job.date)
                        if next_job.date > job.date
                        else timedelta(seconds=0)
                    )

                    plus_time = 0
                    while True:
                        time_of_appointment = round_to_30(
                            job.date
                            + timedelta(
                                minutes=(
                                    self.time_for_one_appointment
                                    if job.id != "XXX"
                                    else 0
                                )
                                + plus_time
                            )
                            + timedelta(seconds=x if job.id != "XXX" else 0)
                        )

                        if time_between_jobs >= timedelta(
                            minutes=self.time_for_one_appointment
                            * (2 if job.id != "XXX" else 1)
                            + plus_time
                        ) + timedelta(seconds=(x if job.id != "XXX" else 0) + y):
                            if time_of_appointment >= datetime.combine(
                                date,
                                datetime.strptime(
                                    self.first_appointment, "%H:%M"
                                ).time(),
                            ):
                                possible_hours.append(time_of_appointment)
                            plus_time += 30
                        else:
                            break
            return possible_hours

    def get_possible_dates(self, chromosome: Individual.Chromosome):
        possible_dates = []
        for date in self.dates:
            for felmero in self.qualified_salesmen:
                possible_dates_felmero = []
                if (
                    self.count_appointments_on_date(date, felmero)
                    < self.max_felmeres_per_day
                ):
                    gap_appointments = self.get_gap_appointment(
                        chromosome, date, felmero=felmero
                    )
                    if gap_appointments:
                        possible_dates_felmero += gap_appointments
                    a = self.check_working_hours(
                        date, felmero=felmero, chromosome=chromosome
                    )
                    if a:
                        possible_dates_felmero += a

                if possible_dates_felmero:
                    possible_dates.append({felmero: possible_dates_felmero})
        OpenSlots.objects.filter(external_id=chromosome.id).delete()
        for i in possible_dates:
            for j, k in i.items():
                for l in k:
                    OpenSlots(external_id=chromosome.id, at=l, user=j).save()
        return possible_dates

    def create_distance_matrix(self, test=False):
        for day in self.dates:
            adatlapok = [
                i
                for i in self.data
                if (i.dates == ["*"] or day in [j.date() for j in i.dates])
            ]
            addresses = [self.start_city] + [
                i.zip for i in adatlapok if len(i.dates) > 1 or i.date == "*"
            ]

            def sort_key(x: Generation.Individual.Chromosome):
                if isinstance(x.date, dt_date):
                    return x.date
                else:
                    return datetime.min.date()

            fixed_adatalapok = [
                i for i in adatlapok if len(i.dates) == 1 and i.date != "*"
            ]
            if fixed_adatalapok:
                for adatlap in fixed_adatalapok:
                    felmero_adatlapok = [
                        i for i in fixed_adatalapok if i.felmero == adatlap.felmero
                    ]
                    felmero_adatlapok.sort(key=sort_key)
                    for i in range(len(felmero_adatlapok)):
                        adatlap = felmero_adatlapok[i]
                        if i + 1 == len(felmero_adatlapok):
                            addresses.append(adatlap.zip)
                            continue
                        next_adatlap = felmero_adatlapok[i + 1]
                        if next_adatlap.date - adatlap.date > timedelta(hours=2):
                            addresses.append(adatlap.zip)
            for origin in list(set(addresses)):
                for destination in addresses:
                    if (
                        origin != destination
                        and is_number(origin)
                        and is_number(destination)
                    ):
                        if not Routes.objects.filter(
                            Q(origin_zip=origin, dest_zip=destination)
                            | Q(origin_zip=destination, dest_zip=origin)
                        ).exists():
                            if test:
                                save = Routes(
                                    origin_zip=origin,
                                    dest_zip=destination,
                                    distance=np.random.randint(0, 10000),
                                    duration=np.random.randint(0, 10000),
                                )
                            else:
                                response = gmaps.routes(
                                    origin=origin, destination=destination
                                )
                                save = Routes(
                                    origin_zip=origin,
                                    dest_zip=destination,
                                    distance=response[0].distance_meters,
                                    duration=response[0].parse_duration(),
                                )
                            save.save()

    def generate_route(self):
        routes = None
        for day in self.dates:
            day_cities = self.Individual(
                outer_instance=self,
                data=[i for i in self.data if i.date == "*" or i.date == day],
            )
            home = self.Individual.Chromosome(
                date=day,
                dates=[],
            )

            day_cities = self.Individual(
                data=([home] + day_cities.data + [home]), outer_instance=self
            )

            self.Individual(data=day_cities.data, outer_instance=self).sort_route()
            if routes is None:
                routes = self.Individual(data=day_cities.data, outer_instance=self)
            else:
                routes = self.Individual(
                    data=routes.data + day_cities.data, outer_instance=self
                )

        return routes

    def __init__(
        self,
        start_city,
        initial_population_size,
        population_size,
        max_generations,
        tournament_size,
        max_felmeres_per_day,
        number_of_work_hours,
        time_for_one_appointment,
        first_appointment,
        needed_skill: Skills,
        data: List[Individual.Chromosome],
        fixed_appointments: List[Individual.Chromosome],
    ):
        # Parameters
        self.population_size = population_size
        self.max_generations = max_generations
        self.tournament_size = tournament_size
        self.initial_population_size = initial_population_size
        self.start_city = start_city
        self.max_felmeres_per_day = max_felmeres_per_day
        self.number_of_work_hours = number_of_work_hours
        self.time_for_one_appointment = time_for_one_appointment
        self.first_appointment = first_appointment
        self.needed_skill = needed_skill
        self.data = data
        self.fixed_appointments = fixed_appointments

        self.qualified_salesmen = [
            i
            for i in Salesmen.objects.all()
            if UserSkills.objects.filter(user=i, skill=self.needed_skill).exists()
        ]

        self.dates = list(
            set(
                [
                    (datetime.now() + timedelta(days=date)).date()
                    for date in range(31)
                    if any(
                        [
                            len(
                                [
                                    j
                                    for i in fixed_appointments
                                    if i.felmero == felmero
                                    for j in i.dates
                                    if j.date()
                                    == (datetime.now() + timedelta(days=date)).date()
                                ]
                            )
                            < self.max_felmeres_per_day
                            for felmero in Salesmen.objects.all()
                        ]
                    )
                    and (datetime.now() + timedelta(days=date)).date().weekday() < 5
                ]
                + [i.date.date() for i in fixed_appointments]
            )
        )

        self.population = [
            self.generate_route() for _ in range(self.initial_population_size)
        ]
        self.start_city = start_city
        self.matrix = Routes.objects.all()

    def crossover(self, parent1: Individual, parent2: Individual):
        size = len(parent1.data)
        child = self.Individual(data=parent2.data.copy(), outer_instance=self)
        while True:
            start, end = sorted(np.random.choice(range(size), size=2, replace=False))
            if (
                len([i for i in range(start, end) if len(parent1.data[i].dates)])
                and start != end
            ):
                break

        for i in range(start, end):
            if len(parent1.data[i].dates):
                child_gene = [
                    j for j in child.data if j.adatlap.Id == parent1.data[i].adatlap.Id
                ]
                child_gene[0].date = parent1.data[i].date
                child.sort_route()

        return child

    def main(self, test=False):
        self.create_distance_matrix(test)
        for _ in range(self.max_generations):
            new_population = []
            for _ in range(population_size):
                parent1, parent2 = (
                    self.tournament_selection(),
                    self.tournament_selection(),
                )

                child = self.crossover(parent1, parent2)
                child = child.mutate()

                new_population.append(child)
            population = new_population

        fitnesses = [route.calculate_fitness() for route in self.population]

        best_route_index = np.argmax(fitnesses)

        best_route = population[best_route_index]
        return self.Individual(data=best_route, outer_instance=self)

    def tournament_selection(self):
        indices = np.random.choice(len(self.population), self.tournament_size)
        tournament_individuals = [self.population[i] for i in indices]
        tournament_fitnesses = [self.population[i].calculate_fitness() for i in indices]

        winner_index = np.argmax(tournament_fitnesses)
        return tournament_individuals[winner_index]


class MiniCRMConnector:
    def __init__(
        self,
        date_field,
        zip_field,
        felmero_field,
        id_field,
        fixed_appointment_condition,
        new_aplicant_condition,
    ):
        self.date_field = date_field
        self.zip_field = zip_field
        self.felmero_field = felmero_field
        self.id_field = id_field
        self.fixed_appointment_condition = fixed_appointment_condition
        self.new_aplicant_condition = new_aplicant_condition
        self.appointments = Appointments.objects.all()

    def fix_appointments(self) -> List[Generation.Individual.Chromosome]:
        return [
            Generation.Individual.Chromosome(
                dates=[i[self.date_field]],
                date=i[self.date_field],
                id=i[self.id_field],
                zip=i[self.zip_field],
                felmero=Salesmen.objects.get(name=i[self.felmero_field]),
            )
            for i in MiniCrmAdatlapok.objects.filter(
                ~Q(
                    Id__in=[
                        i.external_id for i in self.appointments.distinct("external_id")
                    ]
                ),
                Deleted=0,
            ).values()
            if self.fixed_appointment_condition(i) and i[self.felmero_field]
        ]

    def main(self) -> List[Generation.Individual.Chromosome]:
        new_applicants = [
            Generation.Individual.Chromosome(
                dates=["*"],
                id=i[self.id_field],
                zip=i[self.zip_field],
                felmero=Salesmen.objects.get(name=i[self.felmero_field]),
            )
            for i in MiniCrmAdatlapok.objects.filter(
                ~Q(Id__in=[i.external_id for i in self.appointments]),
                Deleted=0,
            ).values()
            if self.new_aplicant_condition(i) and i[self.felmero_field]
        ]
        data = []
        for i in (
            [
                Generation.Individual.Chromosome(
                    dates=[
                        j.date
                        for j in self.appointments
                        if j.external_id == i.external_id
                    ],
                    zip=MiniCrmAdatlapok.objects.filter(Id=i.external_id).values()[0][
                        self.zip_field
                    ],
                    date=MiniCrmAdatlapok.objects.filter(Id=i.external_id).values()[0][
                        self.date_field
                    ],
                    felmero=Salesmen.objects.get(
                        name=MiniCrmAdatlapok.objects.filter(Id=i.external_id).values()[
                            0
                        ][self.felmero_field],
                    ),
                    id=i.external_id,
                )
                for i in self.appointments.distinct("external_id")
            ]
            + self.fix_appointments()
            + new_applicants
        ):
            attr = i.__dict__.copy()
            attr["date"] = i.random_date()
            data.append(
                Generation.Individual.Chromosome(
                    **attr,
                )
            )

        return data


population_size = 1
initial_population_size = 1
max_generations = 1
tournament_size = 1

number_of_work_hours = 8
time_for_one_appointment = 90
max_felmeres_per_day = 5
first_appointment = "08:00"
start_city = 2181
needed_skill = Skills.objects.get(id=1)
minicrm_conn = MiniCRMConnector(
    felmero_field="Felmero2",
    date_field="FelmeresIdopontja2",
    id_field="Id",
    zip_field="Iranyitoszam",
    fixed_appointment_condition=lambda x: x["FelmeresIdopontja2"] is not None
    and x["StatusId"] not in ["3086", "2929"],
    new_aplicant_condition=lambda x: x["FelmeresIdopontja2"] is None
    and x["StatusId"] not in ["3086", "2929"],
)

result = Generation(
    start_city=start_city,
    initial_population_size=initial_population_size,
    max_generations=max_generations,
    tournament_size=tournament_size,
    population_size=population_size,
    max_felmeres_per_day=max_felmeres_per_day,
    number_of_work_hours=number_of_work_hours,
    time_for_one_appointment=time_for_one_appointment,
    first_appointment=first_appointment,
    needed_skill=needed_skill,
    data=minicrm_conn.main(),
    fixed_appointments=minicrm_conn.fix_appointments(),
).get_possible_dates(Generation.Individual.Chromosome(id=44244, dates=["*"], zip=2120))
