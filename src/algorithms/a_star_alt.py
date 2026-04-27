"""A* wrapper using ALT landmark heuristics.

Supports both distance-based and time-based landmark heuristics via the
``use_time_heuristic`` flag, removing the need for a separate a_star_time_alt
module.
"""

from algorithms.a_star import a_star
from algorithms.landmark_heuristic import (
    alt_heuristic,
    time_alt_heuristic,
    make_active_time_alt_heuristic,
    departure_time_alt_heuristic,
)


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
    use_time_heuristic=False,
):
    """Run A* with an ALT landmark heuristic.

    By default uses distance-based landmarks (admissible for cost_by_distance).
    Set ``use_time_heuristic=True`` to use time-based landmarks built on
    min-over-24h travel times, which are admissible for cost_by_time.
    """

    if use_time_heuristic:
        def _heuristic(g, node_id, goal_id):
            return time_alt_heuristic(g, node_id, goal_id, landmark_count=landmark_count)
    else:
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


def a_star_active_alt(
    graph,
    start,
    goal,
    cost_func,
    start_time=0,
    return_visited=False,
    return_stats=False,
    avoid_nodes=None,
    avoid_edges=None,
    landmark_count=16,
    active_count=4,
    heuristic_weight=1.0,
):
    """A* with active landmark selection for time-dependent routing.

    Precomputes ``landmark_count`` time-based landmarks but selects only the
    best ``active_count`` of them for each (start, goal) pair, reducing per-node
    heuristic cost while improving bound tightness over a fixed small set.
    """
    _heuristic = make_active_time_alt_heuristic(
        graph, start, goal,
        landmark_count=landmark_count,
        active_count=active_count,
    )

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


def a_star_departure_alt(
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
    departure_hour=8,
    heuristic_weight=1.0,
):
    """A* with departure-aware ALT heuristic for time-dependent routing.

    Uses min(time_list[departure_hour:]) as the edge cost during landmark
    preprocessing instead of the global 24-hour minimum.  This provides a
    tighter admissible lower bound for queries departing at or after
    ``departure_hour``.
    """
    def _heuristic(g, node_id, goal_id):
        return departure_time_alt_heuristic(
            g, node_id, goal_id,
            departure_hour=departure_hour,
            landmark_count=landmark_count,
        )

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
