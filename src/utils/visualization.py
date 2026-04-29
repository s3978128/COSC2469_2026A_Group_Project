"""ASCII and text-based visualization for road networks and paths."""


def _collect_node_positions(graph):
    """Return mapping node_id -> (x, y) for coordinate-based nodes."""
    positions = {}
    for node_id in graph.nodes():
        node = graph.get_node(node_id)
        if node and node.x is not None and node.y is not None:
            positions[node_id] = (node.x, node.y)
    return positions


def _bresenham_points(x0, y0, x1, y1):
    """Yield integer points on the line from (x0, y0) to (x1, y1)."""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return points


def _draw_edge(grid, source_pos, dest_pos, char, override=False):
    """Draw an edge between two points on a character grid."""
    node_symbols = {"○", "●", "◍", "S", "E"}
    points = _bresenham_points(source_pos[0], source_pos[1], dest_pos[0], dest_pos[1])

    for x, y in points[1:-1]:
        if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
            continue
        if grid[y][x] in node_symbols:
            continue
        if override or grid[y][x] == " ":
            grid[y][x] = char


def render_network_grid(
    graph,
    path=None,
    visited_nodes=None,
    cell_size=3,
    start_node=None,
    end_node=None,
):
    """Render road network as an ASCII grid visualization.

    Parameters
    ----------
    graph : Graph
        The road network to visualize.
    path : list[str], optional
        Shortest path to highlight (node sequence).
    visited_nodes : list[str] or set[str], optional
        Nodes visited by the search algorithm.
    cell_size : int
        Spacing between coordinate positions in characters (default 3).
    start_node : str, optional
        Start node to mark explicitly in the visualization.
    end_node : str, optional
        End node to mark explicitly in the visualization.

    Returns
    -------
    str
        ASCII art representation of the network.
    """
    nodes = graph.nodes()
    if not nodes:
        return "[Empty graph]"

    node_positions = _collect_node_positions(graph)

    if not node_positions:
        return "[No coordinates available]"

    x_values = sorted({x for x, _ in node_positions.values()})
    y_values = sorted({y for _, y in node_positions.values()}, reverse=True)

    step = max(2, int(cell_size))
    width = (len(x_values) - 1) * step + 1
    height = (len(y_values) - 1) * step + 1
    margin = 1

    grid = [[" " for _ in range(width + 2 * margin)] for _ in range(height + 2 * margin)]

    x_index = {value: i for i, value in enumerate(x_values)}
    y_index = {value: i for i, value in enumerate(y_values)}

    normalized_pos = {}
    for node_id, (x, y) in node_positions.items():
        nx = margin + x_index[x] * step
        ny = margin + y_index[y] * step
        normalized_pos[node_id] = (nx, ny)

    path_set = set(path or [])
    visited_set = set(visited_nodes or [])
    effective_start = start_node if start_node is not None else (path[0] if path else None)
    effective_end = end_node if end_node is not None else (path[-1] if path else None)
    path_edges = set()
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            path_edges.add((path[i], path[i + 1]))

    # Draw non-path edges first.
    for node_id in nodes:
        for edge in graph.neighbors(node_id):
            if (node_id, edge.destination) in path_edges:
                continue
            source_pos = normalized_pos.get(node_id)
            dest_pos = normalized_pos.get(edge.destination)
            if source_pos is None or dest_pos is None:
                continue
            _draw_edge(grid, source_pos, dest_pos, char=".")

    # Draw path edges after regular roads so the overlay is always visible.
    for source, destination in path_edges:
        source_pos = normalized_pos.get(source)
        dest_pos = normalized_pos.get(destination)
        if source_pos is None or dest_pos is None:
            continue
        _draw_edge(grid, source_pos, dest_pos, char="=", override=True)

    # Draw nodes last so they remain visible above edges.
    for node_id, (x, y) in normalized_pos.items():
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            if node_id == effective_start:
                grid[y][x] = "S"
            elif node_id == effective_end:
                grid[y][x] = "E"
            elif node_id in path_set:
                grid[y][x] = "●"
            elif node_id in visited_set:
                grid[y][x] = "◍"
            else:
                grid[y][x] = "○"

    lines = []
    lines.append("┌" + "─" * len(grid[0]) + "┐")
    for row in grid:
        lines.append("│" + "".join(row) + "│")
    lines.append("└" + "─" * len(grid[0]) + "┘")

    lines.append("")
    lines.append("Legend:")
    lines.append("  S = start node")
    lines.append("  E = end node")
    lines.append("  ○ = unvisited node")
    lines.append("  ◍ = visited node")
    lines.append("  ● = shortest-path node")
    lines.append("  . = road")
    lines.append("  = = shortest-path edge")

    return "\n".join(lines)


