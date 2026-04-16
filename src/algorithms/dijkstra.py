"""Generic Dijkstra shortest-path algorithm for adjacency-list graphs."""

from utils.min_heap import MinHeap


def dijkstra(graph, start, goal, cost_func, start_time=0):
    """Run Dijkstra's algorithm with a caller-supplied cost function.

    Parameters
    ----------
    graph      : Graph object whose ``neighbors(node_id)`` returns Edge objects.
    start      : Start node id.
    goal       : Destination node id.
    cost_func  : Callable ``(edge, current_time) -> float`` that returns the
                 traversal cost of an edge given the current accumulated time.
    start_time : Initial time value (integer hour, default 0).

    Returns
    -------
    (path, total_cost)
        *path* is a list of node ids from *start* to *goal*.
        *total_cost* is the accumulated cost along that path.
        If *goal* is unreachable, returns ``([], float('inf'))``.
    """
    if start not in graph.adj or goal not in graph.adj:
        raise ValueError("start and goal must exist in the graph")

    best_cost = {start: 0.0}
    current_times = {start: start_time}
    previous = {start: None}
    visited = set()

    pq = MinHeap()
    pq.push((0.0, start_time, start))

    while not pq.is_empty():
        current_cost, current_time, node = pq.pop()

        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            break

        for edge in graph.neighbors(node):
            neighbor = edge.destination
            if neighbor in visited:
                continue

            edge_cost = cost_func(edge, current_time)
            new_cost = current_cost + edge_cost
            new_time = current_time + edge_cost

            if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                best_cost[neighbor] = new_cost
                current_times[neighbor] = new_time
                previous[neighbor] = node
                pq.push((new_cost, new_time, neighbor))

    # ── Path reconstruction ──────────────────────────────────────────
    if goal not in best_cost:
        return [], float('inf')

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    return path, best_cost[goal]


# ── Convenience cost functions ───────────────────────────────────────

# def cost_by_distance(edge, current_time):
#     """Cost function that returns the edge's fixed distance."""
#     return edge.distance


# def cost_by_time(edge, current_time):
#     """Cost function that returns the travel time at the current hour."""
#     hour = int(current_time) % 24
#     return edge.get_travel_time(hour)
