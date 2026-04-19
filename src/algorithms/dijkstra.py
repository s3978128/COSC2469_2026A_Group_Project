"""Generic Dijkstra shortest-path algorithm for adjacency-list graphs."""

from utils.min_heap import MinHeap


def dijkstra(graph, start, goal, cost_func, start_time=0, return_visited=False):
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

    Returns
    -------
    (path, total_cost) or (path, total_cost, visited_order)
        *path* is a list of node ids from *start* to *goal*.
        *total_cost* is the accumulated cost along that path.
        If *goal* is unreachable, returns ``([], float('inf'))``.
    """
    if start not in graph.adj or goal not in graph.adj:
        raise ValueError("start and goal must exist in the graph")

    best_cost = {start: 0.0}
    previous = {start: None}
    visited = set()
    visited_order = []

    pq = MinHeap()
    pq.push((0.0, start_time, start))

    while not pq.is_empty():
        current_cost, current_time, node = pq.pop()

        if node in visited:
            continue
        visited.add(node)
        visited_order.append(node)

        if node == goal:
            break

        for edge in graph.neighbors(node):
            neighbor = edge.destination
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
    if goal not in best_cost:
        if return_visited:
            return [], float('inf'), visited_order
        return [], float('inf')

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    if return_visited:
        return path, best_cost[goal], visited_order

    return path, best_cost[goal]
