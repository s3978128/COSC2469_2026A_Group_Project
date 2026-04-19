"""Run algorithm benchmarks against stored graph datasets."""

import argparse
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.dijkstra import dijkstra
from algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from algorithms.a_star import a_star
from algorithms.a_star_alt import a_star_alt
from algorithms.landmark_heuristic import precompute_alt_landmarks
from algorithms.weighted_a_star import weighted_a_star
from algorithms.bidirectional_a_star import bidirectional_a_star
from cost.distance_cost import cost_by_distance
from cost.time_cost import cost_by_time
from dataio.graph_io import import_graph_csv
from evaluation.benchmark import benchmark_dijkstra, write_runtime_csv


ALGORITHM_REGISTRY = {
    "dijkstra": {
        "fn": dijkstra,
        "cost_types": ("distance", "time"),
    },
    "bidirectional_dijkstra": {
        "fn": bidirectional_dijkstra,
        "cost_types": ("distance",),
    },
    "a_star": {
        "fn": a_star,
        "cost_types": ("distance",),
    },
    "a_star_alt": {
        "fn": a_star_alt,
        "cost_types": ("distance",),
        "kwargs": {"landmark_count": 4},
        "warmup": lambda graph, kwargs: precompute_alt_landmarks(
            graph,
            landmark_count=kwargs.get("landmark_count", 4),
        ),
    },
    "weighted_a_star": {
        "fn": weighted_a_star,
        "cost_types": ("distance",),
        "kwargs": {"heuristic_weight": 1.25},
    },
    "bidirectional_a_star": {
        "fn": bidirectional_a_star,
        "cost_types": ("distance",),
    },
}


def _list_dataset_dirs(base_dir):
    base_path = Path(base_dir)
    if not base_path.exists():
        return []
    return sorted(
        [
            path
            for path in base_path.iterdir()
            if path.is_dir()
            and (path / "nodes.csv").exists()
            and (path / "edges.csv").exists()
        ],
        key=lambda path: path.name,
    )


def _default_dataset_root():
    preferred = ROOT / "data" / "datasets" / "default"
    legacy = ROOT / "data" / "datasets"
    if preferred.exists():
        return preferred
    return legacy


