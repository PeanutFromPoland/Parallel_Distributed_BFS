"""
Generate benchmark graphs and expected BFS results.

Default run generates connected and inconsistent graphs in all sizes and
density profiles:
    python generate_graphs.py

Useful narrower runs:
    python generate_graphs.py --sizes huge --types bb grid
    python generate_graphs.py --sizes medium large --densities sparse dense
    python generate_graphs.py --sizes small --densities sparse --instances 5
    python generate_graphs.py --only inconsistent --parts few many
"""

import argparse
import itertools
import math
import os
import random
import time
from collections import deque


SIZES = {
    "tiny": 50,
    "small": 500,
    "medium": 5_000,
    "large": 50_000,
    "huge": 500_000,
}

DEFAULT_SIZE_NAMES = tuple(SIZES.keys())

DENSITIES = {
    "sparse": 0.1,
    "medium": 0.3,
    "dense": 0.5,
}
DEFAULT_DENSITY_NAMES = tuple(DENSITIES.keys())

PART_COUNTS = {
    "few": 5,
    "medium": 50,
    "many": 500,
}
DEFAULT_PART_COUNT_NAMES = tuple(PART_COUNTS.keys())

GRAPH_TYPES = ["random", "bb", "small_world", "grid"]

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs")
CONNECTED_DIR = os.path.join(BASE_DIR, "connected")
INCONSISTENT_DIR = os.path.join(BASE_DIR, "inconsistent")

SEED = 42
DEFAULT_INSTANCES = 5


def _expand_names(values, allowed, default_names, label):
    names = []
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if not item:
                continue
            if item == "all":
                return list(allowed)
            if item == "default":
                names.extend(default_names)
                continue
            if item not in allowed:
                valid = ", ".join(allowed)
                raise ValueError(f"Unknown {label}: {item}. Available: {valid}")
            names.append(item)

    result = []
    seen = set()
    for name in names:
        if name not in seen:
            result.append(name)
            seen.add(name)
    return result


def _factor_pair_near_square(size):
    width = int(math.sqrt(size))
    while width > 1 and size % width != 0:
        width -= 1
    return width, size // width


def _positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def _instance_seed(base_seed, instance_number):
    return base_seed + (instance_number - 1) * 1_000_003


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate connected and disconnected BFS benchmark graphs.",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        default=list(DEFAULT_SIZE_NAMES),
        help=(
            "Size names to generate: tiny, small, medium, large, huge, "
            "default, all."
        ),
    )
    parser.add_argument(
        "--types",
        nargs="+",
        default=list(GRAPH_TYPES),
        help="Graph types to generate: random, bb, small_world, grid, all.",
    )
    parser.add_argument(
        "--densities",
        nargs="+",
        default=list(DEFAULT_DENSITY_NAMES),
        help="Density profiles: sparse, medium, dense, default, all. Ignored for grid.",
    )
    parser.add_argument(
        "--parts",
        nargs="+",
        default=list(DEFAULT_PART_COUNT_NAMES),
        help=(
            "Disconnected graph part counts: few, medium, many, default, all. "
            "Ignored for connected graphs."
        ),
    )
    parser.add_argument(
        "--only",
        choices=("all", "connected", "inconsistent"),
        default="all",
        help="Limit generation to connected or inconsistent graphs.",
    )
    parser.add_argument(
        "--instances",
        type=_positive_int,
        default=DEFAULT_INSTANCES,
        help=(
            "Number of graph instances per configuration "
            f"(default: {DEFAULT_INSTANCES})."
        ),
    )
    parser.add_argument(
        "--skip-expected",
        action="store_true",
        help="Write graph files only, without expected BFS result files.",
    )
    return parser.parse_args()


# =====================================================================
#  I/O
# =====================================================================
def save_graph(graph, filepath):
    """Save graph (dict[int, list[int]]) to a text file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    num_edges = sum(len(n) for n in graph.values())
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{len(graph)} {num_edges}\n")
        for node in sorted(graph.keys()):
            for neighbor in graph[node]:
                f.write(f"{node} {neighbor}\n")


# =====================================================================
#  Expected BFS results
# =====================================================================
def compute_bfs_expected(graph):
    """
    Compute expected BFS results for every connected component.

    Returns:
        [(start_node, [(node, dist), ...]), ...]
    """
    visited_global = set()
    components = []

    for start in sorted(graph.keys()):
        if start in visited_global:
            continue

        dist = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in dist:
                    dist[neighbor] = dist[node] + 1
                    queue.append(neighbor)

        visited_global.update(dist.keys())
        components.append((start, sorted(dist.items())))

    return components


def save_expected(components, filepath):
    """Save expected BFS results to a text file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for start, pairs in components:
            f.write(f"COMPONENT {start}\n")
            for node, dist in pairs:
                f.write(f"{node} {dist}\n")


def save_instance_count(output_dir, size_name, instances):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{size_name}_instances.txt")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(f"{instances}\n")


