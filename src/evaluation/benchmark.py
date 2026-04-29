"""Simple benchmarking helpers for shortest-path experiments."""

import csv
import numbers
import statistics
import time


def benchmark_dijkstra(
    graph,
    node_pairs,
    dijkstra_fn,
    cost_func,
    start_time=0,
    runs_per_pair=5,
):
    """Benchmark Dijkstra runtime for multiple start/goal pairs.

    Returns
    -------
    list[dict]
        Per-pair benchmark rows with min/mean/max runtime in milliseconds.
    """
    if runs_per_pair < 1:
        raise ValueError("runs_per_pair must be at least 1")

    def _extract_stats(result_tuple):
        """Extract optional stats dict from algorithm return tuple."""
        if not isinstance(result_tuple, tuple) or len(result_tuple) < 3:
            return {}

        # Common shapes:
        # (path, cost, stats)
        # (path, cost, visited)
        # (path, cost, visited, stats)
        if len(result_tuple) >= 4 and isinstance(result_tuple[3], dict):
            return result_tuple[3]
        if len(result_tuple) >= 3 and isinstance(result_tuple[2], dict):
            return result_tuple[2]
        return {}

    results = []
    for start, goal in node_pairs:
        run_times_ms = []
        final_cost = None
        final_path = None
        run_stats = []

        for _ in range(runs_per_pair):
            t0 = time.perf_counter()
            try:
                result = dijkstra_fn(
                    graph,
                    start,
                    goal,
                    cost_func,
                    start_time=start_time,
                    return_stats=True,
                )
            except TypeError:
                # Backward compatibility for algorithms without return_stats.
                result = dijkstra_fn(
                    graph,
                    start,
                    goal,
                    cost_func,
                    start_time=start_time,
                )

            if not isinstance(result, tuple) or len(result) < 2:
                raise ValueError(
                    "Algorithm function must return at least (path, cost)"
                )

            path, cost = result[0], result[1]
            elapsed_ms = (time.perf_counter() - t0) * 1000
            run_times_ms.append(elapsed_ms)
            final_path = path
            final_cost = cost
            stats = _extract_stats(result)
            if stats:
                run_stats.append(stats)

        row = {
            "start": start,
            "goal": goal,
            "runs": runs_per_pair,
            "path_found": bool(final_path),
            "total_cost": float(final_cost),
            "runtime_ms_min": min(run_times_ms),
            "runtime_ms_mean": statistics.mean(run_times_ms),
            "runtime_ms_max": max(run_times_ms),
        }

        if run_stats:
            numeric_keys = sorted(
                {
                    key
                    for stats in run_stats
                    for key, value in stats.items()
                    if isinstance(value, numbers.Number)
                    and not isinstance(value, bool)
                }
            )
            for key in numeric_keys:
                values = [stats[key] for stats in run_stats if key in stats]
                if not values:
                    continue
                row[f"{key}_min"] = min(values)
                row[f"{key}_mean"] = statistics.mean(values)
                row[f"{key}_max"] = max(values)

        results.append(row)

    return results


def write_runtime_csv(rows, output_path):
    """Write benchmark rows to CSV."""
    base_headers = [
        "start",
        "goal",
        "runs",
        "path_found",
        "total_cost",
        "runtime_ms_min",
        "runtime_ms_mean",
        "runtime_ms_max",
    ]

    extra_headers = sorted(
        {
            key
            for row in rows
            for key in row.keys()
            if key not in base_headers
        }
    )
    headers = base_headers + extra_headers

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
