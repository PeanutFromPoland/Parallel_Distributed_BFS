import os


def save_graph(graph, filepath):
    """
    Zapisuje graf (dict[int, list[int]]) do pliku tekstowego.

    Format:
        <liczba_wierzchołków> <liczba_krawędzi>
        <u> <v>
        ...
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    num_nodes = len(graph)
    num_edges = sum(len(neighbors) for neighbors in graph.values())
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{num_nodes} {num_edges}\n")
        for node in sorted(graph.keys()):
            for neighbor in graph[node]:
                f.write(f"{node} {neighbor}\n")


def load_graph(filepath):
    """
    Odczytuje graf (dict[int, list[int]]) z pliku tekstowego.

    Zwraca słownik sąsiedztwa z kluczami int.
    """
    graph = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split()
        num_nodes = int(header[0])

        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            u, v = int(parts[0]), int(parts[1])
            if u not in graph:
                graph[u] = []
            graph[u].append(v)

    # Upewnij się, że wierzchołki bez krawędzi wychodzących też są w grafie
    all_nodes = set(graph.keys())
    for neighbors in list(graph.values()):
        for n in neighbors:
            if n not in all_nodes:
                graph[n] = []
                all_nodes.add(n)

    return graph


def export_to_txt(graph, name = "graph"):
    count_of_nodes = len(graph)
    count_of_edges = sum(len(l) for l in graph.values())
    with open(f"{name}.txt", 'w', encoding='utf-8') as file:
        file.write(str(count_of_nodes) + ' ' + str(count_of_edges) + '\n')
        for node in graph:
            for neighbor in graph[node]:
                if len(node) > 1:
                    file.write(str("".join(str(node[i]) + ' ' for i in range(len(node)))) + ' ' + str("".join(str(neighbor[i]) + ' ' for i in range(len(neighbor)))) + '\n')
                else:
                    file.write(str(node) + ' ' + str(neighbor) + '\n')

def import_from_txt(name):
    if not name.endswith('.txt'):
        name += '.txt'

    with open(name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        graph = {}
        for line in lines[1:]:
            nums = line.split(' ')
            p0, p1 = nums[0:len(nums)//2 - 1], nums[len(nums)//2: -1]
            p0, p1 = tuple(int(i) for i in p0), tuple(int(i) for i in p1)
            print(p0, p1)
            if p0 not in graph:
                graph[p0] = []
            graph[p0].append(p1)
    return graph
