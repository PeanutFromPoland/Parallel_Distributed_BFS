import os
import itertools


SIZES = ["small", "medium", "large"]
GRAPH_TYPES = ["random", "bb", "small_world", "grid"]


def load_graph(filepath):
    graph = {}
    with open(filepath, "r", encoding="utf-8") as f:
        _header = f.readline()

        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            u, v = int(parts[0]), int(parts[1])
            if u not in graph:
                graph[u] = []
            graph[u].append(v)

    all_nodes = set(graph.keys())
    for neighbors in list(graph.values()):
        for n in neighbors:
            if n not in all_nodes:
                graph[n] = []
                all_nodes.add(n)

    return graph


def load_expected(filepath):
    components = []
    current_start = None
    current_dist = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("COMPONENT"):
                if current_start is not None:
                    components.append((current_start, current_dist))
                current_start = int(line.split()[1])
                current_dist = {}
            else:
                parts = line.split()
                if len(parts) >= 2:
                    node, dist = int(parts[0]), int(parts[1])
                    current_dist[node] = dist

    if current_start is not None:
        components.append((current_start, current_dist))

    return components


def collect_graph_files(base_dir):
    connected_dir = os.path.join(base_dir, "connected")
    inconsistent_dir = os.path.join(base_dir, "inconsistent")
    files = []

    for graph_type in GRAPH_TYPES:
        for size_name in SIZES:
            graph_path = os.path.join(
                connected_dir, graph_type, f"{size_name}.txt"
            )
            expected_path = os.path.join(
                connected_dir, graph_type, f"{size_name}_expected.txt"
            )
            if os.path.exists(graph_path) and os.path.exists(expected_path):
                label = f"[Spójny] {graph_type}/{size_name}"
                files.append((graph_path, expected_path, label))

    combinations = list(itertools.product(GRAPH_TYPES, repeat=2))
    for type_a, type_b in combinations:
        combo_name = f"{type_a}_{type_b}"
        for size_name in SIZES:
            graph_path = os.path.join(
                inconsistent_dir, size_name, f"{combo_name}.txt"
            )
            expected_path = os.path.join(
                inconsistent_dir, size_name, f"{combo_name}_expected.txt"
            )
            if os.path.exists(graph_path) and os.path.exists(expected_path):
                label = f"[Niespójny] {combo_name}/{size_name}"
                files.append((graph_path, expected_path, label))

    return files
