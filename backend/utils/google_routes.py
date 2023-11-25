import requests
import json


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


class DistanceMatrix:
    def __init__(self, data):
        self.data = data

    def get_element(self, origin_idx, destination_idx):
        if origin_idx == destination_idx:
            return DistanceMatrixElement({"duration": "0s"})
        distance_obj = [
            i
            for i in self.data
            if i["originIndex"] == origin_idx
            and i["destinationIndex"] == destination_idx
        ]
        if not distance_obj:
            return None
        return DistanceMatrixElement(distance_obj[0])

    def merge(self, other):
        self.data += other.data

    def __str__(self):
        return str(self.data)


class DistanceMatrixElement:
    def __init__(self, element):
        self.originIndex = element.get("originIndex")
        self.destinationIndex = element.get("destinationIndex")
        self.status = element.get("status")
        self.duration = element.get("duration")
        self.staticDuration = element.get("staticDuration")
        self.condition = element.get("condition")
        self.localizedValues = element.get("localizedValues")

    def get_duration_value(self):
        return int(self.duration[:-1] if self.duration else 0)
