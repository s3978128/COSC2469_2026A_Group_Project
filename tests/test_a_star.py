import sys
import unittest
from math import inf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.a_star import a_star
from algorithms.dijkstra import dijkstra
from cost.distance_cost import cost_by_distance
from generator.graph_generator import generate_small_test_graph
from graph.graph import Graph


class TestAStar(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_matches_dijkstra_on_distance(self):
        a_path, a_cost = a_star(self.graph, "A", "F", cost_by_distance)
        d_path, d_cost = dijkstra(self.graph, "A", "F", cost_by_distance)

        self.assertEqual(a_path, d_path)
        self.assertAlmostEqual(a_cost, d_cost)

    def test_unreachable_returns_inf_and_empty_path(self):
        graph = Graph()
        graph.add_node("A", 0.0, 0.0)
        graph.add_node("B", 1.0, 1.0)

        path, cost = a_star(graph, "A", "B", cost_by_distance)
        self.assertEqual(path, [])
        self.assertEqual(cost, inf)

    def test_avoid_nodes_changes_route(self):
        path, distance = a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            avoid_nodes={"C"},
        )
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertAlmostEqual(distance, 13.0)

    def test_avoid_edges_changes_route(self):
        path, distance = a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            avoid_edges={("C", "D")},
        )
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertAlmostEqual(distance, 13.0)

    def test_start_or_goal_blocked_raises_error(self):
        with self.assertRaises(ValueError):
            a_star(
                self.graph,
                "A",
                "F",
                cost_by_distance,
                avoid_nodes={"A"},
            )

    def test_return_stats_reports_expanded_nodes(self):
        path, distance, stats = a_star(
            self.graph,
            "A",
            "F",
            cost_by_distance,
            return_stats=True,
        )
        self.assertEqual(path, ["A", "C", "D", "F"])
        self.assertAlmostEqual(distance, 12.5)
        self.assertIn("expanded_nodes", stats)
        self.assertGreater(stats["expanded_nodes"], 0)


if __name__ == "__main__":
    unittest.main()
