import time
import sys

from algorithms.a_star import a_star, time_euclidean_heuristic
from algorithms.a_star_alt import a_star_alt
from algorithms.a_star_time_alt import a_star_time_alt
from algorithms.bidirectional_a_star import bidirectional_a_star
from algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from algorithms.dijkstra import dijkstra
from algorithms.weighted_a_star import weighted_a_star
from algorithms.landmark_heuristic import precompute_alt_landmarks, precompute_time_alt_landmarks
from cost.distance_cost import cost_by_distance
from cost.time_cost import cost_by_time
from generator.graph_generator import generate_small_test_graph
from utils.visualization import (
    render_network_grid,
    render_path_details,
    render_graph_info,
)

def _ensure_utf8_output():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


MAX_TERMINAL_VISUALIZATION_NODES = 1000


def _should_render_visualization(graph):
    node_count = len(graph.nodes())
    if node_count > MAX_TERMINAL_VISUALIZATION_NODES:
        print(
            f"[Visualization skipped: {node_count} nodes exceeds terminal-safe limit "
            f"({MAX_TERMINAL_VISUALIZATION_NODES}).]"
        )
        return False
    return True


def _parse_avoid_nodes(raw_text, valid_nodes):
    """Parse comma-separated node ids for optional node-avoid constraints."""
    if not raw_text.strip():
        return set()

    parsed = {token.strip() for token in raw_text.split(",") if token.strip()}
    unknown = sorted(node for node in parsed if node not in valid_nodes)
    if unknown:
        raise ValueError(f"Unknown nodes in avoid list: {', '.join(unknown)}")
    return parsed


def _parse_avoid_edges(raw_text, valid_nodes):
    """Parse comma-separated directed edges in SRC->DST format."""
    if not raw_text.strip():
        return set()

    parsed = set()
    for token in raw_text.split(","):
        text = token.strip()
        if not text:
            continue
        if "->" not in text:
            raise ValueError(
                f"Invalid edge format '{text}'. Expected SRC->DST (e.g., N_1_1->N_1_2)."
            )
        source, destination = [part.strip() for part in text.split("->", 1)]
        if source not in valid_nodes or destination not in valid_nodes:
            raise ValueError(f"Unknown edge endpoint in '{text}'")
        parsed.add((source, destination))

    return parsed


def _prompt_optional_constraints(graph):
    """Prompt optional avoid-node and avoid-edge constraints for a query."""
    valid_nodes = set(graph.nodes())

    avoid_nodes_raw = input(
        "Optional avoid nodes (comma-separated, blank for none): "
    ).strip()
    avoid_edges_raw = input(
        "Optional avoid edges (SRC->DST, comma-separated, blank for none): "
    ).strip()

    avoid_nodes = _parse_avoid_nodes(avoid_nodes_raw, valid_nodes)
    avoid_edges = _parse_avoid_edges(avoid_edges_raw, valid_nodes)
    return avoid_nodes, avoid_edges


def _print_graph(graph):
    """Display graph statistics, visual representation, and adjacency list."""
    print(render_graph_info(graph))

    if not _should_render_visualization(graph):
        return

    print("Visual Road Network:")
    print(render_network_grid(graph))

    # print("\nAdjacency List (Detailed):")
    # print("─" * 70)
    for node in sorted(graph.nodes()):
        neighbor_info = []
        for edge in graph.neighbors(node):
            # Infer road type from speed
            speed = (edge.distance / edge.get_travel_time(12)) * 60
            if speed >= 70:
                road_type = "HWY"
            elif speed >= 40:
                road_type = "MAIN"
            else:
                road_type = "LOCAL"

            neighbor_info.append(
                f"{edge.destination}({road_type}, {edge.distance:.1f}km, {edge.get_travel_time(12):.1f}min)"
            )
        # print(f"{node:5s}: {', '.join(neighbor_info)}")
    print("─" * 70)


