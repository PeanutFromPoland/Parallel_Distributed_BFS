import os
import sys
import time
import socket
import logging
import threading
import csv
import statistics
from collections import deque
import cProfile
import pstats
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from graph_loader import load_graph, load_expected, collect_graph_files
from component_detector import (
    detect_components_bfs,
    extract_subgraph,
    greedy_schedule,
)
from shared.protocol import send_msg, recv_msg

GRAPHS_DIR = os.environ.get("GRAPHS_DIR", "/app/graphs")
WORKERS_ENV = os.environ.get("WORKERS", "worker-1:5000,worker-2:5000,worker-3:5000")
WORKER_ADDRESSES = [
    tuple(w.strip().split(":")) for w in WORKERS_ENV.split(",")
]
WORKER_ADDRESSES = [(host, int(port)) for host, port in WORKER_ADDRESSES]

MAX_CONNECT_RETRIES = 30
CONNECT_RETRY_DELAY = 2.0
BENCHMARK_RUNS = int(os.environ.get("BENCHMARK_RUNS", "3"))
RESULTS_DIR = os.environ.get("RESULTS_DIR", "/app/results")
CSV_PATH = os.environ.get(
    "CSV_PATH",
    os.path.join(RESULTS_DIR, "distributed_bfs_results.csv"),
)
PROFILE_PATH = os.environ.get(
    "PROFILE_PATH",
    os.path.join(RESULTS_DIR, "coordinator.prof"),
)

if BENCHMARK_RUNS < 1:
    raise ValueError("BENCHMARK_RUNS musi być >= 1")

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "WARNING").upper(), logging.WARNING),
    format="[COORDINATOR] %(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def sequential_bfs(graph):
    visited = set()
    components = []

    for start in sorted(graph.keys()):
        if start in visited:
            continue
        dist = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nb in graph.get(node, []):
                if nb not in dist:
                    dist[nb] = dist[node] + 1
                    queue.append(nb)
        visited.update(dist.keys())
        components.append((start, dist))

    return components


