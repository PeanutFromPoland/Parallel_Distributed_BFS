import random


class _FenwickTree:
    """Prefix tree for fast weighted sampling."""

    def __init__(self, size):
        self.size = size
        self.tree = [0.0] * (size + 1)

    def add(self, index, delta):
        index += 1
        while index <= self.size:
            self.tree[index] += delta
            index += index & -index

    def total(self):
        return self.prefix_sum(self.size - 1)

    def prefix_sum(self, index):
        index += 1
        result = 0.0
        while index > 0:
            result += self.tree[index]
            index -= index & -index
        return result

    def find_by_prefix(self, target):
        idx = 0
        bit = 1 << (self.size.bit_length() - 1)
        while bit:
            next_idx = idx + bit
            if next_idx <= self.size and self.tree[next_idx] < target:
                target -= self.tree[next_idx]
                idx = next_idx
            bit >>= 1
        return idx


def generate_bb_graph(size, m=2, fitness_range=(0.1, 1.0), start_val=1, unidirectional=True):
    """
    Generate a Bianconi-Barabasi graph.

    The original implementation used random.choices over a growing list of
    weights for every new vertex. That makes generation effectively O(n^2).
    This version keeps the attachment weights in a Fenwick tree, so each
    weighted sample and weight update costs O(log n), which is practical for
    hundreds of thousands of vertices.
    """
    if size < 1:
        raise ValueError("'size' must be >= 1.")
    if m < 1:
        raise ValueError("'m' must be >= 1.")
    if m >= size:
        raise ValueError("'m' must be smaller than 'size'.")

    nodes = list(range(start_val, start_val + size))
    graph = {node: [] for node in nodes}
    fitness = [random.uniform(*fitness_range) for _ in nodes]
    degrees = [0] * size

    initial_count = m + 1
    for i in range(initial_count):
        u = nodes[i]
        for j in range(i + 1, initial_count):
            v = nodes[j]
            graph[u].append(v)
            degrees[i] += 1
            if unidirectional:
                graph[v].append(u)
                degrees[j] += 1

    weights = [0.0] * size
    tree = _FenwickTree(size)

    def set_weight(index, value):
        delta = value - weights[index]
        if delta:
            weights[index] = value
            tree.add(index, delta)

    existing_count = initial_count
    for idx in range(existing_count):
        set_weight(idx, fitness[idx] * max(degrees[idx], 1))

    for new_idx in range(initial_count, size):
        new_node = nodes[new_idx]
        targets = []
        removed_weights = []

        for _ in range(min(m, existing_count)):
            total_weight = tree.total()
            if total_weight <= 0:
                break

            target_idx = tree.find_by_prefix(random.random() * total_weight)
            targets.append(target_idx)
            removed_weights.append((target_idx, weights[target_idx]))
            set_weight(target_idx, 0.0)

        for target_idx, old_weight in removed_weights:
            set_weight(target_idx, old_weight)

        for target_idx in targets:
            target = nodes[target_idx]
            graph[new_node].append(target)
            degrees[new_idx] += 1
            if unidirectional:
                graph[target].append(new_node)
                degrees[target_idx] += 1
            set_weight(target_idx, fitness[target_idx] * max(degrees[target_idx], 1))

        set_weight(new_idx, fitness[new_idx] * max(degrees[new_idx], 1))
        existing_count += 1

    return graph


if __name__ == "__main__":
    from utils import draw_graph

    draw_graph(generate_bb_graph(10, m=3, fitness_range=(0.2, 0.6), unidirectional=True))
