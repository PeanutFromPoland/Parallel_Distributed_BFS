import time
from collections import deque

from utils import draw_graph


def bfs(graph, start = None):
    time_start = time.time()
    unvisited = sorted({key for key in graph.keys()}, key = lambda x: x[0])

    while unvisited:
        start = unvisited[0]
        unvisited.remove(unvisited[0])
        queue = deque([start])
        while queue:
            node = queue.popleft()
            print(node)
            for neighbor in graph[node]:
                if neighbor in unvisited:
                    unvisited.remove(neighbor)
                    queue.append(neighbor)

    print(f"Graph processed in: {(time.time() - time_start):.4f}")

graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E', 'F'],
    'C': ['A'],
    'D': ['B'],
    'E': ['B'],
    'F': ['B'],
    'G': ['H', 'I'],
    'H': ['G'],
    'I': ['G']
}
draw_graph(graph)
bfs(graph)