import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from algorithms.a_star_alt import a_star_departure_alt
from algorithms.degree2_contraction import a_star_contracted, dijkstra_contracted
from algorithms.dijkstra import dijkstra
from cost.time_cost import cost_by_time
from graph.graph import Graph


class TestTimeAlgorithms(unittest.TestCase):
    def _build_midnight_graph(self):
        graph = Graph()
        graph.add_node("S", 0, 0)
        graph.add_node("B", 1, 0)
        graph.add_node("G", 2, 0)

        direct = [150.0] * 24
        s_to_b = [70.0] * 24
        b_to_g = [1.0] * 24
        for hour in range(8, 24):
            b_to_g[hour] = 100.0

        graph.add_one_way_edge("S", "G", 10.0, direct)
        graph.add_one_way_edge("S", "B", 1.0, s_to_b)
        graph.add_one_way_edge("B", "G", 1.0, b_to_g)
        return graph

    def _build_contraction_graph(self):
        graph = Graph()
        graph.add_node("S", 0, 0)
        graph.add_node("X", 1, 0)
        graph.add_node("G", 2, 0)
        time_weights = [1.0] * 24
        graph.add_one_way_edge("S", "X", 1.0, time_weights)
        graph.add_one_way_edge("X", "G", 1.0, time_weights)
        return graph

    def test_departure_alt_matches_dijkstra_across_midnight(self):
        graph = self._build_midnight_graph()
        start_time = 23 * 60

        dijkstra_path, dijkstra_cost = dijkstra(
            graph,
            "S",
            "G",
            cost_by_time,
            start_time=start_time,
        )
        alt_path, alt_cost = a_star_departure_alt(
            graph,
            "S",
            "G",
            cost_by_time,
            start_time=start_time,
            departure_hour=8,
            landmark_count=3,
        )

        self.assertEqual(dijkstra_path, alt_path)
        self.assertAlmostEqual(dijkstra_cost, alt_cost)

    def test_contracted_algorithms_respect_avoid_nodes(self):
        graph = self._build_contraction_graph()

        baseline_path, baseline_cost = dijkstra(
            graph,
            "S",
            "G",
            cost_by_time,
            avoid_nodes={"X"},
        )
        contracted_path, contracted_cost = dijkstra_contracted(
            graph,
            "S",
            "G",
            cost_by_time,
            avoid_nodes={"X"},
        )

        self.assertEqual([], baseline_path)
        self.assertEqual(float("inf"), baseline_cost)
        self.assertEqual([], contracted_path)
        self.assertEqual(float("inf"), contracted_cost)

    def test_contracted_astar_respects_avoid_nodes(self):
        graph = self._build_contraction_graph()

        baseline_path, baseline_cost = dijkstra(
            graph,
            "S",
            "G",
            cost_by_time,
            avoid_nodes={"X"},
        )
        contracted_path, contracted_cost = a_star_contracted(
            graph,
            "S",
            "G",
            cost_by_time,
            avoid_nodes={"X"},
        )

        self.assertEqual([], baseline_path)
        self.assertEqual(float("inf"), baseline_cost)
        self.assertEqual([], contracted_path)
        self.assertEqual(float("inf"), contracted_cost)


if __name__ == "__main__":
    unittest.main()