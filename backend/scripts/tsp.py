from ..utils.logs import log
import os
from typing import List, Dict

import random

import matplotlib.pyplot as plt
import networkx as nx
from ortools.sat.python import cp_model

from ..models import Destinations, DestinationTimes, Results, Routes
from ..utils.google_routes import Client


STARTING_ZIP = "S"
JOB_DURATION = 30


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


def generate_tsp(
    fixed_destinations: List[Dict],
    semi_fixed_destinations: List[Dict],
    free_destinations: List[Dict],
    days: List[int] = range(30),
    time_slots_per_day: List[int] = list(range(8 * 60, 18 * 60)),
):
    # Destinations.objects.all().delete()
    # DestinationTimes.objects.all().delete()
    destinations = (
        [{"zip": STARTING_ZIP, "id": 0}]
        + fixed_destinations
        + semi_fixed_destinations
        + free_destinations
    )

    model = cp_model.CpModel()

    free_vars = {}
    for destination in free_destinations:
        # Destinations(zip=destination["zip"], type="free").save()
        day_var = model.NewIntVar(0, len(days) - 1, f"day_{destination['id']}")
        time_var = model.NewIntVar(
            min(time_slots_per_day),
            max(time_slots_per_day),
            f"time_{destination['id']}",
        )
        free_vars[destination["id"]] = (day_var, time_var)

    semi_fixed_vars = {}
    for destination in semi_fixed_destinations:
        # dest = Destinations(zip=destination["zip"], type="semi-fixed")
        # dest.save()
        option_vars = []
        for option in destination["options"]:
            day, time = option
            # DestinationTimes(destination=dest, day=day, hour=time).save()
            var = model.NewBoolVar(f"option_{destination['id']}_{day}_{time}")
            option_vars.append(var)
        semi_fixed_vars[destination["id"]] = option_vars

        model.Add(sum(option_vars) == 1)

    for destination in fixed_destinations:
        # dest = Destinations(zip=destination["zip"], type="fixed")
        # dest.save()
        # DestinationTimes(
        #     destination=dest, day=destination["day"], hour=destination["time"]
        # ).save()
        free_vars[destination["id"]] = (
            model.NewConstant(destination["day"]),
            model.NewConstant(destination["time"]),
        )
        model.Add(free_vars[destination["id"]][0] == destination["day"])
        model.Add(free_vars[destination["id"]][1] == destination["time"])

    # distance_matrix = create_distance_matrix(zip_codes)
    distance_matrix = {
        "S": {"S": 0, "A": 30, "B": 45, "C": 60, "D": 90},
        "A": {"S": 30, "A": 0, "B": 45, "C": 60, "D": 75},
        "B": {"S": 45, "A": 45, "B": 0, "C": 30, "D": 90},
        "C": {"S": 60, "A": 60, "B": 30, "C": 0, "D": 90},
        "D": {"S": 90, "A": 75, "B": 90, "C": 90, "D": 0},
    }
    n = len(destinations)

    for day in days:
        for time in time_slots_per_day:
            overlapping = []

            for free_id, (day_var, time_var) in free_vars.items():
                is_scheduled = model.NewBoolVar(
                    f"overlap_day_{day}_time_{time}_free_{free_id}"
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

            for semi_id, option_vars in semi_fixed_vars.items():
                for option_index, (option_day, option_time) in enumerate(
                    [i for i in semi_fixed_destinations if semi_id == i["id"]][0][
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
                    tsp_vars[(i, j, day)] = model.NewBoolVar(f"tsp_{i}_{j}_day_{day}")

    for day in days:
        condition_var = model.NewBoolVar(f"condition_var_{day}")
        trips_planned = sum(
            tsp_vars[(i, j, day)] for i in range(n) for j in range(n) if i != j
        )

        model.Add(trips_planned >= 1).OnlyEnforceIf(condition_var)
        model.Add(trips_planned == 0).OnlyEnforceIf(condition_var.Not())

        model.Add(sum(tsp_vars[(0, j, day)] for j in range(1, n)) == 1).OnlyEnforceIf(
            condition_var
        )
        model.Add(sum(tsp_vars[(j, 0, day)] for j in range(1, n)) == 1).OnlyEnforceIf(
            condition_var
        )

    for day in days:
        u = [model.NewIntVar(0, n - 1, f"u_{i}_day_{day}") for i in range(n)]
        for i in range(1, n):
            for j in range(1, n):
                if i != j:
                    model.Add(u[i] - u[j] + (n - 1) * tsp_vars[(i, j, day)] <= n - 2)

    for i in range(1, n):
        model.Add(
            sum(tsp_vars[(i, j, day)] for day in days for j in range(n) if i != j) == 1
        )
        model.Add(
            sum(tsp_vars[(j, i, day)] for day in days for j in range(n) if i != j) == 1
        )

    for day in days:
        for i in range(n):
            for j in range(n):
                if i != j:
                    if i in free_vars.keys():
                        day_var = model.NewBoolVar(f"day_var_{i}_{day}")
                        model.Add(free_vars[i][0] == day).OnlyEnforceIf(day_var)

                        model.Add(tsp_vars[(i, j, day)] == 1).OnlyEnforceIf(day_var)
                        model.Add(tsp_vars[(i, j, day)] == 0).OnlyEnforceIf(
                            day_var.Not()
                        )

                    if j in free_vars.keys():
                        day_var2 = model.NewBoolVar(f"day_var_{j}_{day}")
                        model.Add(free_vars[j][0] == day).OnlyEnforceIf(day_var2)

                        model.Add(tsp_vars[(i, j, day)] == 1).OnlyEnforceIf(day_var2)
                        model.Add(tsp_vars[(i, j, day)] == 0).OnlyEnforceIf(
                            day_var2.Not()
                        )

                    if i in semi_fixed_vars:
                        for option_index, (option_day, _) in enumerate(
                            [t for t in semi_fixed_destinations if i == t["id"]][0][
                                "options"
                            ]
                        ):
                            if option_day == day:
                                model.Add(
                                    sum(
                                        tsp_vars[(i, t, day)]
                                        for t in range(n)
                                        if i != t
                                    )
                                    == 1
                                ).OnlyEnforceIf(semi_fixed_vars[i][option_index])
                                model.Add(
                                    sum(
                                        tsp_vars[(t, i, day)]
                                        for t in range(n)
                                        if i != t
                                    )
                                    == 1
                                ).OnlyEnforceIf(semi_fixed_vars[i][option_index])

    for day in days:
        for i in range(n):
            for j in range(n):
                if i != j:
                    if i in free_vars.keys():
                        if j in free_vars.keys():
                            model.Add(free_vars[i][1] < free_vars[j][1]).OnlyEnforceIf(
                                tsp_vars[(i, j, day)]
                            )
                    for semi_id, option_vars in semi_fixed_vars.items():
                        for option_index, (option_day, option_time) in enumerate(
                            [t for t in semi_fixed_destinations if semi_id == t["id"]][
                                0
                            ]["options"]
                        ):
                            if option_day == day:
                                if i == semi_id:
                                    if j in free_vars.keys():
                                        model.Add(
                                            option_time < free_vars[j][1]
                                        ).OnlyEnforceIf(
                                            option_vars[option_index]
                                        ).OnlyEnforceIf(
                                            tsp_vars[(i, j, day)]
                                        )
                                if j == semi_id:
                                    if i in free_vars.keys():
                                        model.Add(
                                            free_vars[i][1] < option_time
                                        ).OnlyEnforceIf(
                                            option_vars[option_index]
                                        ).OnlyEnforceIf(
                                            tsp_vars[(i, j, day)]
                                        )

                    if i in semi_fixed_vars and j in semi_fixed_vars:
                        if i != j:
                            model.Add(
                                semi_fixed_vars[i] < semi_fixed_vars[j]
                            ).OnlyEnforceIf(tsp_vars[(i, j, day)])

    for day in days:
        for i in destinations:
            if i["id"] != 0:
                for j in destinations:
                    if i["zip"] != j["zip"]:
                        if (
                            i["zip"] in distance_matrix
                            and j["zip"] in distance_matrix[i["zip"]]
                        ):
                            travel_time = distance_matrix[i["zip"]][j["zip"]]
                        else:
                            print(
                                f"Error: Missing distance data for {i['zip']} to {j['zip']}"
                            )
                            return

                        travel_time = distance_matrix[i["zip"]][j["zip"]]
                        end_time_i = model.NewIntVar(
                            min(time_slots_per_day),
                            (max(time_slots_per_day) + 1),
                            f"end_time_{i['id']}_day_{day}",
                        )
                        start_time_j = model.NewIntVar(
                            min(time_slots_per_day),
                            (max(time_slots_per_day) + 1),
                            f"start_time_{j['id']}_day_{day}",
                        )
                        if i["id"] in free_vars.keys():
                            model.Add(
                                end_time_i == free_vars[i["id"]][1] + JOB_DURATION
                            )
                        elif i["id"] in semi_fixed_vars:
                            for option_index, (option_day, option_time) in enumerate(
                                [
                                    t
                                    for t in semi_fixed_destinations
                                    if i["id"] == t["id"]
                                ][0]["options"]
                            ):
                                if option_day == day:
                                    model.Add(
                                        end_time_i == option_time + JOB_DURATION
                                    ).OnlyEnforceIf(
                                        semi_fixed_vars[i["id"]][option_index]
                                    )

                        if j["id"] in free_vars.keys():
                            model.Add(start_time_j == free_vars[j["id"]][1])
                        elif j["id"] in semi_fixed_vars:
                            for option_index, (option_day, option_time) in enumerate(
                                [
                                    t
                                    for t in semi_fixed_destinations
                                    if j["id"] == t["id"]
                                ][0]["options"]
                            ):
                                if option_day == day:
                                    model.Add(
                                        start_time_j == option_time
                                    ).OnlyEnforceIf(
                                        semi_fixed_vars[j["id"]][option_index]
                                    )
                        model.Add(
                            start_time_j >= end_time_i + int(travel_time)
                        ).OnlyEnforceIf(tsp_vars[(i["id"], j["id"], day)])

    model.Minimize(
        sum(
            distance_matrix[i["zip"]][j["zip"]] * tsp_vars[(i["id"], j["id"], day)]
            for day in days
            for i in destinations
            for j in destinations
            if i["id"] != j["id"]
        )
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution found:")

        res = []
        for free_id, (day_var, time_var) in free_vars.items():
            print(
                f"Free Destination {free_id}: Day {solver.Value(day_var)}, Time {solver.Value(time_var)}"
            )
            res.append(
                {
                    "destination": free_id,
                    "day": solver.Value(day_var),
                    "hour": solver.Value(time_var),
                    "type": "free",
                }
            )

        for semi_id, option_vars in semi_fixed_vars.items():
            chosen_option = [
                i for i, var in enumerate(option_vars) if solver.Value(var)
            ]
            if chosen_option:
                day, time = [i for i in semi_fixed_destinations if semi_id == i["id"]][
                    0
                ]["options"][chosen_option[0]]
                print(f"Semi-Fixed Destination {semi_id}: Day {day}, Time {time}")
                res.append(
                    {
                        "destination": semi_id,
                        "day": solver.Value(day),
                        "hour": solver.Value(time),
                        "type": "semi-fixed",
                    }
                )

        G = nx.Graph()
        G.add_nodes_from(range(n))
        routes = []

        for day in days:
            print(f"Day {day} route:")
            for i in range(n):
                for j in range(n):
                    if i != j and solver.Value(tsp_vars[(i, j, day)]):
                        routes.append((i, j))
                        print(f"Travel from {i} to {j}")

        G.add_edges_from(routes)
        nx.draw(G, with_labels=True)
        plt.title("Traveling Salesman Problem Solution")
        plt.show()
        return res
    else:
        print("No solution found.")


def generate_best_for_free(
    fixed_destinations: List[Dict],
    semi_fixed_destinations: List[Dict],
    free_destinations: List[Dict],
    days: List[int] = range(30),
    time_slots_per_day: List[int] = list(range(8, 18)),
):
    for i in free_destinations:
        res = generate_tsp(
            fixed_destinations,
            semi_fixed_destinations,
            [i],
            days,
            time_slots_per_day,
        )
        return [i for i in res if i["type"] == "free"][0]


def generate_best_for_semi_fixed(
    fixed_destinations: List[Dict],
    semi_fixed_destinations: List[Dict],
    days: List[int] = range(30),
    time_slots_per_day: List[int] = list(range(8, 18)),
):
    return generate_tsp(
        fixed_destinations,
        semi_fixed_destinations,
        [],
        days,
        time_slots_per_day,
    )


if __name__ == "__main__":
    # zip_codes = [2181] + [int(i) for i in generate_random_zip_codes(10)]
    zip_codes = ["S"] + ["A", "B", "C", "D"]
    time_slots_per_day = list(range(8 * 60, 18 * 60))
    days = range(30)
    # fixed_destinations = [
    #     {
    #         "zip": zip_codes[i],
    #         "day": random.choice(days),
    #         "time": random.choice(time_slots_per_day),
    #     }
    #     for i in range(1, 3)
    # ]
    fixed_destinations = [
        {"id": 1, "zip": "A", "day": 1, "time": 600},
        {"id": 2, "zip": "C", "day": 2, "time": 690},
    ]

    # semi_fixed_destinations = [
    #     {
    #         "zip": zip_codes[i],
    #         "options": [
    #             (random.choice(days), random.choice(time_slots_per_day))
    #             for _ in range(3)
    #         ],
    #     }
    #     for i in range(3, 6)
    # ]
    semi_fixed_destinations = [
        {"id": 3, "zip": "B", "options": [(1, 570), (1, 720), (1, 900)]},
        {"id": 4, "zip": "D", "options": [(2, 540), (2, 870), (2, 960)]},
    ]

    # free_destinations = [{"zip": zip_codes[i]} for i in range(6, 11)]
    free_destinations = [
        {"id": 5, "zip": "A"},
        {"id": 6, "zip": "B"},
        {"id": 7, "zip": "C"},
    ]

    # res1 = generate_best_for_free(
    #     fixed_destinations, semi_fixed_destinations, free_destinations,  days
    # )

    # res2 = generate_best_for_semi_fixed(
    #     fixed_destinations, semi_fixed_destinations,  days
    # )
    generate_tsp(fixed_destinations, semi_fixed_destinations, free_destinations, days)
