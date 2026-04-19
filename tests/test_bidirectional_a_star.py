import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.bidirectional_a_star import bidirectional_a_star
from algorithms.dijkstra import dijkstra
from cost.distance_cost import cost_by_distance
from generator.graph_generator import generate_small_test_graph


class TestBidirectionalAStar(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_matches_dijkstra_distance_result(self):
        b_path, b_cost = bidirectional_a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
        )
        d_path, d_cost = dijkstra(self.graph, "A", "F", cost_by_distance)
        self.assertEqual(b_path, d_path)
        self.assertAlmostEqual(b_cost, d_cost)

    def test_avoid_nodes_changes_route(self):
        path, distance = bidirectional_a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            avoid_nodes={"C"},
        )
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertAlmostEqual(distance, 13.0)

    def test_avoid_edges_changes_route(self):
        path, distance = bidirectional_a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            avoid_edges={("C", "D")},
        )
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertAlmostEqual(distance, 13.0)

    def test_return_stats_reports_bidirectional_counts(self):
        path, distance, stats = bidirectional_a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            return_stats=True,
        )
        self.assertEqual(path, ["A", "C", "D", "F"])
        self.assertAlmostEqual(distance, 12.5)
        self.assertIn("expanded_nodes", stats)
        self.assertIn("expanded_forward", stats)
        self.assertIn("expanded_backward", stats)
        self.assertEqual(
            stats["expanded_nodes"],
            stats["expanded_forward"] + stats["expanded_backward"],
        )


if __name__ == "__main__":
    unittest.main()
