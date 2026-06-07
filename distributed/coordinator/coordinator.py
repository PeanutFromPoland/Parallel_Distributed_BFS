import os
import sys
import time
import socket
import logging
import threading
from collections import deque
import cProfile

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

    raw_components = detect_components_bfs(graph)
    component_costs = [sum(len(graph.get(v, [])) for v in comp) for comp in raw_components]

    tasks = []
    for comp_vertices in raw_components:
        subgraph = extract_subgraph(graph, comp_vertices)
        start = min(comp_vertices)
        tasks.append((start, subgraph, comp_vertices))

    schedule = greedy_schedule(raw_components, num_workers, component_costs)

    results_lock = threading.Lock()
    all_results: list[tuple[int, dict[int, int]]] = []

    def worker_thread(w_idx: int, comp_indices: list[int]):
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

    total_time = time.perf_counter() - t0

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

    return all_results, total_time


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


def print_summary(results: list[dict], num_workers: int) -> None:
    print("\n" + "=" * 120)
    print("  PODSUMOWANIE — DISTRIBUTED BFS BENCHMARK")
    print("=" * 120)

    header = (
        f"{'Lp.':<5} {'Wierz.':<8} {'Kraw.':<10} "
        f"{'Sklad.':<8} "
        f"{'Seq [s]':<14} {'Dist [s]':<14} {'Speedup':<10} "
        f"{'Popr.':<8} {'Graf'}"
    )
    print(header)
    print("-" * 120)

    total_seq = 0.0
    total_dist = 0.0
    all_correct = True
    errors = []

    for i, r in enumerate(results, 1):
        speedup = r["seq_time"] / r["dist_time"] if r["dist_time"] > 0 else float("inf")
        status = "[OK]" if r["correct"] else "[BLAD]"

        print(
            f"{i:<5} {r['nodes']:<8} {r['edges']:<10} "
            f"{r['num_components']:<8} "
            f"{r['seq_time']:<14.6f} {r['dist_time']:<14.6f} {speedup:<10.2f} "
            f"{status:<8} {r['label']}"
        )

        total_seq += r["seq_time"]
        total_dist += r["dist_time"]

        if not r["correct"]:
            all_correct = False
            errors.append((r["label"], r["msg"]))

    print("-" * 120)
    total_speedup = total_seq / total_dist if total_dist > 0 else float("inf")
    print(f"\n  Workery:                          {num_workers}")
    print(f"  Łączny czas sekwencyjny:          {total_seq:.4f}s")
    print(f"  Łączny czas rozproszony:          {total_dist:.4f}s")
    print(f"  Łączny speedup:                   {total_speedup:.2f}x")
    print(f"  Liczba grafów:                    {len(results)}")

    if all_correct:
        print(f"\n  [OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE")
    else:
        print(f"\n  [BLAD] BLEDY W {len(errors)} GRAFACH:")
        for label, msg in errors:
            print(f"    - {label}: {msg}")

    print("=" * 120)


def main():
    num_workers = len(WORKER_ADDRESSES)

    print("=" * 100)
    print("  DISTRIBUTED BFS — COORDINATOR")
    print(f"  Workerów: {num_workers}")
    print(f"  Adresy: {', '.join(f'{h}:{p}' for h, p in WORKER_ADDRESSES)}")
    print(f"  Katalog grafów: {GRAPHS_DIR}")
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

            t0 = time.perf_counter()
            seq_components = sequential_bfs(graph)
            seq_time = time.perf_counter() - t0

            dist_components, dist_time = distributed_bfs(graph, worker_sockets)

            expected_components = load_expected(expected_path)
            correct, msg = verify_bfs(dist_components, expected_components)

            speedup = seq_time / dist_time if dist_time > 0 else float("inf")
            status = "OK" if correct else f"BLAD: {msg}"
            log.info(
                "seq=%.4fs  dist=%.4fs  speedup=%.2fx  %s",
                seq_time, dist_time, speedup, status,
            )

            all_results.append({
                "label": label,
                "nodes": num_nodes,
                "edges": num_edges,
                "num_components": len(dist_components),
                "seq_time": seq_time,
                "dist_time": dist_time,
                "correct": correct,
                "msg": msg,
            })

        print_summary(all_results, num_workers)

    finally:
        log.info("Wysyłanie SHUTDOWN do workerów...")
        for sock in worker_sockets:
            shutdown_worker(sock)
        log.info("Coordinator zakończony")


if __name__ == "__main__":
    cProfile.run("main()")
