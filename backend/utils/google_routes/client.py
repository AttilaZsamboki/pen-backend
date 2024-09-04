import requests
import json
from .distance_matrix import DistanceMatrix


class Client:
    def __init__(self, key, country="Hungary"):
        self.api_key = key
        self.base_url = "https://routes.googleapis.com/directions/v2:"
        self.country = country

    def distance_matrix(
        self, origin_addresses, dest_addresses, travel_mode="DRIVE", fields=["*"]
    ):
        url = f"{self.base_url}computeRouteMatrix"

        payload = json.dumps(
            {
                "origins": [
                    [{"waypoint": {"address": i}} for i in origin_addresses],
                ],
                "destinations": [
                    [{"waypoint": {"address": i}} for i in dest_addresses],
                ],
                "travelMode": travel_mode,
            }
        )
        headers = {
            "Content-Type": "application/json",
            "X-Goog-FieldMask": ",".join(
                (fields + ["originIndex", "destinationIndex"]) if fields else ["*"]
            ),
            "X-Goog-Api-Key": self.api_key,
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception("Error:", response.status_code, response.text)
        return DistanceMatrix(response.json())

    def routes(self, origin, destination):
        url = f"{self.base_url}computeRoutes"

        payload = json.dumps(
            {
                "origin": {
                    "address": origin + ", " + self.country,
                },
                "destination": {
                    "address": destination + ", " + self.country,
                },
                "travelMode": "DRIVE",
                "routingPreference": "TRAFFIC_UNAWARE",
            }
        )

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return RoutesResult(response.json())


class RoutesResult:
    class Route:
        def __init__(self, data):
            self.duration = data.get("duration")
            self.distance_meters = data.get("distanceMeters")

        def __str__(self):
            return str(self.duration)

        def parse_duration(self):
            return int(self.duration[:-1])

    def __init__(self, data):
        self.routes = [self.Route(i) for i in data.get("routes")]