def _run_shortest_path_query(graph):
    print(f"\nAvailable nodes: {', '.join(sorted(graph.nodes()))}")
    start = input("Start node: ").strip()
    goal = input("Goal node: ").strip()
    time_hour_text = input(
        "Departure hour for travel-time estimate (0-23, default 8): "
    ).strip()
    algo_choice = input(
        "Distance algorithm [dijkstra/a_star/a_star_alt/weighted_a_star/bidirectional_dijkstra/bidirectional_a_star/compare] (default dijkstra): "
    ).strip().lower() or "dijkstra"

    compare_runs = 3
    if algo_choice == "compare":
        compare_runs_text = input(
            "Compare repetitions per algorithm (default 3): "
        ).strip()
        if compare_runs_text:
            try:
                compare_runs = int(compare_runs_text)
                if compare_runs < 1:
                    print("Compare repetitions must be >= 1.")
                    return
            except ValueError:
                print("Compare repetitions must be an integer.")
                return

    try:
        avoid_nodes, avoid_edges = _prompt_optional_constraints(graph)

        if time_hour_text:
            report_hour = int(time_hour_text)
            if not 0 <= report_hour <= 23:
                print("Hour must be between 0 and 23.")
                return
        else:
            report_hour = 8

        algorithm_map = {
            "dijkstra": (dijkstra, {}),
            "a_star": (a_star, {}),
            "a_star_alt": (a_star_alt, {"landmark_count": 4}),
            "weighted_a_star": (weighted_a_star, {"heuristic_weight": 1.25}),
            "bidirectional_dijkstra": (bidirectional_dijkstra, {}),
            "bidirectional_a_star": (bidirectional_a_star, {}),
        }

        if algo_choice == "compare":
            if hasattr(graph, "distance_heuristic_scale"):
                graph.distance_heuristic_scale()

            # Exclude one-time ALT setup from table timings for fairer per-query comparison.
            precompute_alt_landmarks(graph, landmark_count=4)

            print("\nDistance algorithm comparison:")
            print(
                f"(runs per algorithm: {compare_runs}, runtime measured without stats overhead)"
            )
            print("-" * 92)
            print(
                f"{'algorithm':24s} {'cost':>10s} {'exp':>8s} {'ms_mean':>10s} {'ms_max':>10s} {'path'}"
            )
            print("-" * 92)

            comparison_rows = []
            for algo_name, (algo_fn, algo_kwargs) in algorithm_map.items():
                runtimes_ms = []
                for _ in range(compare_runs):
                    t0 = time.perf_counter()
                    algo_fn(
                        graph,
                        start,
                        goal,
                        cost_by_distance,
                        avoid_nodes=avoid_nodes,
                        avoid_edges=avoid_edges,
                        **algo_kwargs,
                    )
                    runtimes_ms.append((time.perf_counter() - t0) * 1000)

                result = algo_fn(
                    graph,
                    start,
                    goal,
                    cost_by_distance,
                    return_visited=True,
                    return_stats=True,
                    avoid_nodes=avoid_nodes,
                    avoid_edges=avoid_edges,
                    **algo_kwargs,
                )

                path = result[0]
                distance = result[1]
                visited = result[2] if len(result) >= 3 else []
                stats = result[3] if len(result) >= 4 and isinstance(result[3], dict) else {}
                expanded = int(stats.get("expanded_nodes", len(visited)))
                runtime_mean = sum(runtimes_ms) / len(runtimes_ms)
                runtime_max = max(runtimes_ms)

                if path:
                    path_preview = f"{path[0]}->{path[-1]} ({len(path)} nodes)"
                else:
                    path_preview = "unreachable"

                print(
                    f"{algo_name:24s} {distance:10.2f} {expanded:8d} {runtime_mean:10.3f} {runtime_max:10.3f} {path_preview}"
                )
                comparison_rows.append(
                    (algo_name, path, distance, visited, expanded, runtime_mean, runtime_max)
                )

            print("-" * 92)

            baseline = next((row[2] for row in comparison_rows if row[0] == "dijkstra"), None)
            if baseline not in (None, float("inf"), 0):
                print("Optimality gaps vs Dijkstra (%):")
                for algo_name, _, distance, _, _, _, _ in comparison_rows:
                    if distance == float("inf"):
                        gap = float("inf")
                    else:
                        gap = ((distance - baseline) / baseline) * 100.0
                    if gap == float("inf"):
                        print(f"- {algo_name}: inf")
                    else:
                        print(f"- {algo_name}: {gap:.4f}%")

            successful = [row for row in comparison_rows if row[1]]
            if not successful:
                print("No path found by any distance algorithm.")
                return

            successful.sort(key=lambda row: row[2])
            _, path, distance, visited, _, _ = successful[0]
        else:
            if algo_choice not in algorithm_map:
                print(f"Unknown distance algorithm '{algo_choice}'.")
                return

            algo_fn, algo_kwargs = algorithm_map[algo_choice]
            path, distance, visited = algo_fn(
                graph,
                start,
                goal,
                cost_by_distance,
                return_visited=True,
                avoid_nodes=avoid_nodes,
                avoid_edges=avoid_edges,
                **algo_kwargs,
            )

        if not path:
            print("No path found.")
            return

        # Visual path display (skip for very large graphs in terminal mode).
        if _should_render_visualization(graph):
            print("\nVisual Route (with shortest path highlighted):")
            print(
                render_network_grid(
                    graph,
                    path=path,
                    visited_nodes=visited,
                    start_node=start,
                    end_node=goal,
                )
            )

        # Detailed path information
        print(
            render_path_details(
                graph,
                path,
                distance,
                cost_type="distance",
                start_time=report_hour * 60,
            )
        )

    except ValueError as error:
        print(f"Error: {error}")


