"""Node model: represents a location in the graph."""


class Node:
    def __init__(self, node_id, x=None, y=None):
        self.id = node_id
        self.x = x
        self.y = y

    def __repr__(self):
        coords = ""
        if self.x is not None and self.y is not None:
            coords = f", x={self.x}, y={self.y}"
        return f"Node({self.id}{coords})"

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return NotImplemented

    def __hash__(self):
        return hash(self.id)
