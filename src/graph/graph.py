#Adjacency list

from edge import Edge
class Graph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []
    
    def add_edge(self, u , v, distance, time_list):
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append(Edge(v, distance, time_list))