def _run_shortest_time_query(graph):
    print(f"\nAvailable nodes: {', '.join(sorted(graph.nodes()))}")
    start = input("Start node: ").strip()
    goal = input("Goal node: ").strip()
    hour = input("Departure hour (0-23): ").strip()
    algo_choice = input(
        "Time algorithm [dijkstra/a_star/a_star_alt/a_star_time_alt/weighted_a_star/compare] (default dijkstra): "
    ).strip().lower() or "dijkstra"

    compare_runs = 3
    if algo_choice == "compare":
        compare_runs_text = input(
            "Compare repetitions per algorithm (default 3): "
        ).strip()
        if compare_runs_text:
            try:
                compare_runs = int(compare_runs_text)
                if compare_runs < 1:
                    print("Compare repetitions must be >= 1.")
                    return
            except ValueError:
                print("Compare repetitions must be an integer.")
                return

    try:
        avoid_nodes, avoid_edges = _prompt_optional_constraints(graph)

        start_hour = int(hour)
        if not 0 <= start_hour <= 23:
            print("Hour must be between 0 and 23.")
            return

        start_time = start_hour * 60  # convert hour to minutes

        # All algorithms use admissible time-based heuristics:
        # - a_star: time_euclidean_heuristic (scale * euclidean in minutes)
        # - a_star_alt: time_alt_heuristic via a_star_time_alt (landmark-based, tighter)
        # - a_star_time_alt: same as a_star_alt for time (explicit wrapper)
        # - weighted_a_star: time_euclidean_heuristic with w=1.25 (intentionally
        #   suboptimal for speed tradeoff, same as distance mode)
        # - bidirectional_dijkstra/a_star: not included (backward search cannot
        #   evaluate time-dependent costs without knowing arrival time)
        algorithm_map = {
            "dijkstra": (dijkstra, {}),
            "a_star": (a_star, {"heuristic_fn": time_euclidean_heuristic}),
            "a_star_alt": (a_star_time_alt, {"landmark_count": 4}),
            "a_star_time_alt": (a_star_time_alt, {"landmark_count": 4}),
            "weighted_a_star": (weighted_a_star, {
                "heuristic_weight": 1.25,
                "heuristic_fn": time_euclidean_heuristic,
            }),
        }
        if algo_choice == "compare":
            # Exclude one-time ALT setup from table timings for fairer per-query comparison.
            precompute_alt_landmarks(graph, landmark_count=4)
            precompute_time_alt_landmarks(graph, landmark_count=4)

            print("\nTime algorithm comparison:")
            print(
                f"(runs per algorithm: {compare_runs}, departure: {start_hour:02d}:00, "
                "runtime measured without stats overhead)"
            )
            print("-" * 96)
            print(
                f"{'algorithm':24s} {'time(min)':>10s} {'exp':>8s} {'ms_mean':>10s} {'ms_max':>10s} {'path'}"
            )
            print("-" * 96)

            comparison_rows = []
            for algo_name, (algo_fn, algo_kwargs) in algorithm_map.items():
                try:
                    runtimes_ms = []
                    for _ in range(compare_runs):
                        t0 = time.perf_counter()
                        algo_fn(
                            graph,
                            start,
                            goal,
                            cost_by_time,
                            start_time,
                            avoid_nodes=avoid_nodes,
                            avoid_edges=avoid_edges,
                            **algo_kwargs,
                        )
                        runtimes_ms.append((time.perf_counter() - t0) * 1000)

                    result = algo_fn(
                        graph,
                        start,
                        goal,
                        cost_by_time,
                        start_time,
                        return_visited=True,
                        return_stats=True,
                        avoid_nodes=avoid_nodes,
                        avoid_edges=avoid_edges,
                        **algo_kwargs,
                    )

                    path = result[0]
                    total_time = result[1]
                    visited = result[2] if len(result) >= 3 else []
                    stats = result[3] if len(result) >= 4 and isinstance(result[3], dict) else {}
                    expanded = int(stats.get("expanded_nodes", len(visited)))
                    runtime_mean = sum(runtimes_ms) / len(runtimes_ms)
                    runtime_max = max(runtimes_ms)

                    if path:
                        path_preview = f"{path[0]}->{path[-1]} ({len(path)} nodes)"
                    else:
                        path_preview = "unreachable"

                    print(
                        f"{algo_name:24s} {total_time:10.2f} {expanded:8d} {runtime_mean:10.3f} {runtime_max:10.3f} {path_preview}"
                    )
                    comparison_rows.append(
                        (algo_name, path, total_time, visited, expanded, runtime_mean, runtime_max)
                    )

                except ValueError as skip_error:
                    print(
                        f"{algo_name:24s} {'N/A':>10s} {'N/A':>8s} {'N/A':>10s} {'N/A':>10s} "
                        f"(skipped: {skip_error})"
                    )

            print("-" * 96)

            baseline = next((row[2] for row in comparison_rows if row[0] == "dijkstra"), None)
            if baseline not in (None, float("inf"), 0):
                print("Optimality gaps vs Dijkstra (%):")
                for algo_name, _, algo_time, _, _, _, _ in comparison_rows:
                    if algo_time == float("inf"):
                        gap = float("inf")
                    else:
                        gap = ((algo_time - baseline) / baseline) * 100.0
                    if gap == float("inf"):
                        print(f"- {algo_name}: inf")
                    else:
                        print(f"- {algo_name}: {gap:.4f}%")

            successful = [row for row in comparison_rows if row[1]]
            if not successful:
                print("No path found by any time algorithm.")
                return

            successful.sort(key=lambda row: row[2])
            _, path, total_time, visited, _, _, _ = successful[0]

        else:
            if algo_choice not in algorithm_map:
                print(f"Unknown time algorithm '{algo_choice}'.")
                return

            algo_fn, algo_kwargs = algorithm_map[algo_choice]
            path, total_time, visited = algo_fn(
                graph,
                start,
                goal,
                cost_by_time,
                start_time,
                return_visited=True,
                avoid_nodes=avoid_nodes,
                avoid_edges=avoid_edges,
                **algo_kwargs,
            )

        if not path:
            print("No path found.")
            return

        # Visual path display (skip for very large graphs in terminal mode).
        if _should_render_visualization(graph):
            print(f"\nVisual Route (departure at {start_hour:02d}:00, shortest time highlighted):")
            print(
                render_network_grid(
                    graph,
                    path=path,
                    visited_nodes=visited,
                    start_node=start,
                    end_node=goal,
                )
            )

        # Detailed path information
        print(render_path_details(
            graph,
            path,
            total_time,
            cost_type="time",
            start_time=start_time
        ))

    except ValueError as error:
        print(f"Error: {error}")


