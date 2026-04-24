"""
Worker BFS — proces roboczy rozproszonego algorytmu BFS.

Nasłuchuje na porcie TCP (domyślnie 5000), odbiera podgrafy od koordynatora,
wykonuje sekwencyjny BFS (kolejka FIFO) i odsyła tablice odległości.

Protokół komunikacji:
    1. Koordynator łączy się i wysyła wiadomość typu "task" lub "shutdown"
    2. Worker wykonuje BFS i odsyła wynik typu "result"
    3. Worker czeka na kolejne zadanie lub zamyka się po "shutdown"

Uruchomienie:
    python worker.py
"""

import os
import sys
import socket
import logging
from collections import deque

# Dodaj ścieżkę do shared/ (montowane w Dockerfile)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from shared.protocol import send_msg, recv_msg

# ─── Konfiguracja ────────────────────────────────────────────────────
WORKER_PORT = int(os.environ.get("WORKER_PORT", "5000"))
WORKER_NAME = os.environ.get("HOSTNAME", "worker-?")

logging.basicConfig(
    level=logging.INFO,
    format=f"[{WORKER_NAME}] %(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─── BFS ─────────────────────────────────────────────────────────────
def bfs(graph: dict[int, list[int]], start: int) -> dict[int, int]:
    """
    Klasyczny sekwencyjny BFS od wierzchołka 'start'.

    Parametry:
        graph : dict[int, list[int]] — lista sąsiedztwa (klucze = int)
        start : int — wierzchołek startowy

    Zwraca:
        dict[int, int] — {node: distance} dla wszystkich wierzchołków
                         osiągalnych od start
    """
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in sorted(graph.get(node, [])):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


# ─── Obsługa połączenia ──────────────────────────────────────────────
def handle_connection(conn: socket.socket, addr: tuple) -> bool:
    """
    Obsługuje pojedyncze połączenie od koordynatora.
    Może obsłużyć wiele zadań w ramach jednego połączenia.

    Zwraca:
        True  — kontynuuj nasłuchiwanie (zadanie wykonane, połączenie zamknięte)
        False — zakończ workera (otrzymano shutdown)
    """
    log.info("Połączenie od koordynatora %s", addr)

    try:
        while True:
            msg = recv_msg(conn)
            if msg is None:
                log.info("Koordynator zamknął połączenie")
                return True

            msg_type = msg.get("type", "")

            if msg_type == "shutdown":
                log.info("Otrzymano SHUTDOWN — zamykanie workera")
                return False

            elif msg_type == "task":
                # Deserializacja podgrafu (klucze JSON to stringi → konwersja na int)
                raw_graph = msg["subgraph"]
                subgraph = {
                    int(k): [int(v) for v in vs]
                    for k, vs in raw_graph.items()
                }
                start = int(msg["start"])
                num_vertices = len(subgraph)
                num_edges = sum(len(n) for n in subgraph.values())

                log.info(
                    "Zadanie: BFS od wierzchołka %d (%d wierzch., %d krawędzi)",
                    start, num_vertices, num_edges,
                )

                # Wykonanie BFS
                dist = bfs(subgraph, start)

                log.info(
                    "BFS zakończony — odwiedzono %d wierzchołków",
                    len(dist),
                )

                # Odesłanie wyniku
                # Konwersja kluczy int → str (JSON wymaga kluczy string)
                result = {
                    "type": "result",
                    "start": start,
                    "dist": {str(k): v for k, v in dist.items()},
                }
                send_msg(conn, result)
                log.info("Wynik odesłany do koordynatora")

            else:
                log.warning("Nieznany typ wiadomości: %s", msg_type)

    except Exception as e:
        log.error("Błąd obsługi połączenia: %s", e, exc_info=True)
        return True
    finally:
        conn.close()


# ─── Serwer TCP ──────────────────────────────────────────────────────
def main():
    log.info("Uruchamianie workera na porcie %d...", WORKER_PORT)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", WORKER_PORT))
    server.listen(1)

    log.info("Worker gotowy — nasłuchuje na 0.0.0.0:%d", WORKER_PORT)

    try:
        while True:
            conn, addr = server.accept()
            should_continue = handle_connection(conn, addr)
            if not should_continue:
                break
    except KeyboardInterrupt:
        log.info("Przerwano (Ctrl+C)")
    finally:
        server.close()
        log.info("Worker zamknięty")


if __name__ == "__main__":
    main()
