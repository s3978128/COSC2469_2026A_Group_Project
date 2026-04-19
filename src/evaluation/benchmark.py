"""Simple benchmarking helpers for shortest-path experiments."""

import csv
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

    results = []
    for start, goal in node_pairs:
        run_times_ms = []
        final_cost = None
        final_path = None

        for _ in range(runs_per_pair):
            t0 = time.perf_counter()
            path, cost = dijkstra_fn(
                graph,
                start,
                goal,
                cost_func,
                start_time=start_time,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000
            run_times_ms.append(elapsed_ms)
            final_path = path
            final_cost = cost

        results.append(
            {
                "start": start,
                "goal": goal,
                "runs": runs_per_pair,
                "path_found": bool(final_path),
                "total_cost": float(final_cost),
                "runtime_ms_min": min(run_times_ms),
                "runtime_ms_mean": statistics.mean(run_times_ms),
                "runtime_ms_max": max(run_times_ms),
            }
        )

    return results


def write_runtime_csv(rows, output_path):
    """Write benchmark rows to CSV."""
    headers = [
        "start",
        "goal",
        "runs",
        "path_found",
        "total_cost",
        "runtime_ms_min",
        "runtime_ms_mean",
        "runtime_ms_max",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
