import itertools
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

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../graphs")
CONNECTED_DIR = os.path.join(BASE_DIR, "connected")
INCONSISTENT_DIR = os.path.join(BASE_DIR, "inconsistent")
SIZES = {
    "tiny": 50,
    "small": 500,
    "medium": 5_000,
    "large": 50_000,
    "huge": 500_000,
}
DENSITIES = ["sparse", "medium", "dense"]
PART_COUNTS = {
    "few": 5,
    "medium": 50,
    "many": 500,
}
GRAPH_TYPES = ["random", "bb", "small_world", "grid"]


def _graph_has_size(filepath, expected_size):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return int(file.readline().split()[0]) == expected_size
    except (OSError, ValueError, IndexError):
        return False


def _iter_graph_instances(graph_dir, size_name, expected_size):
    if not os.path.isdir(graph_dir):
        return

    manifest_path = os.path.join(graph_dir, f"{size_name}_instances.txt")
    try:
        with open(manifest_path, "r", encoding="utf-8") as file:
            instance_count = int(file.readline().strip())
        if instance_count < 1:
            raise ValueError
        filenames = [
            f"{size_name}_{instance_number:03d}.txt"
            for instance_number in range(1, instance_count + 1)
        ]
    except (OSError, ValueError):
        prefix = f"{size_name}_"
        filenames = [
            filename
            for filename in sorted(os.listdir(graph_dir))
            if filename.startswith(prefix)
            and filename.endswith(".txt")
            and not filename.endswith("_expected.txt")
        ]

    prefix = f"{size_name}_"
    for filename in filenames:
        if not filename.startswith(prefix) or not filename.endswith(".txt"):
            continue
        if filename.endswith("_expected.txt"):
            continue

        instance_id = filename[len(prefix):-4]
        if not instance_id.isdigit():
            continue

        graph_path = os.path.join(graph_dir, filename)
        expected_path = os.path.join(
            graph_dir,
            f"{size_name}_{instance_id}_expected.txt",
        )
        if (
            os.path.exists(expected_path)
            and _graph_has_size(graph_path, expected_size)
        ):
            yield graph_path, expected_path, instance_id


def collect_graph_files():
    """Zbiera ścieżki do grafów testowych."""
    files = []
    for graph_type in GRAPH_TYPES:
        density_names = [None] if graph_type == "grid" else DENSITIES
        for density_name in density_names:
            for size_name, expected_size in SIZES.items():
                graph_dir = os.path.join(CONNECTED_DIR, graph_type)
                if density_name is not None:
                    graph_dir = os.path.join(graph_dir, density_name)
                for graph_path, expected_path, instance_id in _iter_graph_instances(
                    graph_dir,
                    size_name,
                    expected_size,
                ):
                    variant = graph_type
                    if density_name is not None:
                        variant = f"{variant}/{density_name}"
                    label = f"[Spójny] {variant}/{size_name} #{instance_id}"
                    files.append((graph_path, expected_path, label))

    combinations = list(itertools.product(GRAPH_TYPES, repeat=2))
    for type_a, type_b in combinations:
        combo_name = f"{type_a}_{type_b}"
        density_names = [None] if type_a == type_b == "grid" else DENSITIES
        for part_name, parts_count in PART_COUNTS.items():
            for density_name in density_names:
                for size_name, expected_size in SIZES.items():
                    if expected_size < parts_count * 2:
                        continue
                    graph_dir = os.path.join(
                        INCONSISTENT_DIR,
                        combo_name,
                        part_name,
                    )
                    if density_name is not None:
                        graph_dir = os.path.join(graph_dir, density_name)
                    for graph_path, expected_path, instance_id in _iter_graph_instances(
                        graph_dir,
                        size_name,
                        expected_size,
                    ):
                        variant = f"{combo_name}/{part_name}"
                        if density_name is not None:
                            variant = f"{variant}/{density_name}"
                        label = (
                            f"[Niespójny] {variant}/{size_name} "
                            f"#{instance_id}"
                        )
                        files.append((graph_path, expected_path, label))
    return files



def load_expected(filepath):
    """Odczytuje oczekiwane wyniki BFS."""
    components = []
    current_start = None
    current_dist = {}
    with open(filepath, 'r', encoding='utf-8') as f:
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

