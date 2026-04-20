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
from cost.distance_cost import cost_by_distance
from cost.time_cost import cost_by_time
from dataio.graph_io import import_graph_csv
from evaluation.benchmark import benchmark_dijkstra, write_runtime_csv


ALGORITHM_REGISTRY = {
    "dijkstra": dijkstra,
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
    datasets_dir=ROOT / "data" / "datasets",
    output_csv=ROOT / "results" / "runtime_results.csv",
    output_analysis=ROOT / "results" / "analysis.txt",
    runs_per_pair=10,
):
    """Benchmark registered algorithms against all stored datasets."""
    dataset_dirs = _list_dataset_dirs(datasets_dir)
    if not dataset_dirs:
        raise FileNotFoundError("No dataset directories found in data/datasets")

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

        for algo_name, algo_fn in ALGORITHM_REGISTRY.items():
            distance_rows = benchmark_dijkstra(
                graph,
                pairs,
                algo_fn,
                cost_by_distance,
                start_time=0,
                runs_per_pair=runs_per_pair,
            )
            time_rows = benchmark_dijkstra(
                graph,
                pairs,
                algo_fn,
                cost_by_time,
                start_time=8 * 60,
                runs_per_pair=runs_per_pair,
            )

            for cost_type, batch in (("distance", distance_rows), ("time", time_rows)):
                for row in batch:
                    row["dataset"] = dataset_dir.name
                    row["algorithm"] = algo_name
                    row["cost_type"] = cost_type
                    row["runs_per_pair"] = runs_per_pair
                    row["edge_node_ratio"] = round(ratio, 2)
                    row["scenario"] = metadata.get("scenario", "unknown")
                    row["seed"] = metadata.get("seed", "unknown")
                    rows.append(row)

            algo_means = [r["runtime_ms_mean"] for r in distance_rows + time_rows]
            analysis_lines.append(
                f"  {algo_name}: mean={statistics.mean(algo_means):.4f} ms, max={max(r['runtime_ms_max'] for r in distance_rows + time_rows):.4f} ms"
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
        default=ROOT / "data" / "datasets",
        help="Directory containing dataset subfolders",
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
    args = parser.parse_args()

    rows = run_dataset_benchmarks(
        datasets_dir=args.datasets_dir,
        output_csv=args.output_csv,
        output_analysis=args.output_analysis,
        runs_per_pair=args.runs_per_pair,
    )
    print(f"Benchmark complete. Wrote {len(rows)} rows.")
    print(f"Runtime CSV: {args.output_csv}")
    print(f"Analysis: {args.output_analysis}")


if __name__ == "__main__":
    main()
