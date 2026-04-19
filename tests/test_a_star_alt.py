import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.a_star_alt import a_star_alt
from algorithms.dijkstra import dijkstra
from cost.distance_cost import cost_by_distance
from generator.graph_generator import generate_small_test_graph


class TestAStarALT(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_matches_dijkstra_cost(self):
        path_alt, cost_alt = a_star_alt(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            landmark_count=4,
        )
        path_dij, cost_dij = dijkstra(self.graph, "A", "F", cost_by_distance)

        self.assertEqual(path_alt, path_dij)
        self.assertAlmostEqual(cost_alt, cost_dij)

    def test_return_stats_has_expanded_nodes(self):
        _, _, stats = a_star_alt(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            return_stats=True,
            landmark_count=4,
        )
        self.assertIn("expanded_nodes", stats)
        self.assertGreater(stats["expanded_nodes"], 0)

    def test_respects_avoid_constraints(self):
        path, distance = a_star_alt(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            avoid_edges={("C", "D")},
            landmark_count=4,
        )
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertAlmostEqual(distance, 13.0)


if __name__ == "__main__":
    unittest.main()
