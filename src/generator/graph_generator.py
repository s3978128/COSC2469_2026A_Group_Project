"""Utility functions for generating realistic road network graphs.

Road networks are modeled with:
- Coordinate-based node placement enabling spatial queries and A* heuristics
- Road types (highway, main, local) with realistic speed/distance profiles
- Proximity-based connectivity maintaining arc/node ratio ≈ 2.6–3.2
- Mixed one-way and two-way roads as directed edges
- Time-dependent traffic with granular rush hour simulation
"""

import math
import random

from graph.graph import Graph


def _traffic_profile(base_time, road_type="main"):
    """Create a 24-hour traffic profile with granular rush hour simulation.

    Parameters
    ----------
    base_time : float
        Base travel time in minutes (no traffic).
    road_type : {"highway", "main", "local"}
        Road classification affects congestion patterns.

    Returns
    -------
    list[float]
        24 travel times (one per hour 0–23) with realistic traffic variation.
    """
    times = []
    for hour in range(24):
        multiplier = 1.0

        # Night: less traffic (0–5)
        if 0 <= hour <= 5:
            multiplier = 0.85

        # Morning rush: 7–9 (peak 8–9)
        elif 6 <= hour <= 9:
            if 8 <= hour <= 9:
                multiplier = 1.5  # Peak congestion
            else:
                multiplier = 1.3

        # Daytime: lighter traffic (10–15)
        elif 10 <= hour <= 15:
            multiplier = 1.0

        # Evening rush: 16–19 (peak 17–18)
        elif 16 <= hour <= 19:
            if 17 <= hour <= 18:
                multiplier = 1.6  # Peak congestion
            else:
                multiplier = 1.4

        # Night recovery: 20–23
        else:
            multiplier = 0.9

        # Road type modulates congestion sensitivity
        # Highways less affected by congestion, local streets more
        if road_type == "highway":
            multiplier = 0.8 + (multiplier - 1.0) * 0.4
        elif road_type == "local":
            multiplier = 1.0 + (multiplier - 1.0) * 1.2

        times.append(round(base_time * multiplier, 2))

    return times


def _hourly_times(base_time):
    """Legacy function for backward compatibility."""
    return _traffic_profile(base_time, road_type="main")


def generate_small_test_graph():
    """Build a small directed graph for testing pathfinding logic.

    Two-way roads are represented as two directed edges.
    One-way roads are represented as a single directed edge.
    """
    graph = Graph()

    # Node coordinates for visualization (arranged in a simple layout)
    node_coords = {
        "A": (0.0, 0.0),
        "B": (1.0, 0.0),
        "C": (0.0, 2.0),
        "D": (1.0, 2.0),
        "E": (2.0, 2.0),
        "F": (1.0, 4.0),
    }

    # Add nodes with coordinates
    for node_id, (x, y) in node_coords.items():
        graph.add_node(node_id, x=x, y=y)

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


# ── Realistic road network generation ────────────────────────────────

class RoadType:
    """Road classification with realistic parameters."""

    HIGHWAY = {
        "avg_distance": (8.0, 15.0),  # km range
        "avg_speed": 80,  # km/h (base)
        "ratio": 0.3,  # proportion of total roads
    }
    MAIN = {
        "avg_distance": (3.0, 7.0),
        "avg_speed": 50,
        "ratio": 0.5,
    }
    LOCAL = {
        "avg_distance": (0.5, 2.5),
        "avg_speed": 30,
        "ratio": 0.2,
    }


SCENARIO_PROFILES = {
    "realistic": {
        "base_degree": (2, 4),
        "hub_degree": None,
        "hub_fraction": 0.0,
        "max_connection_distance": 2.0,
        "two_way_probability": 0.8,
    },
    "mixed": {
        "base_degree": (2, 4),
        "hub_degree": (5, 7),
        "hub_fraction": 0.15,
        "max_connection_distance": 2.4,
        "two_way_probability": 0.75,
    },
    "stress": {
        "base_degree": (3, 6),
        "hub_degree": (6, 8),
        "hub_fraction": 0.30,
        "max_connection_distance": 3.0,
        "two_way_probability": 0.70,
    },
}


