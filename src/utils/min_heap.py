class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        self._swap(0, len(self.heap) - 1)
        item = self.heap.pop()
        self._heapify_down(0)
        return item

    def _heapify_up(self, i):
        parent = (i - 1) // 2
        if i > 0 and self.heap[i][0] < self.heap[parent][0]:
            self._swap(i, parent)
            self._heapify_up(parent)

    def _heapify_down(self, i):
        left = 2 * i + 1
        right = 2 * i + 2
        smallest = i

        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        if smallest != i:
            self._swap(i, smallest)
            self._heapify_down(smallest)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def is_empty(self):
        return len(self.heap) == 0