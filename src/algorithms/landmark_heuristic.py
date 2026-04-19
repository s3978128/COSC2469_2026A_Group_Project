"""ALT-style landmark heuristic utilities for directed distance routing."""

from utils.min_heap import MinHeap


def _single_source_distances(graph, source, use_reverse=False):
    """Compute shortest distances from a source over forward or reverse edges."""
    if source not in graph.adj:
        return {}

    distances = {source: 0.0}
    settled = set()

    pq = MinHeap()
    pq.push((0.0, source))

    while not pq.is_empty():
        current_cost, node = pq.pop()
        if node in settled:
            continue
        settled.add(node)

        if use_reverse:
            neighbors = graph.reverse_neighbors(node)
            for predecessor, edge in neighbors:
                edge_cost = edge.distance
                if edge_cost < 0:
                    raise ValueError("ALT preprocessing requires non-negative edge costs")
                new_cost = current_cost + edge_cost
                if new_cost < distances.get(predecessor, float("inf")):
                    distances[predecessor] = new_cost
                    pq.push((new_cost, predecessor))
        else:
            for edge in graph.neighbors(node):
                edge_cost = edge.distance
                if edge_cost < 0:
                    raise ValueError("ALT preprocessing requires non-negative edge costs")
                neighbor = edge.destination
                new_cost = current_cost + edge_cost
                if new_cost < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_cost
                    pq.push((new_cost, neighbor))

    return distances


def _select_landmarks(graph, landmark_count=4):
    """Select deterministic spread landmarks from available node coordinates."""
    node_ids = graph.nodes()
    if not node_ids:
        return []

    nodes_with_coords = []
    for node_id in node_ids:
        node = graph.get_node(node_id)
        if node is not None and node.x is not None and node.y is not None:
            nodes_with_coords.append((node_id, node.x, node.y))

    selected = []
    if nodes_with_coords:
        # Pick extreme points in two coordinate projections.
        picks = [
            min(nodes_with_coords, key=lambda item: item[1] + item[2])[0],
            max(nodes_with_coords, key=lambda item: item[1] + item[2])[0],
            min(nodes_with_coords, key=lambda item: item[1] - item[2])[0],
            max(nodes_with_coords, key=lambda item: item[1] - item[2])[0],
        ]
        for node_id in picks:
            if node_id not in selected:
                selected.append(node_id)
            if len(selected) >= landmark_count:
                return selected

    # Fill any remaining slots with evenly spaced node ids for determinism.
    if len(selected) < landmark_count:
        ordered = sorted(node_ids)
        step = max(1, len(ordered) // max(1, landmark_count))
        for idx in range(0, len(ordered), step):
            node_id = ordered[idx]
            if node_id not in selected:
                selected.append(node_id)
            if len(selected) >= landmark_count:
                break

    return selected[:landmark_count]


def _ensure_alt_cache(graph, landmark_count=4):
    """Build and cache landmark distance tables on the graph object."""
    requested_count = max(1, int(landmark_count))

    cache = getattr(graph, "_alt_landmark_cache", None)
    if cache and cache.get("landmark_count") == requested_count:
        return cache

    landmarks = _select_landmarks(graph, requested_count)
    dist_from = {}
    dist_to = {}
    for landmark in landmarks:
        dist_from[landmark] = _single_source_distances(graph, landmark, use_reverse=False)
        dist_to[landmark] = _single_source_distances(graph, landmark, use_reverse=True)

    cache = {
        "landmark_count": requested_count,
        "landmarks": tuple(landmarks),
        "dist_from": dist_from,
        "dist_to": dist_to,
    }
    graph._alt_landmark_cache = cache
    return cache


def precompute_alt_landmarks(graph, landmark_count=4):
    """Force-build ALT landmark cache before query-time measurements."""
    _ensure_alt_cache(graph, landmark_count=landmark_count)


def alt_heuristic(graph, node_id, goal_id, landmark_count=4):
    """Return ALT lower-bound estimate for directed graphs.

    Uses both directed inequalities:
    - d(node, goal) >= d(L, goal) - d(L, node)
    - d(node, goal) >= d(node, L) - d(goal, L)
    """
    if node_id == goal_id:
        return 0.0

    cache = _ensure_alt_cache(graph, landmark_count=landmark_count)
    lower_bound = 0.0

    for landmark in cache["landmarks"]:
        from_l = cache["dist_from"][landmark]
        to_l = cache["dist_to"][landmark]

        l_to_goal = from_l.get(goal_id)
        l_to_node = from_l.get(node_id)
        if l_to_goal is not None and l_to_node is not None:
            lower_bound = max(lower_bound, l_to_goal - l_to_node)

        node_to_l = to_l.get(node_id)
        goal_to_l = to_l.get(goal_id)
        if node_to_l is not None and goal_to_l is not None:
            lower_bound = max(lower_bound, node_to_l - goal_to_l)

    return max(0.0, lower_bound)