def connect_to_worker(host, port):
    for attempt in range(1, MAX_CONNECT_RETRIES + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((host, port))
            sock.settimeout(None)
            log.info("Połączono z workerem %s:%d (próba %d)", host, port, attempt)
            return sock
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            if attempt < MAX_CONNECT_RETRIES:
                log.debug(
                    "Worker %s:%d niedostępny (próba %d/%d): %s",
                    host, port, attempt, MAX_CONNECT_RETRIES, e,
                )
                time.sleep(CONNECT_RETRY_DELAY)
            else:
                log.error("Nie udało się połączyć z %s:%d po %d próbach", host, port, MAX_CONNECT_RETRIES)
                raise


def send_task_and_recv_result(sock, subgraph, start):
    task = {
        "type": "task",
        "subgraph": subgraph,
        "start": start,
    }
    send_msg(sock, task)

    result = recv_msg(sock)
    if result is None:
        raise ConnectionError("Worker zamknął połączenie przed wysłaniem wyniku")

    return result["dist"]


def shutdown_worker(sock):
    try:
        send_msg(sock, {"type": "shutdown"})
    except Exception:
        pass
    finally:
        try:
            sock.close()
        except Exception:
            pass


def distributed_bfs(graph, worker_sockets):
    num_workers = len(worker_sockets)

    t0 = time.perf_counter()

    phase_start = time.perf_counter()
    raw_components = detect_components_bfs(graph)
    component_costs = [sum(len(graph.get(v, [])) for v in comp) for comp in raw_components]
    detection_time = time.perf_counter() - phase_start

    phase_start = time.perf_counter()
    tasks = []
    for comp_vertices in raw_components:
        subgraph = extract_subgraph(graph, comp_vertices)
        start = min(comp_vertices)
        tasks.append((start, subgraph, comp_vertices))
    preparation_time = time.perf_counter() - phase_start

    phase_start = time.perf_counter()
    schedule = greedy_schedule(raw_components, num_workers, component_costs)
    scheduling_time = time.perf_counter() - phase_start

    results_lock = threading.Lock()
    all_results: list[tuple[int, dict[int, int]]] = []
    worker_errors = []

    def worker_thread(w_idx: int, comp_indices: list[int]):
        try:
            sock = worker_sockets[w_idx]
            for comp_idx in comp_indices:
                start, subgraph, _vertices = tasks[comp_idx]
                log.debug(
                    "Wysyłanie składowej %d (start=%d, %d wierzch.) → worker %d",
                    comp_idx, start, len(subgraph), w_idx,
                )
                dist = send_task_and_recv_result(sock, subgraph, start)
                with results_lock:
                    all_results.append((start, dist))
        except Exception as exc:
            with results_lock:
                worker_errors.append((w_idx, exc))

    execution_start = time.perf_counter()
    threads = []
    for w_idx, comp_indices in enumerate(schedule):
        if comp_indices:
            t = threading.Thread(
                target=worker_thread, args=(w_idx, comp_indices), daemon=True,
            )
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    execution_time = time.perf_counter() - execution_start
    total_time = time.perf_counter() - t0

    if worker_errors:
        worker_idx, error = worker_errors[0]
        raise RuntimeError(f"Worker {worker_idx} failed: {error}") from error

    all_results.sort(key=lambda x: x[0])

    log.info(
        "Wykryto %d składowych spójności (%s wierzchołków)",
        len(raw_components),
        ", ".join(str(len(c)) for c in raw_components),
    )
    for w_idx, comp_indices in enumerate(schedule):
        if comp_indices:
            comp_sizes = [len(raw_components[ci]) for ci in comp_indices]
            comp_edges = [component_costs[ci] for ci in comp_indices]
            log.info(
                "Worker %d: %d składowych, wierzch.=%s, kraw.=%s",
                w_idx,
                len(comp_indices),
                " + ".join(str(s) for s in comp_sizes),
                " + ".join(str(e) for e in comp_edges),
            )

    profile = {
        "detection_time": detection_time,
        "preparation_time": preparation_time,
        "scheduling_time": scheduling_time,
        "execution_time": execution_time,
        "total_time": total_time,
    }
    return all_results, profile


def verify_bfs(
    actual: list[tuple[int, dict[int, int]]],
    expected: list[tuple[int, dict[int, int]]],
) -> tuple[bool, str]:
    if len(actual) != len(expected):
        return False, (
            f"Liczba komponentów: {len(actual)} (oczekiwano {len(expected)})"
        )

    for i, ((a_start, a_dist), (e_start, e_dist)) in enumerate(
        zip(actual, expected)
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
                return False, f"Komponent {i}: wierzchołek {node} nie odwiedzony"
            if actual_d != expected_d:
                return False, (
                    f"Komponent {i}: wierzchołek {node}: "
                    f"dist={actual_d} (oczekiwano {expected_d})"
                )

    return True, "OK"


def timing_stats(values):
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def export_csv(path, results, num_workers, runs):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    phases = ("detection", "preparation", "scheduling", "execution")
    fields = [
        "record_type",
        "generated_at_utc",
        "label",
        "graph_path",
        "nodes",
        "edges",
        "components",
        "workers",
        "configured_runs",
        "run",
        "seq_time_s",
        "dist_time_s",
        "detection_time_s",
        "preparation_time_s",
        "scheduling_time_s",
        "execution_time_s",
        "speedup",
        "seq_mean_s",
        "seq_median_s",
        "seq_min_s",
        "seq_max_s",
        "seq_stdev_s",
        "dist_mean_s",
        "dist_median_s",
        "dist_min_s",
        "dist_max_s",
        "dist_stdev_s",
    ]
    for phase in phases:
        fields.extend([
            f"{phase}_mean_s",
            f"{phase}_median_s",
            f"{phase}_min_s",
            f"{phase}_max_s",
            f"{phase}_stdev_s",
        ])
    fields.extend(["mean_speedup", "correct", "message"])

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
                "components": result["num_components"],
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
                    "dist_time_s": trial["dist_time"],
                    "detection_time_s": trial["detection_time"],
                    "preparation_time_s": trial["preparation_time"],
                    "scheduling_time_s": trial["scheduling_time"],
                    "execution_time_s": trial["execution_time"],
                    "speedup": trial["speedup"],
                })

            row = {
                **base,
                "record_type": "summary",
                "mean_speedup": (
                    result["seq_stats"]["mean"] / result["dist_stats"]["mean"]
                    if result["dist_stats"]["mean"] > 0
                    else float("inf")
                ),
            }
            for prefix, stats in (
                ("seq", result["seq_stats"]),
                ("dist", result["dist_stats"]),
            ):
                for stat_name, value in stats.items():
                    row[f"{prefix}_{stat_name}_s"] = value
            for phase in phases:
                for stat_name, value in result["phase_stats"][phase].items():
                    row[f"{phase}_{stat_name}_s"] = value
            writer.writerow(row)


