"""
Protokół komunikacji TCP dla rozproszonego BFS.

Format wiadomości:
    <4 bajty długości (big-endian)><JSON payload>

Obsługuje fragmentację TCP — odczyt w pętli aż do pełnego komunikatu.
"""

import json
import struct
import socket


HEADER_SIZE = 4  # 4 bajty na długość wiadomości (big-endian unsigned int)


def send_msg(sock: socket.socket, data: dict) -> None:
    """
    Serializuje słownik do JSON i wysyła przez TCP z nagłówkiem długości.

    Parametry:
        sock : połączony socket TCP
        data : słownik do wysłania
    """
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def recv_msg(sock: socket.socket) -> dict | None:
    """
    Odbiera wiadomość TCP z nagłówkiem długości i deserializuje JSON.

    Zwraca:
        dict z danymi lub None jeśli połączenie zostało zamknięte.
    """
    header = _recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None

    msg_len = struct.unpack("!I", header)[0]
    if msg_len == 0:
        return {}

    payload = _recv_exact(sock, msg_len)
    if payload is None:
        return None

    return json.loads(payload.decode("utf-8"))


def _recv_exact(sock: socket.socket, num_bytes: int) -> bytes | None:
    """
    Odbiera dokładnie 'num_bytes' bajtów z socketa.
    Obsługuje fragmentację TCP (wielokrotne read).

    Zwraca:
        bytes lub None jeśli połączenie zamknięte przedwcześnie.
    """
    chunks = []
    received = 0
    while received < num_bytes:
        chunk = sock.recv(min(num_bytes - received, 65536))
        if not chunk:
            return None
        chunks.append(chunk)
        received += len(chunk)
    return b"".join(chunks)
