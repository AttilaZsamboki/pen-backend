from django.db.models import Q
from pulp import *
from random import uniform

# from ..utils.logs import log
# from ..models import Routes, Salesmen, UserSkills
# from .felmeres_tervezo_2 import MiniCRMConnector, Population

# NEEDED_SKILL = 1
# m = 2
# starting_city = [
#     i.zip
#     for i in Salesmen.objects.all()
#     if UserSkills.objects.filter(user=i, skill=NEEDED_SKILL).exists()
# ][0]


# minicrm_conn = MiniCRMConnector(
#     id_field="Id",
#     zip_field="Iranyitoszam",
#     new_aplicant_condition=lambda x: x["FelmeresIdopontja2"] is None
#     and x["StatusId"] not in [3086, 2929]
#     and x["Iranyitoszam"],
# )
# adatlapok = [Population.Chromosome.Gene(starting_city)] + minicrm_conn.main()
# Population(adatlapok).create_distance_matrix()
# cities = list(map(lambda x: x.zip, adatlapok))
# distances = {
#     ((i.origin_zip, i.dest_zip) if j == 0 else (i.dest_zip, i.origin_zip)): i.duration
#     for j in range(2)
#     for i in Routes.objects.filter(Q(origin_zip__in=cities) | Q(dest_zip__in=cities))
# }

prob = LpProblem("Traveling Salesman Problem", LpMinimize)
L = 2
cities = range(10)
distances = {(i, j): uniform(0, 50) for i in cities for j in cities if i != j}
starting_city = 0

x = LpVariable.dicts(
    "x",
    (cities, cities),
    0,
    1,
    LpBinary,
)

u = LpVariable.dicts("u", cities, 0, len(cities) - 1, LpInteger)

# (1)
prob += lpSum([distances[(i, j)] * x[i][j] for i in cities for j in cities if i != j])


for i in cities:
    if i == starting_city:
        continue
    # (4)
    prob += lpSum([x[i][j] for j in cities if i != j]) == 1
    # (5)
    prob += lpSum([x[j][i] for j in cities if i != j]) == 1

    # (6)
    # prob += u[i] + (L - 2) * x[starting_city][i] - x[i][starting_city] <= L - 1
    # (7)
    prob += u[i] + x[starting_city][i] + 2 * x[i][starting_city] >= 0

for i in cities:
    for j in cities:
        if i != j and (i != starting_city and j != starting_city):
            # (9)
            prob += u[i] - u[j] + L * x[i][j] + (L - 2) * x[j][i] <= L - 1

status = prob.solve()
print(status, LpStatus[status], value(prob.objective))

print("The route:")
for v in prob.variables():
    if v.varValue == 1 and "x" in v.name:
        print(v.name)

import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()

G.add_nodes_from(cities)
routes = [(i, j) for i in cities for j in cities if x[i][j].varValue == 1]

G.add_edges_from(routes)

nx.draw(G, with_labels=True)
plt.title("Traveling Salesman Problem Solution")
plt.show()
