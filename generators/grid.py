from Parallel_Distributed_BFS.utils.visualization import draw_graph


def generate_grid_graph(size):
    graph = {}
    verticles = [(i, j) for i in range(-size, size+1) for j in range(-size, size+1)]
    for p in verticles:
        if p not in graph:
            graph[p] = []
        graph[p].append((p[0] + 1, p[1])) if p[0] + 1 <= size else None
        graph[p].append((p[0], p[1] + 1)) if p[1] + 1 <= size else None
        graph[p].append((p[0] - 1, p[1])) if abs(p[0] - 1) <= size else None
        graph[p].append((p[0], p[1] - 1)) if abs(p[1] - 1) <= size else None

    print(graph)
    return graph


draw_graph(generate_grid_graph(3))