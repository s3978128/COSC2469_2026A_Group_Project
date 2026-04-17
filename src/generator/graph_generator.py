"""Utility functions for generating test graphs."""

from graph.graph import Graph


def _hourly_times(base_time):
    """Create a simple 24-hour traffic profile from a base travel time."""
    times = []
    for hour in range(24):
        multiplier = 1.0
        if 7 <= hour <= 9 or 16 <= hour <= 18:
            multiplier = 1.35
        elif 0 <= hour <= 5:
            multiplier = 0.9
        times.append(round(base_time * multiplier, 2))
    return times


def generate_small_test_graph():
    """Build a small directed graph for testing pathfinding logic.

    Two-way roads are represented as two directed edges.
    One-way roads are represented as a single directed edge.
    """
    graph = Graph()

    # Two-way roads: (node_a, node_b, distance_km, base_travel_time_minutes)
    two_way_roads = [
        ("A", "B", 5.0, 8.0),
        ("A", "C", 7.0, 10.0),
        ("B", "D", 4.5, 7.0),
        ("C", "D", 2.0, 4.0),
        ("C", "E", 6.0, 9.0),
        ("D", "F", 3.5, 6.0),
        ("E", "F", 2.5, 5.0),
    ]

    # One-way roads: (from, to, distance_km, base_travel_time_minutes)
    one_way_roads = [
        ("B", "E", 8.0, 12.0),
    ]

    for u, v, distance, base_time in two_way_roads:
        graph.add_two_way_edge(u, v, distance, _hourly_times(base_time))

    for u, v, distance, base_time in one_way_roads:
        graph.add_one_way_edge(u, v, distance, _hourly_times(base_time))

    return graph
