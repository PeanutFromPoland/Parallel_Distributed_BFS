import random

from utils import draw_graph


def generate_random_graph(size, threshold=0.5, consistency=True, start_val=1, unidirectional=True, seed=42):
    nodes = list(range(start_val, start_val + size))
    graph = {node: [] for node in nodes}

    edges = set()
    max_edges = size * (size - 1) // 2
    target_edges = max(size - 1, int(max_edges * threshold))

    # Dla dużych grafów ograniczamy liczbę krawędzi, aby średni stopień
    # wierzchołka nie przekraczał 30.  Bez tego ograniczenia threshold=0.3
    # przy 50 000 wierzchołków oznaczałby ~375 mln krawędzi (~50+ GB RAM).
    if size > 1000:
        max_reasonable = size * 15   # avg degree ≤ 30
        target_edges = min(target_edges, max_reasonable)

    def add_edge(u, v):
        if u != v and (u, v) not in edges:
            edges.add((min(u, v), max(u, v)))
            graph[u].append(v)
            graph[v].append(u) if unidirectional else None

    random.seed(seed)
    if consistency and size > 1:
        shuffled = nodes[:]
        random.shuffle(shuffled)
        visited = [shuffled[0]]
        for node in shuffled[1:]:
            neighbor = random.choice(visited)
            add_edge(node, neighbor)
            visited.append(node)

    if target_edges > len(edges):
        if max_edges <= 500_000:
            # Mały graf – materializacja listy możliwych krawędzi (oryginał)
            all_possible = [
                (u, v) for u in nodes for v in nodes if u < v and (u, v) not in edges
            ]
            random.shuffle(all_possible)
            for u, v in all_possible:
                if len(edges) >= target_edges:
                    break
                add_edge(u, v)
        else:
            # Duży graf – losowe próbkowanie krawędzi (O(1) pamięci dodatkowej)
            node_min = nodes[0]
            node_max = nodes[-1]
            max_attempts = (target_edges - len(edges)) * 10
            attempts = 0
            while len(edges) < target_edges and attempts < max_attempts:
                u = random.randint(node_min, node_max)
                v = random.randint(node_min, node_max)
                if u != v:
                    add_edge(u, v)
                attempts += 1

    return graph


draw_graph(generate_random_graph(10))