def _sample_pairs(graph, pair_count=5):
    nodes = sorted(graph.nodes())
    if len(nodes) < 2:
        return []

    step = max(1, len(nodes) // 20)
    index_candidates = list(range(0, len(nodes), step))
    reverse_candidates = list(range(len(nodes) - 1, -1, -step))

    selected = []
    seen = set()
    for i in index_candidates:
        for j in reverse_candidates:
            if i == j:
                continue
            start = nodes[i]
            goal = nodes[j]
            key = (start, goal)
            if key in seen:
                continue
            seen.add(key)

            # Keep only reachable pairs for stable runtime comparisons.
            path, _ = dijkstra(graph, start, goal, cost_by_distance)
            if not path:
                continue

            selected.append(key)
            if len(selected) >= pair_count:
                return selected

    return selected


def run_dataset_benchmarks(
    datasets_dir=None,
    output_csv=ROOT / "results" / "runtime_results.csv",
    output_analysis=ROOT / "results" / "analysis.txt",
    runs_per_pair=10,
    split_runtime_stats=True,
):
    """Benchmark registered algorithms against all stored datasets."""
    if datasets_dir is None:
        datasets_dir = _default_dataset_root()

    dataset_dirs = _list_dataset_dirs(datasets_dir)
    if not dataset_dirs:
        raise FileNotFoundError("No dataset directories found in the configured datasets folder")

    rows = []
    analysis_lines = []

    for dataset_dir in dataset_dirs:
        graph, metadata = import_graph_csv(dataset_dir)
        pairs = _sample_pairs(graph, pair_count=5)
        node_count = len(graph.nodes())
        edge_count = sum(len(graph.neighbors(node)) for node in graph.nodes())
        ratio = edge_count / node_count if node_count else 0.0

        if not pairs:
            continue

        analysis_lines.append(f"Dataset: {dataset_dir.name}")
        analysis_lines.append(f"  Nodes: {node_count}")
        analysis_lines.append(f"  Edges: {edge_count}")
        analysis_lines.append(f"  Edge/Node ratio: {ratio:.2f}")
        dataset_rows = []

        for algo_name, algo_meta in ALGORITHM_REGISTRY.items():
            algo_fn = algo_meta["fn"]
            supported_cost_types = algo_meta["cost_types"]
            algo_kwargs = algo_meta.get("kwargs", {})
            warmup_fn = algo_meta.get("warmup")

            if warmup_fn is not None:
                warmup_fn(graph, algo_kwargs)

            batches = []

            def _run_batch(cost_fn, batch_start_time):
                runtime_rows = benchmark_dijkstra(
                    graph,
                    pairs,
                    algo_fn,
                    cost_fn,
                    start_time=batch_start_time,
                    runs_per_pair=runs_per_pair,
                    algorithm_kwargs=algo_kwargs,
                    collect_stats=not split_runtime_stats,
                )

                if not split_runtime_stats:
                    return runtime_rows

                stats_rows = benchmark_dijkstra(
                    graph,
                    pairs,
                    algo_fn,
                    cost_fn,
                    start_time=batch_start_time,
                    runs_per_pair=runs_per_pair,
                    algorithm_kwargs=algo_kwargs,
                    collect_stats=True,
                )

                merged_rows = []
                for idx, runtime_row in enumerate(runtime_rows):
                    row = dict(runtime_row)
                    if idx < len(stats_rows):
                        stats_row = stats_rows[idx]
                        for key, value in stats_row.items():
                            if key in row:
                                continue
                            row[key] = value
                    merged_rows.append(row)
                return merged_rows

            if "distance" in supported_cost_types:
                distance_rows = _run_batch(cost_by_distance, 0)
                batches.append(("distance", distance_rows))

            if "time" in supported_cost_types:
                time_rows = _run_batch(cost_by_time, 8 * 60)
                batches.append(("time", time_rows))

            for cost_type, batch in batches:
                for row in batch:
                    row["dataset"] = dataset_dir.name
                    row["algorithm"] = algo_name
                    row["cost_type"] = cost_type
                    row["runs_per_pair"] = runs_per_pair
                    row["edge_node_ratio"] = round(ratio, 2)
                    row["scenario"] = metadata.get("scenario", "unknown")
                    row["seed"] = metadata.get("seed", "unknown")

                    if node_count > 0 and "expanded_nodes_mean" in row:
                        row["stress_mean"] = row["expanded_nodes_mean"] / node_count
                    if node_count > 0 and "expanded_nodes_max" in row:
                        row["stress_max"] = row["expanded_nodes_max"] / node_count
                    if node_count > 0 and "expanded_nodes_min" in row:
                        row["stress_min"] = row["expanded_nodes_min"] / node_count

                    rows.append(row)
                    dataset_rows.append(row)

            flattened = [row for _, batch in batches for row in batch]
            algo_means = [r["runtime_ms_mean"] for r in flattened]
            analysis_lines.append(
                f"  {algo_name}: mean={statistics.mean(algo_means):.4f} ms, max={max(r['runtime_ms_max'] for r in flattened):.4f} ms"
            )

            expanded_means = [
                r["expanded_nodes_mean"]
                for r in flattened
                if "expanded_nodes_mean" in r
            ]
            if expanded_means:
                analysis_lines.append(
                    f"    expanded_nodes: mean={statistics.mean(expanded_means):.2f}, max={max(expanded_means):.2f}"
                )

            stress_means = [r["stress_mean"] for r in flattened if "stress_mean" in r]
            if stress_means:
                analysis_lines.append(
                    f"    stress: mean={statistics.mean(stress_means):.4f}, max={max(stress_means):.4f}"
                )

        baseline_cost = {
            (row["start"], row["goal"], row["cost_type"]): row["total_cost"]
            for row in dataset_rows
            if row.get("algorithm") == "dijkstra" and row.get("path_found")
        }

        for row in dataset_rows:
            key = (row["start"], row["goal"], row["cost_type"])
            baseline = baseline_cost.get(key)
            if baseline is None or baseline == 0 or not row.get("path_found"):
                continue
            row["optimality_gap_pct"] = (
                (row["total_cost"] - baseline) / baseline
            ) * 100.0

        for algo_name, _ in ALGORITHM_REGISTRY.items():
            gap_values = [
                row["optimality_gap_pct"]
                for row in dataset_rows
                if row.get("algorithm") == algo_name and "optimality_gap_pct" in row
            ]
            if gap_values:
                analysis_lines.append(
                    f"  {algo_name} gap: mean={statistics.mean(gap_values):.4f}%, max={max(gap_values):.4f}%"
                )

        analysis_lines.append("")

    output_csv = Path(output_csv)
    output_analysis = Path(output_analysis)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    write_runtime_csv(rows, output_csv)
    output_analysis.write_text("\n".join(analysis_lines).strip() + "\n", encoding="utf-8")

    return rows


def main():
    parser = argparse.ArgumentParser(description="Benchmark algorithms on stored graph datasets")
    parser.add_argument(
        "--datasets-dir",
        type=Path,
        default=None,
        help="Directory containing dataset subfolders (default benchmark suite if available)",
    )
    parser.add_argument(
        "--runs-per-pair",
        type=int,
        default=10,
        help="Number of benchmark repetitions per start/goal pair",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=ROOT / "results" / "runtime_results.csv",
        help="Runtime CSV output path",
    )
    parser.add_argument(
        "--output-analysis",
        type=Path,
        default=ROOT / "results" / "analysis.txt",
        help="Text summary output path",
    )
    parser.add_argument(
        "--no-split-runtime-stats",
        action="store_true",
        help="Disable split runtime/stat collection and measure both together",
    )
    args = parser.parse_args()

    rows = run_dataset_benchmarks(
        datasets_dir=args.datasets_dir,
        output_csv=args.output_csv,
        output_analysis=args.output_analysis,
        runs_per_pair=args.runs_per_pair,
        split_runtime_stats=not args.no_split_runtime_stats,
    )
    print(f"Benchmark complete. Wrote {len(rows)} rows.")
    print(f"Runtime CSV: {args.output_csv}")
    print(f"Analysis: {args.output_analysis}")


if __name__ == "__main__":
    main()
