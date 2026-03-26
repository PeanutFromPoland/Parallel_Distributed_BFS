"""
Główny program: generacja grafów, zapis, odczyt, BFS i pomiar czasów.

Uruchomienie:
    python main.py
"""

import os
import sys
import time
import random
import itertools
from collections import deque

# ── Rozmiary grafów ──────────────────────────────────────────────────
SIZES = {
    "small":  500,
    "medium": 5_000,
    "large":  15_000,
}

# ── Typy generatorów spójnych ────────────────────────────────────────
GRAPH_TYPES = ["random", "bb", "small_world", "grid"]

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs")
CONNECTED_DIR = os.path.join(BASE_DIR, "connected")
INCONSISTENT_DIR = os.path.join(BASE_DIR, "inconsistent")

SEED = 42


# =====================================================================
#  BFS
# =====================================================================
def bfs(graph, start):
    """BFS z pomiarem czasu. Zwraca czas w sekundach i liczbę odwiedzonych."""
    t0 = time.perf_counter()
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    elapsed = time.perf_counter() - t0
    return elapsed, len(visited)


def bfs_all_components(graph):
    """
    BFS po wszystkich komponentach spójności.
    Zwraca łączny czas i łączną liczbę odwiedzonych wierzchołków.
    """
    unvisited = set(graph.keys())
    total_time = 0.0
    total_visited = 0
    while unvisited:
        start = next(iter(unvisited))
        elapsed, count = bfs(graph, start)
        total_time += elapsed
        total_visited += count
        unvisited -= set(
            _bfs_collect(graph, start)
        )
    return total_time, total_visited


def _bfs_collect(graph, start):
    """Zwraca zbiór wierzchołków osiągalnych z 'start'."""
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited


# =====================================================================
#  I/O grafów
# =====================================================================
def save_graph(graph, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    num_edges = sum(len(n) for n in graph.values())
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{len(graph)} {num_edges}\n")
        for node in sorted(graph.keys()):
            for neighbor in graph[node]:
                f.write(f"{node} {neighbor}\n")


def load_graph(filepath):
    graph = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()  # nagłówek
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            u, v = int(parts[0]), int(parts[1])
            if u not in graph:
                graph[u] = []
            graph[u].append(v)
    # Wierzchołki bez krawędzi wychodzących
    all_nodes = set(graph.keys())
    for neighbors in list(graph.values()):
        for n in neighbors:
            if n not in all_nodes:
                graph[n] = []
                all_nodes.add(n)
    return graph


# =====================================================================
#  Generacja grafów spójnych
# =====================================================================
def generate_connected_graphs():
    """Generuje 12 grafów spójnych (4 typy × 3 rozmiary) i zapisuje do plików."""
    # Import generatorów wewnątrz funkcji, żeby uniknąć matplotlib na import
    from generators.random import generate_random_graph
    from generators.bb import generate_bb_graph
    from generators.small_world import generate_small_world_graph
    from generators.grid import generate_grid_graph
    import math

    files = []

    for graph_type in GRAPH_TYPES:
        for size_name, size in SIZES.items():
            filepath = os.path.join(
                CONNECTED_DIR, graph_type, f"{size_name}.txt"
            )
            label = f"[Spójny] {graph_type}/{size_name} ({size} wierz.)"
            print(f"  Generowanie: {label} ...", end=" ", flush=True)
            t0 = time.perf_counter()

            seed = SEED

            if graph_type == "random":
                graph = generate_random_graph(
                    size=size, threshold=0.3, consistency=True,
                    start_val=1, unidirectional=True, seed=seed,
                )
            elif graph_type == "bb":
                m = min(2, size - 1)
                random.seed(seed)
                graph = generate_bb_graph(
                    size=size, m=m, start_val=1, unidirectional=True,
                )
            elif graph_type == "small_world":
                k = min(4, size - 1)
                if k % 2 != 0:
                    k = max(2, k - 1)
                graph = generate_small_world_graph(
                    size=size, k=k, rewiring_prob=0.1,
                    consistency=True, start_val=1,
                    unidirectional=True, seed=seed,
                )
            elif graph_type == "grid":
                w = max(1, int(math.sqrt(size)))
                h = max(1, size // w)
                while w * h < size:
                    h += 1
                graph = generate_grid_graph(dimensions=(w, h))
                # Przenumeruj tuple → int
                old_keys = sorted(graph.keys())
                mapping = {k: i + 1 for i, k in enumerate(old_keys)}
                graph = {
                    mapping[k]: [mapping[n] for n in ns]
                    for k, ns in graph.items()
                }

            gen_time = time.perf_counter() - t0
            print(f"wygenerowano w {gen_time:.2f}s, "
                  f"{len(graph)} wierz. Zapisuję...", end=" ", flush=True)

            save_graph(graph, filepath)
            print("OK")
            files.append((filepath, label))

    return files


# =====================================================================
#  Generacja grafów niespójnych
# =====================================================================
def generate_all_type_combinations():
    """
    Zwraca 16 kombinacji typów (4×4): każdy typ z każdym typem,
    łącznie z parami identycznymi.
    """
    return list(itertools.product(GRAPH_TYPES, repeat=2))


def generate_inconsistent_graphs():
    """Generuje 48 grafów niespójnych (16 kombinacji × 3 rozmiary)."""
    from generators.inconsistent import generate_inconsistent_graph

    combinations = generate_all_type_combinations()
    files = []

    for idx, (type_a, type_b) in enumerate(combinations, 1):
        combo_name = f"{type_a}_{type_b}"
        part_types = [type_a, type_b]
        parts_count = 2

        for size_name, size in SIZES.items():
            filepath = os.path.join(
                INCONSISTENT_DIR, size_name, f"{combo_name}.txt"
            )
            label = (
                f"[Niespójny] {combo_name}/{size_name} "
                f"({size} wierz., {parts_count} części)"
            )
            print(f"  Generowanie: {label} ...", end=" ", flush=True)
            t0 = time.perf_counter()

            seed = SEED + idx * 1000

            graph = generate_inconsistent_graph(
                total_vertices=size,
                parts_count=parts_count,
                part_types=part_types,
                seed=seed,
            )

            gen_time = time.perf_counter() - t0
            print(f"wygenerowano w {gen_time:.2f}s, "
                  f"{len(graph)} wierz. Zapisuję...", end=" ", flush=True)

            save_graph(graph, filepath)
            print("OK")
            files.append((filepath, label))

    return files


# =====================================================================
#  Wykonanie BFS na wszystkich grafach
# =====================================================================
def run_bfs_on_all(graph_files):
    """
    Odczytuje grafy z plików i wykonuje BFS.
    Zwraca listę wyników: (label, num_nodes, num_edges, bfs_time).
    """
    results = []

    for filepath, label in graph_files:
        print(f"  BFS: {label} ...", end=" ", flush=True)

        graph = load_graph(filepath)
        num_nodes = len(graph)
        num_edges = sum(len(n) for n in graph.values())

        bfs_time, visited = bfs_all_components(graph)

        print(f"{bfs_time:.4f}s  ({visited} odwiedzonych)")
        results.append((label, num_nodes, num_edges, bfs_time))

    return results


# =====================================================================
#  Wyświetlenie podsumowania
# =====================================================================
def print_summary(results):
    print("\n" + "=" * 90)
    print("  PODSUMOWANIE CZASÓW BFS")
    print("=" * 90)

    # Nagłówek tabeli
    print(f"{'Lp.':<5} {'Wierz.':<10} {'Kraw.':<10} {'Czas BFS':<12} {'Graf'}")
    print("-" * 90)

    total_time = 0.0
    connected_time = 0.0
    inconsistent_time = 0.0

    for i, (label, nodes, edges, bfs_time) in enumerate(results, 1):
        print(f"{i:<5} {nodes:<10} {edges:<10} {bfs_time:<12.6f} {label}")
        total_time += bfs_time
        if "[Spójny]" in label:
            connected_time += bfs_time
        else:
            inconsistent_time += bfs_time

    print("-" * 90)
    print(f"\n  Łączny czas BFS (grafy spójne):    {connected_time:.4f}s")
    print(f"  Łączny czas BFS (grafy niespójne): {inconsistent_time:.4f}s")
    print(f"  Łączny czas BFS (wszystkie):       {total_time:.4f}s")
    print(f"  Liczba grafów:                     {len(results)}")
    print("=" * 90)


# =====================================================================
#  MAIN
# =====================================================================
def main():
    print("=" * 70)
    print("  PARALLEL & DISTRIBUTED BFS – BENCHMARK")
    print("=" * 70)

    all_files = []

    # ── Etap 1: Generacja grafów spójnych ──
    print(f"\n{'─' * 70}")
    print("  ETAP 1: Generacja 12 grafów spójnych")
    print(f"{'─' * 70}")
    connected_files = generate_connected_graphs()
    all_files.extend(connected_files)
    print(f"  ✓ Wygenerowano {len(connected_files)} grafów spójnych\n")

    # ── Etap 2: Generacja grafów niespójnych ──
    print(f"{'─' * 70}")
    print("  ETAP 2: Generacja 48 grafów niespójnych")
    print(f"{'─' * 70}")
    inconsistent_files = generate_inconsistent_graphs()
    all_files.extend(inconsistent_files)
    print(f"  ✓ Wygenerowano {len(inconsistent_files)} grafów niespójnych\n")

    # ── Etap 3: BFS na wszystkich grafach ──
    print(f"{'─' * 70}")
    print(f"  ETAP 3: BFS na {len(all_files)} grafach")
    print(f"{'─' * 70}")
    results = run_bfs_on_all(all_files)

    # ── Etap 4: Podsumowanie ──
    print_summary(results)


if __name__ == "__main__":
    main()
