"""Edge model: stores source, destination, distance, and 24-hour travel-time profile."""


class Edge:
    def __init__(self, source, destination, distance, time_list):
        if len(time_list) != 24:
            raise ValueError("time_list must contain exactly 24 values (hours 0-23)")

        self.source = source
        self.destination = destination
        self.distance = float(distance)
        self.time_list = [float(t) for t in time_list]

    def get_travel_time(self, hour):
        """Return the travel time for a given hour (0-23)."""
        if not 0 <= hour <= 23:
            raise ValueError("hour must be in range 0-23")
        return self.time_list[hour]

    # Backward-compatible alias
    travel_time_at = get_travel_time

    def __repr__(self):
        return f"Edge({self.source} -> {self.destination}, distance={self.distance})"
