"""Sea trial for the Lumina Bridge browser boundary.

This trial verifies the narrow browser-facing contract:
- approved origins receive CORS headers;
- localhost origins are allowed for local development;
- unknown origins are rejected;
- the Bridge supports read-only OPTIONS/GET;
- POST remains explicitly rejected.
"""

from __future__ import annotations

import json
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from threading import Thread

from studio.lumina_bridge_server_r1 import (
    LuminaBridgeHandler,
    cors_origin_for,
)


def run() -> dict[str, object]:
    assert cors_origin_for("https://app.ethereonlabs.com") == "https://app.ethereonlabs.com"
    assert cors_origin_for("http://localhost:3000") == "http://localhost:3000"
    assert cors_origin_for("https://not-ethereon.example") is None
    assert cors_origin_for(None) is None

    server = ThreadingHTTPServer(("127.0.0.1", 0), LuminaBridgeHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)

    try:
        connection.request(
            "OPTIONS",
            "/api/bridge",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Private-Network": "true",
            },
        )
        options = connection.getresponse()
        assert options.status == 204
        assert options.getheader("Access-Control-Allow-Origin") == "http://localhost:3000"
        assert options.getheader("Access-Control-Allow-Methods") == "GET, OPTIONS"
        assert options.getheader("Access-Control-Allow-Private-Network") == "true"
        options.read()

        connection.request(
            "GET",
            "/api/boundary",
            headers={"Origin": "https://app.ethereonlabs.com"},
        )
        boundary = connection.getresponse()
        assert boundary.status == 200
        assert boundary.getheader("Access-Control-Allow-Origin") == "https://app.ethereonlabs.com"
        payload = json.loads(boundary.read().decode("utf-8"))
        assert "authority_boundary" in payload

        connection.request(
            "POST",
            "/api/bridge",
            headers={"Origin": "https://app.ethereonlabs.com"},
        )
        post = connection.getresponse()
        assert post.status == 405
        assert post.getheader("Access-Control-Allow-Origin") == "https://app.ethereonlabs.com"
        post.read()
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    return {
        "ok": True,
        "approved_public_origin": True,
        "approved_local_origin": True,
        "unknown_origin_rejected": True,
        "options_read_only_boundary": True,
        "post_rejected": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
