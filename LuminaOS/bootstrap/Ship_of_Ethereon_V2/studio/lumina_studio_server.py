#!/usr/bin/env python3
"""Lumina Studio Server v0.1.

Tiny local HTTP control surface for the governed Lumina runtime.
This is deliberately plain: standard library only, local-first, and subordinate
to RuntimeRunner. It is not a public Chamber surface and not a governance owner.
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

STUDIO_ROOT = Path(__file__).resolve().parent
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

from lumina_cli import DEFAULT_FEATURE_FLAGS, compact_receipt, run_lumina_cycle  # noqa: E402


HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Lumina Studio v0.1</title>
  <style>
    :root { color-scheme: dark; }
    body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; background: #07111f; color: #eaf2ff; }
    main { max-width: 980px; margin: 0 auto; padding: 32px 20px 48px; }
    h1 { margin: 0 0 6px; font-size: clamp(2rem, 5vw, 4rem); letter-spacing: -0.06em; }
    .kicker { color: #f6c96b; text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.78rem; }
    .sub { max-width: 780px; color: #b9c7dc; line-height: 1.55; }
    form { display: grid; gap: 16px; margin-top: 28px; background: rgba(255,255,255,0.045); border: 1px solid rgba(255,255,255,0.12); border-radius: 22px; padding: 22px; box-shadow: 0 24px 80px rgba(0,0,0,0.35); }
    label { display: grid; gap: 6px; color: #cbd8ec; font-size: 0.92rem; }
    input, textarea, select { width: 100%; box-sizing: border-box; border-radius: 12px; border: 1px solid rgba(255,255,255,0.16); background: rgba(0,0,0,0.25); color: #f7fbff; padding: 11px 12px; font: inherit; }
    textarea { min-height: 130px; resize: vertical; }
    .grid { display: grid; gap: 14px; grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    button { justify-self: start; border: 0; border-radius: 999px; padding: 12px 18px; font-weight: 700; background: linear-gradient(135deg, #f6c96b, #fff1b5); color: #111522; cursor: pointer; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.12); border-radius: 18px; padding: 18px; margin-top: 20px; color: #dbe8ff; }
    .receipt { margin-top: 24px; }
    .note { color: #8fa4c3; font-size: 0.9rem; }
    @media (max-width: 760px) { .grid, .grid.two { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main>
    <div class=\"kicker\">Local control surface · governed runtime</div>
    <h1>Lumina Studio v0.1</h1>
    <p class=\"sub\">Run one Lumina cycle through the existing runtime spine. Studio only packages the request and displays the receipt; mode legality, mutation gates, input integrity, capability exposure, checkpoints, and governance history remain owned by the runtime.</p>
    <form method=\"post\" action=\"/run\">
      <label>Operator request
        <textarea name=\"prompt\" required>Review Lumina OS progress and produce the next governed action receipt.</textarea>
      </label>
      <div class=\"grid\">
        <label>Current mode
          <select name=\"current_mode\"><option>Continuity</option><option>Observation</option><option>Sandbox</option><option>DryDock</option><option>Canon</option></select>
        </label>
        <label>Target mode
          <select name=\"target_mode\"><option selected>Observation</option><option>Continuity</option><option>Sandbox</option><option>DryDock</option><option>Canon</option></select>
        </label>
        <label>Action type
          <select name=\"action_type\"><option selected>audit</option><option>transition</option><option>mutation</option><option>promotion</option></select>
        </label>
      </div>
      <div class=\"grid\">
        <label>Focus
          <select name=\"focus\"><option>architecture</option><option selected>continuity</option><option>expression</option><option>integration</option><option>governance_review</option></select>
        </label>
        <label>Depth
          <select name=\"depth\"><option>surface</option><option selected>structural</option><option>foundational</option></select>
        </label>
        <label>Intent
          <select name=\"intent\"><option>read</option><option>build</option><option selected>verify</option><option>compose</option></select>
        </label>
      </div>
      <div class=\"grid two\">
        <label>Project ID
          <input name=\"project_id\" value=\"lumina-os\" />
        </label>
        <label>Action label
          <input name=\"action\" value=\"studio_runtime_cycle_v0_1\" />
        </label>
      </div>
      <label>Annotation
        <input name=\"annotation\" value=\"Studio v0.1 local governed runtime loop\" />
      </label>
      <label><input type=\"checkbox\" name=\"ethereonic_overlay\" value=\"1\" /> Attach optional expressive overlay</label>
      <button type=\"submit\">Run Lumina cycle</button>
      <div class=\"note\">For local use only. Do not expose this server publicly without adding authentication and persistence policy.</div>
    </form>
    <section class=\"receipt\">
      <h2>Last receipt</h2>
      <pre id=\"receipt\">No cycle has run in this page yet.</pre>
    </section>
  </main>
  <script>
    const form = document.querySelector('form');
    const receipt = document.querySelector('#receipt');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      receipt.textContent = 'Running Lumina cycle…';
      const body = new URLSearchParams(new FormData(form));
      try {
        const response = await fetch('/run', { method: 'POST', body });
        const data = await response.json();
        receipt.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        receipt.textContent = 'Lumina Studio request failed: ' + err;
      }
    });
  </script>
</body>
</html>"""