# =====================================================================
#  Connected graph generation
# =====================================================================
def _density_degree(density):
    """Map density profile values 0.1/0.3/0.5 to 1/2/4 attachments."""
    return max(1, round(density * 8))


def make_connected_graph(graph_type, size, seed_val, density=None):
    """Generate a connected graph with integer vertex ids starting at 1."""
    from generators.random import generate_random_graph
    from generators.bb import generate_bb_graph
    from generators.small_world import generate_small_world_graph
    from generators.grid import generate_grid_graph

    if graph_type == "random":
        if density is None:
            raise ValueError("Random graph generation requires a density profile.")
        return generate_random_graph(
            size=size,
            threshold=density,
            consistency=True,
            start_val=1,
            unidirectional=True,
            seed=seed_val,
        )

    if graph_type == "bb":
        if density is None:
            raise ValueError("BB graph generation requires a density profile.")
        m = min(_density_degree(density), size - 1)
        random.seed(seed_val)
        return generate_bb_graph(
            size=size,
            m=m,
            start_val=1,
            unidirectional=True,
        )

    if graph_type == "small_world":
        if density is None:
            raise ValueError("Small-world graph generation requires a density profile.")
        k = min(2 * _density_degree(density), size - 1)
        if k % 2 != 0:
            k = max(2, k - 1)
        return generate_small_world_graph(
            size=size,
            k=k,
            rewiring_prob=0.1,
            consistency=True,
            start_val=1,
            unidirectional=True,
            seed=seed_val,
        )

    if graph_type == "grid":
        width, height = _factor_pair_near_square(size)
        graph = generate_grid_graph(dimensions=(width, height))
        old_keys = sorted(graph.keys())
        mapping = {key: i + 1 for i, key in enumerate(old_keys)}
        return {mapping[key]: [mapping[n] for n in neighbors] for key, neighbors in graph.items()}

    raise ValueError(f"Unknown graph type: {graph_type}")


# =====================================================================
#  Main generation logic
# =====================================================================
def generate_connected(
    sizes,
    graph_types,
    densities,
    write_expected=True,
    instances=DEFAULT_INSTANCES,
):
    count = 0
    for graph_type in graph_types:
        graph_densities = [(None, None)] if graph_type == "grid" else densities.items()
        for density_name, density in graph_densities:
            for size_name, size in sizes.items():
                if density_name is None:
                    output_dir = os.path.join(CONNECTED_DIR, graph_type)
                    variant_name = f"{graph_type}/{size_name}"
                else:
                    output_dir = os.path.join(CONNECTED_DIR, graph_type, density_name)
                    variant_name = f"{graph_type}/{density_name}/{size_name}"

                save_instance_count(output_dir, size_name, instances)
                for instance_number in range(1, instances + 1):
                    stem = f"{size_name}_{instance_number:03d}"
                    graph_path = os.path.join(output_dir, f"{stem}.txt")
                    expected_path = os.path.join(output_dir, f"{stem}_expected.txt")
                    label = (
                        f"{variant_name} #{instance_number:03d} "
                        f"({size} vertices)"
                    )

                    print(f"  {label} ...", end=" ", flush=True)
                    t0 = time.perf_counter()

                    graph = make_connected_graph(
                        graph_type,
                        size,
                        _instance_seed(SEED, instance_number),
                        density,
                    )
                    save_graph(graph, graph_path)

                    if write_expected:
                        expected = compute_bfs_expected(graph)
                        save_expected(expected, expected_path)

                    elapsed = time.perf_counter() - t0
                    edge_count = (
                        sum(len(neighbors) for neighbors in graph.values()) // 2
                    )
                    avg_degree = 2 * edge_count / len(graph) if graph else 0
                    print(
                        f"OK ({len(graph)} vertices, {edge_count} edges, "
                        f"avg degree {avg_degree:.2f}, {elapsed:.2f}s)"
                    )
                    count += 1

    return count