def render_path_details(graph, path, cost, cost_type="distance", start_time=0):
    """Render detailed path information including segment breakdown.

    Parameters
    ----------
    graph : Graph
        The road network.
    path : list[str]
        Node sequence of the path.
    cost : float
        Total cost (distance or time).
    cost_type : {"distance", "time"}
        Type of cost being displayed.
    start_time : int
        Start time in minutes (for time-based routing).

    Returns
    -------
    str
        Formatted path details.
    """
    if not path:
        return "[No path found]"

    lines = []
    lines.append("")
    lines.append("╔════════════════════════════════════╗")
    lines.append(f"║ SHORTEST PATH DETAILS ({cost_type.upper()}) ║")
    lines.append("╚════════════════════════════════════╝")
    lines.append("")
    lines.append(f"Route: {' → '.join(path)}")

    # Always report both totals for the selected path.
    total_distance = 0.0
    total_travel_time = 0.0

    rolling_time = start_time
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]

        edge = None
        for e in graph.neighbors(from_node):
            if e.destination == to_node:
                edge = e
                break

        if edge is None:
            continue

        total_distance += edge.distance
        hour = int(rolling_time // 60) % 24
        segment_time = edge.get_travel_time(hour)
        total_travel_time += segment_time
        rolling_time += segment_time

    lines.append(f"Total distance: {total_distance:.2f} km")
    lines.append(f"Total travel time: {total_travel_time:.2f} min")

    if cost_type == "distance":
        lines.append(f"Optimized objective: distance = {cost:.2f} km")
    else:
        lines.append(f"Optimized objective: time = {cost:.2f} min")
    lines.append("")
    lines.append("Segment breakdown:")
    lines.append("─" * 70)

    current_time = start_time
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]

        # Find edge
        edge = None
        for e in graph.neighbors(from_node):
            if e.destination == to_node:
                edge = e
                break

        if edge:
            distance = edge.distance
            hour = int(current_time // 60) % 24
            segment_time = edge.get_travel_time(hour)
            current_time += segment_time

            # Infer road type from speed
            speed = (distance / edge.get_travel_time(12)) * 60
            if speed >= 70:
                road_type = "Highway"
            elif speed >= 40:
                road_type = "Main Road"
            else:
                road_type = "Local St."

            lines.append(
                f"  {from_node:5s} → {to_node:5s}   {distance:6.1f} km   "
                f"{segment_time:7.2f} min   {road_type:12s}"
            )

    lines.append("─" * 70)
    lines.append("")

    return "\n".join(lines)


def render_graph_info(graph):
    """Render summary statistics about the graph.

    Parameters
    ----------
    graph : Graph
        The road network.

    Returns
    -------
    str
        Graph statistics.
    """
    num_nodes = len(graph.nodes())
    num_edges = sum(len(graph.neighbors(n)) for n in graph.nodes())

    lines = []
    lines.append("")
    lines.append("╔═══════════════════════════════════╗")
    lines.append("║     ROAD NETWORK STATISTICS      ║")
    lines.append("╚═══════════════════════════════════╝")
    lines.append(f"  Nodes (intersections): {num_nodes}")
    lines.append(f"  Edges (roads):         {num_edges}")
    if num_nodes > 0:
        lines.append(f"  Edge/Node ratio:       {num_edges / num_nodes:.2f}")

    # Check for coordinates
    has_coords = False
    for node_id in graph.nodes():
        node = graph.get_node(node_id)
        if node.x is not None and node.y is not None:
            has_coords = True
            break

    lines.append(f"  Coordinate-based:      {'Yes' if has_coords else 'No'}")
    lines.append("")

    return "\n".join(lines)
