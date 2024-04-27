from django.db.models import Q
from pulp import *

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
    and x["Iranyitoszam"]
    and x["Deleted"] == "0",
)
nodes = minicrm_conn.main() + list(
    map(lambda i: Population.Chromosome.Gene(zip=i, dates=[]), salesmen)
)
salesmen += [
    i.zip for i in nodes if i not in salesmen and i.dates and i.dates[0] != "*"
]
zips = list(map(lambda i: i.zip, nodes))


def create_distance_matrix():
    print("Creating distance matrix...")
    num_requests = 0
    addresses: List[str] = [i.zip for i in nodes]
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
distances = {
    ((i.origin_zip, i.dest_zip) if j == 0 else (i.dest_zip, i.origin_zip)): i.duration
    for j in range(2)
    for i in Routes.objects.filter(
        Q(origin_zip__in=list(map(lambda i: i.zip, nodes)))
        | Q(dest_zip__in=list(map(lambda i: i.zip, nodes)))
    )
}

M = 1000

x = LpVariable.dicts(
    "x",
    (zips, zips, salesmen),
    0,
    1,
    LpBinary,
)
y = LpVariable.dicts(
    "y",
    (zips, salesmen),
    0,
    1,
    LpBinary,
)
u = LpVariable.dicts("u", (zips, salesmen), 0, len(nodes) - 1, LpInteger)

# (1)
prob += lpSum(
    [
        distances[(i.zip, j.zip)] * x[i.zip][j.zip][k]
        for i in nodes
        for j in nodes
        for k in salesmen
        if i.zip != j.zip
    ]
)

for k in salesmen:
    for i in nodes:
        if i.zip == k:
            continue
        # (4)
        prob += lpSum([x[i.zip][j.zip][k] for j in nodes if i != j]) == y[i.zip][k]
        # (5)
        prob += lpSum([x[j.zip][i.zip][k] for j in nodes if i != j]) == y[i.zip][k]
        # (6)
        prob += u[i.zip] + (L - 2) * x[k][i.zip][k] - x[i.zip][k][k] <= L - 1
        # (7)
        prob += u[i.zip] + x[k][i.zip][k] + 2 * x[i.zip][k][k] >= 0

for i in nodes:
    prob += lpSum([y[i.zip][k] for k in salesmen]) >= 1

for k in salesmen:
    for i in nodes:
        for j in nodes:
            if i.zip != j.zip and (i.zip != k and j.zip != k):
                # (9)
                prob += (
                    u[i.zip][k]
                    - u[j.zip][k]
                    + L * x[i.zip][j.zip][k]
                    + (L - 2) * x[j.zip][i.zip][k]
                    <= L - 1
                )


solver = PULP_CBC_CMD(timeLimit=3000)
status = prob.solve(solver)
print(status, LpStatus[status], value(prob.objective))

print("The route:")
for v in prob.variables():
    if v.varValue == 1 and "x" in v.name:
        print(v.name)

import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()

G.add_nodes_from(zips)
routes = [
    (i.zip, j.zip)
    for i in nodes
    for j in nodes
    for k in salesmen
    if x[i.zip][j.zip][k].varValue == 1
]

G.add_edges_from(routes)

nx.draw(G, with_labels=True)
plt.title("Traveling Salesman Problem Solution")
plt.show()
