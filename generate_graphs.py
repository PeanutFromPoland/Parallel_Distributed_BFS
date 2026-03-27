"""
Jednorazowa generacja wszystkich grafów (spójnych i niespójnych)
wraz z oczekiwanymi wynikami BFS.

Uruchomienie:
    python generate_graphs.py

Struktura wyjściowa:
    graphs/
    ├── connected/
    │   ├── random/   small.txt, small_expected.txt, medium.txt, ...
    │   ├── bb/
    │   ├── small_world/
    │   └── grid/
    └── inconsistent/
        ├── small/    random_random.txt, random_random_expected.txt, ...
        ├── medium/
        └── large/
"""

import os
import sys
import time
import random
import math
import itertools
from collections import deque

# ── Konfiguracja ─────────────────────────────────────────────────────
SIZES = {
    "small":  50,
    "medium": 500,
    "large":  5_000,
}

GRAPH_TYPES = ["random", "bb", "small_world", "grid"]

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs")
CONNECTED_DIR = os.path.join(BASE_DIR, "connected")
INCONSISTENT_DIR = os.path.join(BASE_DIR, "inconsistent")

SEED = 42


# =====================================================================
#  I/O
# =====================================================================
def save_graph(graph, filepath):
    """Zapisuje graf (dict[int, list[int]]) do pliku tekstowego."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    num_edges = sum(len(n) for n in graph.values())
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{len(graph)} {num_edges}\n")
        for node in sorted(graph.keys()):
            for neighbor in graph[node]:
                f.write(f"{node} {neighbor}\n")


# =====================================================================
#  Generacja oczekiwanych wyników BFS
# =====================================================================
def compute_bfs_expected(graph):
    """
    Oblicza oczekiwane wyniki BFS: dla każdego komponentu spójności
    (od wierzchołka o najmniejszym numerze) zwraca listę (node, dist).

    Zwraca listę komponentów:
        [(start_node, [(node, dist), ...]), ...]
    """
    visited_global = set()
    components = []

    for start in sorted(graph.keys()):
        if start in visited_global:
            continue

        # BFS od start
        dist = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in sorted(graph[node]):  # sortowanie → determinizm
                if neighbor not in dist:
                    dist[neighbor] = dist[node] + 1
                    queue.append(neighbor)

        visited_global.update(dist.keys())
        pairs = sorted(dist.items())
        components.append((start, pairs))

    return components


def save_expected(components, filepath):
    """Zapisuje oczekiwane wyniki BFS do pliku."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for start, pairs in components:
            f.write(f"COMPONENT {start}\n")
            for node, dist in pairs:
                f.write(f"{node} {dist}\n")


# =====================================================================
#  Generatory grafów spójnych
# =====================================================================
def make_connected_graph(graph_type, size, seed_val):
    """Generuje graf spójny wskazanego typu z kluczami int od 1."""
    from generators.random import generate_random_graph
    from generators.bb import generate_bb_graph
    from generators.small_world import generate_small_world_graph
    from generators.grid import generate_grid_graph

    if graph_type == "random":
        return generate_random_graph(
            size=size, threshold=0.3, consistency=True,
            start_val=1, unidirectional=True, seed=seed_val,
        )
    elif graph_type == "bb":
        m = min(2, size - 1)
        random.seed(seed_val)
        return generate_bb_graph(
            size=size, m=m, start_val=1, unidirectional=True,
        )
    elif graph_type == "small_world":
        k = min(4, size - 1)
        if k % 2 != 0:
            k = max(2, k - 1)
        return generate_small_world_graph(
            size=size, k=k, rewiring_prob=0.1,
            consistency=True, start_val=1,
            unidirectional=True, seed=seed_val,
        )
    elif graph_type == "grid":
        w = max(1, int(math.sqrt(size)))
        h = max(1, size // w)
        while w * h < size:
            h += 1
        graph = generate_grid_graph(dimensions=(w, h))
        # tuple → int
        old_keys = sorted(graph.keys())
        mapping = {k: i + 1 for i, k in enumerate(old_keys)}
        return {mapping[k]: [mapping[n] for n in ns] for k, ns in graph.items()}
    else:
        raise ValueError(f"Nieznany typ: {graph_type}")


# =====================================================================
#  Główna logika generacji
# =====================================================================
def generate_connected():
    """Generuje 12 grafów spójnych + expected."""
    count = 0
    for graph_type in GRAPH_TYPES:
        for size_name, size in SIZES.items():
            graph_path = os.path.join(CONNECTED_DIR, graph_type, f"{size_name}.txt")
            expected_path = os.path.join(CONNECTED_DIR, graph_type, f"{size_name}_expected.txt")
            label = f"{graph_type}/{size_name} ({size} wierz.)"

            print(f"  {label} ...", end=" ", flush=True)
            t0 = time.perf_counter()

            graph = make_connected_graph(graph_type, size, SEED)
            save_graph(graph, graph_path)

            expected = compute_bfs_expected(graph)
            save_expected(expected, expected_path)

            elapsed = time.perf_counter() - t0
            print(f"OK ({len(graph)} wierz., {elapsed:.2f}s)")
            count += 1

    return count


def generate_inconsistent():
    """Generuje 48 grafów niespójnych + expected."""
    from generators.inconsistent import generate_inconsistent_graph

    combinations = list(itertools.product(GRAPH_TYPES, repeat=2))
    count = 0

    for idx, (type_a, type_b) in enumerate(combinations, 1):
        combo_name = f"{type_a}_{type_b}"
        part_types = [type_a, type_b]

        for size_name, size in SIZES.items():
            graph_path = os.path.join(INCONSISTENT_DIR, size_name, f"{combo_name}.txt")
            expected_path = os.path.join(INCONSISTENT_DIR, size_name, f"{combo_name}_expected.txt")
            label = f"{combo_name}/{size_name} ({size} wierz.)"

            print(f"  {label} ...", end=" ", flush=True)
            t0 = time.perf_counter()

            graph = generate_inconsistent_graph(
                total_vertices=size,
                parts_count=2,
                part_types=part_types,
                seed=SEED + idx * 1000,
            )
            save_graph(graph, graph_path)

            expected = compute_bfs_expected(graph)
            save_expected(expected, expected_path)

            elapsed = time.perf_counter() - t0
            print(f"OK ({len(graph)} wierz., {elapsed:.2f}s)")
            count += 1

    return count


# =====================================================================
#  MAIN
# =====================================================================
def main():
    print("=" * 60)
    print("  GENERACJA GRAFÓW + OCZEKIWANE WYNIKI BFS")
    print("=" * 60)

    print(f"\n--- Grafy spójne (4 typy × 3 rozmiary) ---")
    n1 = generate_connected()
    print(f"  [OK] {n1} grafów spójnych\n")

    print(f"--- Grafy niespójne (16 kombinacji × 3 rozmiary) ---")
    n2 = generate_inconsistent()
    print(f"  [OK] {n2} grafów niespójnych\n")

    print(f"Łącznie wygenerowano {n1 + n2} grafów z oczekiwanymi wynikami.")
    print(f"Katalog: {BASE_DIR}")
    print("\nTeraz możesz uruchomić:  python main.py")


if __name__ == "__main__":
    main()
