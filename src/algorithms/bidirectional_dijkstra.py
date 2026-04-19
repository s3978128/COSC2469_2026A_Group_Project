"""Bidirectional Dijkstra for static non-negative edge costs.

This implementation is intended for distance-style objectives where edge costs
are time-independent during the search.
"""

import heapq


def bidirectional_dijkstra(
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
    """Run bidirectional Dijkstra from start and goal.

    Parameters mirror ``algorithms.dijkstra.dijkstra`` for compatibility.
    """
    if start not in graph.adj or goal not in graph.adj:
        raise ValueError("start and goal must exist in the graph")

    blocked_nodes = set(avoid_nodes or [])
    blocked_edges = set(avoid_edges or [])

    if start in blocked_nodes or goal in blocked_nodes:
        raise ValueError("start/goal cannot be in avoid_nodes")

    if start_time != 0:
        raise ValueError("bidirectional_dijkstra only supports start_time=0")

    if start == goal:
        stats = {
            "expanded_nodes": 1,
            "expanded_forward": 1,
            "expanded_backward": 0,
        }
        if return_visited and return_stats:
            return [start], 0.0, [start], stats
        if return_visited:
            return [start], 0.0, [start]
        if return_stats:
            return [start], 0.0, stats
        return [start], 0.0

    dist_f = {start: 0.0}
    dist_b = {goal: 0.0}

    prev_f = {start: None}
    next_b = {goal: None}

    pq_f = [(0.0, start)]
    pq_b = [(0.0, goal)]

    settled_f = set()
    settled_b = set()
    expanded_forward = 0
    expanded_backward = 0

    visited_order = []
    seen_visited = set()

    best_cost = float("inf")
    meeting_node = None

    def _record_visit(node_id):
        if node_id not in seen_visited:
            seen_visited.add(node_id)
            visited_order.append(node_id)

    while pq_f and pq_b:
        if pq_f[0][0] + pq_b[0][0] >= best_cost:
            break

        # Expand one node from the side with smaller frontier key.
        expand_forward = pq_f[0][0] <= pq_b[0][0]

        if expand_forward:
            current_cost, node = heapq.heappop(pq_f)
            if node in settled_f:
                continue
            settled_f.add(node)
            _record_visit(node)
            expanded_forward += 1

            if node in dist_b and current_cost + dist_b[node] < best_cost:
                best_cost = current_cost + dist_b[node]
                meeting_node = node

            for edge in graph.neighbors(node):
                neighbor = edge.destination
                if neighbor in blocked_nodes:
                    continue
                if (edge.source, edge.destination) in blocked_edges:
                    continue

                edge_cost = cost_func(edge, 0)
                if edge_cost < 0:
                    raise ValueError("Dijkstra requires non-negative edge costs")

                new_cost = current_cost + edge_cost
                if new_cost < dist_f.get(neighbor, float("inf")):
                    dist_f[neighbor] = new_cost
                    prev_f[neighbor] = node
                    heapq.heappush(pq_f, (new_cost, neighbor))

                    if neighbor in dist_b and new_cost + dist_b[neighbor] < best_cost:
                        best_cost = new_cost + dist_b[neighbor]
                        meeting_node = neighbor
        else:
            current_cost, node = heapq.heappop(pq_b)
            if node in settled_b:
                continue
            settled_b.add(node)
            _record_visit(node)
            expanded_backward += 1

            if node in dist_f and current_cost + dist_f[node] < best_cost:
                best_cost = current_cost + dist_f[node]
                meeting_node = node

            for predecessor, edge in graph.reverse_neighbors(node):
                if predecessor in blocked_nodes:
                    continue
                if (edge.source, edge.destination) in blocked_edges:
                    continue

                edge_cost = cost_func(edge, 0)
                if edge_cost < 0:
                    raise ValueError("Dijkstra requires non-negative edge costs")

                new_cost = current_cost + edge_cost
                if new_cost < dist_b.get(predecessor, float("inf")):
                    dist_b[predecessor] = new_cost
                    next_b[predecessor] = node
                    heapq.heappush(pq_b, (new_cost, predecessor))

                    if predecessor in dist_f and new_cost + dist_f[predecessor] < best_cost:
                        best_cost = new_cost + dist_f[predecessor]
                        meeting_node = predecessor

    stats = {
        "expanded_nodes": expanded_forward + expanded_backward,
        "expanded_forward": expanded_forward,
        "expanded_backward": expanded_backward,
    }

    if meeting_node is None:
        if return_visited and return_stats:
            return [], float("inf"), visited_order, stats
        if return_visited:
            return [], float("inf"), visited_order
        if return_stats:
            return [], float("inf"), stats
        return [], float("inf")

    # Reconstruct start -> meeting
    left_path = []
    cursor = meeting_node
    while cursor is not None:
        left_path.append(cursor)
        cursor = prev_f.get(cursor)
    left_path.reverse()

    # Reconstruct meeting -> goal using next_b mapping.
    right_path = []
    cursor = next_b.get(meeting_node)
    while cursor is not None:
        right_path.append(cursor)
        cursor = next_b.get(cursor)

    path = left_path + right_path

    if return_visited and return_stats:
        return path, best_cost, visited_order, stats
    if return_visited:
        return path, best_cost, visited_order
    if return_stats:
        return path, best_cost, stats
    return path, best_cost
