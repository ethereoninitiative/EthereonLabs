#!/usr/bin/env python3
"""Lumina Bridge Server R1 — local, read-only ship-position surface."""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse

STUDIO_ROOT = Path(__file__).resolve().parent
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

from lumina_bridge_state_r1 import AUTHORITY_BOUNDARY, build_bridge_state  # noqa: E402

HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lumina Bridge R1</title>
  <style>
    :root {
      color-scheme: dark;
      --abyss: #030812;
      --deep: #071626;
      --glass: rgba(10, 29, 48, 0.72);
      --line: rgba(133, 207, 255, 0.22);
      --cyan: #8ee8ff;
      --gold: #f0cf82;
      --ink: #eaf5ff;
      --muted: #91a9bd;
      --good: #9ef0c3;
      --warn: #ffd58e;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 82% 18%, rgba(50, 141, 196, .20), transparent 34%),
        radial-gradient(circle at 18% 8%, rgba(240, 207, 130, .10), transparent 28%),
        linear-gradient(180deg, #02050c 0%, var(--deep) 54%, #03101a 100%);
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: .35;
      background-image:
        linear-gradient(rgba(142,232,255,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(142,232,255,.035) 1px, transparent 1px);
      background-size: 42px 42px;
      mask-image: linear-gradient(to bottom, black, transparent 88%);
    }
    main { width: min(1220px, calc(100% - 32px)); margin: 0 auto; padding: 34px 0 54px; position: relative; }
    header { display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: end; margin-bottom: 24px; }
    .eyebrow { color: var(--gold); text-transform: uppercase; letter-spacing: .22em; font-size: .75rem; }
    h1 { margin: 6px 0 2px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(2.4rem, 7vw, 5.8rem); font-weight: 500; letter-spacing: -.045em; }
    .subtitle { color: var(--muted); max-width: 760px; line-height: 1.55; }
    button { border: 1px solid var(--line); background: rgba(142,232,255,.08); color: var(--ink); border-radius: 999px; padding: 11px 16px; cursor: pointer; }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }
    .panel { grid-column: span 4; min-height: 180px; padding: 19px; border: 1px solid var(--line); border-radius: 20px; background: var(--glass); backdrop-filter: blur(14px); box-shadow: 0 24px 70px rgba(0,0,0,.28); }
    .panel.wide { grid-column: span 8; }
    .panel.full { grid-column: 1 / -1; min-height: auto; }
    .panel h2 { margin: 0 0 13px; font-family: Georgia, "Times New Roman", serif; font-size: 1.25rem; font-weight: 500; color: #f7fbff; }
    .metric { display: grid; grid-template-columns: minmax(120px, .8fr) 1.2fr; gap: 14px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.07); }
    .metric:last-child { border-bottom: 0; }
    .label { color: var(--muted); }
    .value { text-align: right; overflow-wrap: anywhere; }
    .good { color: var(--good); }
    .warn { color: var(--warn); }
    .command { display: block; border: 1px solid rgba(142,232,255,.14); border-radius: 12px; padding: 9px 11px; margin-top: 8px; background: rgba(0,0,0,.20); color: var(--cyan); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; overflow-wrap: anywhere; }
    .boundary { color: var(--muted); font-size: .88rem; line-height: 1.5; }
    .loading { color: var(--muted); }
    @media (max-width: 900px) { header { grid-template-columns: 1fr; align-items: start; } .panel, .panel.wide { grid-column: 1 / -1; } }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <div class="eyebrow">Ship of Ethereon · Lumina habitat · read-only orientation</div>
        <h1>The Bridge</h1>
        <div class="subtitle">A unified view of workspace, continuity, runtime witness, and committed authority. Bridge orients; Studio performs explicit governed actions.</div>
      </div>
      <button id="refresh" type="button">Refresh position</button>
    </header>
    <section class="grid" id="panels"><div class="panel full loading">Reading the ship's position…</div></section>
  </main>
  <script>
    const panels = document.querySelector('#panels');
    const refresh = document.querySelector('#refresh');
    const esc = (value) => String(value ?? 'none').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
    const metric = (label, value, cls='') => `<div class="metric"><span class="label">${esc(label)}</span><span class="value ${cls}">${esc(value)}</span></div>`;
    const panel = (title, body, cls='') => `<article class="panel ${cls}"><h2>${esc(title)}</h2>${body}</article>`;

    function render(data) {
      const workspace = data.workspace || {};
      const project = workspace.project || {};
      const session = workspace.harbor_session || {};
      const continuity = data.continuity || {};
      const runtime = data.runtime_witness || {};
      const alignment = data.runtime_truth_alignment || {};
      const authority = data.authority || {};
      const committed = authority.committed || {};
      const governance = committed.governance_chain || {};
      const canon = committed.canon_lineage || {};
      const navigation = data.navigation || {};
      const correlation = data.correlation || {};
      const refs = correlation.references || {};
      const probe = runtime.probe || {};

      const blocks = [];
      blocks.push(panel('Ship Position',
        metric('Project', project.name || project.slug) +
        metric('Harbor session', session.title || session.session_id) +
        metric('Current mode', runtime.current_mode) +
        metric('Latest action', runtime.requested_action) +
        metric('Witness status', runtime.status, runtime.halted ? 'warn' : 'good'), 'wide'));
      blocks.push(panel('Continuity',
        metric('Shape', continuity.latest_shape) +
        metric('Local receipts', continuity.local_receipt_count) +
        `<div class="boundary">${esc(continuity.drift_note || 'No local drift note available.')}</div>`));
      blocks.push(panel('Committed Authority',
        metric('Governance', governance.status, governance.valid ? 'good' : 'warn') +
        metric('Governance events', governance.event_count) +
        metric('Canon head', canon.current_head, canon.valid ? 'good' : 'warn') +
        metric('Canon records', canon.record_count)));
      blocks.push(panel('Runtime Witness',
        metric('Run ID', runtime.run_id) +
        metric('Action type', runtime.action_type) +
        metric('Probe', probe.instrument_version) +
        metric('Coherence', probe.coherence) +
        metric('Presence', probe.presence) +
        metric('Lock', probe.lock)));
      blocks.push(panel('Truth Alignment',
        metric('Latest receipt', alignment.latest_cycle_present ? 'present' : 'missing') +
        metric('Public truth', alignment.public_truth_present ? 'present' : 'missing') +
        metric('Run/timestamp', alignment.aligned ? 'aligned' : 'not aligned', alignment.aligned ? 'good' : 'warn') +
        `<div class="boundary">Observed local emptiness does not override committed canon or governance evidence.</div>`));
      blocks.push(panel('Correlation References',
        metric('Project', refs.project_slug) +
        metric('Harbor session', refs.harbor_session_id) +
        metric('Runtime session', refs.runtime_session_id) +
        metric('Context bundle', refs.context_bundle_id) +
        `<div class="boundary">${esc(correlation.note)}</div>`));
      const commands = (navigation.commands || []).map(command => `<code class="command">${esc(command)}</code>`).join('');
      blocks.push(panel('Navigation',
        `<div>${esc(navigation.recommended_action)}</div>` + commands +
        `<div class="boundary" style="margin-top:12px">${esc(navigation.rule)}</div>`, 'wide'));
      blocks.push(panel('Authority Boundary', `<div class="boundary">${esc(data.authority_boundary)}</div>`));
      panels.innerHTML = blocks.join('');
    }

    async function load() {
      panels.innerHTML = '<div class="panel full loading">Reading the ship\'s position…</div>';
      try {
        const response = await fetch('/api/bridge');
        const data = await response.json();
        render(data);
      } catch (error) {
        panels.innerHTML = `<div class="panel full warn">Bridge state could not be read: ${esc(error)}</div>`;
      }
    }
    refresh.addEventListener('click', load);
    load();
  </script>
</body>
</html>'''


class LuminaBridgeHandler(BaseHTTPRequestHandler):
    server_version = "LuminaBridge/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/bridge"}:
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/bridge":
            query = parse_qs(urlparse(self.path).query)
            try:
                limit = max(1, min(int((query.get("limit") or ["12"])[0]), 100))
            except Exception:
                limit = 12
            payload = build_bridge_state(limit=limit)
            self._send(
                200,
                json.dumps(payload, indent=2).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        if path == "/api/boundary":
            self._send(
                200,
                json.dumps({"authority_boundary": AUTHORITY_BOUNDARY}, indent=2).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        self._send(404, b'{"error":"not found"}', "application/json; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        self._send(
            405,
            b'{"error":"Bridge R1 is read-only; use Lumina Studio for explicit governed actions."}',
            "application/json; charset=utf-8",
        )

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[lumina-bridge] " + (fmt % args) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the local read-only Lumina Bridge R1 surface.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), LuminaBridgeHandler)
    print(f"Lumina Bridge R1: http://{args.host}:{args.port}/bridge")
    print("Read-only surface. Use Lumina Studio for explicit governed actions.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
