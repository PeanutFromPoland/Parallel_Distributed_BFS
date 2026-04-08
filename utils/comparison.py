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


def print_summary_sequential(results):
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
    print(f"\n  Łączny czas BFS (spójne):    {connected_time:.4f}s")
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

def print_summary_parallel(results_seq, results_par, num_workers):
    """Drukuje zestawienie wyników sekwencyjnych i równoległych."""
    print("\n" + "=" * 120)
    print("  PODSUMOWANIE – PARALLEL BFS BENCHMARK")
    print("=" * 120)

    header = (
        f"{'Lp.':<5} {'Wierz.':<8} {'Kraw.':<10} "
        f"{'Seq [s]':<14} {'Par [s]':<14} {'Speedup':<10} "
        f"{'Popr.':<8} {'Graf'}"
    )
    print(header)
    print("-" * 120)

    total_seq_inconsistent = 0.0
    total_seq_connected = 0.0
    total_par_inconsistent = 0.0
    total_par_connected = 0.0
    all_correct = True
    errors = []

    for i, (r_seq, r_par) in enumerate(zip(results_seq, results_par), 1):
        label, nodes, edge_count, seq_time, _, _ = r_seq
        _, _, _, par_time, correct, msg = r_par

        speedup = seq_time / par_time if par_time > 0 else float('inf')
        status = "[OK]" if correct else "[BLAD]"

        print(
            f"{i:<5} {nodes:<8} {edge_count:<10} "
            f"{seq_time:<14.6f} {par_time:<14.6f} {speedup:<10.2f} "
            f"{status:<8} {label}"
        )

        if "[Spójny]" in label:
            total_seq_connected += seq_time
            total_par_connected += par_time
        else:
            total_seq_inconsistent += seq_time
            total_par_inconsistent += par_time
        if not correct:
            all_correct = False
            errors.append((label, msg))

    total_seq = total_seq_inconsistent + total_seq_connected
    total_par = total_par_inconsistent + total_par_connected

    print("-" * 120)
    total_speedup = total_seq / total_par if total_par > 0 else float('inf')
    print(f"\nProcesy robocze:                  {num_workers}")
    print(f"  Łączny czas sekwencyjny:          {total_seq:.4f}s")
    print(f"        czas (spójne):              {total_seq_connected:.4f}s")
    print(f"        czas (niespójne):           {total_seq_inconsistent:.4f}s")
    print(f"  Łączny czas równoległy:           {total_par:.4f}s")
    print(f"        czas (spójne):              {total_par_connected:.4f}s")
    print(f"        czas (niespójne):           {total_par_inconsistent:.4f}s")
    print(f"  Łączny speedup:                   {total_speedup:.2f}x")
    print(f"  Liczba grafów:                    {len(results_seq)}")

    if all_correct:
        print(f"\n  [OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE")
    else:
        print(f"\n  [BLAD] BLEDY W {len(errors)} GRAFACH:")
        for label, msg in errors:
            print(f"    - {label}: {msg}")

    print("=" * 120)