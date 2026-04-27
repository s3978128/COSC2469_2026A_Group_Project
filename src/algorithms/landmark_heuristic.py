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


# ---------------------------------------------------------------------------
# Time-based ALT: uses min travel time across all 24 hours as edge cost.
# This is always a valid lower bound on cost_by_time, making the heuristic
# admissible and consistent for time-dependent A* queries.
# ---------------------------------------------------------------------------

def _min_travel_time(edge):
    """Return the minimum travel time for an edge over all 24 hours."""
    return min(edge.time_list)


def _single_source_min_time_distances(graph, source, use_reverse=False):
    """Dijkstra from *source* using min-over-24h travel time as edge cost."""
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
            for predecessor, edge in graph.reverse_neighbors(node):
                edge_cost = _min_travel_time(edge)
                new_cost = current_cost + edge_cost
                if new_cost < distances.get(predecessor, float("inf")):
                    distances[predecessor] = new_cost
                    pq.push((new_cost, predecessor))
        else:
            for edge in graph.neighbors(node):
                edge_cost = _min_travel_time(edge)
                new_cost = current_cost + edge_cost
                if new_cost < distances.get(edge.destination, float("inf")):
                    distances[edge.destination] = new_cost
                    pq.push((new_cost, edge.destination))

    return distances


def _ensure_time_alt_cache(graph, landmark_count=4):
    """Build and cache time-based ALT landmark tables on the graph object."""
    requested_count = max(1, int(landmark_count))

    cache = getattr(graph, "_time_alt_landmark_cache", None)
    if cache and cache.get("landmark_count") == requested_count:
        return cache

    landmarks = _select_landmarks(graph, requested_count)
    dist_from = {}
    dist_to = {}
    for landmark in landmarks:
        dist_from[landmark] = _single_source_min_time_distances(graph, landmark, use_reverse=False)
        dist_to[landmark] = _single_source_min_time_distances(graph, landmark, use_reverse=True)

    cache = {
        "landmark_count": requested_count,
        "landmarks": tuple(landmarks),
        "dist_from": dist_from,
        "dist_to": dist_to,
    }
    graph._time_alt_landmark_cache = cache
    return cache


def precompute_time_alt_landmarks(graph, landmark_count=4):
    """Force-build time-based ALT landmark cache before query-time measurements."""
    _ensure_time_alt_cache(graph, landmark_count=landmark_count)


def time_alt_heuristic(graph, node_id, goal_id, landmark_count=4):
    """Admissible ALT lower-bound on travel time for time-dependent routing.

    Uses min-over-24h travel time distances to landmarks.  The lower bound is
    always <= the actual cost_by_time path cost, so A* remains optimal.
    """
    if node_id == goal_id:
        return 0.0

    cache = _ensure_time_alt_cache(graph, landmark_count=landmark_count)
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


# ---------------------------------------------------------------------------
# Active landmark selection: precompute more landmarks, pick best per query.
# ---------------------------------------------------------------------------

def _select_active_time_landmarks(cache, start_id, goal_id, active_count):
    """Select up to active_count landmarks that give the tightest bounds for
    the (start, goal) pair.  Uses the ALT paper heuristic: score each landmark
    by the maximum triangle-inequality bound it can produce between start and
    goal, then return the top-scoring ones.
    """
    scored = []
    for landmark in cache["landmarks"]:
        from_l = cache["dist_from"][landmark]
        to_l   = cache["dist_to"][landmark]

        score = 0.0
        l_to_goal  = from_l.get(goal_id,  0.0)
        l_to_start = from_l.get(start_id, 0.0)
        score = max(score, l_to_goal - l_to_start)

        start_to_l = to_l.get(start_id, 0.0)
        goal_to_l  = to_l.get(goal_id,  0.0)
        score = max(score, start_to_l - goal_to_l)

        scored.append((score, landmark))

    scored.sort(reverse=True)
    return [lm for _, lm in scored[:active_count]]


