import random

from utils import draw_graph


def _is_connected(graph):
    if not graph:
        return True

    start = next(iter(graph))
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        stack.extend(neigh for neigh in graph[node] if neigh not in visited)

    return len(visited) == len(graph)


def generate_small_world_graph(
        size,
        k=4,
        rewiring_prob=0.1,
        consistency=True,
        start_val=1,
        unidirectional=True,
        seed=42,
):
    """
    Generuje graf small-world modelem Wattsa-Strogatza.

    Parametry:
    - size: liczba wierzchołków
    - k: liczba najbliższych sąsiadów każdego wierzchołka w grafie bazowym
         (musi być parzysta i mniejsza od size)
    - rewiring_prob: prawdopodobieństwo przepięcia krawędzi
    - consistency: jeśli True, podejmuje próby uzyskania spójnego grafu
    - start_val: numer pierwszego wierzchołka
    - unidirectional: zachowane dla zgodności z Twoim interfejsem;
                      gdy True, dodaje krawędź w obie strony
    - seed: ziarno losowości
    """
    if size <= 0:
        return {}

    if size == 1:
        return {start_val: []}

    if k >= size:
        raise ValueError("k musi być mniejsze od size")
    if k % 2 != 0:
        raise ValueError("k musi być parzyste")

    rng = random.Random(seed)

    def build_graph():
        nodes = list(range(start_val, start_val + size))
        graph = {node: [] for node in nodes}
        edges = set()

        def add_edge(u, v):
            if u == v:
                return
            edge = (min(u, v), max(u, v))
            if edge in edges:
                return
            edges.add(edge)
            graph[u].append(v)
            if unidirectional:
                graph[v].append(u)

        def remove_edge(u, v):
            edge = (min(u, v), max(u, v))
            if edge not in edges:
                return
            edges.remove(edge)
            if v in graph[u]:
                graph[u].remove(v)
            if unidirectional and u in graph[v]:
                graph[v].remove(u)

        # 1. Tworzymy pierścień regularny:
        # każdy wierzchołek łączy się z k/2 sąsiadami po obu stronach
        half = k // 2
        for i in range(size):
            u = nodes[i]
            for offset in range(1, half + 1):
                v = nodes[(i + offset) % size]
                add_edge(u, v)

        # 2. Przepinamy część krawędzi
        for i in range(size):
            u = nodes[i]
            for offset in range(1, half + 1):
                v = nodes[(i + offset) % size]

                if rng.random() < rewiring_prob:
                    # usuwamy starą krawędź
                    remove_edge(u, v)

                    # szukamy nowego celu
                    possible = [
                        x for x in nodes
                        if x != u and (min(u, x), max(u, x)) not in edges
                    ]

                    # gdyby nie było możliwego wyboru, przywracamy starą krawędź
                    if not possible:
                        add_edge(u, v)
                        continue

                    new_v = rng.choice(possible)
                    add_edge(u, new_v)

        return graph

    if not consistency:
        return build_graph()

    # kilka prób, żeby zachować spójność
    for attempt in range(20):
        graph = build_graph()
        if _is_connected(graph):
            return graph
        rng.seed(seed + attempt + 1)

    return graph

