import sys
import unittest

INF = float("inf")


# ---------------------------------------------------------------------------
# Priority queue (binary min-heap)
# ---------------------------------------------------------------------------
class PriorityQueue:
    """
    Min-priority queue: pop() always returns the entry with the smallest cost.
    Stored as a list where node i has children 2i+1 and 2i+2, parent (i-1)//2.
    push -> O(log n)    pop -> O(log n)
    """

    def __init__(self):
        self.heap = []

    def is_empty(self):
        return len(self.heap) == 0

    def push(self, cost, node):
        self.heap.append((cost, node))
        i = len(self.heap) - 1
        # sift up: swap with parent while smaller than parent
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[i][0] < self.heap[parent][0]:
                self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
                i = parent
            else:
                break

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty priority queue")
        smallest = self.heap[0]
        last = self.heap.pop()
        if self.heap:
            self.heap[0] = last
            i, n = 0, len(self.heap)
            # sift down: swap with the smaller child while larger than it
            while True:
                left, right, small = 2 * i + 1, 2 * i + 2, i
                if left < n and self.heap[left][0] < self.heap[small][0]:
                    small = left
                if right < n and self.heap[right][0] < self.heap[small][0]:
                    small = right
                if small == i:
                    break
                self.heap[i], self.heap[small] = self.heap[small], self.heap[i]
                i = small
        return smallest

    def contents(self):
        return sorted(self.heap)


# ---------------------------------------------------------------------------
# Dijkstra's algorithm
# ---------------------------------------------------------------------------
def dijkstra(graph, source, destination, trace=False):
    """
    graph: adjacency list {node: [(neighbour, weight), ...]}
    Returns (path, total_cost). If unreachable: (None, INF).

    Steps:
      1. Set every distance to infinity, the source to 0, push (0, source).
      2. Pop the node with the smallest distance. Its distance is now final.
      3. Relax each outgoing road: if dist[u] + w < dist[v], update v,
         remember u as v's previous node, and push (new distance, v).
      4. Stop when the destination is popped; follow 'previous' back to the source.
    """
    if source not in graph:
        raise KeyError(f"Unknown source node: {source}")
    if destination not in graph:
        raise KeyError(f"Unknown destination node: {destination}")
    for u in graph:
        for v, w in graph[u]:
            if w < 0:
                raise ValueError(f"Negative weight on road {u}->{v}; Dijkstra needs weights >= 0")

    distance = {node: INF for node in graph}
    previous = {node: None for node in graph}
    visited = set()

    distance[source] = 0
    queue = PriorityQueue()
    queue.push(0, source)
    step = 0

    while not queue.is_empty():
        current_cost, u = queue.pop()

        if u in visited:  # outdated (stale) queue entry
            if trace:
                print(f"  pop ({current_cost}, {u}) is stale, skip")
            continue
        visited.add(u)
        step += 1
        if trace:
            print(f"Step {step}: pop ({current_cost}, {u}) -> {u} is final at {current_cost}")

        if u == destination:
            break

        for v, w in graph[u]:
            if v in visited:
                continue
            new_cost = current_cost + w
            if new_cost < distance[v]:
                old = distance[v]
                distance[v] = new_cost
                previous[v] = u
                queue.push(new_cost, v)
                if trace:
                    note = "new" if old == INF else f"better than {old}"
                    print(f"  relax {u}->{v}: {current_cost} + {w} = {new_cost} ({note})")
        if trace:
            print(f"  queue: {queue.contents()}")

    if distance[destination] == INF:
        return None, INF

    path, node = [], destination
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    return path, distance[destination]


# ---------------------------------------------------------------------------
# Case-study road network (two-way roads)
# ---------------------------------------------------------------------------
GRAPH = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("C", 1), ("D", 5)],
    "C": [("A", 2), ("B", 1), ("D", 8), ("E", 10)],
    "D": [("B", 5), ("C", 8), ("E", 2)],
    "E": [("C", 10), ("D", 2)],
}


def main():
    print("Dijkstra's algorithm: shortest route from A to E\n")
    path, cost = dijkstra(GRAPH, "A", "E", trace=True)
    print("\nShortest path:", " -> ".join(path))
    print("Total cost   :", cost)

    print("\nShortest distance from A to every node:")
    for node in GRAPH:
        p, c = dijkstra(GRAPH, "A", node)
        print(f"  A -> {node}: cost {c:<3} path {' -> '.join(p)}")


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------
class TestDijkstra(unittest.TestCase):
    def test_case_study(self):
        self.assertEqual(dijkstra(GRAPH, "A", "E"), (["A", "C", "B", "D", "E"], 10))

    def test_all_distances_from_A(self):
        expected = {"A": 0, "B": 3, "C": 2, "D": 8, "E": 10}
        for node, cost in expected.items():
            self.assertEqual(dijkstra(GRAPH, "A", node)[1], cost)

    def test_source_equals_destination(self):
        self.assertEqual(dijkstra(GRAPH, "C", "C"), (["C"], 0))

    def test_unreachable(self):
        g = {"A": [("B", 1)], "B": [("A", 1)], "Z": []}
        self.assertEqual(dijkstra(g, "A", "Z"), (None, INF))

    def test_invalid_node(self):
        with self.assertRaises(KeyError):
            dijkstra(GRAPH, "A", "Q")

    def test_negative_weight_rejected(self):
        g = {"A": [("B", -1)], "B": []}
        with self.assertRaises(ValueError):
            dijkstra(g, "A", "B")

    def test_priority_queue_order(self):
        q = PriorityQueue()
        for c in [7, 3, 9, 1, 5, 3]:
            q.push(c, str(c))
        self.assertEqual([q.pop()[0] for _ in range(6)], [1, 3, 3, 5, 7, 9])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        main()
