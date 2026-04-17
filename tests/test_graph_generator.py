import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from generator.graph_generator import generate_small_test_graph


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


if __name__ == "__main__":
    unittest.main()