class Args:
    def __init__(self, payload: Dict[str, Any]):
        self.prompt = [payload.get("prompt", "Lumina Studio runtime cycle")]
        self.current_mode = payload.get("current_mode", "Continuity")
        self.target_mode = payload.get("target_mode", "Observation")
        self.action_type = payload.get("action_type", "audit")
        self.action = payload.get("action") or None
        self.project_id = payload.get("project_id", "lumina-os")
        self.focus = payload.get("focus", "continuity")
        self.depth = payload.get("depth", "structural")
        self.intent = payload.get("intent", "verify")
        self.annotation = payload.get("annotation") or None
        self.note = payload.get("note") or None
        self.feature_flags = list(DEFAULT_FEATURE_FLAGS)
        self.artifacts = []
        self.ethereonic_overlay = bool(payload.get("ethereonic_overlay"))
        self.json = False
        self.receipt_json = True


def _single(values: Dict[str, Any], key: str, default: str = "") -> str:
    value = values.get(key, [default])
    if isinstance(value, list):
        return value[0] if value else default
    return str(value)


def _payload_from_body(raw_body: bytes, content_type: str) -> Dict[str, Any]:
    if "application/json" in content_type:
        return json.loads(raw_body.decode("utf-8") or "{}")
    parsed = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
    payload = {key: _single(parsed, key) for key in parsed}
    payload["ethereonic_overlay"] = "ethereonic_overlay" in parsed
    return payload


class LuminaStudioHandler(BaseHTTPRequestHandler):
    server_version = "LuminaStudio/0.1"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/" or path == "/studio":
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/health":
            self._send(200, json.dumps({"ok": True, "service": "lumina-studio", "version": "0.1"}).encode("utf-8"), "application/json")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/run":
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length)
        try:
            payload = _payload_from_body(raw, self.headers.get("Content-Type", ""))
            result = run_lumina_cycle(Args(payload))
            receipt = compact_receipt(result)
            self._send(200, json.dumps(receipt, indent=2).encode("utf-8"), "application/json")
        except Exception as exc:  # pragma: no cover - operator feedback path
            body = json.dumps({"ok": False, "error": str(exc)}, indent=2).encode("utf-8")
            self._send(500, body, "application/json")


def main() -> int:
    host = "127.0.0.1"
    port = 8765
    server = ThreadingHTTPServer((host, port), LuminaStudioHandler)
    print(f"Lumina Studio v0.1 running at http://{host}:{port}/studio")
    print("Use Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLumina Studio stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
