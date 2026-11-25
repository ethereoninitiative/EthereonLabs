#!/usr/bin/env python3
"""Exercise real Linux Unix-socket credentials and a strictly bounded request."""
import json
import os
import socket
import threading

from hearth_broker_r1 import REQUEST, serve


def exchange(request, uid):
    client, server = socket.socketpair()
    results = []
    def run():
        with server:
            results.append(serve(server, uid))
    with client:
        client.settimeout(5)
        # Queue the request before the server can reject the peer.
        client.sendall(request)
        client.shutdown(socket.SHUT_WR)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        with client.makefile("rb") as stream:
            wire = json.loads(stream.readline(1025))
        thread.join(5)
        assert not thread.is_alive() and results == [wire]
        return wire


def main():
    uid = os.getuid()
    good = exchange(REQUEST, uid)
    checks = {
        "actual_disk_observation": good["status"] == "observed" and 0 <= good["free_bytes"] <= good["total_bytes"],
        "different_uid_denied": exchange(REQUEST, uid + 1)["reason"] == "peer_not_allowed",
        "unknown_operation_denied": exchange(b'{"version":1,"operation":"other"}\n', uid)["status"] == "denied",
        "caller_path_denied": exchange(b'{"version":1,"operation":"disk_status","path":"/tmp"}\n', uid)["status"] == "denied",
        "malformed_denied": exchange(b'not JSON\n', uid)["status"] == "denied",
        "trailing_request_denied": exchange(REQUEST * 2, uid)["status"] == "denied",
        "oversized_rejected": exchange(b'x' * 129, uid)["status"] == "unavailable",
        "no_mutation_authority": good["host_mutation_authority"] is False,
        "minimized_receipt": set(good) == {"schema", "status", "host_mutation_authority", "total_bytes", "free_bytes"},
    }
    print(json.dumps({"checks": checks, "passed": all(checks.values()), "systemd_tested": False}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
