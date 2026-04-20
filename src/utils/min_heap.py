"""Min-heap (priority queue) implemented from scratch."""


class MinHeap:
    """A binary min-heap that supports push and pop operations.

    Items are compared using their natural ordering (e.g. tuples compare
    element-by-element), so pushing (priority, data) tuples works correctly.
    """

    def __init__(self):
        self._data = []

    def push(self, item):
        """Insert an item into the heap."""
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        """Remove and return the smallest item."""
        if not self._data:
            raise IndexError("pop from empty heap")
        self._swap(0, len(self._data) - 1)
        item = self._data.pop()
        if self._data:
            self._sift_down(0)
        return item

    def is_empty(self):
        """Return True if the heap contains no items."""
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    # ── internal helpers ─────────────────────────────────────────────

    def _sift_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self._data[index] < self._data[parent]:
                self._swap(index, parent)
                index = parent
            else:
                break

    def _sift_down(self, index):
        size = len(self._data)
        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2
            if left < size and self._data[left] < self._data[smallest]:
                smallest = left
            if right < size and self._data[right] < self._data[smallest]:
                smallest = right
            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]
