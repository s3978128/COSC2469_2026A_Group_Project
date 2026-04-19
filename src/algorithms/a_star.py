"""A* shortest-path search for distance-style routing.

This implementation mirrors the Dijkstra API used across the project so it can
plug into CLI/benchmark code with minimal changes.
"""

from utils.min_heap import MinHeap


def _default_heuristic(graph, node_id, goal_id):
    """Return an admissible geometric heuristic when coordinates are available.

    Falls back to 0.0 if coordinates are missing, which makes A* behave like
    Dijkstra while preserving correctness.
    """
    node = graph.get_node(node_id)
    goal = graph.get_node(goal_id)
    if node is None or goal is None:
        return 0.0
    if node.x is None or node.y is None or goal.x is None or goal.y is None:
        return 0.0
    scale = 0.0
    if hasattr(graph, "distance_heuristic_scale"):
        scale = float(graph.distance_heuristic_scale())
    return scale * graph.euclidean_distance(node, goal)


def a_star(
    graph,
    start,
    goal,
    cost_func,
    start_time=0,
    return_visited=False,
    return_stats=False,
    avoid_nodes=None,
    avoid_edges=None,
    heuristic_fn=None,
    heuristic_weight=1.0,
):
    """Run A* with a caller-supplied edge cost function.

    Parameters mirror ``algorithms.dijkstra.dijkstra`` with an additional
    ``heuristic_fn(graph, node_id, goal_id) -> float`` override.
    """
    if start not in graph.adj or goal not in graph.adj:
        raise ValueError("start and goal must exist in the graph")
    if heuristic_weight < 1.0:
        raise ValueError("heuristic_weight must be >= 1.0")

    blocked_nodes = set(avoid_nodes or [])
    blocked_edges = set(avoid_edges or [])

    if start in blocked_nodes or goal in blocked_nodes:
        raise ValueError("start/goal cannot be in avoid_nodes")

    heuristic = heuristic_fn or _default_heuristic

    g_score = {start: 0.0}
    previous = {start: None}
    visited = set()
    visited_order = []
    expanded_nodes = 0

    # (f_score, g_score, current_time, node_id)
    open_heap = MinHeap()
    open_heap.push(
        (heuristic_weight * heuristic(graph, start, goal), 0.0, float(start_time), start)
    )

    while not open_heap.is_empty():
        _, current_cost, current_time, node = open_heap.pop()

        if node in visited:
            continue
        visited.add(node)
        visited_order.append(node)
        expanded_nodes += 1

        if node == goal:
            break

        for edge in graph.neighbors(node):
            neighbor = edge.destination
            if neighbor in blocked_nodes:
                continue
            if (edge.source, edge.destination) in blocked_edges:
                continue
            if neighbor in visited:
                continue

            edge_cost = cost_func(edge, current_time)
            if edge_cost < 0:
                raise ValueError("A* requires non-negative edge costs")

            tentative_g = current_cost + edge_cost
            next_time = current_time + edge_cost

            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                previous[neighbor] = node
                f_score = tentative_g + (heuristic_weight * heuristic(graph, neighbor, goal))
                open_heap.push((f_score, tentative_g, next_time, neighbor))

    stats = {
        "expanded_nodes": expanded_nodes,
    }

    if goal not in g_score:
        if return_visited and return_stats:
            return [], float("inf"), visited_order, stats
        if return_visited:
            return [], float("inf"), visited_order
        if return_stats:
            return [], float("inf"), stats
        return [], float("inf")

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    if return_visited and return_stats:
        return path, g_score[goal], visited_order, stats
    if return_visited:
        return path, g_score[goal], visited_order
    if return_stats:
        return path, g_score[goal], stats
    return path, g_score[goal]
