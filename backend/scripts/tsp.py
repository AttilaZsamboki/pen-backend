from ..utils.logs import log
import os
from typing import List, Dict

import random

import matplotlib.pyplot as plt
import networkx as nx
from ortools.sat.python import cp_model

from ..models import Destinations, DestinationTimes, Results, Routes
from ..utils.google_routes import Client


def generate_random_zip_codes(n):
    zips = list(set(Routes.objects.all().values_list("origin_zip", flat=True)))
    return random.sample(zips, n)


from typing import List, Dict
import os
from ..models import Routes


def create_distance_matrix(addresses: List[str]) -> Dict[str, Dict[str, float]]:
    print("Creating distance matrix...")
    num_requests = 0
    all_routes = list(Routes.objects.all())
    gmaps = Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))
    distance_matrix = {}

    for origin in list(set(addresses)):
        distance_matrix[origin] = {}
        for destination in addresses:
            if origin != destination:
                existing_route = [
                    route
                    for route in all_routes
                    if (
                        (route.origin_zip == origin and route.dest_zip == destination)
                        or (
                            route.origin_zip == destination and route.dest_zip == origin
                        )
                    )
                ]
                if not existing_route:
                    num_requests += 1
                    print(num_requests)
                    response = gmaps.routes(
                        origin=str(origin), destination=str(destination)
                    )
                    duration = response.routes[0].parse_duration()
                    save = Routes(
                        origin_zip=origin,
                        dest_zip=destination,
                        distance=response.routes[0].distance_meters,
                        duration=duration,
                    )
                    all_routes.append(save)
                    save.save()
                else:
                    duration = existing_route[0].duration

                distance_matrix[origin][destination] = duration / 60

    print("Number of requests: ", num_requests)
    return distance_matrix


