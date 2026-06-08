"""
Run BFS scaling benchmarks for multiple process and worker counts.

By default this executes:
  - local parallel BFS with 4, 8, 12, and 16 processes,
  - distributed BFS with 2, 3, 5, and 10 Docker workers.

Each configuration writes its own CSV under results/scaling/. A combined
summary is written to results/scaling/scaling_summary.csv.
"""

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

from utils import collect_graph_files


ROOT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = ROOT_DIR / "results" / "scaling"
SCALING_COMPOSE = ROOT_DIR / "distributed" / "docker-compose.scaling.yml"
LEGACY_PARALLEL_CSV = ROOT_DIR / "results" / "parallel_bfs_results.csv"
LEGACY_DISTRIBUTED_CSV = ROOT_DIR / "results" / "distributed_bfs_results.csv"

DEFAULT_PROCESS_COUNTS = (4, 8, 12, 16)
DEFAULT_STATION_COUNTS = (2, 3, 5, 10)


def positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def unique_positive(values):
    result = []
    seen = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run parallel and distributed BFS scaling benchmarks.",
    )
    parser.add_argument(
        "--processes",
        nargs="+",
        type=positive_int,
        default=list(DEFAULT_PROCESS_COUNTS),
        help="Local process counts (default: 4 8 12 16).",
    )
    parser.add_argument(
        "--stations",
        nargs="+",
        type=positive_int,
        default=list(DEFAULT_STATION_COUNTS),
        help="Docker worker counts (default: 2 3 5 10; maximum: 10).",
    )
    parser.add_argument(
        "--runs",
        type=positive_int,
        default=3,
        help="Runs per graph and configuration (default: 3).",
    )
    parser.add_argument(
        "--parallel-only",
        action="store_true",
        help="Run only the local multiprocessing benchmark.",
    )
    parser.add_argument(
        "--distributed-only",
        action="store_true",
        help="Run only the Docker distributed benchmark.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing benchmarks.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recompute configurations even when a complete CSV already exists.",
    )
    return parser.parse_args()


def run_command(command, env=None, dry_run=False):
    printable = subprocess.list2cmdline([str(item) for item in command])
    print(f"\n> {printable}", flush=True)
    if dry_run:
        return
    subprocess.run(
        [str(item) for item in command],
        cwd=ROOT_DIR,
        env=env,
        check=True,
    )


def find_docker():
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Nie znaleziono programu docker w PATH.")
    return docker


def parallel_csv_path(processes):
    return RESULTS_DIR / f"parallel_processes_{processes}.csv"


def distributed_csv_path(stations):
    return RESULTS_DIR / f"distributed_stations_{stations}.csv"


def inspect_result_file(
    path,
    workers,
    runs,
    time_column,
    expected_graphs,
    newest_input_mtime,
):
    if not path.exists():
        return None
    if path.stat().st_mtime < newest_input_mtime:
        return None

    summaries = 0
    trials = 0
    all_correct = True
    sequential_sum = 0.0
    variant_sum = 0.0

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                if int(row["workers"]) != workers:
                    return None
                if int(row["configured_runs"]) != runs:
                    return None

                if row["record_type"] == "run":
                    trials += 1
                elif row["record_type"] == "summary":
                    summaries += 1
                    sequential_sum += float(row["seq_mean_s"])
                    variant_sum += float(row[time_column])
                    all_correct = (
                        all_correct
                        and row["correct"].strip().lower() == "true"
                    )
    except (OSError, KeyError, TypeError, ValueError):
        return None

    if summaries != expected_graphs or trials != expected_graphs * runs:
        return None
    if not all_correct:
        return None

    return {
        "configurations": summaries,
        "sequential_sum_s": sequential_sum,
        "variant_sum_s": variant_sum,
        "global_speedup": (
            sequential_sum / variant_sum
            if variant_sum > 0
            else float("inf")
        ),
        "all_correct": all_correct,
    }


def find_existing_result(
    target_path,
    legacy_path,
    workers,
    runs,
    time_column,
    expected_graphs,
    newest_input_mtime,
    force,
):
    if force:
        return None

    candidates = [target_path]
    if legacy_path is not None:
        candidates.append(legacy_path)

    for path in candidates:
        result = inspect_result_file(
            path,
            workers,
            runs,
            time_column,
            expected_graphs,
            newest_input_mtime,
        )
        if result is not None:
            print(
                f"\n=== Reusing complete result: {path.relative_to(ROOT_DIR)} ===",
                flush=True,
            )
            return path
    return None


def run_parallel(
    process_counts,
    runs,
    dry_run,
    force,
    expected_graphs,
    newest_input_mtime,
):
    result_paths = {}
    for processes in process_counts:
        output_path = parallel_csv_path(processes)
        legacy_path = LEGACY_PARALLEL_CSV if processes == 16 else None
        existing = find_existing_result(
            output_path,
            legacy_path,
            processes,
            runs,
            "par_mean_s",
            expected_graphs,
            newest_input_mtime,
            force,
        )
        if existing is not None:
            result_paths[processes] = existing
            continue

        print(
            f"\n=== Parallel BFS: {processes} processes, {runs} runs ===",
            flush=True,
        )
        run_command(
            [
                sys.executable,
                "main.py",
                "--workers",
                processes,
                "--runs",
                runs,
                "--csv",
                output_path,
            ],
            dry_run=dry_run,
        )
        result_paths[processes] = output_path
    return result_paths


