"""Graph represented using an adjacency list with Node and Edge objects."""

import math

from graph.edge import Edge
from graph.node import Node


class Graph:
    def __init__(self):
        self._nodes = {}  # node_id -> Node
        self.adj = {}     # node_id -> list[Edge]
        self._reverse_adj_cache = None  # node_id -> list[(pred_id, edge)]
        self._distance_heuristic_scale_cache = None
        self._time_heuristic_scale_cache = None
        self._alt_landmark_cache = None

    # ── Node operations ──────────────────────────────────────────────

    def add_node(self, node_id, x=None, y=None):
        """Add a node if it does not already exist."""
        if node_id not in self._nodes:
            self._nodes[node_id] = Node(node_id, x, y)
            self.adj[node_id] = []

    def get_node(self, node_id):
        """Return the Node object for the given id, or None."""
        return self._nodes.get(node_id)

    # ── Edge operations ──────────────────────────────────────────────

    def add_edge(self, from_id, to_id, distance, time_weights):
        """Add a directed edge from from_id to to_id.

        time_weights must be a list of exactly 24 values.
        """
        if len(time_weights) != 24:
            raise ValueError("time_weights must contain exactly 24 values")

        self.add_node(from_id)
        self.add_node(to_id)

        self.adj[from_id].append(Edge(from_id, to_id, distance, time_weights))
        # Any edge mutation invalidates reverse-index cache.
        self._reverse_adj_cache = None
        self._distance_heuristic_scale_cache = None
        self._time_heuristic_scale_cache = None
        self._alt_landmark_cache = None

    def add_two_way_edge(self, node_a, node_b, distance, time_weights):
        """Add edges in both directions (two-way road)."""
        self.add_edge(node_a, node_b, distance, time_weights)
        self.add_edge(node_b, node_a, distance, time_weights)

    def add_one_way_edge(self, from_id, to_id, distance, time_weights):
        """Add an edge in one direction only (one-way road)."""
        self.add_edge(from_id, to_id, distance, time_weights)

    # ── Query operations ─────────────────────────────────────────────

    def get_neighbors(self, node_id):
        """Return the list of outgoing edges for a node."""
        return self.adj.get(node_id, [])

    def neighbors(self, node_id):
        """Alias for get_neighbors (backward compatibility)."""
        return self.get_neighbors(node_id)

    def _build_reverse_adj_cache(self):
        """Build node -> incoming edge list once for reverse traversals."""
        reverse = {node_id: [] for node_id in self._nodes.keys()}
        for source in self._nodes.keys():
            for edge in self.adj.get(source, []):
                reverse[edge.destination].append((source, edge))
        self._reverse_adj_cache = reverse

    def reverse_neighbors(self, node_id):
        """Return incoming edges as (predecessor_id, edge) tuples."""
        if self._reverse_adj_cache is None:
            self._build_reverse_adj_cache()
        return self._reverse_adj_cache.get(node_id, [])

    def distance_heuristic_scale(self):
        """Return a safe scale for Euclidean lower-bound distance heuristics.

        If edge distances and coordinates imply ``distance >= s * euclidean`` on
        all observed edges, then ``h(n) = s * euclidean(n, goal)`` is admissible.
        """
        if self._distance_heuristic_scale_cache is not None:
            return self._distance_heuristic_scale_cache

        min_ratio = float("inf")
        found_ratio = False

        for source, edges in self.adj.items():
            source_node = self.get_node(source)
            if source_node is None:
                continue
            if source_node.x is None or source_node.y is None:
                continue

            for edge in edges:
                dest_node = self.get_node(edge.destination)
                if dest_node is None:
                    continue
                if dest_node.x is None or dest_node.y is None:
                    continue

                euclidean = self.euclidean_distance(source_node, dest_node)
                if euclidean <= 0:
                    continue

                ratio = edge.distance / euclidean
                min_ratio = min(min_ratio, ratio)
                found_ratio = True

        self._distance_heuristic_scale_cache = min_ratio if found_ratio else 0.0
        return self._distance_heuristic_scale_cache

    def time_heuristic_scale(self):
        """Return a safe scale for Euclidean lower-bound time heuristics.

        Computes ``min over all edges of (min_travel_time / euclidean_distance)``.
        This gives a scale in minutes-per-km such that
        ``h(n) = scale * euclidean(n, goal)`` is always <= actual travel time,
        making it admissible for time-dependent A* queries with cost_by_time.
        """
        if self._time_heuristic_scale_cache is not None:
            return self._time_heuristic_scale_cache

        min_ratio = float("inf")
        found_ratio = False

        for source, edges in self.adj.items():
            source_node = self.get_node(source)
            if source_node is None:
                continue
            if source_node.x is None or source_node.y is None:
                continue

            for edge in edges:
                dest_node = self.get_node(edge.destination)
                if dest_node is None:
                    continue
                if dest_node.x is None or dest_node.y is None:
                    continue

                euclidean = self.euclidean_distance(source_node, dest_node)
                if euclidean <= 0:
                    continue

                min_time = min(edge.time_list)
                ratio = min_time / euclidean
                min_ratio = min(min_ratio, ratio)
                found_ratio = True

        self._time_heuristic_scale_cache = min_ratio if found_ratio else 0.0
        return self._time_heuristic_scale_cache

    def nodes(self):
        """Return a list of all node IDs."""
        return list(self._nodes.keys())

    # ── Heuristic helpers ────────────────────────────────────────────

    @staticmethod
    def euclidean_distance(node_a, node_b):
        """Compute the Euclidean distance between two Node objects.

        Both nodes must have coordinates (x, y) set.
        """
        if (node_a.x is None or node_a.y is None
                or node_b.x is None or node_b.y is None):
            raise ValueError(
                "Both nodes must have coordinates for distance calculation"
            )
        return math.sqrt((node_a.x - node_b.x) ** 2
                         + (node_a.y - node_b.y) ** 2)

    def __repr__(self):
        return f"Graph(nodes={len(self._nodes)})"
