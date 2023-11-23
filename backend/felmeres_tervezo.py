import math
import time
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
    appointments = Appointments.objects.all().distinct("adatlap__Id")
    data["addresses"] = [get_address(i.adatlap) for i in appointments]
    data["ids"] = [i.adatlap for i in appointments]
    return data


def create_distance_matrix(data):
    addresses = data["addresses"]
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


data = create_data()
distance_matrix = create_distance_matrix(data)
population_size = 1000
max_generations = 1000


def generate_route(cities):
    return np.random.permutation(cities)


def calculate_distance(route):
    return sum(
        distance_matrix[int(route[i - 1][0])][int(route[i][0])]
        for i in range(len(route))
    )


def calculate_fitness(route):
    if calculate_distance(route) == 0:
        return 0
    return 1 / calculate_distance(route)


def selection(population, fitnesses):
    indices = np.random.choice(
        np.arange(len(population)), size=2, p=fitnesses / fitnesses.sum()
    )
    return population[indices[0]], population[indices[1]]


def crossover(parent1, parent2):
    size = len(parent1)
    # Generate a random range within the route
    start, end = sorted(np.random.choice(range(size), size=2, replace=False))

    # Fill the child with cities from parent2
    child = parent2.copy()

    # Replace the selected section with cities from parent1
    child[start:end] = parent1[start:end]

    # Create a set for quick lookup
    child_set = set(map(tuple, child[start:end]))

    # Fill the remaining positions with the nodes from parent2 in the order they appear
    pointer = end
    for item in parent2:
        if tuple(item) not in child_set:
            if pointer == size:
                pointer = 0
            child[pointer] = item
            child_set.add(tuple(item))
            pointer += 1

    return child


def mutate(route):
    size = len(route)
    # Ensure we have two distinct random indices
    while True:
        i, j = np.random.choice(range(size), size=2, replace=False)
        if i != j:
            break
    # Swap the cities at these indices
    original_route = route.copy()
    route[i], route[j] = original_route[j], original_route[i]
    return route


# Initialize population
population = [
    generate_route([(int(idx), i) for idx, i in enumerate(data["addresses"])])
    for _ in range(1000)
]

# Main loop
elitism_size = 10  # Number of elite individuals

for generation in range(max_generations):
    fitnesses = np.array([calculate_fitness(route) for route in population])

    # Sort the population by fitness
    sorted_indices = np.argsort(fitnesses)[::-1]
    population = [population[i] for i in sorted_indices]

    # Select the elite individuals
    elites = population[:elitism_size]

    new_population = []
    for _ in range(population_size - elitism_size):  # Adjusted for elitism
        parent1, parent2 = selection(population, fitnesses)
        child = crossover(parent1, parent2)
        child = mutate(child)
        new_population.append(child)

    # Add the elites to the new population
    population = elites + new_population

# Calculate fitnesses for all routes in the population
fitnesses = [calculate_fitness(route) for route in population]

# Get the index of the route with the highest fitness
best_route_index = np.argmax(fitnesses)

# Get the best route
best_route = population[best_route_index]
print(calculate_distance(best_route))
print(best_route)