def compose_base_command(docker, project_name):
    return [
        docker,
        "compose",
        "-f",
        SCALING_COMPOSE,
        "-p",
        project_name,
    ]


def run_distributed(
    station_counts,
    runs,
    dry_run,
    force,
    expected_graphs,
    newest_input_mtime,
):
    docker = None
    result_paths = {}

    for stations in station_counts:
        if stations > 10:
            raise ValueError(
                f"Liczba stacji {stations} przekracza limit 10 zdefiniowany "
                "w docker-compose.scaling.yml."
            )

        worker_services = [
            f"worker-{number}" for number in range(1, stations + 1)
        ]
        worker_addresses = ",".join(
            f"{service}:5000" for service in worker_services
        )
        project_name = f"bfs-scaling-{stations}"
        output_path = distributed_csv_path(stations)
        legacy_path = LEGACY_DISTRIBUTED_CSV if stations == 3 else None
        existing = find_existing_result(
            output_path,
            legacy_path,
            stations,
            runs,
            "dist_mean_s",
            expected_graphs,
            newest_input_mtime,
            force,
        )
        if existing is not None:
            result_paths[stations] = existing
            continue

        if docker is None:
            docker = find_docker()
        container_output_path = (
            f"/app/results/scaling/{output_path.name}"
        )
        env = os.environ.copy()
        env.update({
            "WORKERS": worker_addresses,
            "BENCHMARK_RUNS": str(runs),
            "CSV_PATH": container_output_path,
            "LOG_LEVEL": "WARNING",
        })
        compose = compose_base_command(docker, project_name)

        print(
            f"\n=== Distributed BFS: {stations} stations, {runs} runs ===",
            flush=True,
        )
        try:
            run_command(
                [*compose, "build", "worker-1", "coordinator"],
                env=env,
                dry_run=dry_run,
            )
            run_command(
                [
                    *compose,
                    "up",
                    "--abort-on-container-exit",
                    "--exit-code-from",
                    "coordinator",
                    "coordinator",
                    *worker_services,
                ],
                env=env,
                dry_run=dry_run,
            )
        finally:
            run_command(
                [*compose, "down", "--remove-orphans"],
                env=env,
                dry_run=dry_run,
            )
        result_paths[stations] = output_path
    return result_paths


def summarize_file(
    path,
    variant,
    workers,
    runs,
    time_column,
    expected_graphs,
    newest_input_mtime,
):
    result = inspect_result_file(
        path,
        workers,
        runs,
        time_column,
        expected_graphs,
        newest_input_mtime,
    )
    if result is None:
        return None

    return {
        "variant": variant,
        "workers": workers,
        **result,
        "source_csv": str(path.relative_to(ROOT_DIR)),
    }


def write_summary(
    parallel_results,
    distributed_results,
    runs,
    expected_graphs,
    newest_input_mtime,
):
    rows = []
    for processes, path in parallel_results.items():
        row = summarize_file(
            path,
            "parallel",
            processes,
            runs,
            "par_mean_s",
            expected_graphs,
            newest_input_mtime,
        )
        if row is not None:
            rows.append(row)

    for stations, path in distributed_results.items():
        row = summarize_file(
            path,
            "distributed",
            stations,
            runs,
            "dist_mean_s",
            expected_graphs,
            newest_input_mtime,
        )
        if row is not None:
            rows.append(row)

    if not rows:
        return

    summary_path = RESULTS_DIR / "scaling_summary.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nScaling summary: {summary_path}", flush=True)
    for row in rows:
        print(
            f"  {row['variant']:<11} workers={row['workers']:<2} "
            f"speedup={row['global_speedup']:.3f}x "
            f"correct={row['all_correct']}",
            flush=True,
        )


def main():
    args = parse_args()
    if args.parallel_only and args.distributed_only:
        raise SystemExit(
            "--parallel-only and --distributed-only cannot be used together."
        )

    process_counts = unique_positive(args.processes)
    station_counts = unique_positive(args.stations)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    graph_files = collect_graph_files()
    expected_graphs = len(graph_files)
    if expected_graphs == 0:
        raise SystemExit(
            "Nie znaleziono kompletnego zestawu grafów i plików expected. "
            "Uruchom najpierw generate_graphs.py."
        )
    newest_input_mtime = max(
        path.stat().st_mtime
        for graph_path, expected_path, _label in graph_files
        for path in (Path(graph_path), Path(expected_path))
    )

    parallel_results = {}
    distributed_results = {}
    if not args.distributed_only:
        parallel_results = run_parallel(
            process_counts,
            args.runs,
            args.dry_run,
            args.force,
            expected_graphs,
            newest_input_mtime,
        )
    if not args.parallel_only:
        distributed_results = run_distributed(
            station_counts,
            args.runs,
            args.dry_run,
            args.force,
            expected_graphs,
            newest_input_mtime,
        )
    if not args.dry_run:
        write_summary(
            parallel_results,
            distributed_results,
            args.runs,
            expected_graphs,
            newest_input_mtime,
        )


if __name__ == "__main__":
    main()
