"""
BFS Benchmark – odczyt grafów, wykonanie BFS, weryfikacja poprawności,
pomiar czasów i podsumowanie.

Uruchomienie:
    python generate_graphs.py   # jednorazowo (jeśli jeszcze nie wygenerowano)
    python main.py              # benchmark + weryfikacja
"""

import os
import time
import itertools
from collections import deque

# ── Konfiguracja ─────────────────────────────────────────────────────
SIZES = ["small", "medium", "large"]
GRAPH_TYPES = ["random", "bb", "small_world", "grid"]

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs")
CONNECTED_DIR = os.path.join(BASE_DIR, "connected")
INCONSISTENT_DIR = os.path.join(BASE_DIR, "inconsistent")


# =====================================================================
#  I/O
# =====================================================================
def load_graph(filepath):
    """Odczytuje graf (dict[int, list[int]]) z pliku tekstowego."""
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


def load_expected(filepath):
    """
    Odczytuje oczekiwane wyniki BFS.

    Zwraca listę komponentów:
        [(start_node, {node: dist, ...}), ...]
    """
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


# =====================================================================
#  BFS
# =====================================================================
def bfs_with_distances(graph, start):
    """
    BFS od 'start'. Zwraca dict {node: distance}.
    Sąsiadów sortujemy, żeby wynik był deterministyczny.
    """
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in sorted(graph[node]):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


def bfs_all_components(graph):
    """
    BFS po wszystkich komponentach spójności
    (zaczynając od wierzchołka o najmniejszym numerze w każdym).

    Zwraca:
        components: [(start, {node: dist}), ...]
        total_time: łączny czas BFS (sekundy)
    """
    visited_global = set()
    components = []

    t0 = time.perf_counter()

    for start in sorted(graph.keys()):
        if start in visited_global:
            continue
        dist = bfs_with_distances(graph, start)
        visited_global.update(dist.keys())
        components.append((start, dist))

    total_time = time.perf_counter() - t0
    return components, total_time


# =====================================================================
#  Weryfikacja poprawności
# =====================================================================
def verify_bfs(actual_components, expected_components):
    """
    Porównuje wyniki BFS z oczekiwanymi.
    Zwraca (is_correct, error_message).
    """
    if len(actual_components) != len(expected_components):
        return False, (
            f"Liczba komponentów: {len(actual_components)} "
            f"(oczekiwano {len(expected_components)})"
        )

    for i, ((a_start, a_dist), (e_start, e_dist)) in enumerate(
        zip(actual_components, expected_components)
    ):
        if a_start != e_start:
            return False, (
                f"Komponent {i}: start={a_start} (oczekiwano {e_start})"
            )
        if len(a_dist) != len(e_dist):
            return False, (
                f"Komponent {i} (start={a_start}): "
                f"{len(a_dist)} wierz. (oczekiwano {len(e_dist)})"
            )
        for node, expected_d in e_dist.items():
            actual_d = a_dist.get(node)
            if actual_d is None:
                return False, (
                    f"Komponent {i}: wierzchołek {node} nie odwiedzony"
                )
            if actual_d != expected_d:
                return False, (
                    f"Komponent {i}: wierzchołek {node}: "
                    f"dist={actual_d} (oczekiwano {expected_d})"
                )

    return True, "OK"


# =====================================================================
#  Zbieranie ścieżek do grafów
# =====================================================================
def collect_graph_files():
    """
    Zbiera wszystkie pary (graph_path, expected_path, label).
    """
    files = []

    # Grafy spójne
    for graph_type in GRAPH_TYPES:
        for size_name in SIZES:
            graph_path = os.path.join(CONNECTED_DIR, graph_type, f"{size_name}.txt")
            expected_path = os.path.join(CONNECTED_DIR, graph_type, f"{size_name}_expected.txt")
            if os.path.exists(graph_path) and os.path.exists(expected_path):
                label = f"[Spójny] {graph_type}/{size_name}"
                files.append((graph_path, expected_path, label))

    # Grafy niespójne
    combinations = list(itertools.product(GRAPH_TYPES, repeat=2))
    for type_a, type_b in combinations:
        combo_name = f"{type_a}_{type_b}"
        for size_name in SIZES:
            graph_path = os.path.join(INCONSISTENT_DIR, size_name, f"{combo_name}.txt")
            expected_path = os.path.join(INCONSISTENT_DIR, size_name, f"{combo_name}_expected.txt")
            if os.path.exists(graph_path) and os.path.exists(expected_path):
                label = f"[Niespójny] {combo_name}/{size_name}"
                files.append((graph_path, expected_path, label))

    return files


# =====================================================================
#  Podsumowanie
# =====================================================================
def print_summary(results):
    print("\n" + "=" * 100)
    print("  PODSUMOWANIE – BFS BENCHMARK")
    print("=" * 100)

    header = f"{'Lp.':<5} {'Wierz.':<8} {'Kraw.':<10} {'Czas BFS':<12} {'Poprawność':<12} {'Graf'}"
    print(header)
    print("-" * 100)

    total_time = 0.0
    connected_time = 0.0
    inconsistent_time = 0.0
    all_correct = True
    errors = []

    for i, (label, nodes, edges, bfs_time, correct, msg) in enumerate(results, 1):
        status = "[OK]" if correct else "[BLAD]"
        print(f"{i:<5} {nodes:<8} {edges:<10} {bfs_time:<12.6f} {status:<12} {label}")
        total_time += bfs_time
        if "[Spójny]" in label:
            connected_time += bfs_time
        else:
            inconsistent_time += bfs_time
        if not correct:
            all_correct = False
            errors.append((label, msg))

    print("-" * 100)
    print(f"\n  Łączny czas BFS (spójne):      {connected_time:.4f}s")
    print(f"  Łączny czas BFS (niespójne):   {inconsistent_time:.4f}s")
    print(f"  Łączny czas BFS (wszystkie):   {total_time:.4f}s")
    print(f"  Liczba grafów:                 {len(results)}")

    if all_correct:
        print(f"\n  [OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE")
    else:
        print(f"\n  [BLAD] BLEDY W {len(errors)} GRAFACH:")
        for label, msg in errors:
            print(f"    - {label}: {msg}")

    print("=" * 100)


# =====================================================================
#  MAIN
# =====================================================================
def main():
    print("=" * 60)
    print("  BFS BENCHMARK + WERYFIKACJA POPRAWNOŚCI")
    print("=" * 60)

    graph_files = collect_graph_files()

    if not graph_files:
        print("\n  Brak grafów! Najpierw uruchom:")
        print("    python generate_graphs.py")
        return

    print(f"\n  Znaleziono {len(graph_files)} grafów.\n")
    print(f"{'-' * 60}")
    print(f"  Wykonywanie BFS i weryfikacja...")
    print(f"{'-' * 60}")

    results = []

    for graph_path, expected_path, label in graph_files:
        print(f"  {label} ...", end=" ", flush=True)

        graph = load_graph(graph_path)
        num_nodes = len(graph)
        num_edges = sum(len(n) for n in graph.values())

        # BFS
        actual_components, bfs_time = bfs_all_components(graph)

        # Weryfikacja
        expected_components = load_expected(expected_path)
        correct, msg = verify_bfs(actual_components, expected_components)

        status = "OK" if correct else f"BŁĄD: {msg}"
        print(f"{bfs_time:.4f}s  {status}")

        results.append((label, num_nodes, num_edges, bfs_time, correct, msg))

    print_summary(results)


if __name__ == "__main__":
    main()
