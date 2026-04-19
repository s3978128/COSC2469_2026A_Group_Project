"""Weighted A* for distance routing.

Weighted A* uses ``f(n) = g(n) + w*h(n)`` with ``w >= 1`` to trade optimality
for speed. With ``w=1`` this is standard A*.
"""

from algorithms.a_star import a_star


def weighted_a_star(
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
    heuristic_weight=1.25,
):
    """Run weighted A* with a Dijkstra-compatible function signature."""
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
        heuristic_fn=heuristic_fn,
        heuristic_weight=heuristic_weight,
    )
