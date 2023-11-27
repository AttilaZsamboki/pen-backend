import requests
import json
from .distance_matrix import DistanceMatrix


class Client:
    def __init__(self, key):
        self.api_key = key

    def distance_matrix(
        self, origin_addresses, dest_addresses, travel_mode="DRIVE", fields=["*"]
    ):
        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

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
            "X-Goog-FieldMask": ",".join(fields + ["originIndex", "destinationIndex"]),
            "X-Goog-Api-Key": self.api_key,
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception("Error:", response.status_code, response.text)
        return DistanceMatrix(response.json())
