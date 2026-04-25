import pickle
import struct
import socket


HEADER_SIZE = 4

def send_msg(sock, data):
    payload = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def recv_msg(sock):
    header = _recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None

    msg_len = struct.unpack("!I", header)[0]
    if msg_len == 0:
        return {}

    payload = _recv_exact(sock, msg_len)
    if payload is None:
        return None

    return pickle.loads(payload)


def _recv_exact(sock, num_bytes):
    chunks = []
    received = 0
    while received < num_bytes:
        chunk = sock.recv(min(num_bytes - received, 65536))
        if not chunk:
            return None
        chunks.append(chunk)
        received += len(chunk)
    return b"".join(chunks)
