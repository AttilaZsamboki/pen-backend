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
        return int(self.duration[:-1] if self.duration else -9999)