def print_summary(results: list[dict], num_workers: int, runs: int) -> None:
    print("\n" + "=" * 138)
    print("  PODSUMOWANIE — DISTRIBUTED BFS BENCHMARK")
    print("=" * 138)

    header = (
        f"{'Lp.':<5} {'Wierz.':<8} {'Kraw.':<10} "
        f"{'Sklad.':<8} "
        f"{'Seq avg [s]':<14} {'Seq sd':<11} "
        f"{'Dist avg [s]':<14} {'Dist sd':<11} {'Speedup':<10} "
        f"{'Popr.':<8} {'Graf'}"
    )
    print(header)
    print("-" * 138)

    total_seq = 0.0
    total_dist = 0.0
    all_correct = True
    errors = []

    for i, r in enumerate(results, 1):
        seq_mean = r["seq_stats"]["mean"]
        dist_mean = r["dist_stats"]["mean"]
        speedup = seq_mean / dist_mean if dist_mean > 0 else float("inf")
        status = "[OK]" if r["correct"] else "[BLAD]"

        print(
            f"{i:<5} {r['nodes']:<8} {r['edges']:<10} "
            f"{r['num_components']:<8} "
            f"{seq_mean:<14.6f} {r['seq_stats']['stdev']:<11.6f} "
            f"{dist_mean:<14.6f} {r['dist_stats']['stdev']:<11.6f} "
            f"{speedup:<10.2f} "
            f"{status:<8} {r['label']}"
        )

        total_seq += seq_mean
        total_dist += dist_mean

        if not r["correct"]:
            all_correct = False
            errors.append((r["label"], r["msg"]))

    print("-" * 138)
    total_speedup = total_seq / total_dist if total_dist > 0 else float("inf")
    print(f"\n  Workery:                          {num_workers}")
    print(f"  Powtórzenia na graf:              {runs}")
    print(f"  Suma średnich czasów sekw.:       {total_seq:.4f}s")
    print(f"  Suma średnich czasów rozpr.:      {total_dist:.4f}s")
    print(f"  Łączny speedup ze średnich:       {total_speedup:.2f}x")
    print(f"  Liczba grafów:                    {len(results)}")
    print(f"  Łączna liczba prób:               {len(results) * runs}")

    if all_correct:
        print(f"\n  [OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE")
    else:
        print(f"\n  [BLAD] BLEDY W {len(errors)} GRAFACH:")
        for label, msg in errors:
            print(f"    - {label}: {msg}")

    print("=" * 138)


