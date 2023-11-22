import math
import numpy as np
import googlemaps
import os
from .utils.logs import log
from .models import Appointments
from .utils.utils import get_address

gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))


def create_data():
    """Creates the data."""
    data = {}
    data["API_key"] = os.getenv("GOOGLE_MAPS_API_KEY")
    appointments = Appointments.objects.all()
    data["addresses"] = ["Budapest"] + [get_address(i.adatlap) for i in appointments]
    return data


def create_distance_matrix(data):
    addresses = data["addresses"]
    API_key = data["API_key"]
    # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
    max_elements = 100
    num_addresses = len(addresses)  # 16 in this example.
    # Maximum number of rows that can be computed per request (6 in this example).
    max_rows = max_elements // num_addresses
    # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        origin_addresses = addresses[i * max_rows : (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)

    # Get the remaining remaining r rows, if necessary.
    if r > 0:
        origin_addresses = addresses[q * max_rows : q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
    return distance_matrix


def send_request(origin_addresses, dest_addresses, API_key):
    """Build and send request for the given origin and destination addresses."""

    def build_address_str(addresses):
        # Build a pipe-separated string of addresses
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


distance_matrix = create_distance_matrix(create_data())
dates = {
    i.adatlap.Id: [
        j["date"] for j in Appointments.objects.filter(adatlap=i.adatlap).values("date")
    ]
    for i in Appointments.objects.all().distinct("adatlap__Id")
}
population_size = 64
max_generations = 12


def generate_route(cities):
    return np.random.permutation(cities)


def calculate_distance(route):
    return sum(distance_matrix[route[i - 1], route[i]] for i in range(len(route)))


def calculate_fitness(route):
    return 1 / calculate_distance(route)


def selection(population, fitnesses):
    return population[
        np.random.choice(
            np.arange(len(population)), size=2, p=fitnesses / fitnesses.sum()
        )
    ]


def crossover(parent1, parent2):
    cut = np.random.randint(len(parent1))
    child = np.concatenate((parent1[:cut], parent2[cut:]))
    return child


def mutate(route):
    i, j = np.random.randint(len(route), size=2)
    route[i], route[j] = route[j], route[i]
    return route


# Initialize population
population = [
    generate_route([get_address(i.adatlap) for i in Appointments.objects.all()])
    for _ in range(len(Appointments.objects.all()))
]

# Main loop
for generation in range(max_generations):
    fitnesses = np.array([calculate_fitness(route) for route in population])
    new_population = []
    for _ in range(population_size):
        parent1, parent2 = selection(population, fitnesses)
        child = crossover(parent1, parent2)
        child = mutate(child)
        new_population.append(child)
    population = new_population

print(population)
