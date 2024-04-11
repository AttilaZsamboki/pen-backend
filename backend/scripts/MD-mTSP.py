import numpy as np
from django.db.models import Q
from pulp import *
from pyscipopt import Model

from ..utils.google_routes import Client
from ..utils.logs import log
from ..models import Routes, Salesmen, UserSkills
from .felmeres_tervezo import MiniCRMConnector, Population

NEEDED_SKILL = 1
L = 5
salesmen = [
    i.zip
    for i in Salesmen.objects.all()
    if UserSkills.objects.filter(user=i, skill=NEEDED_SKILL).exists()
]

prob = LpProblem("Traveling Salesman Problem", LpMinimize)

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
    and x["Iranyitoszam"],
)
adatlapok = minicrm_conn.main() + list(
    map(lambda i: Population.Chromosome.Gene(zip=i, dates=[]), salesmen)
)


def create_distance_matrix():
    print("Creating distance matrix...")
    num_requests = 0
    addresses: List[str] = [i.zip for i in adatlapok]
    all_routes = list(Routes.objects.all())
    gmaps = Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))

    for origin in list(set(addresses)):
        for destination in addresses:
            if origin != destination:
                if not len(
                    [
                        route
                        for route in all_routes
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
                    num_requests += 1
                    print(num_requests)
                    response = gmaps.routes(origin=origin, destination=destination)
                    save = Routes(
                        origin_zip=origin,
                        dest_zip=destination,
                        distance=response.routes[0].distance_meters,
                        duration=response.routes[0].parse_duration(),
                    )
                    all_routes.append(save)
                    save.save()
    print("Number of requests: ", num_requests)


create_distance_matrix()
nodes = list(map(lambda x: x.zip, adatlapok))
distances = {
    ((i.origin_zip, i.dest_zip) if j == 0 else (i.dest_zip, i.origin_zip)): i.duration
    for j in range(2)
    for i in Routes.objects.filter(Q(origin_zip__in=nodes) | Q(dest_zip__in=nodes))
}

M = 1000

x = LpVariable.dicts(
    "x",
    (nodes, nodes, salesmen),
    0,
    1,
    LpBinary,
)
y = LpVariable.dicts(
    "y",
    (nodes, salesmen),
    0,
    1,
    LpBinary,
)
u = LpVariable.dicts("u", (nodes, salesmen), 0, len(nodes) - 1, LpInteger)

# (1)
prob += lpSum(
    [
        distances[(i, j)] * x[i][j][k]
        for i in nodes
        for j in nodes
        for k in salesmen
        if i != j
    ]
)

for k in salesmen:
    for i in nodes:
        if i == k:
            continue
        # (4)
        prob += lpSum([x[i][j][k] for j in nodes if i != j]) == y[i][k]
        # (5)
        prob += lpSum([x[j][i][k] for j in nodes if i != j]) == y[i][k]
        # (6)
        prob += u[i] + (L - 2) * x[k][i][k] - x[i][k][k] <= L - 1
        # (7)
        prob += u[i] + x[k][i][k] + 2 * x[i][k][k] >= 0

for i in nodes:
    prob += lpSum([y[i][k] for k in salesmen]) >= 1

for k in salesmen:
    for i in nodes:
        for j in nodes:
            if i != j and (i != k and j != k):
                # (9)
                prob += (
                    u[i][k] - u[j][k] + L * x[i][j][k] + (L - 2) * x[j][i][k] <= L - 1
                )

status = prob.solve()
print(status, LpStatus[status], value(prob.objective))

print("The route:")
for v in prob.variables():
    if v.varValue == 1 and "x" in v.name:
        print(v.name)

import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()

G.add_nodes_from(nodes)
routes = [
    (i, j) for i in nodes for j in nodes for k in salesmen if x[i][j][k].varValue == 1
]

G.add_edges_from(routes)

nx.draw(G, with_labels=True)
plt.title("Traveling Salesman Problem Solution")
plt.show()
