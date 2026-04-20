"""Generate and persist benchmark datasets of multiple graph sizes."""

import argparse
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dataio.graph_io import export_graph_csv
from generator.graph_generator import generate_realistic_graph


DATASET_SPECS = [
    {"name": "graph_100", "rows": 10, "cols": 10, "scenario": "realistic"},
    {"name": "graph_1000", "rows": 25, "cols": 40, "scenario": "mixed"},
    {"name": "graph_5000", "rows": 50, "cols": 100, "scenario": "mixed"},
]


def generate_and_export_datasets(base_dir=ROOT / "data" / "datasets", seed=42, max_nodes=10000):
    """Generate configured datasets and export each as CSV+JSON."""
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    created = []
    for spec in DATASET_SPECS:
        node_count = spec["rows"] * spec["cols"]
        if node_count > max_nodes:
            continue

        t0 = time.perf_counter()
        graph = generate_realistic_graph(
            rows=spec["rows"],
            cols=spec["cols"],
            seed=seed,
            scenario=spec["scenario"],
        )
        elapsed = time.perf_counter() - t0

        dataset_dir = base_path / spec["name"]
        metadata = {
            "dataset_name": spec["name"],
            "rows": spec["rows"],
            "cols": spec["cols"],
            "scenario": spec["scenario"],
            "seed": seed,
            "generated_seconds": round(elapsed, 4),
        }
        export_graph_csv(graph, dataset_dir, metadata=metadata)

        created.append((spec["name"], node_count, elapsed))

    return created


def main():
    parser = argparse.ArgumentParser(description="Generate graph datasets for benchmarking")
    parser.add_argument("--seed", type=int, default=42, help="Random seed used by all datasets")
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=10000,
        help="Skip dataset specs larger than this node count",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=ROOT / "data" / "datasets",
        help="Output base directory",
    )
    args = parser.parse_args()

    created = generate_and_export_datasets(
        base_dir=args.base_dir,
        seed=args.seed,
        max_nodes=args.max_nodes,
    )

    if not created:
        print("No datasets generated. Check max-nodes setting.")
        return

    print("Generated datasets:")
    for name, node_count, elapsed in created:
        print(f"- {name}: nodes={node_count}, generation={elapsed:.3f}s")


if __name__ == "__main__":
    main()
