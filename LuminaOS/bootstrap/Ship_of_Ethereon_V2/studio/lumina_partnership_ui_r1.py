#!/usr/bin/env python3
"""Loopback-only human-facing project board for the Lumina Partnership R1 store."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import webbrowser

HTML_PATH = Path(__file__).with_name("lumina_partnership_r1.html")


def make_handler(workspace, project: str, token: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "LuminaPartnership/1"

        def send_payload(self, status: int, data: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                             "style-src 'self' 'unsafe-inline'; object-src 'none'; "
                             "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def as_json(self, status: int, payload: dict) -> None:
            self.send_payload(status, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")

        def path_only(self) -> str:
            return urlsplit(self.path).path

        def host_allowed(self) -> bool:
            # Reject DNS rebinding and non-loopback Host headers.
            allowed = {f"127.0.0.1:{self.server.server_port}",
                       f"localhost:{self.server.server_port}"}
            return self.headers.get("Host") in allowed

        def do_GET(self) -> None:
            if not self.host_allowed():
                return self.as_json(403, {"error": "invalid localhost host"})
            path = self.path_only()
            if path == "/":
                page = HTML_PATH.read_text(encoding="utf-8").replace("__LUMINA_CSRF_TOKEN__", token)
                return self.send_payload(200, page.encode("utf-8"), "text/html; charset=utf-8")
            if path == "/api/board":
                return self.as_json(200, workspace.board(project))
            if path == "/health":
                return self.as_json(200, {"ok": True, "project": project, "listen": "loopback"})
            return self.as_json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if not self.host_allowed():
                return self.as_json(403, {"error": "invalid localhost host"})
            origin = self.headers.get("Origin")
            allowed_origin = {
                f"http://127.0.0.1:{self.server.server_port}",
                f"http://localhost:{self.server.server_port}",
            }
            if origin is not None and origin not in allowed_origin:
                return self.as_json(403, {"error": "foreign origin denied"})
            if self.headers.get("Sec-Fetch-Site", "same-origin") not in ("same-origin", "none"):
                return self.as_json(403, {"error": "cross-site request denied"})
            if not secrets.compare_digest(self.headers.get("X-Lumina-Intent", ""), token):
                return self.as_json(403, {"error": "local intent token required"})
            if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                return self.as_json(415, {"error": "JSON required"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 16000:
                    return self.as_json(413, {"error": "payload size out of range"})
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError("expected JSON object")
                path = self.path_only()
                if path == "/api/task":
                    result = workspace.add_task(project, str(data.get("title", "")), str(data.get("detail", "")))
                elif path == "/api/decide":
                    result = workspace.decide(project, str(data.get("id", "")), str(data.get("decision", "")))
                elif path == "/api/done":
                    result = workspace.complete(project, str(data.get("id", "")))
                else:
                    return self.as_json(404, {"error": "not found"})
                self.as_json(200, {"ok": True, "result": result})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.as_json(400, {"error": str(exc)})
            except Exception:
                self.as_json(500, {"error": "local workspace request failed"})

        def log_message(self, format: str, *args) -> None:
            # Avoid logging task text, agent proposals, or state to the console.
            return

    return Handler


def serve(workspace, project: str, port: int = 8768, *, open_browser: bool = True) -> None:
    if not 1 <= port <= 65535:
        raise ValueError("port must be 1-65535")
    token = secrets.token_urlsafe(32)
    with ThreadingHTTPServer(("127.0.0.1", port), make_handler(workspace, project, token)) as server:
        server.daemon_threads = True
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Lumina Partnership R1 (local only): {url}", flush=True)
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