def generate_tsp():
    Destinations.objects.all().delete()
    DestinationTimes.objects.all().delete()
    zip_codes = [2181] + [int(i) for i in generate_random_zip_codes(10)]

    days = range(30)
    time_slots_per_day = list(range(8, 18))
    starting_zip = 2181

    fixed_destinations = [
        {
            "zip": zip_codes[i],
            "day": random.choice(days),
            "time": random.choice(time_slots_per_day),
        }
        for i in range(1, 3)
    ]

    semi_fixed_destinations = [
        {
            "zip": zip_codes[i],
            "options": [
                (random.choice(days), random.choice(time_slots_per_day))
                for _ in range(3)
            ],
        }
        for i in range(3, 6)
    ]

    free_destinations = [{"zip": zip_codes[i]} for i in range(6, 11)]

    job_duration = 30

    model = cp_model.CpModel()

    free_vars = {}
    for destination in free_destinations:
        Destinations(zip=destination["zip"], type="free").save()
        day_var = model.NewIntVar(0, len(days) - 1, f"day_{destination['zip']}")
        time_var = model.NewIntVar(
            min(time_slots_per_day),
            max(time_slots_per_day),
            f"time_{destination['zip']}",
        )
        free_vars[destination["zip"]] = (day_var, time_var)

    semi_fixed_vars = {}
    for destination in semi_fixed_destinations:
        dest = Destinations(zip=destination["zip"], type="semi-fixed")
        dest.save()
        option_vars = []
        for option in destination["options"]:
            day, time = option
            DestinationTimes(destination=dest, day=day, hour=time).save()
            var = model.NewBoolVar(f"option_{destination['zip']}_{day}_{time}")
            option_vars.append(var)
        semi_fixed_vars[destination["zip"]] = option_vars

        model.Add(sum(option_vars) == 1)

    for destination in fixed_destinations:
        dest = Destinations(zip=destination["zip"], type="fixed")
        dest.save()
        DestinationTimes(
            destination=dest, day=destination["day"], hour=destination["time"]
        ).save()
        free_vars[destination["zip"]] = (
            model.NewConstant(destination["day"]),
            model.NewConstant(destination["time"]),
        )
        model.Add(free_vars[destination["zip"]][0] == destination["day"])
        model.Add(free_vars[destination["zip"]][1] == destination["time"])

    distance_matrix = create_distance_matrix(zip_codes)
    n = len(distance_matrix)

    for day in days:
        for time in time_slots_per_day:
            overlapping = []

            for free_zip, (day_var, time_var) in free_vars.items():
                is_scheduled = model.NewBoolVar(
                    f"overlap_day_{day}_time_{time}_free_{free_zip}"
                )

                time_diff = model.NewBoolVar("time_diff")
                day_diff = model.NewBoolVar("day_diff")

                model.Add(time_var != time).OnlyEnforceIf(time_diff.Not())
                model.Add(time_var == time).OnlyEnforceIf(time_diff)

                model.Add(day_var != day).OnlyEnforceIf(day_diff.Not())
                model.Add(day_var == day).OnlyEnforceIf(day_diff)

                model.AddBoolOr([time_diff, day_diff]).OnlyEnforceIf(is_scheduled)
                model.AddBoolOr([time_diff.Not(), day_diff.Not()]).OnlyEnforceIf(
                    is_scheduled.Not()
                )
                overlapping.append(is_scheduled)

            for semi_zip, option_vars in semi_fixed_vars.items():
                for option_index, (option_day, option_time) in enumerate(
                    [i for i in semi_fixed_destinations if semi_zip == i["zip"]][0][
                        "options"
                    ]
                ):
                    if option_day == day and option_time == time:
                        overlapping.append(option_vars[option_index])

            model.Add(sum(overlapping) <= 1)

    tsp_vars = {}
    for day in days:
        for i in range(n):
            for j in range(n):
                if i != j:
                    tsp_vars[(zip_codes[i], zip_codes[j], day)] = model.NewBoolVar(
                        f"tsp_{zip_codes[i]}_{zip_codes[j]}_day_{day}"
                    )

    for day in days:
        condition_var = model.NewBoolVar(f"condition_var_{day}")
        trips_planned = sum(
            tsp_vars[(zip_codes[i], zip_codes[j], day)]
            for i in range(n)
            for j in range(n)
            if i != j
        )

        model.Add(trips_planned >= 1).OnlyEnforceIf(condition_var)
        model.Add(trips_planned == 0).OnlyEnforceIf(condition_var.Not())

        model.Add(
            sum(tsp_vars[(starting_zip, zip_codes[j], day)] for j in range(1, n)) == 1
        ).OnlyEnforceIf(condition_var)
        model.Add(
            sum(tsp_vars[(zip_codes[j], starting_zip, day)] for j in range(1, n)) == 1
        ).OnlyEnforceIf(condition_var)

    for day in days:
        u = [model.NewIntVar(0, n - 1, f"u_{zip_codes[i]}_day_{day}") for i in range(n)]
        for i in range(1, n):
            for j in range(1, n):
                if i != j:
                    model.Add(
                        u[i]
                        - u[j]
                        + (n - 1) * tsp_vars[(zip_codes[i], zip_codes[j], day)]
                        <= n - 2
                    )

    for i in range(1, n):
        model.Add(
            sum(
                tsp_vars[(zip_codes[i], zip_codes[j], day)]
                for day in days
                for j in range(n)
                if i != j
            )
            == 1
        )
        model.Add(
            sum(
                tsp_vars[(zip_codes[j], zip_codes[i], day)]
                for day in days
                for j in range(n)
                if i != j
            )
            == 1
        )

    for day in days:
        for i in range(n):
            for j in range(n):
                if i != j:
                    if zip_codes[i] in free_vars.keys():
                        day_var = model.NewBoolVar(f"day_var_{zip_codes[i]}_{day}")
                        model.Add(free_vars[zip_codes[i]][0] == day).OnlyEnforceIf(
                            day_var
                        )

                        model.Add(
                            tsp_vars[(zip_codes[i], zip_codes[j], day)] == 1
                        ).OnlyEnforceIf(day_var)
                        model.Add(
                            tsp_vars[(zip_codes[i], zip_codes[j], day)] == 0
                        ).OnlyEnforceIf(day_var.Not())

                    if zip_codes[j] in free_vars.keys():
                        day_var2 = model.NewBoolVar(f"day_var_{zip_codes[j]}_{day}")
                        model.Add(free_vars[zip_codes[j]][0] == day).OnlyEnforceIf(
                            day_var2
                        )

                        model.Add(
                            tsp_vars[(zip_codes[i], zip_codes[j], day)] == 1
                        ).OnlyEnforceIf(day_var2)
                        model.Add(
                            tsp_vars[(zip_codes[i], zip_codes[j], day)] == 0
                        ).OnlyEnforceIf(day_var2.Not())

                    if zip_codes[i] in semi_fixed_vars:
                        for option_index, (option_day, _) in enumerate(
                            [
                                t
                                for t in semi_fixed_destinations
                                if zip_codes[i] == t["zip"]
                            ][0]["options"]
                        ):
                            if option_day == day:
                                model.Add(
                                    sum(
                                        tsp_vars[(zip_codes[i], zip_codes[t], day)]
                                        for t in range(n)
                                        if zip_codes[i] != zip_codes[t]
                                    )
                                    == 1
                                ).OnlyEnforceIf(
                                    semi_fixed_vars[zip_codes[i]][option_index]
                                )
                                model.Add(
                                    sum(
                                        tsp_vars[(zip_codes[t], zip_codes[i], day)]
                                        for t in range(n)
                                        if zip_codes[i] != zip_codes[t]
                                    )
                                    == 1
                                ).OnlyEnforceIf(
                                    semi_fixed_vars[zip_codes[i]][option_index]
                                )

                                model.Add(
                                    sum(
                                        tsp_vars[(zip_codes[t], zip_codes[i], day)]
                                        for t in range(n)
                                        if zip_codes[i] != zip_codes[t]
                                    )
                                    == 0
                                ).OnlyEnforceIf(
                                    semi_fixed_vars[zip_codes[i]][option_index].Not()
                                )

    for day in days:
        for i in range(n):
            for j in range(n):
                if i != j:
                    if zip_codes[i] in free_vars.keys():
                        if zip_codes[j] in free_vars.keys():
                            model.Add(
                                free_vars[zip_codes[i]][1] < free_vars[zip_codes[j]][1]
                            ).OnlyEnforceIf(tsp_vars[(zip_codes[i], zip_codes[j], day)])
                    for semi_zip, option_vars in semi_fixed_vars.items():
                        for option_index, (option_day, option_time) in enumerate(
                            [
                                t
                                for t in semi_fixed_destinations
                                if semi_zip == t["zip"]
                            ][0]["options"]
                        ):
                            if option_day == day:
                                if zip_codes[i] == semi_zip:
                                    if zip_codes[j] in free_vars.keys():
                                        model.Add(
                                            option_time < free_vars[zip_codes[j]][1]
                                        ).OnlyEnforceIf(
                                            option_vars[option_index]
                                        ).OnlyEnforceIf(
                                            tsp_vars[(zip_codes[i], zip_codes[j], day)]
                                        )
                                if zip_codes[j] == semi_zip:
                                    if zip_codes[i] in free_vars.keys():
                                        model.Add(
                                            free_vars[zip_codes[i]][1] < option_time
                                        ).OnlyEnforceIf(
                                            option_vars[option_index]
                                        ).OnlyEnforceIf(
                                            tsp_vars[(zip_codes[i], zip_codes[j], day)]
                                        )

                    if (
                        zip_codes[i] in semi_fixed_vars
                        and zip_codes[j] in semi_fixed_vars
                    ):
                        if zip_codes[i] != zip_codes[j]:
                            model.Add(
                                semi_fixed_vars[zip_codes[i]]
                                < semi_fixed_vars[zip_codes[j]]
                            ).OnlyEnforceIf(tsp_vars[(zip_codes[i], zip_codes[j], day)])

    for day in days:
        for i in range(1, n):
            for j in range(n):
                if i != j:
                    if (
                        zip_codes[i] in distance_matrix
                        and zip_codes[j] in distance_matrix[zip_codes[i]]
                    ):
                        travel_time = distance_matrix[zip_codes[i]][zip_codes[j]]
                    else:
                        print(
                            f"Error: Missing distance data for {zip_codes[i]} to {zip_codes[j]}"
                        )
                        return

                    travel_time = distance_matrix[zip_codes[i]][zip_codes[j]]
                    end_time_i = model.NewIntVar(
                        min(time_slots_per_day) * 60,
                        (max(time_slots_per_day) + 1) * 60,
                        f"end_time_{zip_codes[i]}_day_{day}",
                    )
                    start_time_j = model.NewIntVar(
                        min(time_slots_per_day) * 60,
                        (max(time_slots_per_day) + 1) * 60,
                        f"start_time_{zip_codes[j]}_day_{day}",
                    )
                    if zip_codes[i] in free_vars.keys():
                        model.Add(
                            end_time_i == free_vars[zip_codes[i]][1] * 60 + job_duration
                        )
                    elif zip_codes[i] in semi_fixed_vars:
                        for option_index, (option_day, option_time) in enumerate(
                            [
                                t
                                for t in semi_fixed_destinations
                                if zip_codes[i] == t["zip"]
                            ][0]["options"]
                        ):
                            if option_day == day:
                                model.Add(end_time_i == option_time * 60 + job_duration)

                    if zip_codes[j] in free_vars.keys():
                        model.Add(start_time_j == free_vars[zip_codes[j]][1] * 60)
                    elif zip_codes[j] in semi_fixed_vars:
                        for option_index, (option_day, option_time) in enumerate(
                            [
                                t
                                for t in semi_fixed_destinations
                                if zip_codes[j] == t["zip"]
                            ][0]["options"]
                        ):
                            if option_day == day:
                                model.Add(start_time_j == option_time * 60)
                    model.Add(
                        start_time_j >= end_time_i + int(travel_time)
                    ).OnlyEnforceIf(tsp_vars[(zip_codes[i], zip_codes[j], day)])

    model.Minimize(
        sum(
            distance_matrix[zip_codes[i]][zip_codes[j]]
            * tsp_vars[(zip_codes[i], zip_codes[j], day)]
            for day in days
            for i in range(n)
            for j in range(n)
            if i != j
        )
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution found:")

        for free_zip, (day_var, time_var) in free_vars.items():
            print(
                f"Free Destination {free_zip}: Day {solver.Value(day_var)}, Time {solver.Value(time_var)}"
            )
            Results(
                destination=Destinations.objects.get(zip=free_zip),
                day=solver.Value(day_var),
                hour=solver.Value(time_var),
            ).save()

        for semi_zip, option_vars in semi_fixed_vars.items():
            chosen_option = [
                i for i, var in enumerate(option_vars) if solver.Value(var)
            ]
            if chosen_option:
                day, time = [
                    i for i in semi_fixed_destinations if semi_zip == i["zip"]
                ][0]["options"][chosen_option[0]]
                print(f"Semi-Fixed Destination {semi_zip}: Day {day}, Time {time}")
                Results(
                    destination=Destinations.objects.get(zip=semi_zip),
                    day=solver.Value(day),
                    hour=solver.Value(time),
                ).save()

        G = nx.Graph()
        G.add_nodes_from(zip_codes)
        routes = []

        for day in days:
            print(f"Day {day} route:")
            for i in range(n):
                for j in range(n):
                    if i != j and solver.Value(
                        tsp_vars[(zip_codes[i], zip_codes[j], day)]
                    ):
                        routes.append((zip_codes[i], zip_codes[j]))
                        print(f"Travel from {zip_codes[i]} to {zip_codes[j]}")

        G.add_edges_from(routes)
        nx.draw(G, with_labels=True)
        plt.title("Traveling Salesman Problem Solution")
        plt.show()
    else:
        print("No solution found.")


if __name__ == "__main__":
    generate_tsp()
