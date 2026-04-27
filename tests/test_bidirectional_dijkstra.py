import sys
import unittest
from math import inf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from algorithms.dijkstra import dijkstra
from cost.distance_cost import cost_by_distance
from graph.graph import Graph
from generator.graph_generator import generate_small_test_graph


class TestBidirectionalDijkstra(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_matches_dijkstra_distance_result(self):
        path_1, cost_1 = dijkstra(self.graph, "A", "F", cost_by_distance)
        path_2, cost_2 = bidirectional_dijkstra(
            self.graph,
            "A",
            "F",
            cost_by_distance,
        )
        self.assertEqual(path_2, path_1)
        self.assertAlmostEqual(cost_2, cost_1)

    def test_avoid_nodes_changes_route(self):
        path, cost = bidirectional_dijkstra(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            avoid_nodes={"C"},
        )
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertAlmostEqual(cost, 13.0)

    def test_avoid_edges_changes_route(self):
        path, cost = bidirectional_dijkstra(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            avoid_edges={("C", "D")},
        )
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertAlmostEqual(cost, 13.0)

    def test_unreachable_returns_inf(self):
        graph = Graph()
        graph.add_node("A")
        graph.add_node("B")

        path, cost = bidirectional_dijkstra(graph, "A", "B", cost_by_distance)
        self.assertEqual(path, [])
        self.assertEqual(cost, inf)

    def test_return_stats_reports_bidirectional_counts(self):
        path, cost, stats = bidirectional_dijkstra(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            return_stats=True,
        )
        self.assertEqual(path, ["A", "C", "D", "F"])
        self.assertAlmostEqual(cost, 12.5)
        self.assertIn("expanded_nodes", stats)
        self.assertIn("expanded_forward", stats)
        self.assertIn("expanded_backward", stats)
        self.assertEqual(
            stats["expanded_nodes"],
            stats["expanded_forward"] + stats["expanded_backward"],
        )


if __name__ == "__main__":
    unittest.main()