def _select_network():
    from dataio.graph_io import import_graph_csv
    from generator.graph_generator import generate_realistic_graph

    print("\n" + "=" * 50)
    print("SMART PATH FINDER - Network Selection")
    print("=" * 50)
    print("1. Small test graph (6 nodes, simple)")
    print("2. Realistic network (5x5, mostly 2-4 links per node)")
    print("3. Mixed network (5x5, includes high-degree hubs)")
    print("4. Stress network (6x6, denser connectivity)")
    print("5. Load network from dataset folder")

    choice = input("Select network (1-5): ").strip()

    if choice == "1":
        print("-> Loaded small test graph")
        return generate_small_test_graph()
    if choice == "2":
        print("-> Generating realistic 5x5 network...")
        return generate_realistic_graph(5, 5, seed=42, scenario="realistic")
    if choice == "3":
        print("-> Generating mixed 5x5 network with hubs...")
        return generate_realistic_graph(5, 5, seed=42, scenario="mixed")
    if choice == "4":
        print("-> Generating stress 6x6 network...")
        return generate_realistic_graph(6, 6, seed=42, scenario="stress")
    if choice == "5":
        dataset_path = input("Dataset folder path (e.g., data/datasets/default/graph_100): ").strip()
        try:
            graph, metadata = import_graph_csv(dataset_path)
            print(
                "-> Loaded dataset "
                f"{metadata.get('dataset_name', 'unknown')} "
                f"(nodes={len(graph.nodes())})"
            )
            return graph
        except (FileNotFoundError, ValueError) as error:
            print(f"Could not load dataset: {error}")
            print("Using small test graph instead.")
            return generate_small_test_graph()

    print("Invalid choice. Using small test graph.")
    return generate_small_test_graph()


