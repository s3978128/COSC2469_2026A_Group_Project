"""Graph represented using an adjacency list."""

from graph.edge import Edge


class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u, v, distance, time_list):
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append(Edge(v, distance, time_list))

        if not self.directed:
            self.adj[v].append(Edge(u, distance, time_list))

    def neighbors(self, node):
        return self.adj.get(node, [])

    def nodes(self):
        return list(self.adj.keys())

    def __repr__(self):
        return f"Graph(nodes={len(self.adj)}, directed={self.directed})"