def make_active_time_alt_heuristic(graph, start_id, goal_id,
                                    landmark_count=16, active_count=4):
    """Return a heuristic closure with landmarks pre-selected for (start, goal).

    Precomputes ``landmark_count`` landmarks (if not already cached) but only
    uses the best ``active_count`` of them during the actual A* expansion.
    This amortises landmark preprocessing across queries while keeping per-node
    heuristic evaluation cheap.
    """
    cache = _ensure_time_alt_cache(graph, landmark_count=landmark_count)
    active = _select_active_time_landmarks(cache, start_id, goal_id, active_count)

    def _heuristic(g, node_id, goal_id_inner):
        if node_id == goal_id_inner:
            return 0.0
        lower_bound = 0.0
        for landmark in active:
            from_l = cache["dist_from"][landmark]
            to_l   = cache["dist_to"][landmark]

            l_to_goal = from_l.get(goal_id_inner)
            l_to_node = from_l.get(node_id)
            if l_to_goal is not None and l_to_node is not None:
                lower_bound = max(lower_bound, l_to_goal - l_to_node)

            node_to_l = to_l.get(node_id)
            goal_to_l = to_l.get(goal_id_inner)
            if node_to_l is not None and goal_to_l is not None:
                lower_bound = max(lower_bound, node_to_l - goal_to_l)

        return max(0.0, lower_bound)

    return _heuristic


# ---------------------------------------------------------------------------
# Departure-aware ALT: queried with a departure hour, but the bound must
# remain admissible even when paths cross midnight.  We therefore use the
# global 24-hour minimum for correctness.
# ---------------------------------------------------------------------------

def _single_source_departure_time_distances(graph, source, departure_hour,
                                             use_reverse=False):
    """Dijkstra using the global minimum travel time as edge cost.

    The departure_hour parameter is retained for API compatibility, but the
    safe admissible lower bound for a periodic time-dependent graph is the
    minimum over all 24 hours.
    """
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
            for predecessor, edge in graph.reverse_neighbors(node):
                edge_cost = min(edge.time_list)
                new_cost = current_cost + edge_cost
                if new_cost < distances.get(predecessor, float("inf")):
                    distances[predecessor] = new_cost
                    pq.push((new_cost, predecessor))
        else:
            for edge in graph.neighbors(node):
                edge_cost = min(edge.time_list)
                new_cost = current_cost + edge_cost
                if new_cost < distances.get(edge.destination, float("inf")):
                    distances[edge.destination] = new_cost
                    pq.push((new_cost, edge.destination))

    return distances


def _ensure_departure_alt_cache(graph, departure_hour=8, landmark_count=4):
    """Build and cache departure-aware landmark distance tables."""
    requested_count = max(1, int(landmark_count))
    dep_hour = int(departure_hour) % 24

    cache_attr = "_departure_alt_caches"
    all_caches = getattr(graph, cache_attr, {})

    key = (dep_hour, requested_count)
    if key in all_caches:
        return all_caches[key]

    landmarks = _select_landmarks(graph, requested_count)
    dist_from = {}
    dist_to = {}
    for landmark in landmarks:
        dist_from[landmark] = _single_source_departure_time_distances(
            graph, landmark, dep_hour, use_reverse=False
        )
        dist_to[landmark] = _single_source_departure_time_distances(
            graph, landmark, dep_hour, use_reverse=True
        )

    cache = {
        "landmark_count": requested_count,
        "departure_hour": dep_hour,
        "landmarks": tuple(landmarks),
        "dist_from": dist_from,
        "dist_to": dist_to,
    }
    all_caches[key] = cache
    setattr(graph, cache_attr, all_caches)
    return cache


def precompute_departure_alt_landmarks(graph, departure_hour=8, landmark_count=4):
    """Force-build departure-aware ALT landmark cache before query-time measurement."""
    _ensure_departure_alt_cache(graph, departure_hour=departure_hour,
                                 landmark_count=landmark_count)


def departure_time_alt_heuristic(graph, node_id, goal_id,
                                  departure_hour=8, landmark_count=4):
    """Admissible ALT lower-bound for time-dependent routing.

    The departure_hour parameter is kept for API compatibility, but the bound
    uses the global 24-hour minimum so it remains admissible across midnight.
    """
    if node_id == goal_id:
        return 0.0

    cache = _ensure_departure_alt_cache(graph, departure_hour=departure_hour,
                                         landmark_count=landmark_count)
    lower_bound = 0.0

    for landmark in cache["landmarks"]:
        from_l = cache["dist_from"][landmark]
        to_l   = cache["dist_to"][landmark]

        l_to_goal = from_l.get(goal_id)
        l_to_node = from_l.get(node_id)
        if l_to_goal is not None and l_to_node is not None:
            lower_bound = max(lower_bound, l_to_goal - l_to_node)

        node_to_l = to_l.get(node_id)
        goal_to_l = to_l.get(goal_id)
        if node_to_l is not None and goal_to_l is not None:
            lower_bound = max(lower_bound, node_to_l - goal_to_l)

    return max(0.0, lower_bound)


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
