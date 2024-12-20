import os
import random
import time
from datetime import date as dt_date
from datetime import datetime, timedelta
from typing import List
from multiprocessing import Pool, freeze_support, cpu_count

import numpy as np
from django.db.models import Q
from django import db

from ..utils.logs import log
from ..models import (
    BestSlots,
    MiniCrmAdatlapok,
    Routes,
    Salesmen,
    SchedulerSettings,
    Skills,
    Slots,
    UnschedulableTimes,
    UserSkills,
    Chromosomes as ChromosomeModel,
)
from ..utils.google_routes import Client
from ..utils.utils import round_to_30

## Todo: NE FELEJTSD EL ODAíRNI A VÉGÉRE A Y-t!!!!!!!
gmaps = Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))


from datetime import timedelta
import time
from django.db import OperationalError


class Generation:
    class Individual:
        class Chromosome:
            def __init__(
                self,
                dates,
                external_id=0,
                zip=None,
                date=None,
                felmero: Salesmen | None = None,
            ):
                # Validate external_id is an integer
                if not isinstance(external_id, str) and not isinstance(
                    external_id, int
                ):
                    raise ValueError("external_id must be an integer")

                # Validate dates is a list of datetime objects
                if not all(isinstance(d, datetime) or d == "*" for d in dates):
                    raise ValueError("dates must be a list of datetime objects")

                # Validate zip is a string and follows a specific format (e.g., 5 digits)
                if zip is not None and type(zip) != str:
                    raise ValueError("zip must be a 5-digit string")

                # Validate felmero is an instance of Salesmen
                if felmero is not None and not isinstance(felmero, Salesmen):
                    raise ValueError("felmero must be an instance of Salesmen")

                if date is not None and not isinstance(date, datetime) and date != "*":
                    raise ValueError("date must be a datetime object or None")

                self.external_id = external_id
                self.dates: List[datetime] = dates
                self.date: datetime = date
                self.zip: str = zip
                self.felmero: Salesmen = felmero

            def random_date(self):
                if not self.dates:
                    return None
                if len(self.dates) == 1:
                    return self.dates[0]

                available_dates = [d for d in self.dates if d != self.date]
                return random.choice(available_dates) if available_dates else None

            def __str__(self):
                return str(self.__dict__)

        def __init__(self, outer_instance, data=None):
            if data:
                self.data = [
                    self.Chromosome(**i.__dict__) for i in data if i is not None
                ]
            else:
                self.data = None
            self.outer_instace: Generation = outer_instance

        def __eq__(self, other):
            self.sort_route()
            other.sort_route()
            for i in range(len(self.data)):
                if (
                    self.data[i].date != other.data[i].date
                    or self.data[i].felmero != other.data[i].felmero
                ):
                    return False
            return True

        def sort_route(self):
            def sort_key(x: Generation.Individual.Chromosome):
                if isinstance(x.date, dt_date):
                    return x.date
                else:
                    return datetime.combine(dt_date.today(), datetime.min.time())

            self.data.sort(key=sort_key)

        def __str__(self):
            return str(self.data)

        def calculate_distance(self):
            distances = []
            for i in self.outer_instace.qualified_salesmen:
                data = [k for k in self.data if k.felmero == i]
                for j in range(len(data)):
                    origin = 0 if j == 0 else data[j - 1].zip
                    dest = data[j].zip
                    if origin and dest:
                        distance = [
                            route
                            for route in self.outer_instace.all_routes
                            if (route.origin_zip == origin and route.dest_zip == dest)
                            or (route.origin_zip == dest and route.dest_zip == origin)
                        ]
                        if distance:
                            distances.append(distance[0].duration)

            return sum(distances)

        def calculate_fitness(self):
            distance = self.calculate_distance()
            if distance == 0:
                return 0
            return 1 / distance

        def print_route(self, print_starting_city=False):
            route = [
                (
                    (
                        i.date,
                        i.external_id,
                        i.zip,
                    )
                    if i.external_id != 0 or print_starting_city
                    else " - "
                )
                for i in self.data
            ]

            print(route)

        def mutate(self):
            size = len(self.data)
            num_actual_mutations = 0
            while num_actual_mutations < self.outer_instace.mutation_range:
                start = np.random.randint(0, size)
                dates = self.data[start].dates
                if len(dates):
                    if len(dates) == 1:
                        if dates[0] == "*":
                            possible_dates = Generation.Individual(
                                data=self.outer_instace.data,
                                outer_instance=self.outer_instace,
                            ).get_possible_dates(self.data[start])
                            if possible_dates:
                                new_date = possible_dates[
                                    np.random.randint(low=0, high=len(possible_dates))
                                ]
                                self.data[start].date = new_date["date"]
                                self.data[start].felmero = new_date["felmero"]
                                num_actual_mutations += 1
                    else:
                        new_date = self.data[start].random_date()
                        self.data[start].date = new_date
                    self.sort_route()
            print("Mutációk száma: " + str(num_actual_mutations) + "/10")
            return self

        def get_gap_appointment(
            self, chromosome: Chromosome, date: dt_date, felmero: Salesmen
        ):
            all_routes = self.outer_instace.all_routes
            jobs_on_day = [
                self.Chromosome(
                    felmero=felmero,
                    zip=felmero.zip,
                    external_id="XXX",
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
                len_jobs_on_day = len(jobs_on_day)
                for i in range(len_jobs_on_day):
                    if i + 1 == len_jobs_on_day:
                        continue
                    job = jobs_on_day[i]
                    next_job = jobs_on_day[i + 1]
                    if job.zip and next_job.zip:
                        x = [
                            route
                            for route in all_routes
                            if (
                                (
                                    route.origin_zip == job.zip
                                    and route.dest_zip == chromosome.zip
                                )
                                or (
                                    route.origin_zip == chromosome.zip
                                    and route.dest_zip == job.zip
                                )
                            )
                        ]

                        y = [
                            route
                            for route in all_routes
                            if (
                                (
                                    route.origin_zip == chromosome.zip
                                    and route.dest_zip == next_job.zip
                                )
                                or (
                                    route.origin_zip == next_job.zip
                                    and route.dest_zip == chromosome.zip
                                )
                            )
                        ]

                        if not x or not y:
                            continue
                        x = x[0].duration
                        y = y[0].duration

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
                                        self.outer_instace.time_for_one_appointment
                                        if job.external_id != "XXX"
                                        else 0
                                    )
                                    + plus_time
                                )
                                + timedelta(
                                    seconds=x if job.external_id != "XXX" else 0
                                )
                            )

                            if time_between_jobs >= timedelta(
                                minutes=self.outer_instace.time_for_one_appointment
                                * (2 if job.external_id != "XXX" else 1)
                                + plus_time
                            ) + timedelta(
                                seconds=(x if job.external_id != "XXX" else 0) + y
                            ):
                                if time_of_appointment >= datetime.combine(
                                    date,
                                    datetime.strptime(
                                        self.outer_instace.first_appointment, "%H:%M"
                                    ).time(),
                                ) and self.is_appointment_schedulable(
                                    time_of_appointment, felmero
                                ):
                                    possible_hours.append(time_of_appointment)
                                plus_time += 30
                            else:
                                break
                return possible_hours

        def is_appointment_schedulable(self, appointment_time: dt_date, user: Salesmen):
            unschedulable_times = [
                i
                for i in self.outer_instace.all_unschedulable_times
                if i.user == user or i.user is None
            ]
            for unschedulable_time in unschedulable_times:
                repeat_time = unschedulable_time.repeat_time
                from_field = unschedulable_time.from_field
                to = unschedulable_time.to

                if repeat_time:
                    duration = to - from_field

                    for i in range(len(self.outer_instace.dates)):
                        date: datetime = from_field + timedelta(days=repeat_time * i)
                        if date.date() not in self.outer_instace.dates:
                            if date.date() > max(self.outer_instace.dates):
                                break
                            continue
                        if date <= appointment_time < date + duration:
                            return False
                else:
                    if from_field <= appointment_time <= to:
                        return False
            return True

        def get_possible_dates(self, chromosome: Chromosome):
            MAX_RETRIES = 5

            for attempt in range(MAX_RETRIES):
                try:
                    Slots.objects.filter(external_id=chromosome.external_id).delete()
                    break
                except OperationalError:
                    if attempt < MAX_RETRIES - 1:
                        continue
                    else:
                        raise
            possible_dates = []
            slots_to_save = []
            for date in self.outer_instace.dates:
                if date < datetime.date(
                    datetime.now()
                    + timedelta(days=self.outer_instace.selection_within_time_period)
                ):
                    continue
                for felmero in self.outer_instace.qualified_salesmen:
                    if (
                        self.count_appointments_on_date(date, felmero)
                        < self.outer_instace.max_appointment_per_day
                    ):
                        gap_appointments = self.get_gap_appointment(
                            chromosome, date, felmero=felmero
                        )
                        if gap_appointments:
                            for i in gap_appointments:
                                possible_dates.append({"felmero": felmero, "date": i})
                                slots_to_save.append(
                                    Slots(
                                        external_id=chromosome.external_id,
                                        at=i,
                                        user=felmero,
                                    )
                                )
                        a = self.check_working_hours(
                            date, felmero=felmero, chromosome=chromosome
                        )
                        if a:
                            for i in a:
                                possible_dates.append({"felmero": felmero, "date": i})
                                slots_to_save.append(
                                    Slots(
                                        external_id=chromosome.external_id,
                                        at=i,
                                        user=felmero,
                                    )
                                )

            def create_slots_with_retry(slots_to_save):
                max_retries = 3
                retry_delay = 1

                for retry in range(max_retries):
                    try:
                        Slots.objects.bulk_create(slots_to_save)
                        break
                    except OperationalError as e:
                        if retry < max_retries - 1:
                            print(
                                f"Encountered OperationalError: {e}. Retrying in {retry_delay} seconds..."
                            )
                            time.sleep(retry_delay)
                        else:
                            raise

            create_slots_with_retry(slots_to_save)
            return possible_dates

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
            self,
            date,
            felmero: Salesmen,
            plus_time=0,
            chromosome: Chromosome = None,
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
                if not first_appointment.zip:
                    return
                z = [
                    route
                    for route in self.outer_instace.all_routes
                    if (
                        (
                            route.origin_zip == felmero.zip
                            and route.dest_zip == first_appointment.zip
                        )
                        or (
                            route.origin_zip == first_appointment.zip
                            and route.dest_zip == felmero.zip
                        )
                    )
                ]
                if not z:
                    return

                z = z[0].duration
                a = min(
                    datetime.combine(
                        date,
                        datetime.strptime(
                            self.outer_instace.first_appointment, "%H:%M"
                        ).time(),
                    ),
                    first_appointment.date - timedelta(seconds=z),
                )

                last_appointment = jobs_on_day[-1]
                x = [
                    route
                    for route in self.outer_instace.all_routes
                    if (
                        (
                            route.origin_zip == chromosome.zip
                            and route.dest_zip == last_appointment.zip
                        )
                        or (
                            route.origin_zip == last_appointment.zip
                            and route.dest_zip == chromosome.zip
                        )
                    )
                ]

                if not x:
                    return

                x = x[0].duration
                y = self.get_time_home(chromosome, felmero=felmero)
                if not y:
                    return
                b = (
                    last_appointment.date.replace(minute=0, second=0)
                    + max(timedelta(minutes=plus_time), timedelta(seconds=x))
                    + timedelta(minutes=2 * self.outer_instace.time_for_one_appointment)
                    + timedelta(seconds=y)
                )

                if (
                    b - a < timedelta(hours=self.outer_instace.number_of_work_hours)
                    and b > a
                ):
                    if self.is_appointment_schedulable(
                        last_appointment.date
                        + timedelta(minutes=self.outer_instace.time_for_one_appointment)
                        + max(timedelta(seconds=x), timedelta(minutes=plus_time)),
                        felmero,
                    ):
                        possible_hours += [
                            round_to_30(
                                last_appointment.date
                                + timedelta(
                                    minutes=self.outer_instace.time_for_one_appointment
                                )
                                + max(
                                    timedelta(seconds=x), timedelta(minutes=plus_time)
                                )
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
                time_home = self.get_time_home(chromosome, felmero=felmero)
                if not time_home:
                    return possible_hours
                while True:
                    if timedelta(minutes=plus_time) + timedelta(
                        seconds=time_home
                    ) * 2 < timedelta(
                        hours=self.outer_instace.number_of_work_hours
                    ) and self.is_appointment_schedulable(
                        datetime.combine(
                            date,
                            datetime.strptime(
                                self.outer_instace.first_appointment, "%H:%M"
                            ).time(),
                        )
                        + timedelta(minutes=plus_time),
                        felmero,
                    ):
                        possible_hours.append(
                            datetime.combine(
                                date,
                                datetime.strptime(
                                    self.outer_instace.first_appointment, "%H:%M"
                                ).time(),
                            )
                            + timedelta(minutes=plus_time)
                        )
                        plus_time += 30
                    else:
                        break
                return possible_hours

        def get_time_home(self, chromosome: Chromosome, felmero: Salesmen = None):
            time_home = [
                route
                for route in self.outer_instace.all_routes
                if (
                    (
                        route.origin_zip == felmero.zip
                        and route.dest_zip == chromosome.zip
                    )
                    or (
                        route.origin_zip == chromosome.zip
                        and route.dest_zip == felmero.zip
                    )
                )
            ]

            if not time_home:
                return

            return time_home[0].duration

    def create_distance_matrix(self, test=False):
        print("Creating distance matrix...")
        num_requests = 0
        for day in self.dates:
            adatlapok = [
                i
                for i in self.data
                if (i.dates == ["*"] or day in [j.date() for j in i.dates])
            ]
            addresses: List[str] = [i.zip for i in self.qualified_salesmen] + [
                i.zip for i in adatlapok if len(i.dates) > 1 or i.date == "*"
            ]

            def sort_key(x: Generation.Individual.Chromosome):
                return x.date if isinstance(x.date, dt_date) else datetime.min.date()

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

                        if (
                            next_adatlap.date - adatlap.date
                            >= timedelta(minutes=self.time_for_one_appointment)
                            or i == 0
                        ):
                            addresses.append(adatlap.zip)
            for origin in list(set(addresses)):
                for destination in addresses:
                    if origin != destination:
                        if not len(
                            [
                                route
                                for route in self.all_routes
                                if (
                                    (
                                        route.origin_zip == origin
                                        and route.dest_zip == destination
                                    )
                                    or (
                                        route.origin_zip == destination
                                        and route.dest_zip == origin
                                    )
                                )
                            ]
                        ):
                            if test:
                                save = Routes(
                                    origin_zip=origin,
                                    dest_zip=destination,
                                    distance=np.random.randint(0, 10000),
                                    duration=np.random.randint(0, 10000),
                                )
                            else:
                                num_requests += 1
                                print(num_requests)
                                response = gmaps.routes(
                                    origin=origin, destination=destination
                                )
                                save = Routes(
                                    origin_zip=origin,
                                    dest_zip=destination,
                                    distance=response.routes[0].distance_meters,
                                    duration=response.routes[0].parse_duration(),
                                )
                            self.all_routes.append(save)
                            save.save()
        print("Requestek száma: " + str(num_requests))

    def generate_route(self):
        routes = self.Individual(self)
        for day in self.dates:

            def get_homes(start=True):
                return [
                    self.Individual.Chromosome(
                        date=datetime.combine(
                            day, datetime.min.time() if start else datetime.max.time()
                        ),
                        dates=[],
                        zip=i.zip,
                        felmero=i,
                    )
                    for i in self.qualified_salesmen
                ]

            day_cities = self.Individual(
                outer_instance=self,
                data=[i for i in self.data if i.date == "*" or i.date.date() == day],
            )
            day_cities = self.Individual(
                data=(
                    get_homes()
                    + (day_cities.data if day_cities.data else [])
                    + get_homes(start=False)
                ),
                outer_instance=self,
            )

            self.Individual(data=day_cities.data, outer_instance=self).sort_route()
            if routes.data is None:
                routes = self.Individual(data=day_cities.data, outer_instance=self)
            else:
                routes = self.Individual(
                    data=routes.data + day_cities.data, outer_instance=self
                )

        return routes

    def __init__(
        self,
        initial_population_size=None,
        population_size=None,
        max_generations=None,
        tournament_size=None,
        max_appointment_per_day=0,
        number_of_work_hours=None,
        time_for_one_appointment=None,
        first_appointment=None,
        needed_skill: Skills = Skills(),
        data: List[Individual.Chromosome] = [],
        fixed_appointments: List[Individual.Chromosome] = [],
        plan_timespan=31,
        num_best_slots=5,
        allow_weekends=False,
        selection_within_time_period=3,
        elitism_size=10,
        mutation_range=5,
    ):
        # Parameters
        self.population_size = population_size
        self.max_generations = max_generations
        self.tournament_size = tournament_size
        self.initial_population_size = initial_population_size
        self.max_appointment_per_day = max_appointment_per_day
        self.number_of_work_hours = number_of_work_hours
        self.time_for_one_appointment = time_for_one_appointment
        self.first_appointment = first_appointment
        self.needed_skill = needed_skill
        self.data = data
        self.fixed_appointments = fixed_appointments
        self.plan_timespan = plan_timespan
        self.num_best_slots = num_best_slots
        self.allow_weekends = allow_weekends
        self.selection_within_time_period = selection_within_time_period
        self.elitism_size = elitism_size
        self.mutation_range = mutation_range

        self.qualified_salesmen = [
            i
            for i in Salesmen.objects.all()
            if UserSkills.objects.filter(user=i, skill=self.needed_skill).exists()
        ]

        self.dates: List[dt_date] = list(
            set(
                [
                    (datetime.now() + timedelta(days=date)).date()
                    for date in range(self.plan_timespan)
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
                            < self.max_appointment_per_day
                            for felmero in Salesmen.objects.all()
                        ]
                    )
                    and (
                        (datetime.now() + timedelta(days=date)).date().weekday() < 5
                        or self.allow_weekends
                    )
                ]
                + [i.date.date() for i in fixed_appointments if i.date > datetime.now()]
            )
        )

        self.all_routes = list(Routes.objects.all())
        self.all_unschedulable_times = list(UnschedulableTimes.objects.all())

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
                    j
                    for j in child.data
                    if j.external_id == parent1.data[i].external_id
                ]
                child_gene[0].date, child_gene[0].felmero = (
                    parent1.data[i].date,
                    parent1.data[i].felmero,
                )
                child.sort_route()

        return child

    def assign_new_applicants_dates(self):
        for i in self.data:
            if i.dates == ["*"]:
                possible_dates = self.Individual(
                    data=self.data, outer_instance=self
                ).get_possible_dates(i)
                if possible_dates:
                    num_possible_dates = len(possible_dates)
                    rand_date = possible_dates[
                        np.random.randint(low=0, high=num_possible_dates)
                    ]
                    i.date = rand_date["date"]
                    i.felmero = rand_date["felmero"]

    def generate_individual(self):
        self.assign_new_applicants_dates()
        return self.generate_route()

    def generate_individuals_batch(self, batch_size):
        """Generate a batch of individuals."""
        return [self.generate_individual() for _ in range(batch_size)]

    def generate_initial_population_batched(self, num_processes=None):
        batch_size = 10
        num_full_batches = self.population_size // batch_size
        remainder = self.population_size % batch_size

        batch_sizes = [batch_size] * num_full_batches
        if remainder > 0:
            batch_sizes.append(remainder)

        with Pool(processes=num_processes) as pool:
            population_batches = pool.map(self.generate_individuals_batch, batch_sizes)

        population = [
            individual for batch in population_batches for individual in batch
        ]
        return population

    def main(self, test=False):
        start_time = time.time()

        num_process = cpu_count()
        if not test:
            self.create_distance_matrix(test)

        self.population = self.generate_initial_population_batched(
            num_processes=num_process
        )
        print(
            "Initial population length: " + str(len([i for i in self.population if i]))
        )

        for _ in range(self.max_generations):
            self.run_one_generation()
        print("Population length: " + str(len(self.population)))

        print("Calculating fitnesses...")
        fitnesses = np.array([route.calculate_fitness() for route in self.population])

        sorted_fitnesses = np.argsort(fitnesses)[::-1]
        sorted_population: List[Generation.Individual] = [
            self.population[i] for i in sorted_fitnesses
        ]
        print("Sorted population len:" + str(len(sorted_population)))

        ChromosomeModel.objects.all().delete()
        ChromosomeModel.objects.bulk_create(
            [
                ChromosomeModel(
                    level=i + 1,
                    duration=individual.calculate_distance(),
                    **chromosome.__dict__,
                )
                for i, individual in enumerate(sorted_population)
                for chromosome in individual.data
            ]
        )
        BestSlots.objects.all().delete()

        self.process_individuals(sorted_population)

        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")

    def create_or_get_slot(self, chromosome: Individual.Chromosome):
        slot, _ = Slots.objects.get_or_create(
            external_id=chromosome.external_id,
            at=chromosome.date,
            user=chromosome.felmero,
        )
        return slot

    def process_individuals(self, population: List[Individual]):
        saved_slots = {}
        print("Processing individuals...")
        for item in self.data:
            if item.dates == ["*"]:
                for individual in population:
                    for chromosome in individual.data:
                        if str(chromosome.external_id) == str(item.external_id):
                            if chromosome.date != "*" and (
                                chromosome.date.strftime("%Y-%m-%d %H:%M")
                                + " - "
                                + (
                                    chromosome.felmero.name
                                    if chromosome.felmero
                                    else ""
                                )
                            ) not in saved_slots.get(chromosome.external_id, []):
                                slot = self.create_or_get_slot(chromosome)
                                saved_slots[chromosome.external_id] = saved_slots.get(
                                    chromosome.external_id, []
                                ) + [
                                    chromosome.date.strftime("%Y-%m-%d %H:%M")
                                    + " - "
                                    + chromosome.felmero.name
                                ]
                                level = len(saved_slots.get(chromosome.external_id, 0))

                                BestSlots(
                                    slot=slot,
                                    level=level,
                                ).save()

    def evaluate_fitness_wrapper(self, individual: Individual):
        # Wrapper function to evaluate fitness of an individual
        return individual.calculate_fitness()

    def generate_child(self, parents):
        db.connections.close_all()  # Close existing connections
        parent1, parent2 = parents
        print("Crossover...")
        child = self.crossover(parent1, parent2)
        print("Mutation...")
        return child.mutate()

    def run_one_generation(self):
        num_processes = cpu_count()
        pool = Pool(processes=num_processes)

        fitnesses = pool.map(self.evaluate_fitness_wrapper, self.population)

        sorted_fitnesses = np.argsort(fitnesses)[::-1]
        population: List[Generation.Individual] = [
            self.population[i] for i in sorted_fitnesses
        ]

        elites = population[: self.elitism_size]

        parents = [
            (self.tournament_selection(), self.tournament_selection())
            for _ in range(population_size)
        ]

        new_population = pool.map(self.generate_child, parents)

        self.population = new_population + elites

    def tournament_selection(self):
        if not self.population:
            return None
        indices = np.random.choice(len(self.population), self.tournament_size)
        tournament_individuals: List[Generation.Individual] = [
            self.population[i] for i in indices
        ]
        tournament_fitnesses = [
            self.population[i].calculate_fitness()
            for i in indices
            if self.population[i] is not None
        ]
        if not tournament_fitnesses:
            return None

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
        self.appointments = Slots.objects.filter(booked=True)

    def fix_appointments(self) -> List[Generation.Individual.Chromosome]:
        appointments: List[Generation.Individual.Chromosome] = []
        for i in MiniCrmAdatlapok.objects.filter(
            ~Q(
                Id__in=[
                    i.external_id for i in self.appointments.distinct("external_id")
                ]
            ),
            Deleted=0,
        ).values():
            if len(appointments) > 10:
                break
            if (
                self.fixed_appointment_condition(i)
                and i[self.felmero_field]
                and i[self.date_field].date() > datetime.now().date()
            ):
                salesman = Salesmen.objects.filter(name=i[self.felmero_field])
                if not salesman.exists():
                    continue

                appointments.append(
                    Generation.Individual.Chromosome(
                        dates=[i[self.date_field]],
                        date=i[self.date_field],
                        external_id=i[self.id_field],
                        zip=i[self.zip_field],
                        felmero=salesman.first(),
                    )
                )
        return appointments

    def main(self) -> List[Generation.Individual.Chromosome]:
        new_applicants = [
            Generation.Individual.Chromosome(
                dates=["*"],
                external_id=i[self.id_field],
                zip=i[self.zip_field],
            )
            for i in MiniCrmAdatlapok.objects.filter(
                ~Q(Id__in=[i.external_id for i in self.appointments]),
                Deleted=0,
            ).values()
            if self.new_aplicant_condition(i) and i[self.zip_field]
        ][:5]
        data: List[Generation.Individual.Chromosome] = []
        for i in (
            [
                Generation.Individual.Chromosome(
                    dates=[
                        j.at
                        for j in self.appointments
                        if j.external_id == i.external_id
                    ],
                    zip=MiniCrmAdatlapok.objects.filter(Id=i.external_id).values()[0][
                        self.zip_field
                    ],
                    date=MiniCrmAdatlapok.objects.filter(Id=i.external_id).values()[0][
                        self.date_field
                    ],
                    external_id=i.external_id,
                    felmero=i.user,
                )
                for i in self.appointments.distinct("external_id")
            ]
            + self.fix_appointments()
            + new_applicants
        ):
            if not i.zip:
                continue
            attr = i.__dict__.copy()
            attr["date"] = i.random_date()
            data.append(
                Generation.Individual.Chromosome(
                    **attr,
                )
            )

        return data