def _euclidean_distance(p1, p2):
    """Compute Euclidean distance between two (x, y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _generate_grid_nodes(rows, cols, spacing=1.0):
    """Generate node positions on a regular grid.

    Parameters
    ----------
    rows, cols : int
        Grid dimensions.
    spacing : float
        Distance between adjacent grid points (km).

    Returns
    -------
    dict[str, tuple[float, float]]
        Mapping node_id -> (x, y) coordinates.
    """
    nodes = {}
    for i in range(rows):
        for j in range(cols):
            node_id = f"N_{i}_{j}"
            x = i * spacing
            y = j * spacing
            nodes[node_id] = (x, y)
    return nodes


def _find_nearby_nodes(node_id, node_positions, max_distance, exclude_self=True):
    """Find all nodes within max_distance of a given node.

    Parameters
    ----------
    node_id : str
    node_positions : dict
    max_distance : float
        Search radius in km.
    exclude_self : bool

    Returns
    -------
    list[str]
        Sorted by distance (nearest first).
    """
    if node_id not in node_positions:
        return []

    pos = node_positions[node_id]
    nearby = []

    for other_id, other_pos in node_positions.items():
        if exclude_self and other_id == node_id:
            continue

        dist = _euclidean_distance(pos, other_pos)
        if dist <= max_distance:
            nearby.append((dist, other_id))

    nearby.sort()
    return [node_id for _, node_id in nearby]


def _choose_road_type(rng):
    """Randomly choose a road type weighted by typical proportions."""
    rand = rng.random()
    if rand < RoadType.HIGHWAY["ratio"]:
        return "highway"
    elif rand < RoadType.HIGHWAY["ratio"] + RoadType.MAIN["ratio"]:
        return "main"
    else:
        return "local"


def _sample_road_distance(road_type, rng):
    """Sample a realistic distance for a road type."""
    if road_type == "highway":
        return rng.uniform(*RoadType.HIGHWAY["avg_distance"])
    elif road_type == "main":
        return rng.uniform(*RoadType.MAIN["avg_distance"])
    else:
        return rng.uniform(*RoadType.LOCAL["avg_distance"])


def _distance_to_travel_time(distance_km, road_type):
    """Convert distance to base travel time (minutes) for a road type."""
    if road_type == "highway":
        speed = RoadType.HIGHWAY["avg_speed"]
    elif road_type == "main":
        speed = RoadType.MAIN["avg_speed"]
    else:
        speed = RoadType.LOCAL["avg_speed"]

    return (distance_km / speed) * 60


def _build_degree_targets(node_ids, nearby_map, rng, profile):
    """Build per-node out-degree targets for the selected scenario."""
    min_degree, max_degree = profile["base_degree"]
    targets = {
        node_id: rng.randint(min_degree, max_degree)
        for node_id in node_ids
    }

    hub_degree = profile["hub_degree"]
    hub_fraction = profile["hub_fraction"]
    if hub_degree and hub_fraction > 0:
        hub_count = min(len(node_ids), max(1, int(len(node_ids) * hub_fraction)))
        for hub_id in rng.sample(node_ids, hub_count):
            targets[hub_id] = rng.randint(hub_degree[0], hub_degree[1])

    # Clamp targets to the number of available nearby nodes.
    for node_id in node_ids:
        targets[node_id] = min(targets[node_id], len(nearby_map[node_id]))

    return targets


def _add_directed_edge_if_missing(graph, source, destination, distance, time_weights):
    """Add a directed edge only if the source does not already point to destination."""
    if any(edge.destination == destination for edge in graph.neighbors(source)):
        return False

    graph.add_one_way_edge(source, destination, distance, time_weights)
    return True


def generate_realistic_graph(rows=4, cols=4, seed=42, scenario="realistic"):
    """Generate a realistic urban road network on a grid.

    Nodes are placed on a grid; edges connect nearby nodes with realistic
    road classifications, distances, and traffic patterns.

    Parameters
    ----------
    rows, cols : int
        Grid dimensions (default 4×4 = 16 nodes ≈ 42–52 edges).
    seed : int
        Random seed for reproducibility.
    scenario : {"realistic", "mixed", "stress"}
        Connectivity profile:
        - realistic: mostly 2–4 outgoing roads per node.
        - mixed: mostly 2–4 with a small fraction of 5–7 road hubs.
        - stress: denser graph with broader 3–8 connectivity.

    Returns
    -------
    Graph
        Directed graph with coordinates and realistic traffic profiles.
    """
    if scenario not in SCENARIO_PROFILES:
        valid = ", ".join(sorted(SCENARIO_PROFILES))
        raise ValueError(f"Unknown scenario '{scenario}'. Expected one of: {valid}")

    profile = SCENARIO_PROFILES[scenario]
    rng = random.Random(seed)
    graph = Graph()

    # Generate grid nodes with coordinates
    node_positions = _generate_grid_nodes(rows, cols, spacing=1.0)

    # Add all nodes to graph
    for node_id, (x, y) in node_positions.items():
        graph.add_node(node_id, x=x, y=y)

    node_ids = sorted(node_positions.keys())
    nearby_map = {
        node_id: _find_nearby_nodes(
            node_id,
            node_positions,
            profile["max_connection_distance"],
            exclude_self=True,
        )
        for node_id in node_ids
    }
    degree_targets = _build_degree_targets(node_ids, nearby_map, rng, profile)

    # Build outgoing links per node; optional reverse links create two-way roads.
    for node_id in node_ids:
        candidates = list(nearby_map[node_id])
        rng.shuffle(candidates)

        while len(graph.neighbors(node_id)) < degree_targets[node_id] and candidates:
            neighbor_id = candidates.pop()

            road_type = _choose_road_type(rng)
            distance = _sample_road_distance(road_type, rng)
            time_weights = _traffic_profile(
                _distance_to_travel_time(distance, road_type),
                road_type,
            )

            added = _add_directed_edge_if_missing(
                graph,
                node_id,
                neighbor_id,
                distance,
                time_weights,
            )
            if not added:
                continue

            should_add_reverse = rng.random() < profile["two_way_probability"]
            neighbor_has_capacity = (
                len(graph.neighbors(neighbor_id)) < degree_targets[neighbor_id]
            )
            if should_add_reverse and neighbor_has_capacity:
                _add_directed_edge_if_missing(
                    graph,
                    neighbor_id,
                    node_id,
                    distance,
                    time_weights,
                )

    return graph
