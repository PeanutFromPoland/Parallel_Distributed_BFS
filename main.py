"""
BFS Benchmark – odczyt grafów, wykonanie BFS, weryfikacja poprawności,
pomiar czasów i podsumowanie.

Uruchomienie:
    python generate_graphs.py   # jednorazowo (jeśli jeszcze nie wygenerowano)
    python main.py              # benchmark + weryfikacja
"""

from utils import (
    load_graph,
    load_expected,
    collect_graph_files,
    verify_bfs,
    print_summary_sequential
)

from baseline import bfs_all_components


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

    print_summary_sequential(results)


if __name__ == "__main__":
    main()
