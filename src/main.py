from algorithms.dijkstra import dijkstra
from cost.distance_cost import cost_by_distance
from cost.time_cost import cost_by_time
from generator.graph_generator import generate_small_test_graph
from utils.visualization import (
    render_network_grid,
    render_path_details,
    render_graph_info,
)


def _print_graph(graph):
    """Display graph statistics, visual representation, and adjacency list."""
    print(render_graph_info(graph))

    print("Visual Road Network:")
    print(render_network_grid(graph))

    print("\nAdjacency List (Detailed):")
    print("─" * 70)
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

    try:
        path, distance, visited = dijkstra(
            graph,
            start,
            goal,
            cost_by_distance,
            return_visited=True,
        )
        if not path:
            print("No path found.")
            return

        # Visual path display
        print("\nVisual Route (with shortest path highlighted):")
        print(render_network_grid(graph, path=path, visited_nodes=visited))

        # Detailed path information
        print(render_path_details(graph, path, distance, cost_type="distance"))

    except ValueError as error:
        print(f"Error: {error}")


def _run_shortest_time_query(graph):
    print(f"\nAvailable nodes: {', '.join(sorted(graph.nodes()))}")
    start = input("Start node: ").strip()
    goal = input("Goal node: ").strip()
    hour = input("Departure hour (0-23): ").strip()

    try:
        start_hour = int(hour)
        if not 0 <= start_hour <= 23:
            print("Hour must be between 0 and 23.")
            return

        start_time = start_hour * 60  # convert hour to minutes
        path, total_time, visited = dijkstra(
            graph,
            start,
            goal,
            cost_by_time,
            start_time,
            return_visited=True,
        )
        if not path:
            print("No path found.")
            return

        # Visual path display
        print(f"\nVisual Route (departure at {start_hour:02d}:00, shortest time highlighted):")
        print(render_network_grid(graph, path=path, visited_nodes=visited))

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
    from generator.graph_generator import generate_realistic_graph

    print("\n" + "=" * 50)
    print("SMART PATH FINDER - Network Selection")
    print("=" * 50)
    print("1. Small test graph (6 nodes, simple)")
    print("2. Realistic network (5x5, mostly 2-4 links per node)")
    print("3. Mixed network (5x5, includes high-degree hubs)")
    print("4. Stress network (6x6, denser connectivity)")

    choice = input("Select network (1-4): ").strip()

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

    print("Invalid choice. Using small test graph.")
    return generate_small_test_graph()


def _run_benchmarks():
    from evaluation.run_benchmarks import run_default_benchmarks

    print("\nRunning benchmark suite...")
    rows = run_default_benchmarks()
    print(f"Benchmark complete. Rows written: {len(rows)}")
    print("Files updated:")
    print("- results/runtime_results.csv")
    print("- results/analysis.txt")


def main():
    graph = _select_network()

    while True:
        print("\n" + "=" * 50)
        print("=== Smart Path Finder CLI ===")
        print("=" * 50)
        print("1. Show network visualization")
        print("2. Find shortest distance path")
        print("3. Find shortest time path")
        print("4. Change network")
        print("5. Run benchmark suite")
        print("6. Exit")
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            _print_graph(graph)
        elif choice == "2":
            _run_shortest_path_query(graph)
        elif choice == "3":
            _run_shortest_time_query(graph)
        elif choice == "4":
            graph = _select_network()
        elif choice == "5":
            _run_benchmarks()
        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()
