"""Edge model: stores distance and 24-hour travel-time profile."""


class Edge:
    def __init__(self, destination, distance, time_list):
        if len(time_list) != 24:
            raise ValueError("time_list must contain exactly 24 values (hours 0-23)")

        self.destination = destination
        self.distance = float(distance)
        self.time_list = [float(t) for t in time_list]

    def travel_time_at(self, hour):
        if not 0 <= hour <= 23:
            raise ValueError("hour must be in range 0-23")
        return self.time_list[hour]

    def __repr__(self):
        return f"Edge(dest={self.destination}, distance={self.distance})"