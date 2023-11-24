import math
import random
import numpy as np
import googlemaps
import os
from ..utils.logs import log
from ..models import Appointments
from ..models import MiniCrmAdatlapok
from ..utils.utils import get_address
from django.db.models import Q

gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))


def print_route(route):
    print(
        [
            (
                i["adatlap"].Id,
                i["address"],
                f"{i['date'].month}-{i['date'].day} {i['date'].hour}H",
            )
            if i["address"] != "Budapest"
            else " - "
            for i in route
        ]
    )
    return


def create_data():
    data = {}
    data["API_key"] = os.getenv("GOOGLE_MAPS_API_KEY")
    appointments = Appointments.objects.all()
    fixed_appointments = [
        {
            "dates": [i.FelmeresIdopontja2],
            "address": get_address(i),
            "fixed": True,
            "adatlap": i,
        }
        for i in MiniCrmAdatlapok.objects.filter(
            ~Q(Id__in=[i.adatlap.Id for i in appointments.distinct("adatlap__Id")]),
            ~Q(StatusId__in=["2929", "3086"]),
            FelmeresIdopontja2__date__in=[
                i.date.replace(hour=0, minute=0)
                for i in appointments.distinct("adatlap__Id")
            ],
        )[:3]
    ]
    data["addresses"] = [
        {
            "date": random_date(i),
            **i,
        }
        for i in [
            {
                "dates": [j.date for j in appointments if j.adatlap.Id == i.adatlap.Id],
                "address": get_address(i.adatlap),
                "fixed": False,
                "adatlap": i.adatlap,
            }
            for i in appointments.distinct("adatlap__Id")
        ]
        + fixed_appointments
    ]
    return data


def random_date(i):
    return (
        i["dates"][np.random.randint(low=0, high=len(i["dates"]))]
        if len(i["dates"]) != 0
        else i["dates"][0]
    )


def create_distance_matrix(data):
    addresses = ["Budapest"] + [i["address"] for i in data["addresses"]]
    max_elements = 100
    num_addresses = len(addresses)
    q, r = divmod(num_addresses * num_addresses, max_elements)
    dest_addresses = addresses
    distance_matrix = []
    for i in range(q):
        origin_addresses = addresses[i * max_elements : (i + 1) * max_elements]
        response = send_request(origin_addresses, dest_addresses)
        distance_matrix += build_distance_matrix(response)
    if r > 0:
        origin_addresses = addresses[q * max_elements : q * max_elements + r]
        response = send_request(origin_addresses, dest_addresses)
        distance_matrix += build_distance_matrix(response)
    return distance_matrix


def send_request(origin_addresses, dest_addresses):
    """Build and send request for the given origin and destination addresses."""

    def build_address_str(addresses):
        address_str = ""
        for i in range(len(addresses) - 1):
            address_str += addresses[i] + "|"
        address_str += addresses[-1]
        return address_str

    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)
    result = gmaps.distance_matrix(origin_address_str, dest_address_str)
    return result


def build_distance_matrix(response):
    distance_matrix = []
    for row in response["rows"]:
        row_list = [
            math.floor(row["elements"][j]["duration"]["value"] / 60)
            for j in range(len(row["elements"]))
        ]
        distance_matrix.append(row_list)
    return distance_matrix


def generate_route(cities, days):
    routes = []
    for day in days:
        day_cities = [
            i
            for i in cities
            if i["date"].replace(hour=0, minute=0) == day.date.replace(hour=0, minute=0)
        ]
        day_cities.append(
            {
                "id": 0,
                "date": day.date.replace(hour=0, minute=0),
                "dates": [day.date.replace(hour=0, minute=0)],
                "address": start_city,
                "fixed": True,
                "adatlap": MiniCrmAdatlapok(),
            },
        )

        sort_route(day_cities)
        routes += day_cities

    return routes


def sort_route(route):
    route.sort(key=lambda x: x["date"] if x else None)


def calculate_distance(route):
    return sum(
        distance_matrix[int(route[i - 1]["id"])][int(route[i]["id"])]
        for i in range(len(route))
    )


def calculate_fitness(route):
    if calculate_distance(route) == 0:
        return 0
    return 1 / calculate_distance(route)


def tournament_selection(population, fitnesses, tournament_size):
    indices = np.random.choice(len(population), tournament_size)
    tournament_individuals = [population[i] for i in indices]
    tournament_fitnesses = [fitnesses[i] for i in indices]

    winner_index = np.argmax(tournament_fitnesses)
    return tournament_individuals[winner_index]


def crossover(parent1, parent2):
    size = len(parent1)
    # Generate a random range within the route
    child = parent2.copy()
    while True:
        start, end = sorted(np.random.choice(range(size), size=2, replace=False))
        if (
            len([i for i in range(start, end) if not parent1[i]["fixed"]])
            and start != end
        ):
            break

    for i in range(start, end):
        if not parent1[i]["fixed"]:
            child_gene = [
                j for j in child if j["adatlap"].Id == parent1[i]["adatlap"].Id
            ]
            child_gene[0]["date"] = parent1[i]["date"]
            sort_route(child)

    return child


def mutate(route):
    size = len(route)
    while True:
        i = np.random.randint(0, size)
        if not route[i]["fixed"] and len(route[i]["dates"]):
            new_date = random_date(route[i])
            route[i]["date"] = new_date
            sort_route(route)
            break
    return route


data = create_data()
distance_matrix = create_distance_matrix(data)
population_size = 1000
max_generations = 1000
tournament_size = 4
start_city = "Budapest"

population = [
    generate_route(
        [{"id": int(idx) + 1, **i} for idx, i in enumerate(data["addresses"])],
        Appointments.objects.all().distinct("date__date"),
    )
    for _ in range(512)
]

print_route(population[0])
for generation in range(max_generations):
    fitnesses = np.array([calculate_fitness(route) for route in population])
    new_population = []
    for _ in range(population_size):
        parent1, parent2 = tournament_selection(
            population, fitnesses, tournament_size
        ), tournament_selection(population, fitnesses, tournament_size)
        child = crossover(parent1, parent2)
        child = mutate(child)
        new_population.append(child)
    population = new_population

fitnesses = [calculate_fitness(route) for route in population]

best_route_index = np.argmax(fitnesses)

best_route = population[best_route_index]
print_route(best_route)
