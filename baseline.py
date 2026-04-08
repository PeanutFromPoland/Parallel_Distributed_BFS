import time
from collections import deque



def bfs(graph, start):
    """
    BFS od 'start'. Zwraca dict {node: distance}.
    Sąsiadów sortujemy, żeby wynik był deterministyczny.
    """
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in sorted(graph[node]):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


def bfs_all_components(graph):
    """
    BFS po wszystkich komponentach spójności
    (zaczynając od wierzchołka o najmniejszym numerze w każdym).

    Zwraca:
        components: [(start, {node: dist}), ...]
        total_time: łączny czas BFS (sekundy)
    """
    visited_global = set()
    components = []

    t0 = time.perf_counter()

    for start in sorted(graph.keys()):
        if start in visited_global:
            continue
        dist = bfs(graph, start)
        visited_global.update(dist.keys())
        components.append((start, dist))

    total_time = time.perf_counter() - t0
    return components, total_time
