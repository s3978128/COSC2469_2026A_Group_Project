"""A* wrapper using ALT landmark heuristics."""

from algorithms.a_star import a_star
from algorithms.landmark_heuristic import alt_heuristic


def a_star_alt(
    graph,
    start,
    goal,
    cost_func,
    start_time=0,
    return_visited=False,
    return_stats=False,
    avoid_nodes=None,
    avoid_edges=None,
    landmark_count=4,
    heuristic_weight=1.0,
):
    """Run A* with ALT-based heuristic on distance routing tasks."""

    def _heuristic(g, node_id, goal_id):
        return alt_heuristic(g, node_id, goal_id, landmark_count=landmark_count)

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
