import numpy as np
from ..utils.google_routes import Client, DistanceMatrix
import os
from ..utils.logs import log
from ..models import Appointments
from ..models import MiniCrmAdatlapok
from ..utils.utils import get_address
import json
from django.db.models import Q

gmaps = Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))


class Generation:
    class Individual:
        class Chromosome:
            def __init__(
                self, dates, id=0, address=None, fixed=None, adatlap=None, date=None
            ):
                self.id = id
                self.dates = dates
                self.date = date
                self.address = address
                self.fixed = fixed
                self.adatlap = adatlap

            def random_date(self):
                return (
                    self.dates[np.random.randint(low=0, high=len(self.dates))]
                    if len(self.dates) != 0
                    else self.dates[0]
                )

            def __str__(self):
                return str(self.__dict__)

        def __init__(self, outer_instance, data=None):
            self.data = [self.Chromosome(**i.__dict__) for i in data if i is not None]
            self.outer_instace = outer_instance

        def sort_route(self):
            self.data.sort(key=lambda x: x.date if x.date else 0)

        def __str__(self):
            return str(self.data)

        def calculate_distance(self):
            distances = []
            for i in range(len(self.data)):
                matrix = self.outer_instace.matrix[
                    self.data[i].date.replace(hour=0, minute=0)
                ]
                if matrix:
                    origin_idx = 0 if i == 0 else int(self.data[i - 1].id)
                    distance = matrix.get_element(
                        origin_idx=origin_idx,
                        destination_idx=int(self.data[i].id),
                    )
                    if distance:
                        distances.append(distance.get_duration_value())

            return sum(distances)

        def calculate_fitness(self):
            if self.calculate_distance() == 0:
                return 0
            return 1 / self.calculate_distance()

        def print_route(self, print_starting_city=False):
            route = [
                (
                    i.adatlap.Id,
                    i.address,
                    f"{i.date.month}-{i.date.day} {i.date.hour}H",
                )
                if i.address != "Budapest" or print_starting_city
                else " - "
                for i in self.data
            ]

            print(route)

        def mutate(self):
            size = len(self.data)
            data = self.data.copy()
            while True:
                i = np.random.randint(0, size)
                if not data[i].fixed and len(data[i].dates):
                    new_date = self.data[i].random_date()
                    data[i].date = new_date
                    Generation.Individual(data=data, outer_instance=self).sort_route()
                    break
            return self.data

    def create_distance_matrix(self, starting_city):
        addresses = [starting_city] + [i.address for i in self.data]
        dates = set([j.replace(hour=0, minute=0) for i in self.data for j in i.dates])
        result = {}
        for date in dates:
            addresses = [starting_city] + [
                i.address for i in self.data if i.date.replace(hour=0, minute=0) == date
            ]
            response = gmaps.distance_matrix(addresses, addresses)
            result[date] = response
        return result

    def generate_route(self, cities, dates):
        routes = None
        for day in dates:
            day_cities = self.Individual(
                outer_instance=self,
                data=[
                    i
                    for i in cities
                    if i.date.replace(hour=0, minute=0)
                    == day.date.replace(hour=0, minute=0)
                    and i.address is not None
                ],
            )
            home = self.Individual.Chromosome(
                id=0,
                date=day.date.replace(hour=0, minute=0),
                dates=[day.date.replace(hour=0, minute=0)],
                address=self.start_city,
                fixed=True,
                adatlap=MiniCrmAdatlapok(),
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
    ):
        # Parameters
        self.population_size = population_size
        self.max_generations = max_generations
        self.tournament_size = tournament_size
        self.initial_population_size = initial_population_size
        self.start_city = start_city

        # Data
        appointments = Appointments.objects.all()
        fixed_appointments = [
            self.Individual.Chromosome(
                dates=[i.FelmeresIdopontja2],
                address=get_address(i),
                fixed=True,
                adatlap=i,
            )
            for i in MiniCrmAdatlapok.objects.filter(
                ~Q(Id__in=[i.adatlap.Id for i in appointments.distinct("adatlap__Id")]),
                ~Q(StatusId__in=["2929", "3086"]),
                FelmeresIdopontja2__date__in=[
                    i.date.replace(hour=0, minute=0)
                    for i in appointments.distinct("adatlap__Id")
                ],
            )[:3]
        ]
        data = []
        for i in [
            self.Individual.Chromosome(
                dates=[j.date for j in appointments if j.adatlap.Id == i.adatlap.Id],
                address=get_address(i.adatlap),
                fixed=False,
                adatlap=i.adatlap,
            )
            for i in appointments.distinct("adatlap__Id")
        ] + fixed_appointments:
            attr = i.__dict__.copy()
            attr.pop("date")
            data.append(
                self.Individual.Chromosome(
                    date=i.random_date(),
                    **attr,
                )
            )
        self.data = data
        self.population = [
            self.generate_route(
                cities=[
                    self.Individual.Chromosome(
                        id=int(idx) + 1,
                        **{j: k for j, k in i.__dict__.items() if j != "id"},
                    )
                    for idx, i in enumerate(data)
                ],
                dates=Appointments.objects.all().distinct("date__date"),
            )
            for _ in range(self.initial_population_size)
        ]
        self.start_city = start_city
        self.matrix = self.create_distance_matrix(starting_city=start_city)

    def crossover(self, parent1, parent2):
        size = len(parent1.data)
        child = self.Individual(data=parent2.data.copy(), outer_instance=self)
        while True:
            start, end = sorted(np.random.choice(range(size), size=2, replace=False))
            if (
                len([i for i in range(start, end) if not parent1.data[i].fixed])
                and start != end
            ):
                break

        for i in range(start, end):
            if not parent1.data[i].fixed:
                child_gene = [
                    j for j in child.data if j.adatlap.Id == parent1.data[i].adatlap.Id
                ]
                child_gene[0].date = parent1.data[i].date
                child.sort_route()

        return child

    def main(self):
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


population_size = 1000
initial_population_size = 512
max_generations = 1000
tournament_size = 4
start_city = "Budapest"

result = Generation(
    start_city=start_city,
    initial_population_size=initial_population_size,
    max_generations=max_generations,
    tournament_size=tournament_size,
    population_size=population_size,
).main()
result.print_route()
