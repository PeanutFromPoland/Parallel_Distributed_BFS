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


def print_summary(results, num_workers, runs):
    """Drukuje zestawienie średnich wyników sekwencyjnych i równoległych."""
    print("\n" + "=" * 132)
    print("  PODSUMOWANIE - PARALLEL BFS BENCHMARK")
    print("=" * 132)

    header = (
        f"{'Lp.':<5} {'Wierz.':<8} {'Kraw.':<10} "
        f"{'Seq avg [s]':<14} {'Seq sd':<11} "
        f"{'Par avg [s]':<14} {'Par sd':<11} "
        f"{'Speedup':<10} {'Popr.':<8} {'Graf'}"
    )
    print(header)
    print("-" * 132)

    total_seq_connected = 0.0
    total_seq_inconsistent = 0.0
    total_par_connected = 0.0
    total_par_inconsistent = 0.0
    all_correct = True
    errors = []

    for i, result in enumerate(results, 1):
        seq_mean = result["seq_stats"]["mean"]
        par_mean = result["par_stats"]["mean"]
        speedup = seq_mean / par_mean if par_mean > 0 else float("inf")
        status = "[OK]" if result["correct"] else "[BLAD]"

        print(
            f"{i:<5} {result['nodes']:<8} {result['edges']:<10} "
            f"{seq_mean:<14.6f} {result['seq_stats']['stdev']:<11.6f} "
            f"{par_mean:<14.6f} {result['par_stats']['stdev']:<11.6f} "
            f"{speedup:<10.2f} {status:<8} {result['label']}"
        )

        if "[Spójny]" in result["label"]:
            total_seq_connected += seq_mean
            total_par_connected += par_mean
        else:
            total_seq_inconsistent += seq_mean
            total_par_inconsistent += par_mean

        if not result["correct"]:
            all_correct = False
            errors.append((result["label"], result["msg"]))

    total_seq = total_seq_connected + total_seq_inconsistent
    total_par = total_par_connected + total_par_inconsistent
    total_speedup = total_seq / total_par if total_par > 0 else float("inf")

    print("-" * 132)
    print(f"\n  Procesy robocze:                  {num_workers}")
    print(f"  Powtórzenia na graf:              {runs}")
    print(f"  Suma średnich czasów sekw.:       {total_seq:.4f}s")
    print(f"        grafy spójne:               {total_seq_connected:.4f}s")
    print(f"        grafy niespójne:            {total_seq_inconsistent:.4f}s")
    print(f"  Suma średnich czasów równ.:       {total_par:.4f}s")
    print(f"        grafy spójne:               {total_par_connected:.4f}s")
    print(f"        grafy niespójne:            {total_par_inconsistent:.4f}s")
    print(f"  Łączny speedup ze średnich:       {total_speedup:.2f}x")
    print(f"  Liczba grafów:                    {len(results)}")
    print(f"  Łączna liczba prób:               {len(results) * runs}")

    if all_correct:
        print("\n  [OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE")
    else:
        print(f"\n  [BLAD] BLEDY W {len(errors)} GRAFACH:")
        for label, msg in errors:
            print(f"    - {label}: {msg}")

    print("=" * 132)
