"""
Parallel BFS – wersja równoległa z pamięcią współdzieloną.

Wykorzystuje moduł multiprocessing (procesy, nie wątki) w celu
osiągnięcia rzeczywistej równoległości obliczeń, omijając GIL Pythona.

Algorytm:
    1.  Graf konwertowany jest na format CSR (Compressed Sparse Row) oparty
        na tablicach ctypes, udostępnianych procesom roboczym przez RawArray
        (pamięć współdzielona, brak locków – dane tylko do odczytu).
    2.  Bieżący frontier (warstwa BFS) jest dzielony na ~równe fragmenty
        między procesy robocze (partycjonowanie 1D).
    3.  Każdy proces przetwarza swój fragment frontieru:
        -  dla każdego wierzchołka z fragmentu przegląda listę sąsiadów,
        -  sprawdza w współdzielonej tablicy visited (RawArray, read-only
           w workerach), czy sąsiad był już odwiedzony,
        -  zwraca listę kandydatów (potencjalnie nowych wierzchołków).
    4.  Proces główny zbiera listy kandydatów ze wszystkich workerów,
        deduplikuje je (filtruje już odwiedzone), aktualizuje tablice
        visited i dist, buduje frontier następnego poziomu.
    5.  Kroki 2-4 powtarzane są do wyczerpania frontieru.
    6.  Dla grafów niespójnych: po opróżnieniu frontieru szukany jest
        kolejny nieodwiedzony wierzchołek i BFS startuje z nowego źródła.

Kluczowe decyzje projektowe:
    - Workery TYLKO CZYTAJĄ z pamięci współdzielonej → brak locków, brak
      deadlocków, minimalne narzuty synchronizacji.
    - Deduplikacja i zapis do visited/dist odbywa się WYŁĄCZNIE w procesie
      głównym → gwarancja poprawności.
    - Pula procesów tworzona jest raz i wykorzystywana wielokrotnie
      (koszt startu workerów jest jednorazowy).

Uruchomienie:
    python parallel.py
"""

import os
import sys
import time
import ctypes
import multiprocessing as mp
from multiprocessing import RawArray
from baseline import bfs_all_components as bfs_all_components_sequential
from utils import load_graph, collect_graph_files, load_expected, print_summary_parallel, verify_bfs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def graph_to_csr(graph):
    """
    Konwertuje graf (dict[int, list[int]]) na format CSR.

    Zwraca:
        node_ids  : posortowana lista węzłów (mapowanie indeks -> id)
        offsets   : lista przesunięć (długość n+1)
        edges     : spłaszczona lista sąsiadów (indeksy, nie id)
        id_to_idx : mapowanie id -> indeks
    """
    node_ids = sorted(graph.keys())
    id_to_idx = {nid: idx for idx, nid in enumerate(node_ids)}
    n = len(node_ids)

    offsets = [0] * (n + 1)
    edge_list = []

    offset = 0
    for idx, nid in enumerate(node_ids):
        offsets[idx] = offset
        neighbors = sorted(graph[nid])
        for nb in neighbors:
            edge_list.append(id_to_idx[nb])
        offset += len(neighbors)
    offsets[n] = offset

    return node_ids, offsets, edge_list, id_to_idx


def _worker_expand(frontier_chunk):
    """
    Przetwarza fragment frontieru i zwraca listę kandydatów
    (sąsiadów, którzy wg odczytu visited jeszcze nie byli odwiedzeni).

    Worker TYLKO CZYTA z pamięci współdzielonej – brak locków.
    Ostateczna deduplikacja odbywa się w procesie głównym.
    """
    offsets = _w_offsets
    edges = _w_edges
    visited = _w_visited

    candidates = []
    for u in frontier_chunk:
        start = offsets[u]
        end = offsets[u + 1]
        for j in range(start, end):
            v = edges[j]
            if visited[v] == 0:
                candidates.append(v)

    return candidates


def _init_worker(offsets_shm, edges_shm, visited_shm):
    """
    Inicjalizuje zmienne globalne procesu roboczego,
    mapując pamięć współdzieloną na tablice dostępne z poziomu workera.
    """
    global _w_offsets, _w_edges, _w_visited
    _w_offsets = offsets_shm
    _w_edges = edges_shm
    _w_visited = visited_shm


