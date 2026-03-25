import random

from utils import draw_graph


def generate_random_graph(size, threshold=0.5, consistency=True, start_val=1, unidirectional=True):
    nodes = list(range(start_val, start_val + size))
    graph = {node: [] for node in nodes}

    edges = set()
    max_edges = size * (size - 1) // 2
    target_edges = max(size - 1, int(max_edges * threshold))

    def add_edge(u, v):
        if u != v and (u, v) not in edges:
            edges.add((min(u, v), max(u, v)))
            graph[u].append(v)
            graph[v].append(u) if unidirectional else None

    if consistency and size > 1:
        shuffled = nodes[:]
        random.shuffle(shuffled)
        visited = [shuffled[0]]
        for node in shuffled[1:]:
            neighbor = random.choice(visited)
            add_edge(node, neighbor)
            visited.append(node)

    if target_edges > len(edges):
        all_possible = [
            (u, v) for u in nodes for v in nodes if u < v and (u, v) not in edges
        ]
        random.shuffle(all_possible)
        for u, v in all_possible:
            if len(edges) >= target_edges:
                break
            add_edge(u, v)

    return graph


draw_graph(generate_random_graph(10))