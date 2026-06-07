"""
BFS Benchmark – odczyt grafów, wykonanie BFS, weryfikacja poprawności,
pomiar czasów i podsumowanie.

Uruchomienie:
    python generate_graphs.py   # jednorazowo (jeśli jeszcze nie wygenerowano)
    python main.py              # benchmark + weryfikacja
"""

import multiprocessing as mp

from src import sequential_bfs
from src.parallel import create_parallel_context, destroy_parallel_context, parallel_bfs
from utils import load_graph, collect_graph_files, load_expected, verify_bfs, print_summary


def read_graph_header(path):
    with open(path, "r", encoding="utf-8") as file:
        nodes, edges = file.readline().split()[:2]
    return int(nodes), int(edges)


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

    max_nodes = 0
    max_edges = 0
    for graph_path, _, _ in graph_files:
        nodes, edges = read_graph_header(graph_path)
        max_nodes = max(max_nodes, nodes)
        max_edges = max(max_edges, edges)

    context = create_parallel_context(
        num_workers,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )

    results_seq = []
    results_par = []

    try:
        for graph_path, expected_path, label in graph_files:
            print(f"  {label} ...", end=" ", flush=True)

            graph = load_graph(graph_path)
            num_nodes = len(graph)
            num_edges = sum(len(n) for n in graph.values())

            seq_components, seq_time = sequential_bfs(graph)
            par_components, par_time = parallel_bfs(graph, context)

            expected_components = load_expected(expected_path)
            correct, msg = verify_bfs(par_components, expected_components)

            speedup = seq_time / par_time if par_time > 0 else float('inf')
            status = "OK" if correct else f"BŁĄD: {msg}"
            print(f"seq={seq_time:.4f}s  par={par_time:.4f}s  "
                  f"speedup={speedup:.2f}x  {status}")

            results_seq.append((label, num_nodes, num_edges, seq_time, True, "OK"))
            results_par.append((label, num_nodes, num_edges, par_time, correct, msg))
    finally:
        destroy_parallel_context(context)

    print_summary(results_seq, results_par, num_workers)


if __name__ == "__main__":
    mp.freeze_support()
    main()
