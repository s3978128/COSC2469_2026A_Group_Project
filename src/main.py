from algorithms.dijkstra import dijkstra
from cost.distance_cost import cost_by_distance
from cost.time_cost import cost_by_time
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
        path, distance = dijkstra(graph, start, goal, cost_by_distance)
        if not path:
            print("No path found.")
            return

        print(f"Shortest distance from {start} to {goal}: {distance}")
        print(f"Path: {' -> '.join(path)}")
    except ValueError as error:
        print(f"Error: {error}")


def _run_shortest_time_query(graph):
    print(f"Available nodes: {', '.join(graph.nodes())}")
    start = input("Start node: ").strip()
    goal = input("Goal node: ").strip()
    hour = input("Departure hour (0-23): ").strip()

    try:
        start_hour = int(hour)
        if not 0 <= start_hour <= 23:
            print("Hour must be between 0 and 23.")
            return

        start_time = start_hour * 60  # convert hour to minutes
        path, total_time = dijkstra(graph, start, goal, cost_by_time, start_time)
        if not path:
            print("No path found.")
            return

        print(f"Shortest travel time from {start} to {goal} (departing at hour {start_hour}): {total_time} minutes")
        print(f"Path: {' -> '.join(path)}")
    except ValueError as error:
        print(f"Error: {error}")


def main():
    graph = generate_small_test_graph()

    while True:
        print("\n=== Smart Path Finder CLI ===")
        print("1. Show graph")
        print("2. Find shortest distance path")
        print("3. Find shortest time path")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            _print_graph(graph)
        elif choice == "2":
            _run_shortest_path_query(graph)
        elif choice == "3":
            _run_shortest_time_query(graph)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
