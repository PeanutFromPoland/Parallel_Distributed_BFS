import os
import itertools


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


def collect_graph_files(base_dir):
    connected_dir = os.path.join(base_dir, "connected")
    inconsistent_dir = os.path.join(base_dir, "inconsistent")
    files = []

    for graph_type in GRAPH_TYPES:
        density_names = [None] if graph_type == "grid" else DENSITIES
        for density_name in density_names:
            for size_name, expected_size in SIZES.items():
                graph_dir = os.path.join(connected_dir, graph_type)
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
                        inconsistent_dir,
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
