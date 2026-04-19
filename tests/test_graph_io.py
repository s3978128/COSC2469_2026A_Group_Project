import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dataio.graph_io import export_graph_csv, import_graph_csv
from evaluation.benchmark_datasets import run_dataset_benchmarks
from generator.graph_generator import generate_small_test_graph


class TestGraphIO(unittest.TestCase):
    def test_export_import_roundtrip(self):
        graph = generate_small_test_graph()

        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_dir = Path(temp_dir) / "graph_test"
            export_graph_csv(
                graph,
                dataset_dir,
                metadata={"dataset_name": "graph_test", "seed": 123},
            )

            loaded_graph, metadata = import_graph_csv(dataset_dir)

            self.assertEqual(set(graph.nodes()), set(loaded_graph.nodes()))
            self.assertEqual(metadata.get("dataset_name"), "graph_test")
            self.assertEqual(metadata.get("seed"), 123)

            original_edges = sum(len(graph.neighbors(n)) for n in graph.nodes())
            loaded_edges = sum(len(loaded_graph.neighbors(n)) for n in loaded_graph.nodes())
            self.assertEqual(original_edges, loaded_edges)

    def test_dataset_benchmark_from_exported_graph(self):
        graph = generate_small_test_graph()

        with tempfile.TemporaryDirectory() as temp_dir:
            datasets_dir = Path(temp_dir) / "datasets"
            dataset_dir = datasets_dir / "graph_small"
            output_csv = Path(temp_dir) / "runtime.csv"
            output_analysis = Path(temp_dir) / "analysis.txt"

            export_graph_csv(
                graph,
                dataset_dir,
                metadata={"dataset_name": "graph_small", "scenario": "test"},
            )

            rows = run_dataset_benchmarks(
                datasets_dir=datasets_dir,
                output_csv=output_csv,
                output_analysis=output_analysis,
                runs_per_pair=2,
            )

            self.assertGreater(len(rows), 0)
            self.assertTrue(output_csv.exists())
            self.assertTrue(output_analysis.exists())


if __name__ == "__main__":
    unittest.main()