def _generate_and_export_datasets():
    from generator.generate_datasets import generate_and_export_datasets

    print("\nGenerating datasets (100, 1000, 5000 nodes)...")
    created = generate_and_export_datasets(seed=42, max_nodes=10000)
    if not created:
        print("No datasets generated.")
        return

    print("Datasets generated in data/datasets:")
    for name, node_count, elapsed in created:
        print(f"- {name}: nodes={node_count}, generation={elapsed:.3f}s")


def _run_dataset_benchmarks():
    from evaluation.benchmark_datasets import run_dataset_benchmarks

    print("\nRunning benchmark suite on stored datasets...")
    rows = run_dataset_benchmarks(runs_per_pair=10)
    print(f"Benchmark complete. Rows written: {len(rows)}")
    print("Files updated:")
    print("- results/runtime_results.csv")
    print("- results/analysis.txt")


def _print_cli_help():
    print("\nQuick guide:")
    print("- Pick a network first (or load one from data/datasets/...).")
    print("- Use option 1 to inspect the current network and node IDs.")
    print("- Use option 2 or 3 to run shortest-path queries.")
    print("- Distance and time queries support algorithm selection or compare mode.")
    print("- Time compare benchmarks all algorithms using cost_by_time and your departure hour.")
    print("- Queries support optional avoid nodes/edges (blank to skip).")
    print("- In route view: S=start, E=end, ●=path, ◍=visited.")
    print("- Use option 5 to generate datasets and 6 to benchmark them.")


def main():
    _ensure_utf8_output()
    _print_cli_help()
    graph = _select_network()

    while True:
        print("\n" + "=" * 50)
        print("=== Smart Path Finder CLI ===")
        print("=" * 50)
        print("1. Show network visualization")
        print("2. Find shortest distance path")
        print("3. Find shortest time path")
        print("4. Change network")
        print("5. Generate and export datasets")
        print("6. Benchmark stored datasets")
        print("7. Exit")
        choice = input("Choose an option (1-7, h for help): ").strip().lower()

        if choice == "h":
            _print_cli_help()
        elif choice == "1":
            _print_graph(graph)
        elif choice == "2":
            _run_shortest_path_query(graph)
        elif choice == "3":
            _run_shortest_time_query(graph)
        elif choice == "4":
            graph = _select_network()
        elif choice == "5":
            _generate_and_export_datasets()
        elif choice == "6":
            _run_dataset_benchmarks()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1-7 or h.")


if __name__ == "__main__":
    main()
