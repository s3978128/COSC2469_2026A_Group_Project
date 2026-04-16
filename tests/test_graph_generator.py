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

    def test_graph_is_undirected_for_sample_road(self):
        neighbors_a = {edge.destination for edge in self.graph.neighbors("A")}
        neighbors_b = {edge.destination for edge in self.graph.neighbors("B")}
        self.assertIn("B", neighbors_a)
        self.assertIn("A", neighbors_b)


if __name__ == "__main__":
    unittest.main()
