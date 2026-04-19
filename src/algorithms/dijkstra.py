"""Generic Dijkstra shortest-path algorithm for adjacency-list graphs."""

from utils.min_heap import MinHeap


def dijkstra(
    graph,
    start,
    goal,
    cost_func,
    start_time=0,
    return_visited=False,
    return_stats=False,
    avoid_nodes=None,
    avoid_edges=None,
):
    """Run Dijkstra's algorithm with a caller-supplied cost function.

    Parameters
    ----------
    graph      : Graph object whose ``neighbors(node_id)`` returns Edge objects.
    start      : Start node id.
    goal       : Destination node id.
    cost_func  : Callable ``(edge, current_time) -> float`` that returns the
                 traversal cost of an edge given the current accumulated time.
    start_time : Initial time value passed to ``cost_func`` (default 0).
                 For time-based routing in this project, this value is minutes.

    return_visited : bool
        When True, also return the list of visited nodes in expansion order.

    return_stats : bool
        When True, include a stats dictionary containing explainability metrics.

    avoid_nodes : iterable[str] | None
        Optional set/list of node ids that must not appear in the route.

    avoid_edges : iterable[tuple[str, str]] | None
        Optional set/list of directed edges (source, destination) to avoid.

    Returns
    -------
    (path, total_cost), (path, total_cost, visited_order),
    (path, total_cost, stats), or (path, total_cost, visited_order, stats)
        *path* is a list of node ids from *start* to *goal*.
        *total_cost* is the accumulated cost along that path.
        If *goal* is unreachable, returns ``([], float('inf'))``.
    """
    if start not in graph.adj or goal not in graph.adj:
        raise ValueError("start and goal must exist in the graph")

    blocked_nodes = set(avoid_nodes or [])
    blocked_edges = set(avoid_edges or [])

    if start in blocked_nodes or goal in blocked_nodes:
        raise ValueError("start/goal cannot be in avoid_nodes")

    best_cost = {start: 0.0}
    previous = {start: None}
    visited = set()
    visited_order = []
    expanded_nodes = 0

    pq = MinHeap()
    pq.push((0.0, start_time, start))

    while not pq.is_empty():
        current_cost, current_time, node = pq.pop()

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
                raise ValueError("Dijkstra requires non-negative edge costs")

            new_cost = current_cost + edge_cost
            new_time = current_time + edge_cost

            if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                best_cost[neighbor] = new_cost
                previous[neighbor] = node
                pq.push((new_cost, new_time, neighbor))

    # Path reconstruction
    stats = {
        "expanded_nodes": expanded_nodes,
    }

    if goal not in best_cost:
        if return_visited and return_stats:
            return [], float('inf'), visited_order, stats
        if return_visited:
            return [], float('inf'), visited_order
        if return_stats:
            return [], float('inf'), stats
        return [], float('inf')

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    if return_visited and return_stats:
        return path, best_cost[goal], visited_order, stats
    if return_visited:
        return path, best_cost[goal], visited_order
    if return_stats:
        return path, best_cost[goal], stats

    return path, best_cost[goal]
