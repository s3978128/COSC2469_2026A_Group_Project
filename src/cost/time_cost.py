def cost_by_time(edge, current_time):
    """Cost function that returns the travel time at the current hour."""
    hour = int(current_time) % 24
    return edge.get_travel_time(hour)
