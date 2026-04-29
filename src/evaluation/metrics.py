"""Path quality and reporting helpers for route evaluation."""


def _find_edge(graph, source, destination):
    """Return the directed edge source -> destination, or None if missing."""
    for edge in graph.neighbors(source):
        if edge.destination == destination:
            return edge
    return None


def path_total_distance(graph, path):
    """Return the total physical distance for a path.

    Raises
    ------
    ValueError
        If any consecutive node pair in the path is not connected.
    """
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path) - 1):
        edge = _find_edge(graph, path[i], path[i + 1])
        if edge is None:
            raise ValueError(f"No edge found for segment {path[i]} -> {path[i + 1]}")
        total += edge.distance
    return total


def path_total_travel_time(graph, path, start_time=0):
    """Return total travel time in minutes for a path with hour-based traffic.

    Parameters
    ----------
    start_time : int or float
        Start time in minutes.
    """
    if len(path) < 2:
        return 0.0

    total = 0.0
    current_time = float(start_time)

    for i in range(len(path) - 1):
        edge = _find_edge(graph, path[i], path[i + 1])
        if edge is None:
            raise ValueError(f"No edge found for segment {path[i]} -> {path[i + 1]}")

        hour = int(current_time // 60) % 24
        segment_time = edge.get_travel_time(hour)
        total += segment_time
        current_time += segment_time

    return total


def build_path_report(graph, path, optimized_cost, start_time=0):
    """Build a compact dictionary of path metrics for analysis output."""
    return {
        "path": list(path),
        "path_length_nodes": len(path),
        "optimized_cost": float(optimized_cost),
        "distance": path_total_distance(graph, path),
        "travel_time": path_total_travel_time(graph, path, start_time=start_time),
    }
