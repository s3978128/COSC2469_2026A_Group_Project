import sys
import unittest
from math import inf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.dijkstra import dijkstra
from cost.distance_cost import cost_by_distance
from cost.time_cost import cost_by_time
from generator.graph_generator import generate_small_test_graph
from graph.graph import Graph


class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_shortest_path_a_to_f(self):
        path, distance = dijkstra(self.graph, "A", "F", cost_by_distance)
        self.assertAlmostEqual(distance, 12.5)
        self.assertEqual(path, ["A", "C", "D", "F"])

    def test_same_start_and_goal(self):
        path, distance = dijkstra(self.graph, "C", "C", cost_by_distance)
        self.assertEqual(distance, 0.0)
        self.assertEqual(path, ["C"])

    def test_unreachable_returns_inf_and_empty_path(self):
        graph = Graph()
        graph.add_node("A")
        graph.add_node("B")

        path, distance = dijkstra(graph, "A", "B", cost_by_distance)
        self.assertEqual(distance, inf)
        self.assertEqual(path, [])

    def test_invalid_node_raises_error(self):
        with self.assertRaises(ValueError):
            dijkstra(self.graph, "A", "Z", cost_by_distance)

    def test_shortest_time_path_a_to_f_at_midnight(self):
        path, total_time = dijkstra(
            self.graph,
            "A",
            "F",
            cost_by_time,
            start_time=0,
        )
        self.assertEqual(path, ["A", "C", "D", "F"])
        # Expected: A→C (10*0.85) + C→D (4*0.85) + D→F (6*0.85) = 17.0
        self.assertAlmostEqual(total_time, 17.0)

    def test_negative_cost_raises_error(self):
        def negative_cost(edge, current_time):
            return -1

        with self.assertRaises(ValueError):
            dijkstra(self.graph, "A", "F", negative_cost)

    def test_return_visited_includes_start_and_goal(self):
        path, distance, visited = dijkstra(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            return_visited=True,
        )
        self.assertEqual(path, ["A", "C", "D", "F"])
        self.assertAlmostEqual(distance, 12.5)
        self.assertEqual(visited[0], "A")
        self.assertIn("F", visited)

if __name__ == "__main__":
    unittest.main()
