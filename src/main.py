from algorithms.dijkstra import shortest_distance_path
from generator.graph_generator import generate_small_test_graph


def _print_graph(graph):
    print("\nSmall test graph (adjacency list):")
    for node in graph.nodes():
        neighbor_info = []
        for edge in graph.neighbors(node):
            neighbor_info.append(
                f"{edge.destination}(distance={edge.distance}, time@08={edge.travel_time_at(8)})"
            )
        print(f"{node}: {', '.join(neighbor_info)}")


def _run_shortest_path_query(graph):
    print(f"Available nodes: {', '.join(graph.nodes())}")
    start = input("Start node: ").strip()
    goal = input("Goal node: ").strip()

    try:
        distance, path = shortest_distance_path(graph, start, goal)
        if not path:
            print("No path found.")
            return

        print(f"Shortest distance from {start} to {goal}: {distance}")
        print(f"Path: {' -> '.join(path)}")
    except ValueError as error:
        print(f"Error: {error}")


def main():
    graph = generate_small_test_graph()

    while True:
        print("\n=== Smart Path Finder CLI ===")
        print("1. Show graph")
        print("2. Find shortest distance path")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            _print_graph(graph)
        elif choice == "2":
            _run_shortest_path_query(graph)
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
