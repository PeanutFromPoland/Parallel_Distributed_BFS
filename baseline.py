import time
from collections import deque

from generators import generate_grid_graph
from utils import draw_graph, import_from_txt, export_to_txt


def bfs(graph, start):
    time_start = time.time()
    queue = deque([start])
    visited = {start}
    while queue:
        node = queue.popleft()
        print(node, graph[node])
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

        # print(node, queue, visited)
    print(f"Graph processed in: {(time.time() - time_start):.4f}")

graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F', 'G'],
    'D': ['E'],
    'E': ['F'],
    'F': ['G'],
    'G': ['H'],
    'H': ['I'],
    'I': []
}
import_from_txt("graph.txt")

# draw_graph(generate_grid_graph(3))
# bfs(generate_grid_graph(3), (0, 0))