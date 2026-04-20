"""CSV/JSON import-export helpers for graph datasets."""

import csv
import json
from pathlib import Path

from graph.graph import Graph


EDGE_TIME_HEADERS = [f"time_{hour}" for hour in range(24)]


def _edge_count(graph):
    return sum(len(graph.neighbors(node_id)) for node_id in graph.nodes())


def export_graph_csv(graph, output_dir, metadata=None):
    """Export a graph to nodes.csv, edges.csv, and metadata.json.

    Parameters
    ----------
    graph : Graph
        Graph instance to export.
    output_dir : str | Path
        Target dataset directory.
    metadata : dict | None
        Optional metadata merged with auto-generated stats.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    nodes_csv = output_path / "nodes.csv"
    edges_csv = output_path / "edges.csv"
    metadata_json = output_path / "metadata.json"

    with nodes_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["node_id", "x", "y"])
        writer.writeheader()
        for node_id in sorted(graph.nodes()):
            node = graph.get_node(node_id)
            writer.writerow(
                {
                    "node_id": node_id,
                    "x": "" if node is None or node.x is None else node.x,
                    "y": "" if node is None or node.y is None else node.y,
                }
            )

    edge_headers = ["source", "destination", "distance"] + EDGE_TIME_HEADERS
    with edges_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=edge_headers)
        writer.writeheader()
        for source in sorted(graph.nodes()):
            for edge in graph.neighbors(source):
                row = {
                    "source": edge.source,
                    "destination": edge.destination,
                    "distance": edge.distance,
                }
                for hour in range(24):
                    row[f"time_{hour}"] = edge.time_list[hour]
                writer.writerow(row)

    summary = {
        "node_count": len(graph.nodes()),
        "edge_count": _edge_count(graph),
        "edge_node_ratio": round(
            (_edge_count(graph) / len(graph.nodes())) if graph.nodes() else 0.0,
            2,
        ),
    }

    if metadata:
        summary.update(metadata)

    metadata_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def import_graph_csv(input_dir):
    """Import a graph from nodes.csv and edges.csv.

    Returns
    -------
    tuple[Graph, dict]
        The reconstructed graph and metadata dictionary (if available).
    """
    input_path = Path(input_dir)
    nodes_csv = input_path / "nodes.csv"
    edges_csv = input_path / "edges.csv"
    metadata_json = input_path / "metadata.json"

    if not nodes_csv.exists() or not edges_csv.exists():
        raise FileNotFoundError("nodes.csv and edges.csv are required")

    graph = Graph()

    with nodes_csv.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            node_id = row["node_id"]
            x_val = row.get("x", "")
            y_val = row.get("y", "")
            x = None if x_val in ("", None) else float(x_val)
            y = None if y_val in ("", None) else float(y_val)
            graph.add_node(node_id, x=x, y=y)

    with edges_csv.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            source = row["source"]
            destination = row["destination"]
            distance = float(row["distance"])
            time_weights = [float(row[f"time_{hour}"]) for hour in range(24)]
            graph.add_one_way_edge(source, destination, distance, time_weights)

    metadata = {}
    if metadata_json.exists():
        metadata = json.loads(metadata_json.read_text(encoding="utf-8"))

    return graph, metadata
