#!/usr/bin/env python3
"""Lumina Studio Server v0.3.1.

Tiny local HTTP control surface for the Lumina runtime.
Standard library only and local-first.

v0.3.1 keeps the v0.2 page intact and adds two read-only JSON endpoints:
- /api/governance
- /api/presets
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
from lumina_governance_viewer import latest_governance_views  # noqa: E402
from lumina_presets import presets_payload  # noqa: E402
from lumina_state_browser import state_snapshot  # noqa: E402


HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Lumina Studio v0.3.1</title>
  <style>
    :root { color-scheme: dark; }
    body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; background: #07111f; color: #eaf2ff; }
    main { max-width: 1080px; margin: 0 auto; padding: 32px 20px 48px; }
    h1 { margin: 0 0 6px; font-size: clamp(2rem, 5vw, 4rem); letter-spacing: -0.06em; }
    h2 { margin-top: 0; }
    .kicker { color: #f6c96b; text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.78rem; }
    .sub { max-width: 820px; color: #b9c7dc; line-height: 1.55; }
    form, .panel { display: grid; gap: 16px; margin-top: 28px; background: rgba(255,255,255,0.045); border: 1px solid rgba(255,255,255,0.12); border-radius: 22px; padding: 22px; box-shadow: 0 24px 80px rgba(0,0,0,0.35); }
    label { display: grid; gap: 6px; color: #cbd8ec; font-size: 0.92rem; }
    input, textarea, select { width: 100%; box-sizing: border-box; border-radius: 12px; border: 1px solid rgba(255,255,255,0.16); background: rgba(0,0,0,0.25); color: #f7fbff; padding: 11px 12px; font: inherit; }
    textarea { min-height: 130px; resize: vertical; }
    .grid { display: grid; gap: 14px; grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; }
    button { justify-self: start; border: 0; border-radius: 999px; padding: 12px 18px; font-weight: 700; background: linear-gradient(135deg, #f6c96b, #fff1b5); color: #111522; cursor: pointer; }
    button.secondary { background: rgba(255,255,255,0.12); color: #eaf2ff; border: 1px solid rgba(255,255,255,0.16); }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.12); border-radius: 18px; padding: 18px; margin-top: 20px; color: #dbe8ff; }
    .receipt { margin-top: 24px; }
    .note { color: #8fa4c3; font-size: 0.9rem; }
    .cards { display: grid; gap: 12px; }
    .card { border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 14px; background: rgba(0,0,0,0.18); }
    .card strong { color: #fff3bd; }
    .muted { color: #90a4c4; }
    @media (max-width: 760px) { .grid, .grid.two { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main>
    <div class=\"kicker\">Local control surface · runtime receipts · read-only APIs</div>
    <h1>Lumina Studio v0.3.1</h1>
    <p class=\"sub\">Run one Lumina cycle, inspect recent receipts, and use local JSON endpoints for governance views and presets. The page stays intentionally plain while the APIs grow underneath it.</p>
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
          <input name=\"action\" value=\"studio_runtime_cycle_v0_3_1\" />
        </label>
      </div>
      <label>Annotation
        <input name=\"annotation\" value=\"Studio v0.3.1 local runtime loop with read-only APIs\" />
      </label>
      <label><input type=\"checkbox\" name=\"ethereonic_overlay\" value=\"1\" /> Attach optional expressive overlay</label>
      <div class=\"actions\">
        <button type=\"submit\">Run Lumina cycle</button>
        <button type=\"button\" class=\"secondary\" id=\"refresh-state\">Refresh state</button>
      </div>
      <div class=\"note\">Read-only JSON endpoints: /api/state, /api/governance, /api/presets. For local use only.</div>
    </form>
    <section class=\"receipt\">
      <h2>Last receipt</h2>
      <pre id=\"receipt\">No cycle has run in this page yet.</pre>
    </section>
    <section class=\"panel\">
      <h2>Runtime state</h2>
      <div id=\"state-cards\" class=\"cards\"><div class=\"muted\">State not loaded yet.</div></div>
      <pre id=\"state-json\">Click Refresh state to inspect recent runtime receipts.</pre>
    </section>
  </main>
  <script>
    const form = document.querySelector('form');
    const receipt = document.querySelector('#receipt');
    const stateJson = document.querySelector('#state-json');
    const stateCards = document.querySelector('#state-cards');
    const refreshButton = document.querySelector('#refresh-state');

    function renderStateCards(data) {
      const runs = data.latest_runs || [];
      const governance = data.governance || {};
      const cards = [];
      cards.push(`<div class=\"card\"><strong>Receipts:</strong> ${data.receipt_count_returned || 0}<br><span class=\"muted\">State root: ${data.state_root || 'unknown'}</span></div>`);
      cards.push(`<div class=\"card\"><strong>Governance events:</strong> ${governance.event_count || 0}<br><span class=\"muted\">Latest: ${governance.latest_event_type || 'none'}</span></div>`);
      cards.push(`<div class=\"card\"><strong>Canon head:</strong> ${data.canon_head || 'none'}<br><span class=\"muted\">Records: ${data.canon_record_count || 0}</span></div>`);
      for (const run of runs.slice(0, 5)) {
        cards.push(`<div class=\"card\"><strong>${run.run_id || 'unknown run'}</strong><br>${run.requested_mode || '?'} → ${run.target_mode || '?'} · ${run.action_type || '?'} · halted: ${run.halted}<br><span class=\"muted\">${run.requested_action || ''}</span></div>`);
      }
      stateCards.innerHTML = cards.join('');
    }

    async function refreshState() {
      stateJson.textContent = 'Reading emitted runtime state…';
      try {
        const response = await fetch('/api/state?limit=12');
        const data = await response.json();
        renderStateCards(data);
        stateJson.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        stateJson.textContent = 'State refresh failed: ' + err;
      }
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      receipt.textContent = 'Running Lumina cycle…';
      const body = new URLSearchParams(new FormData(form));
      try {
        const response = await fetch('/run', { method: 'POST', body });
        const data = await response.json();
        receipt.textContent = JSON.stringify(data, null, 2);
        await refreshState();
      } catch (err) {
        receipt.textContent = 'Lumina Studio request failed: ' + err;
      }
    });

    refreshButton.addEventListener('click', refreshState);
    refreshState();
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


def _query_limit(path: str, default: int = 20) -> int:
    query = parse_qs(urlparse(path).query)
    try:
        return max(1, min(int(_single(query, "limit", str(default))), 100))
    except Exception:
        return default


class LuminaStudioHandler(BaseHTTPRequestHandler):
    server_version = "LuminaStudio/0.3.1"

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
            self._send(200, json.dumps({"ok": True, "service": "lumina-studio", "version": "0.3.1"}).encode("utf-8"), "application/json")
            return
        if path == "/api/state":
            payload = state_snapshot(limit=_query_limit(self.path, 20))
            self._send(200, json.dumps(payload, indent=2).encode("utf-8"), "application/json")
            return
        if path == "/api/governance":
            payload = latest_governance_views(limit=_query_limit(self.path, 12))
            self._send(200, json.dumps(payload, indent=2).encode("utf-8"), "application/json")
            return
        if path == "/api/presets":
            self._send(200, json.dumps(presets_payload(), indent=2).encode("utf-8"), "application/json")
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
    print(f"Lumina Studio v0.3.1 running at http://{host}:{port}/studio")
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