def generate_inconsistent(
    sizes,
    graph_types,
    densities,
    part_counts,
    write_expected=True,
    instances=DEFAULT_INSTANCES,
):
    from generators.inconsistent import generate_inconsistent_graph

    combinations = list(itertools.product(graph_types, repeat=2))
    count = 0

    for idx, (type_a, type_b) in enumerate(combinations, 1):
        combo_name = f"{type_a}_{type_b}"
        part_types = [type_a, type_b]
        graph_densities = [(None, 0.3)] if all(
            graph_type == "grid" for graph_type in part_types
        ) else densities.items()

        for part_name, parts_count in part_counts.items():
            for density_name, density in graph_densities:
                for size_name, size in sizes.items():
                    if size < parts_count * 2:
                        print(
                            f"  SKIP {combo_name}/{part_name}/{size_name}: "
                            f"{size} vertices cannot form {parts_count} "
                            f"non-empty parts with at least 2 vertices"
                        )
                        continue

                    output_dir = os.path.join(
                        INCONSISTENT_DIR,
                        combo_name,
                        part_name,
                    )
                    variant_name = f"{combo_name}/{part_name}"
                    if density_name is not None:
                        output_dir = os.path.join(output_dir, density_name)
                        variant_name = f"{variant_name}/{density_name}"
                    variant_name = f"{variant_name}/{size_name}"

                    save_instance_count(output_dir, size_name, instances)
                    for instance_number in range(1, instances + 1):
                        stem = f"{size_name}_{instance_number:03d}"
                        graph_path = os.path.join(output_dir, f"{stem}.txt")
                        expected_path = os.path.join(
                            output_dir,
                            f"{stem}_expected.txt",
                        )
                        label = (
                            f"{variant_name} #{instance_number:03d} "
                            f"({size} vertices, {parts_count} parts)"
                        )

                        print(f"  {label} ...", end=" ", flush=True)
                        t0 = time.perf_counter()

                        graph = generate_inconsistent_graph(
                            total_vertices=size,
                            parts_count=parts_count,
                            part_types=part_types,
                            seed=_instance_seed(
                                SEED + idx * 1000 + parts_count,
                                instance_number,
                            ),
                            density=density,
                        )
                        save_graph(graph, graph_path)

                        if write_expected:
                            expected = compute_bfs_expected(graph)
                            save_expected(expected, expected_path)

                        elapsed = time.perf_counter() - t0
                        edge_count = (
                            sum(len(neighbors) for neighbors in graph.values()) // 2
                        )
                        avg_degree = 2 * edge_count / len(graph) if graph else 0
                        print(
                            f"OK ({len(graph)} vertices, {edge_count} edges, "
                            f"avg degree {avg_degree:.2f}, {elapsed:.2f}s)"
                        )
                        count += 1

    return count


# =====================================================================
#  MAIN
# =====================================================================
def main():
    args = parse_args()
    size_names = _expand_names(args.sizes, SIZES.keys(), DEFAULT_SIZE_NAMES, "size")
    graph_types = _expand_names(args.types, GRAPH_TYPES, GRAPH_TYPES, "graph type")
    density_names = _expand_names(
        args.densities,
        DENSITIES.keys(),
        DEFAULT_DENSITY_NAMES,
        "density",
    )
    part_count_names = _expand_names(
        args.parts,
        PART_COUNTS.keys(),
        DEFAULT_PART_COUNT_NAMES,
        "part count",
    )
    selected_sizes = {name: SIZES[name] for name in size_names}
    selected_densities = {name: DENSITIES[name] for name in density_names}
    selected_part_counts = {
        name: PART_COUNTS[name]
        for name in part_count_names
    }
    write_expected = not args.skip_expected

    print("=" * 72)
    print("  GRAPH GENERATION + EXPECTED BFS RESULTS")
    print("=" * 72)
    print(f"  Sizes: {', '.join(f'{name}={SIZES[name]}' for name in size_names)}")
    print(f"  Types: {', '.join(graph_types)}")
    print(
        "  Densities: "
        + ", ".join(f"{name}={DENSITIES[name]}" for name in density_names)
        + " (grid: single variant)"
    )
    print(
        "  Disconnected parts: "
        + ", ".join(
            f"{name}={PART_COUNTS[name]}"
            for name in part_count_names
        )
    )
    print(f"  Instances per configuration: {args.instances}")
    print(f"  Expected BFS files: {'yes' if write_expected else 'no'}")

    n1 = 0
    n2 = 0

    if args.only in ("all", "connected"):
        variants_per_size = sum(
            1 if graph_type == "grid" else len(selected_densities)
            for graph_type in graph_types
        )
        print(
            f"\n--- Connected graphs "
            f"({variants_per_size} variants x {len(selected_sizes)} sizes "
            f"x {args.instances} instances) ---"
        )
        n1 = generate_connected(
            selected_sizes,
            graph_types,
            selected_densities,
            write_expected,
            args.instances,
        )
        print(f"  [OK] {n1} connected graphs\n")

    if args.only in ("all", "inconsistent"):
        combinations = list(itertools.product(graph_types, repeat=2))
        configuration_count = sum(
            1 if type_a == type_b == "grid" else len(selected_densities)
            for type_a, type_b in combinations
            for parts_count in selected_part_counts.values()
            for size in selected_sizes.values()
            if size >= parts_count * 2
        )
        print(
            f"--- Inconsistent graphs "
            f"({configuration_count} valid configurations "
            f"x {args.instances} instances) ---"
        )
        n2 = generate_inconsistent(
            selected_sizes,
            graph_types,
            selected_densities,
            selected_part_counts,
            write_expected,
            args.instances,
        )
        print(f"  [OK] {n2} inconsistent graphs\n")

    print(f"Generated {n1 + n2} graph files.")
    print(f"Directory: {BASE_DIR}")


if __name__ == "__main__":
    main()
