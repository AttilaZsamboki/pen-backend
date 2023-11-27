from .distance_matrix_element import DistanceMatrixElement


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
