#!/usr/bin/env python3
"""Hearth Linux read-only broker; systemd supplies one connected Unix socket."""
import argparse
import json
import os
import pwd
import shutil
import socket
import struct
import sys
import time

REQUEST = b'{"version":1,"operation":"disk_status"}\n'
SOCKET_PATH = "/run/lumina-hearth.sock"
MAX_REQUEST = 128


def peer_uid(conn):
    if conn.family != socket.AF_UNIX or conn.type != socket.SOCK_STREAM:
        raise ValueError("expected Unix stream")
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    return struct.unpack("3i", raw)[1]


def read_request(conn):
    deadline = time.monotonic() + 2
    data = bytearray()
    while len(data) <= MAX_REQUEST:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("request deadline")
        conn.settimeout(remaining)
        chunk = conn.recv(MAX_REQUEST + 1 - len(data))
        if not chunk:
            return bytes(data)
        data.extend(chunk)
    raise ValueError("request too large")


def reply(conn, status, **fields):
    payload = {"schema": "hearth-broker-receipt-r1", "status": status,
               "host_mutation_authority": False, **fields}
    conn.settimeout(2)
    try:
        conn.sendall((json.dumps(payload, separators=(",", ":")) + "\n").encode())
    except OSError:
        pass
    return payload


def serve(conn, allowed_uid):
    try:
        if peer_uid(conn) != allowed_uid:
            return reply(conn, "denied", reason="peer_not_allowed")
        if read_request(conn) != REQUEST:
            return reply(conn, "denied", reason="invalid_request")
        usage = shutil.disk_usage("/")
        if usage.total <= 0 or not 0 <= usage.free <= usage.total:
            return reply(conn, "unavailable", reason="invalid_measurement")
        return reply(conn, "observed", total_bytes=usage.total, free_bytes=usage.free)
    except (OSError, ValueError, struct.error):
        return reply(conn, "unavailable", reason="request_or_probe_failed")


def query():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(5)
        conn.connect(SOCKET_PATH)
        conn.sendall(REQUEST)
        conn.shutdown(socket.SHUT_WR)
        with conn.makefile("rb") as stream:
            data = stream.readline(1025)
        if not data.endswith(b"\n") or len(data) > 1024:
            raise ValueError("invalid receipt framing")
        receipt = json.loads(data)
        if not isinstance(receipt, dict) or receipt.get("schema") != "hearth-broker-receipt-r1" or receipt.get("host_mutation_authority") is not False:
            raise ValueError("invalid receipt")
        return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    server = sub.add_parser("serve-stdio")
    server.add_argument("--allowed-user", required=True)
    sub.add_parser("query")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Linux required")
    try:
        if args.command == "serve-stdio":
            uid = pwd.getpwnam(args.allowed_user).pw_uid
            # No direct root service or authorization of root clients.
            if os.geteuid() == 0 or uid == 0 or uid == os.geteuid():
                parser.error("broker and client require distinct non-root accounts")
            with socket.socket(fileno=os.dup(0)) as conn:
                receipt = serve(conn, uid)
        else:
            receipt = query()
            print(json.dumps(receipt, indent=2))
        return 0 if receipt.get("status") == "observed" else 1
    except (OSError, KeyError, ValueError):
        print("Hearth broker unavailable", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
