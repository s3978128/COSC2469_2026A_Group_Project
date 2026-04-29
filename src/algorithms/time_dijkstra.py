from utils.min_heap import MinHeap

def shortest_time_path(graph, start, end, start_hour):
    dist = {node: float('inf') for node in graph.adj}
    prev = {node: None for node in graph.adj}

    dist[start] = 0

    heap = MinHeap()
    heap.push((0, start, start_hour))

    while not heap.is_empty():
        current_time, u, current_hour = heap.pop()

        # 🔥 IMPORTANT: skip outdated entries
        if current_time > dist[u]:
            continue

        if u == end:
            break

        for edge in graph.adj[u]:
            v = edge.destination

            # get time based on current hour
            edge_time = edge.time_list[current_hour]

            new_time = current_time + edge_time

            # update hour after traveling
            next_hour = int(new_time % 24)

            if new_time < dist[v]:
                dist[v] = new_time
                prev[v] = u
                heap.push((new_time, v, next_hour))

    # reconstruct path
    path = []
    curr = end
    while curr:
        path.append(curr)
        curr = prev[curr]

    path.reverse()

    return dist[end], path