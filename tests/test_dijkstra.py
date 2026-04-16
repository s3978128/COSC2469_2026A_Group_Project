import sys
import unittest
from math import inf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.dijkstra import shortest_distance_path
from generator.graph_generator import generate_small_test_graph
from graph.graph import Graph


class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_shortest_path_a_to_f(self):
        distance, path = shortest_distance_path(self.graph, "A", "F")
        self.assertAlmostEqual(distance, 12.5)
        self.assertEqual(path, ["A", "C", "D", "F"])

    def test_same_start_and_goal(self):
        distance, path = shortest_distance_path(self.graph, "C", "C")
        self.assertEqual(distance, 0.0)
        self.assertEqual(path, ["C"])

    def test_unreachable_returns_inf_and_empty_path(self):
        graph = Graph(directed=True)
        graph.add_node("A")
        graph.add_node("B")

        distance, path = shortest_distance_path(graph, "A", "B")
        self.assertEqual(distance, inf)
        self.assertEqual(path, [])

    def test_invalid_node_raises_error(self):
        with self.assertRaises(ValueError):
            shortest_distance_path(self.graph, "A", "Z")


if __name__ == "__main__":
    unittest.main()
