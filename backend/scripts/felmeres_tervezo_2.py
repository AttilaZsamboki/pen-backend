from ..utils.logs import log  # noqa

import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import numpy as np
from django import db
from django.db.models import Q

from ..models import BestSlots
from ..models import Chromosomes as ChromosomeModel
from ..models import (
    MiniCrmAdatlapok,
    Routes,
    Salesmen,
    SchedulerSettings,
    Skills,
    Slots,
    UnschedulableTimes,
    UserSkills,
)
from ..utils.google_routes import Client
from ..utils.utils import round_to_30

## Todo: NE FELEJTSD EL ODAíRNI A VÉGÉRE A Y-t!!!!!!!
gmaps = Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))


class Population:
    class Chromosome:

        @dataclass
        class Gene:
            dates: List[datetime]
            date: datetime = field(default=None)
            zip: str = field(default="")
            felmero: Salesmen = field(default=Salesmen())
            external_id: int = field(default=0)

            def random_date(self):
                if not self.dates:
                    return None
                if len(self.dates) == 1:
                    return self.dates[0]

                available_dates = [d for d in self.dates if d != self.date]
                return random.choice(available_dates) if available_dates else None

        def __init__(self, outer_instance, genes=None):
            if genes:
                self.genes = [self.Gene(**i.__dict__) if i else None for i in genes]
            else:
                self.genes = None
            self.outer_instace: Population = outer_instance

        def __eq__(self, other):
            self.sort_route()
            other.sort_route()
            for i in range(len(self.genes)):
                if (
                    self.genes[i].date != other.data[i].date
                    or self.genes[i].felmero != other.data[i].felmero
                ):
                    return False
            return True

        def set_data(self, data):
            self.genes = [self.Gene(**i.__dict__) for i in data if i is not None]
            return self

        def filter(self, **kwargs):
            return [
                i
                for i in self.genes
                if all([i.__dict__[k] == v for k, v in kwargs.items()])
            ]

        def __str__(self):
            return str(self.genes)

        def calculate_distance(self):
            distances = []
            for j in range(len(self.genes)):
                origin = 0 if j == 0 else self.genes[j - 1].zip
                dest = self.genes[j].zip
                if origin and dest:

                    # 0 time
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

        def mutate(self):
            mutate_rate = 0.025
            for i, gene in enumerate(self.genes):
                if i > len(self.genes) // 2:
                    mutate_rate = 0.05
                if np.random.rand() < mutate_rate:
                    self.swap(
                        gene, self.genes[np.random.randint(low=0, high=len(self.genes))]
                    )
            return self

        def swap(self, gene_1: Gene, gene_2: Gene):
            a, b = self.genes.index(gene_1), self.genes.index(gene_2)
            self.genes[b], self.genes[a] = self.genes[a], self.genes[b]

    def create_distance_matrix(self, test=False):
        print("Creating distance matrix...")
        num_requests = 0
        addresses: List[str] = [i.zip for i in self.initial_data]

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

    def generate_route(self, _):

        return self.Chromosome(
            outer_instance=self,
            genes=self.initial_data,
        )

    def __init__(
        self,
        initial_data: List[Chromosome.Gene] = [],
        initial_population_size=10,
        population_size=10,
        max_generations=10,
        tournament_size=2,
        max_appointment_per_day=5,
        number_of_work_hours=8,
        time_for_one_appointment=90,
        first_appointment="8:00",
        needed_skill: Skills = Skills.objects.get(id=1),
        fixed_appointments: List[Chromosome.Gene] = [],
        plan_timespan=90,
        num_best_slots=5,
        allow_weekends=False,
        selection_within_time_period=3,
        elitism_size=10,
        mutation_range=3,
        crossover_range=5,
        elitism=True,
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
        self.initial_data = initial_data
        self.fixed_appointments = fixed_appointments
        self.plan_timespan = plan_timespan
        self.num_best_slots = num_best_slots
        self.allow_weekends = allow_weekends
        self.selection_within_time_period = selection_within_time_period
        self.elitism_size = elitism_size
        self.mutation_range = mutation_range
        self.crossover_range = crossover_range
        self.elitism = elitism

        self.all_routes = list(Routes.objects.all())

    def crossover(self, parent_1: Chromosome, parent_2: Chromosome):
        def fill_with_parent1_genes(
            child: Population.Chromosome, parent: Population.Chromosome, genes_n: int
        ):
            start_at = np.random.randint(0, len(parent.genes) - genes_n - 1)
            finish_at = start_at + genes_n
            for i in range(start_at, finish_at):
                child.genes[i] = parent_1.genes[i]

        def fill_with_parent2_genes(child, parent):
            j = 0
            for i in range(0, len(parent.genes)):
                if child.genes[i] == None:
                    while parent.genes[j] in child.genes:
                        j += 1
                    child.genes[i] = parent.genes[j]
                    j += 1

        genes_n = len(parent_1.genes)
        child = Population.Chromosome(
            genes=[None for _ in range(genes_n)], outer_instance=self
        )
        fill_with_parent1_genes(child, parent_1, genes_n // 2)
        fill_with_parent2_genes(child, parent_2)

        return child

    def generate_individual(self):

        # util function that sorts that organizes the routes, it works or it doesnt, no need to test
        result = self.generate_route()
        # ----------------------------------------------------

        return result

    def main(self, test=False):
        start_time = time.time()

        # util function it works or it doesnt, no need to test
        if not test:
            self.create_distance_matrix(test)
        # ----------------------------------------------------

        # its not a 100% efficient, but it is not worth testing, the only thing that can go wrong is the random choice (not likely)
        self.population = list(
            map(self.generate_route, range(self.initial_population_size))
        )
        print(
            "Initial population length: " + str(len([i for i in self.population if i]))
        )
        # ----------------------------------------------------

        for _ in range(self.max_generations):
            self.run_one_generation()
        print("Population length: " + str(len(self.population)))

        self.process_individuals()

        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")

    def process_individuals(self):
        print("Calculating fitnesses...")
        fitnesses = np.array([route.calculate_fitness() for route in self.population])

        sorted_fitnesses = np.argsort(fitnesses)[::-1]
        sorted_population: List[Population.Chromosome] = [
            self.population[i] for i in sorted_fitnesses
        ]
        print("Sorted population len:" + str(len(sorted_population)))

        ChromosomeModel.objects.all().delete()
        ChromosomeModel.objects.bulk_create(
            [
                ChromosomeModel(
                    level=i + 1,
                    duration=individual.calculate_distance(),
                    **gene.__dict__,
                )
                for i, individual in enumerate(sorted_population)
                for gene in individual.genes
            ]
        )
        BestSlots.objects.all().delete()

    def generate_child(
        self,
        parents,
    ):
        db.connections.close_all()

        parent1, parent2 = parents

        # has been tested and it works
        child = self.crossover(parent1, parent2)
        # ----------------------------------------------------

        mutated_child = child.mutate()

        return mutated_child

    def get_parents(self, _):
        return (self.tournament_selection(), self.tournament_selection())

    def run_one_generation(self):
        start_time = time.time()

        # has been tested and it works, the efficiency can be improved
        start_fitness_time = time.time()
        fitnesses = [i.calculate_fitness() for i in self.population]
        end_fitness_time = time.time()
        print("Time to calculate fitnesses: ", end_fitness_time - start_fitness_time)
        # ----------------------------------------------------

        # Tested and works correctly, efficiency is also good (less than 0.00 seconds)
        sorted_fitnesses = np.argsort(fitnesses)[::-1]
        population: List[Population.Chromosome] = [
            self.population[i] for i in sorted_fitnesses
        ]
        # ----------------------------------------------------

        # Tested and works correctly, takes around 0.00 seconds
        parents = map(self.get_parents, range(self.population_size))
        # ----------------------------------------------------

        # Time is decent compared to this is the main function (around 7 seconds)
        start_new_population_time = time.time()
        new_population = list(map(self.generate_child, parents))
        end_new_population_time = time.time()
        print(
            "Time to generate new population: ",
            end_new_population_time - start_new_population_time,
        )
        # ----------------------------------------------------

        if self.elitism:
            self.population = new_population + population[: self.elitism_size]
        else:
            self.population = new_population + population

        end_time = time.time()
        print("Total time: ", end_time - start_time)

    def tournament_selection(self):
        if not self.population:
            return None
        indices = np.random.choice(len(self.population), self.tournament_size)
        tournament_individuals: List[Population.Chromosome] = [
            self.population[i] for i in indices
        ]
        tournament_fitnesses = [
            self.population[i].calculate_fitness()
            for i in indices
            if self.population[i] is not None
        ]
        if not tournament_fitnesses:
            print("Tournament fitnesses are empty")
            return None

        winner_index = np.argmax(tournament_fitnesses)
        return tournament_individuals[winner_index]


# class MiniCRMConnector:
#     def __init__(
#         self,
#         zip_field,
#         id_field,
#         new_aplicant_condition,
#     ):
#         self.zip_field = zip_field
#         self.id_field = id_field
#         self.new_aplicant_condition = new_aplicant_condition
#         self.appointments = Slots.objects.filter(booked=True)

#     def main(self) -> List[Population.Chromosome.Gene]:
#         return [
#             Population.Chromosome.Gene(
#                 external_id=i[self.id_field],
#                 zip=i[self.zip_field],
#             )
#             for i in MiniCrmAdatlapok.objects.filter(
#                 ~Q(Id__in=[i.external_id for i in self.appointments]),
#                 Deleted=0,
#             ).values()
#             if self.new_aplicant_condition(i) and i[self.zip_field]
#         ]


# Example usage:
if __name__ == "__main__":

    from .felmeres_tervezo import MiniCRMConnector

    minicrm_conn = MiniCRMConnector(
        id_field="Id",
        zip_field="Iranyitoszam",
        new_aplicant_condition=lambda x: x["FelmeresIdopontja2"] is None
        and x["StatusId"] not in [3086, 2929]
        and x["Iranyitoszam"],
        felmero_field="Felmero2",
        date_field="FelmeresIdopontja2",
        fixed_appointment_condition=lambda x: x["FelmeresIdopontja2"] is not None
        and x["StatusId"] not in [3086, 2929]
        and x["Iranyitoszam"]
        and x["Deleted"] == "0",
    )

    result = Population(
        initial_data=minicrm_conn.main(),
        max_generations=100,
        population_size=100,
    )
    result.main(False)
