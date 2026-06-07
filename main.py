"""
BFS benchmark: repeated sequential and parallel runs with CSV export.

Usage:
    python main.py
    python main.py --runs 5 --csv results/parallel_bfs.csv
"""

import argparse
import csv
import multiprocessing as mp
import os
import statistics
from datetime import datetime, timezone

from src import sequential_bfs
from src.parallel import create_parallel_context, destroy_parallel_context, parallel_bfs
from utils import load_graph, collect_graph_files, load_expected, verify_bfs, print_summary


DEFAULT_RUNS = 3
DEFAULT_CSV_PATH = os.path.join("results", "parallel_bfs_results.csv")


def positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def parse_args():
    parser = argparse.ArgumentParser(description="Repeated parallel BFS benchmark.")
    parser.add_argument(
        "--runs",
        type=positive_int,
        default=DEFAULT_RUNS,
        help=f"Algorithm runs per graph (default: {DEFAULT_RUNS}).",
    )
    parser.add_argument(
        "--csv",
        default=DEFAULT_CSV_PATH,
        help=f"CSV output path (default: {DEFAULT_CSV_PATH}).",
    )
    return parser.parse_args()


def read_graph_header(path):
    with open(path, "r", encoding="utf-8") as file:
        nodes, edges = file.readline().split()[:2]
    return int(nodes), int(edges)


def timing_stats(values):
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def export_csv(path, results, num_workers, runs):
    output_dir = os.path.dirname(os.path.abspath(path))
    os.makedirs(output_dir, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    fields = [
        "record_type",
        "generated_at_utc",
        "label",
        "graph_path",
        "nodes",
        "edges",
        "workers",
        "configured_runs",
        "run",
        "seq_time_s",
        "par_time_s",
        "speedup",
        "seq_mean_s",
        "seq_median_s",
        "seq_min_s",
        "seq_max_s",
        "seq_stdev_s",
        "par_mean_s",
        "par_median_s",
        "par_min_s",
        "par_max_s",
        "par_stdev_s",
        "mean_speedup",
        "correct",
        "message",
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for result in results:
            base = {
                "generated_at_utc": generated_at,
                "label": result["label"],
                "graph_path": result["graph_path"],
                "nodes": result["nodes"],
                "edges": result["edges"],
                "workers": num_workers,
                "configured_runs": runs,
                "correct": result["correct"],
                "message": result["msg"],
            }
            for trial in result["trials"]:
                writer.writerow({
                    **base,
                    "record_type": "run",
                    "run": trial["run"],
                    "seq_time_s": trial["seq_time"],
                    "par_time_s": trial["par_time"],
                    "speedup": trial["speedup"],
                })

            seq_stats = result["seq_stats"]
            par_stats = result["par_stats"]
            writer.writerow({
                **base,
                "record_type": "summary",
                "seq_mean_s": seq_stats["mean"],
                "seq_median_s": seq_stats["median"],
                "seq_min_s": seq_stats["min"],
                "seq_max_s": seq_stats["max"],
                "seq_stdev_s": seq_stats["stdev"],
                "par_mean_s": par_stats["mean"],
                "par_median_s": par_stats["median"],
                "par_min_s": par_stats["min"],
                "par_max_s": par_stats["max"],
                "par_stdev_s": par_stats["stdev"],
                "mean_speedup": (
                    seq_stats["mean"] / par_stats["mean"]
                    if par_stats["mean"] > 0
                    else float("inf")
                ),
            })


def main():
    args = parse_args()
    num_workers = mp.cpu_count()

    print("=" * 80)
    print("  PARALLEL BFS BENCHMARK + WERYFIKACJA POPRAWNOŚCI")
    print(f"  Liczba procesów roboczych: {num_workers}")
    print(f"  Liczba powtórzeń:          {args.runs}")
    print(f"  Plik CSV:                  {os.path.abspath(args.csv)}")
    print("=" * 80)

    graph_files = collect_graph_files()
    if not graph_files:
        print("\n  Brak grafów! Najpierw uruchom:")
        print("    python generate_graphs.py")
        return

    print(f"\n  Znaleziono {len(graph_files)} grafów.\n")

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
    results = []

    try:
        for graph_path, expected_path, label in graph_files:
            print(f"  {label}")
            graph = load_graph(graph_path)
            expected_components = load_expected(expected_path)
            num_nodes = len(graph)
            num_edges = sum(len(neighbors) for neighbors in graph.values())
            trials = []
            graph_correct = True
            messages = []

            for run_number in range(1, args.runs + 1):
                seq_components, seq_time = sequential_bfs(graph)
                par_components, par_time = parallel_bfs(graph, context)

                seq_correct, seq_msg = verify_bfs(seq_components, expected_components)
                par_correct, par_msg = verify_bfs(par_components, expected_components)
                correct = seq_correct and par_correct
                if not correct:
                    graph_correct = False
                    messages.append(
                        f"run {run_number}: seq={seq_msg}; par={par_msg}"
                    )

                speedup = seq_time / par_time if par_time > 0 else float("inf")
                status = "OK" if correct else "BLAD"
                print(
                    f"    run {run_number}/{args.runs}: "
                    f"seq={seq_time:.6f}s par={par_time:.6f}s "
                    f"speedup={speedup:.2f}x {status}"
                )
                trials.append({
                    "run": run_number,
                    "seq_time": seq_time,
                    "par_time": par_time,
                    "speedup": speedup,
                })

            seq_stats = timing_stats([trial["seq_time"] for trial in trials])
            par_stats = timing_stats([trial["par_time"] for trial in trials])
            results.append({
                "label": label,
                "graph_path": os.path.abspath(graph_path),
                "nodes": num_nodes,
                "edges": num_edges,
                "trials": trials,
                "seq_stats": seq_stats,
                "par_stats": par_stats,
                "correct": graph_correct,
                "msg": " | ".join(messages) if messages else "OK",
            })
    finally:
        destroy_parallel_context(context)

    print_summary(results, num_workers, args.runs)
    export_csv(args.csv, results, num_workers, args.runs)
    print(f"\n  Wyniki CSV zapisano w: {os.path.abspath(args.csv)}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
