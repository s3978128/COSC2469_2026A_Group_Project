"""Run scenario benchmarks and write reviewable outputs under results/."""

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
from evaluation.benchmark import benchmark_dijkstra, write_runtime_csv
from generator.graph_generator import generate_realistic_graph


def _edge_count(graph):
    return sum(len(graph.neighbors(node_id)) for node_id in graph.nodes())


def _sample_pairs(graph):
    """Pick deterministic node pairs spread across the sorted node list."""
    nodes = sorted(graph.nodes())
    if len(nodes) < 2:
        return []

    pairs = [
        (nodes[0], nodes[-1]),
        (nodes[len(nodes) // 4], nodes[(3 * len(nodes)) // 4]),
        (nodes[len(nodes) // 3], nodes[(2 * len(nodes)) // 3]),
    ]

    # Deduplicate and avoid start == goal.
    seen = set()
    unique = []
    for start, goal in pairs:
        if start == goal:
            continue
        key = (start, goal)
        if key not in seen:
            seen.add(key)
            unique.append(key)
    return unique


def run_default_benchmarks(
    output_csv=ROOT / "results" / "runtime_results.csv",
    output_analysis=ROOT / "results" / "analysis.txt",
    seed=42,
):
    """Run benchmark suite for realistic/mixed/stress scenarios."""
    scenarios = [
        ("realistic", 5, 5),
        ("mixed", 5, 5),
        ("stress", 6, 6),
    ]

    rows = []
    analysis_lines = []

    for scenario, rows_count, cols_count in scenarios:
        graph = generate_realistic_graph(
            rows=rows_count,
            cols=cols_count,
            seed=seed,
            scenario=scenario,
        )
        pairs = _sample_pairs(graph)
        edges = _edge_count(graph)
        ratio = edges / len(graph.nodes()) if graph.nodes() else 0.0

        distance_rows = benchmark_dijkstra(
            graph,
            pairs,
            dijkstra,
            cost_by_distance,
            start_time=0,
            runs_per_pair=20,
        )
        time_rows = benchmark_dijkstra(
            graph,
            pairs,
            dijkstra,
            cost_by_time,
            start_time=8 * 60,
            runs_per_pair=20,
        )

        for cost_type, batch in (("distance", distance_rows), ("time", time_rows)):
            for row in batch:
                row["scenario"] = scenario
                row["grid"] = f"{rows_count}x{cols_count}"
                row["cost_type"] = cost_type
                row["seed"] = seed
                row["edge_node_ratio"] = round(ratio, 2)
                rows.append(row)

        scenario_means = [row["runtime_ms_mean"] for row in distance_rows + time_rows]
        analysis_lines.append(f"Scenario: {scenario} ({rows_count}x{cols_count})")
        analysis_lines.append(f"  Nodes: {len(graph.nodes())}")
        analysis_lines.append(f"  Edges: {edges}")
        analysis_lines.append(f"  Edge/Node ratio: {ratio:.2f}")
        analysis_lines.append(
            f"  Mean runtime across cases: {statistics.mean(scenario_means):.4f} ms"
        )
        analysis_lines.append(
            f"  Max runtime across cases: {max(row['runtime_ms_max'] for row in distance_rows + time_rows):.4f} ms"
        )
        analysis_lines.append("")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    write_runtime_csv(rows, output_csv)
    output_analysis.write_text("\n".join(analysis_lines).strip() + "\n", encoding="utf-8")

    return rows


if __name__ == "__main__":
    result_rows = run_default_benchmarks()
    print(f"Benchmark complete. Wrote {len(result_rows)} rows to results/runtime_results.csv")
    print("Analysis summary written to results/analysis.txt")
