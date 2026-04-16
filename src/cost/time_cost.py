def cost_by_time(edge, current_time):
    """Cost function that returns the travel time at the current hour.

    current_time is in minutes. The hour (0-23) is derived by
    dividing by 60 and taking mod 24.
    """
    hour = int(current_time // 60) % 24
    return edge.get_travel_time(hour)