initial_population_size = 5
population_size = 5
max_generations = 10
tournament_size = 4
elitism_size = 10

number_of_work_hours = 8
time_for_one_appointment = 90
max_felmeres_per_day = 5
first_appointment = "08:00"
needed_skill = Skills.objects.get(id=1)
minicrm_conn = MiniCRMConnector(
    felmero_field="Felmero2",
    date_field="FelmeresIdopontja2",
    id_field="Id",
    zip_field="Iranyitoszam",
    fixed_appointment_condition=lambda x: x["FelmeresIdopontja2"] is not None
    and x["StatusId"] not in [3086, 2929]
    and x["Iranyitoszam"],
    new_aplicant_condition=lambda x: x["FelmeresIdopontja2"] is None
    and x["StatusId"] not in [3086, 2929]
    and x["Iranyitoszam"],
)
num_best_slots = 5
plan_timespan = 90
allow_weekends = SchedulerSettings.objects.get(name="Allow weekends").value == "1"
selection_within_time_period = 3
mutation_range = 10

fixed_appointments = minicrm_conn.fix_appointments()
result = Generation(
    initial_population_size=initial_population_size,
    max_generations=max_generations,
    tournament_size=tournament_size,
    population_size=population_size,
    max_appointment_per_day=max_felmeres_per_day,
    number_of_work_hours=number_of_work_hours,
    time_for_one_appointment=time_for_one_appointment,
    first_appointment=first_appointment,
    needed_skill=needed_skill,
    data=minicrm_conn.main(),
    fixed_appointments=fixed_appointments,
    plan_timespan=plan_timespan,
    num_best_slots=num_best_slots,
    allow_weekends=allow_weekends,
    selection_within_time_period=selection_within_time_period,
    elitism_size=elitism_size,
    mutation_range=mutation_range,
)


# Example usage:
if __name__ == "__main__":
    freeze_support()
    result.main(False)