def main():
    num_workers = len(WORKER_ADDRESSES)

    print("=" * 100)
    print("  DISTRIBUTED BFS — COORDINATOR")
    print(f"  Workerów: {num_workers}")
    print(f"  Adresy: {', '.join(f'{h}:{p}' for h, p in WORKER_ADDRESSES)}")
    print(f"  Katalog grafów: {GRAPHS_DIR}")
    print(f"  Powtórzenia na graf: {BENCHMARK_RUNS}")
    print(f"  CSV: {CSV_PATH}")
    print(f"  Profil cProfile: {PROFILE_PATH}")
    print("=" * 100)

    graph_files = collect_graph_files(GRAPHS_DIR)
    if not graph_files:
        log.error("Brak grafów w %s! Uruchom najpierw generate_graphs.py", GRAPHS_DIR)
        sys.exit(1)

    log.info("Znaleziono %d grafów", len(graph_files))

    log.info("Łączenie z workerami...")
    worker_sockets = []
    try:
        for host, port in WORKER_ADDRESSES:
            sock = connect_to_worker(host, port)
            worker_sockets.append(sock)

        log.info("Wszystkie workery połączone!")

        all_results = []

        for graph_path, expected_path, label in graph_files:
            log.info("─" * 60)
            log.info("Graf: %s", label)

            graph = load_graph(graph_path)
            num_nodes = len(graph)
            num_edges = sum(len(n) for n in graph.values())
            expected_components = load_expected(expected_path)
            trials = []
            graph_correct = True
            messages = []
            num_components = len(expected_components)

            for run_number in range(1, BENCHMARK_RUNS + 1):
                t0 = time.perf_counter()
                seq_components = sequential_bfs(graph)
                seq_time = time.perf_counter() - t0

                dist_components, dist_profile = distributed_bfs(
                    graph,
                    worker_sockets,
                )
                dist_time = dist_profile["total_time"]
                num_components = len(dist_components)

                seq_correct, seq_msg = verify_bfs(
                    seq_components,
                    expected_components,
                )
                dist_correct, dist_msg = verify_bfs(
                    dist_components,
                    expected_components,
                )
                correct = seq_correct and dist_correct
                if not correct:
                    graph_correct = False
                    messages.append(
                        f"run {run_number}: seq={seq_msg}; dist={dist_msg}"
                    )

                speedup = seq_time / dist_time if dist_time > 0 else float("inf")
                status = "OK" if correct else "BLAD"
                log.info(
                    "run=%d/%d seq=%.6fs dist=%.6fs speedup=%.2fx "
                    "detect=%.6fs prepare=%.6fs schedule=%.6fs "
                    "execute=%.6fs %s",
                    run_number,
                    BENCHMARK_RUNS,
                    seq_time,
                    dist_time,
                    speedup,
                    dist_profile["detection_time"],
                    dist_profile["preparation_time"],
                    dist_profile["scheduling_time"],
                    dist_profile["execution_time"],
                    status,
                )
                trials.append({
                    "run": run_number,
                    "seq_time": seq_time,
                    "dist_time": dist_time,
                    "detection_time": dist_profile["detection_time"],
                    "preparation_time": dist_profile["preparation_time"],
                    "scheduling_time": dist_profile["scheduling_time"],
                    "execution_time": dist_profile["execution_time"],
                    "speedup": speedup,
                })

            all_results.append({
                "label": label,
                "graph_path": os.path.abspath(graph_path),
                "nodes": num_nodes,
                "edges": num_edges,
                "num_components": num_components,
                "trials": trials,
                "seq_stats": timing_stats([
                    trial["seq_time"] for trial in trials
                ]),
                "dist_stats": timing_stats([
                    trial["dist_time"] for trial in trials
                ]),
                "phase_stats": {
                    phase: timing_stats([
                        trial[f"{phase}_time"] for trial in trials
                    ])
                    for phase in (
                        "detection",
                        "preparation",
                        "scheduling",
                        "execution",
                    )
                },
                "correct": graph_correct,
                "msg": " | ".join(messages) if messages else "OK",
            })

        print_summary(all_results, num_workers, BENCHMARK_RUNS)
        export_csv(CSV_PATH, all_results, num_workers, BENCHMARK_RUNS)
        print(f"\n  Wyniki CSV zapisano w: {CSV_PATH}")

    finally:
        log.info("Wysyłanie SHUTDOWN do workerów...")
        for sock in worker_sockets:
            shutdown_worker(sock)
        log.info("Coordinator zakończony")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(os.path.abspath(PROFILE_PATH)), exist_ok=True)
    profiler = cProfile.Profile()
    try:
        profiler.enable()
        main()
    finally:
        profiler.disable()
        profiler.dump_stats(PROFILE_PATH)
        print(f"\n  Profil cProfile zapisano w: {PROFILE_PATH}")
        pstats.Stats(profiler).sort_stats("cumulative").print_stats(40)
