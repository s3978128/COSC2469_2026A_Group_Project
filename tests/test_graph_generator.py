import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from generator.graph_generator import generate_realistic_graph, generate_small_test_graph


class TestGraphGenerator(unittest.TestCase):
    def setUp(self):
        self.graph = generate_small_test_graph()

    def test_expected_nodes_exist(self):
        expected = {"A", "B", "C", "D", "E", "F"}
        self.assertEqual(set(self.graph.nodes()), expected)

    def test_each_edge_has_24_hourly_values(self):
        for node in self.graph.nodes():
            for edge in self.graph.neighbors(node):
                self.assertEqual(len(edge.time_list), 24)

    def test_two_way_road_has_edges_in_both_directions(self):
        """A-B is a two-way road, so both A->B and B->A should exist."""
        neighbors_a = {edge.destination for edge in self.graph.neighbors("A")}
        neighbors_b = {edge.destination for edge in self.graph.neighbors("B")}
        self.assertIn("B", neighbors_a)
        self.assertIn("A", neighbors_b)

    def test_one_way_road_has_edge_in_one_direction(self):
        """B-E is a one-way road, so B->E exists but E->B does not."""
        neighbors_b = {edge.destination for edge in self.graph.neighbors("B")}
        neighbors_e = {edge.destination for edge in self.graph.neighbors("E")}
        self.assertIn("E", neighbors_b)
        self.assertNotIn("B", neighbors_e)

    def test_realistic_scenario_degree_range(self):
        graph = generate_realistic_graph(5, 5, seed=42, scenario="realistic")
        degrees = [len(graph.neighbors(node)) for node in graph.nodes()]
        self.assertGreaterEqual(min(degrees), 2)
        self.assertLessEqual(max(degrees), 4)

    def test_mixed_scenario_includes_hub_nodes(self):
        graph = generate_realistic_graph(5, 5, seed=42, scenario="mixed")
        degrees = [len(graph.neighbors(node)) for node in graph.nodes()]
        self.assertGreaterEqual(max(degrees), 5)

    def test_no_duplicate_directed_edges(self):
        graph = generate_realistic_graph(6, 6, seed=42, scenario="stress")
        for node in graph.nodes():
            destinations = [edge.destination for edge in graph.neighbors(node)]
            self.assertEqual(len(destinations), len(set(destinations)))


if __name__ == "__main__":
    unittest.main()