def parallel_bfs(graph, num_workers=None):
    """
    Równoległy BFS po wszystkich komponentach spójności.

    Parametry:
        graph       : dict[int, list[int]] – lista sąsiedztwa
        num_workers : liczba procesów roboczych (domyślnie: liczba rdzeni CPU)

    Zwraca:
        components : [(start_node, {node: dist}), ...]
        total_time : łączny czas BFS w sekundach
    """
    if num_workers is None:
        num_workers = mp.cpu_count()

    # ── Konwersja do CSR ──────────────────────────────────────────────
    node_ids, offsets, edges, id_to_idx = graph_to_csr(graph)
    n = len(node_ids)
    m = len(edges)

    # ── Pamięć współdzielona – graf (read-only) ──────────────────────
    offsets_shm = RawArray(ctypes.c_int64, n + 1)
    for i in range(n + 1):
        offsets_shm[i] = offsets[i]

    if m > 0:
        edges_shm = RawArray(ctypes.c_int64, m)
        for i in range(m):
            edges_shm[i] = edges[i]
    else:
        edges_shm = RawArray(ctypes.c_int64, 1)

    visited_shm = RawArray(ctypes.c_int32, n)  # 0 = nieodwiedzony

    dist_local = [-1] * n

    pool = mp.Pool(
        processes=num_workers,
        initializer=_init_worker,
        initargs=(offsets_shm, edges_shm, visited_shm)
    )

    # Minimalna wielkość frontieru, poniżej której nie opłaca się
    # rozsyłać pracy do procesów (overhead > zysk)
    PARALLEL_THRESHOLD = max(64, num_workers * 4)

    components = []

    t0 = time.perf_counter()

    try:
        for start_idx in range(n):
            if visited_shm[start_idx] != 0:
                continue

            # Inicjalizacja BFS dla nowej składowej
            start_node = node_ids[start_idx]
            visited_shm[start_idx] = 1
            dist_local[start_idx] = 0

            frontier = [start_idx]
            component_indices = [start_idx]

            current_dist = 0

            while frontier:
                current_dist += 1

                if len(frontier) >= PARALLEL_THRESHOLD:
                    chunk_size = max(1, (len(frontier) + num_workers - 1) // num_workers)
                    chunks = []
                    for i in range(0, len(frontier), chunk_size):
                        chunks.append(frontier[i:i + chunk_size])

                    results = pool.map(_worker_expand, chunks)

                    next_frontier = []
                    for candidates in results:
                        for v in candidates:
                            if visited_shm[v] == 0:
                                visited_shm[v] = 1
                                dist_local[v] = current_dist
                                next_frontier.append(v)
                                component_indices.append(v)
                else:
                    next_frontier = []
                    for u in frontier:
                        start = offsets_shm[u]
                        end = offsets_shm[u + 1]
                        for j in range(start, end):
                            v = edges_shm[j]
                            if visited_shm[v] == 0:
                                visited_shm[v] = 1
                                dist_local[v] = current_dist
                                next_frontier.append(v)
                                component_indices.append(v)

                frontier = next_frontier

            component_dist = {}
            for idx in component_indices:
                component_dist[node_ids[idx]] = dist_local[idx]

            components.append((start_node, component_dist))

    finally:
        pool.close()
        pool.join()

    total_time = time.perf_counter() - t0
    return components, total_time


def main():
    num_workers = mp.cpu_count()

    print("=" * 80)
    print("  PARALLEL BFS BENCHMARK + WERYFIKACJA POPRAWNOŚCI")
    print(f"  Liczba procesów roboczych: {num_workers}")
    print(f"  Liczba rdzeni CPU:         {mp.cpu_count()}")
    print("=" * 80)

    graph_files = collect_graph_files()

    if not graph_files:
        print("\n  Brak grafów! Najpierw uruchom:")
        print("    python generate_graphs.py")
        return

    print(f"\n  Znaleziono {len(graph_files)} grafów.\n")
    print(f"{'-' * 80}")
    print(f"  Wykonywanie BFS i weryfikacja...")
    print(f"{'-' * 80}")

    results_seq = []
    results_par = []

    for graph_path, expected_path, label in graph_files:
        print(f"  {label} ...", end=" ", flush=True)

        graph = load_graph(graph_path)
        num_nodes = len(graph)
        num_edges = sum(len(n) for n in graph.values())

        seq_components, seq_time = bfs_all_components_sequential(graph)
        par_components, par_time = parallel_bfs(graph, num_workers)

        expected_components = load_expected(expected_path)
        correct, msg = verify_bfs(par_components, expected_components)

        speedup = seq_time / par_time if par_time > 0 else float('inf')
        status = "OK" if correct else f"BŁĄD: {msg}"
        print(f"seq={seq_time:.4f}s  par={par_time:.4f}s  "
              f"speedup={speedup:.2f}x  {status}")

        results_seq.append((label, num_nodes, num_edges, seq_time, True, "OK"))
        results_par.append((label, num_nodes, num_edges, par_time, correct, msg))

    print_summary_parallel(results_seq, results_par, num_workers)


if __name__ == "__main__":
    mp.freeze_support()
    main()
