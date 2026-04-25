import os
import sys
import socket
import logging
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from shared.protocol import send_msg, recv_msg

WORKER_PORT = int(os.environ.get("WORKER_PORT", "5000"))
WORKER_NAME = os.environ.get("HOSTNAME", "worker-?")

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "WARNING").upper(), logging.WARNING),
    format=f"[{WORKER_NAME}] %(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

def bfs(graph, start):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


def handle_connection(conn, addr):
    log.debug("Połączenie od koordynatora %s", addr)

    try:
        while True:
            msg = recv_msg(conn)
            if msg is None:
                log.debug("Koordynator zamknął połączenie")
                return True

            msg_type = msg.get("type", "")

            if msg_type == "shutdown":
                log.debug("Otrzymano SHUTDOWN — zamykanie workera")
                return False

            elif msg_type == "task":
                subgraph = msg["subgraph"]
                start = int(msg["start"])
                num_vertices = len(subgraph)
                num_edges = sum(len(n) for n in subgraph.values())

                log.debug(
                    "Zadanie: BFS od wierzchołka %d (%d wierzch., %d krawędzi)",
                    start, num_vertices, num_edges,
                )

                # Wykonanie BFS
                dist = bfs(subgraph, start)

                log.debug(
                    "BFS zakończony — odwiedzono %d wierzchołków",
                    len(dist),
                )

                result = {
                    "type": "result",
                    "start": start,
                    "dist": dist,
                }
                send_msg(conn, result)
                log.debug("Wynik odesłany do koordynatora")

            else:
                log.warning("Nieznany typ wiadomości: %s", msg_type)

    except Exception as e:
        log.error("Błąd obsługi połączenia: %s", e, exc_info=True)
        return True
    finally:
        conn.close()


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
