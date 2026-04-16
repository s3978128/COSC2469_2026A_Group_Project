"""Dijkstra shortest path (distance-based) for adjacency-list graphs."""

import heapq
from math import inf


def shortest_distance_path(graph, start, goal):
	"""Return (total_distance, path_nodes) from start to goal.

	If goal is unreachable, returns (inf, []).
	"""
	if start not in graph.adj or goal not in graph.adj:
		raise ValueError("start and goal must exist in the graph")

	distances = {node: inf for node in graph.nodes()}
	previous = {node: None for node in graph.nodes()}
	distances[start] = 0.0

	pq = [(0.0, start)]

	while pq:
		current_distance, node = heapq.heappop(pq)

		if current_distance > distances[node]:
			continue

		if node == goal:
			break

		for edge in graph.neighbors(node):
			new_distance = current_distance + edge.distance
			if new_distance < distances[edge.destination]:
				distances[edge.destination] = new_distance
				previous[edge.destination] = node
				heapq.heappush(pq, (new_distance, edge.destination))

	if distances[goal] == inf:
		return inf, []

	path = []
	current = goal
	while current is not None:
		path.append(current)
		current = previous[current]
	path.reverse()

	return distances[goal], path
