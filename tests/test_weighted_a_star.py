import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.dijkstra import dijkstra
from algorithms.weighted_a_star import weighted_a_star
from cost.distance_cost import cost_by_distance
from generator.graph_generator import generate_small_test_graph


class TestWeightedAStar(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_weighted_a_star_returns_valid_path(self):
        path, cost = weighted_a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            heuristic_weight=1.25,
        )
        self.assertTrue(path)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "F")
        self.assertGreater(cost, 0.0)

    def test_weighted_cost_not_better_than_optimal(self):
        weighted_path, weighted_cost = weighted_a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            heuristic_weight=1.5,
        )
        optimal_path, optimal_cost = dijkstra(
            self.graph,
            "A",
            "F",
            cost_by_distance,
        )
        self.assertTrue(weighted_path)
        self.assertTrue(optimal_path)
        self.assertGreaterEqual(weighted_cost, optimal_cost)

    def test_invalid_weight_raises_error(self):
        with self.assertRaises(ValueError):
            weighted_a_star(
                self.graph,
                "A",
                "F",
                cost_by_distance,
                heuristic_weight=0.99,
            )

    def test_return_stats_reports_expanded_nodes(self):
        _, _, stats = weighted_a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            heuristic_weight=1.25,
            return_stats=True,
        )
        self.assertIn("expanded_nodes", stats)
        self.assertGreater(stats["expanded_nodes"], 0)


if __name__ == "__main__":
    unittest.main()
