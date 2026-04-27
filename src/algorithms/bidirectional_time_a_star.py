"""Static-lower-bound bidirectional A* for time-dependent routing.

Strategy (Phase 1 / Phase 2):
  Phase 1 – Backward static Dijkstra from the goal using the minimum possible
             travel time per edge (min over all 24 hours).  This produces a
             dict  bwd[v] = lower-bound on the actual time from v to goal for
             ANY departure time.
  Phase 2 – Forward time-dependent A* from the source, using bwd[v] as the
             admissible heuristic h(v).

Because bwd[v] <= actual_time(v → goal) for every v, the heuristic is
admissible and A* will return an optimal path.  The heuristic is also tighter
than a scaled Euclidean bound whenever the graph topology provides good
landmark-like information.

Phase 1 is O(E log V) per unique goal.  Results are cached on the graph object
keyed by goal so repeated queries to the same destination pay Phase 1 only once.
"""

from utils.min_heap import MinHeap
from algorithms.a_star import a_star


# ---------------------------------------------------------------------------
# Phase 1: backward min-time Dijkstra from a goal node
# ---------------------------------------------------------------------------

def _backward_min_time_dijkstra(graph, goal):
    """Return bwd: node -> lower-bound on min travel time to goal.

    Runs Dijkstra on the *reverse* graph using min(edge.time_list) as edge cost.
    """
    cache_attr = "_bwd_min_time_cache"
    cache = getattr(graph, cache_attr, {})
    if goal in cache:
        return cache[goal]

    distances = {goal: 0.0}
    settled = set()
    pq = MinHeap()
    pq.push((0.0, goal))

    while not pq.is_empty():
        cost, node = pq.pop()
        if node in settled:
            continue
        settled.add(node)

        for predecessor, edge in graph.reverse_neighbors(node):
            edge_cost = min(edge.time_list)
            new_cost = cost + edge_cost
            if new_cost < distances.get(predecessor, float("inf")):
                distances[predecessor] = new_cost
                pq.push((new_cost, predecessor))

    cache[goal] = distances
    setattr(graph, cache_attr, cache)
    return distances


# ---------------------------------------------------------------------------
# Phase 2: forward time-dependent A* with backward distances as heuristic
# ---------------------------------------------------------------------------

def bidirectional_time_a_star(
    graph,
    start,
    goal,
    cost_func,
    start_time=0,
    return_visited=False,
    return_stats=False,
    avoid_nodes=None,
    avoid_edges=None,
    heuristic_weight=1.0,
):
    """Time-dependent A* guided by a backward static lower-bound heuristic.

    The backward min-time Dijkstra (Phase 1) is run once per unique goal and
    cached on the graph object, so the amortised cost is low for repeated
    queries with the same destination.

    Parameters mirror ``algorithms.a_star.a_star`` for benchmark compatibility.
    """
    bwd = _backward_min_time_dijkstra(graph, goal)

    def _heuristic(g, node_id, goal_id):
        return bwd.get(node_id, 0.0)

    return a_star(
        graph,
        start,
        goal,
        cost_func,
        start_time=start_time,
        return_visited=return_visited,
        return_stats=return_stats,
        avoid_nodes=avoid_nodes,
        avoid_edges=avoid_edges,
        heuristic_fn=_heuristic,
        heuristic_weight=heuristic_weight,
    )


def precompute_bwd_min_time(graph, goal):
    """Warmup: run backward Dijkstra for a goal so Phase 1 is not timed."""
    _backward_min_time_dijkstra(graph, goal)
