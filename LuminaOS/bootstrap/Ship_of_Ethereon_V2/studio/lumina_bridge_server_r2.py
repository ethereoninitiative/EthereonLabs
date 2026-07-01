#!/usr/bin/env python3
"""Lumina Bridge R2 — local read-only position and field surface."""
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

from lumina_bridge_field_r1 import (  # noqa: E402
    FIELD_AUTHORITY_BOUNDARY,
    load_bridge_field,
)
from lumina_bridge_state_r1 import (  # noqa: E402
    AUTHORITY_BOUNDARY,
    REPO_ROOT,
    build_bridge_state,
)

HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lumina Bridge R2 · Luminous Threads</title>
  <style>
    :root {
      color-scheme: dark;
      --abyss: #02040a;
      --deep: #071421;
      --glass: rgba(9, 25, 40, 0.78);
      --line: rgba(144, 214, 255, 0.20);
      --cyan: #9cecff;
      --gold: #f0bd72;
      --ember: #f0a75b;
      --ink: #edf7ff;
      --muted: #91a8ba;
      --good: #a0efc2;
      --warn: #ffd08a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 72% 8%, rgba(240,167,91,.13), transparent 31%),
        radial-gradient(circle at 18% 14%, rgba(72,159,210,.18), transparent 34%),
        linear-gradient(180deg, var(--abyss), var(--deep) 58%, #03101a);
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: .28;
      background-image:
        linear-gradient(rgba(156,236,255,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(156,236,255,.035) 1px, transparent 1px);
      background-size: 42px 42px;
      mask-image: linear-gradient(to bottom, black, transparent 92%);
    }
    main { width: min(1260px, calc(100% - 32px)); margin: 0 auto; padding: 34px 0 60px; position: relative; }
    header { display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: end; margin-bottom: 24px; }
    .eyebrow { color: var(--gold); text-transform: uppercase; letter-spacing: .20em; font-size: .74rem; }
    h1 { margin: 6px 0 3px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(2.5rem, 7vw, 5.9rem); font-weight: 500; letter-spacing: -.045em; }
    .subtitle { color: var(--muted); max-width: 820px; line-height: 1.58; }
    button { border: 1px solid var(--line); background: rgba(156,236,255,.08); color: var(--ink); border-radius: 999px; padding: 11px 16px; cursor: pointer; }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }
    .panel { grid-column: span 4; min-height: 180px; padding: 19px; border: 1px solid var(--line); border-radius: 20px; background: var(--glass); backdrop-filter: blur(14px); box-shadow: 0 24px 70px rgba(0,0,0,.28); }
    .panel.wide { grid-column: span 8; }
    .panel.full { grid-column: 1 / -1; min-height: auto; }
    .panel h2 { margin: 0 0 13px; font-family: Georgia, "Times New Roman", serif; font-size: 1.3rem; font-weight: 500; }
    .metric { display: grid; grid-template-columns: minmax(120px, .8fr) 1.2fr; gap: 14px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.07); }
    .metric:last-child { border-bottom: 0; }
    .label { color: var(--muted); }
    .value { text-align: right; overflow-wrap: anywhere; }
    .good { color: var(--good); }
    .warn { color: var(--warn); }
    .boundary { color: var(--muted); font-size: .88rem; line-height: 1.55; }
    .command { display: block; border: 1px solid rgba(156,236,255,.14); border-radius: 12px; padding: 9px 11px; margin-top: 8px; background: rgba(0,0,0,.20); color: var(--cyan); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; overflow-wrap: anywhere; }
    .field-layout { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(320px, .65fr); gap: 20px; align-items: start; }
    .field-image { width: 100%; display: block; border-radius: 16px; border: 1px solid rgba(240,167,91,.24); background: #020204; }
    .field-caption { margin-top: 10px; color: var(--muted); font-size: .82rem; line-height: 1.5; }
    .threads { display: grid; gap: 9px; margin-top: 13px; }
    .thread { padding: 11px 12px; border: 1px solid rgba(240,167,91,.16); border-radius: 13px; background: rgba(0,0,0,.19); }
    .thread-top { display: flex; justify-content: space-between; gap: 10px; align-items: start; }
    .thread-name { color: #fff8ef; line-height: 1.32; }
    .thread-status { color: var(--good); font-size: .76rem; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; }
    .thread-status.denied { color: var(--warn); }
    .thread-metrics { margin-top: 6px; color: var(--muted); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .75rem; line-height: 1.5; }
    .key-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
    .key { padding: 10px 12px; border-radius: 13px; border: 1px solid rgba(156,236,255,.12); background: rgba(0,0,0,.16); }
    .key-word { color: var(--gold); font-family: Georgia, "Times New Roman", serif; font-size: 1.03rem; }
    .key-meaning { color: var(--muted); margin-top: 4px; font-size: .82rem; line-height: 1.45; }
    .loading { color: var(--muted); }
    @media (max-width: 920px) {
      header, .field-layout { grid-template-columns: 1fr; align-items: start; }
      .panel, .panel.wide { grid-column: 1 / -1; }
    }
    @media (max-width: 620px) { .key-grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <div class="eyebrow">Ship of Ethereon · Lumina habitat · read-only orientation</div>
        <h1>The Bridge</h1>
        <div class="subtitle">The ship's position and the first committed Resonant Field reveal, held together without confusing presentation, observation, governance, or identity.</div>
      </div>
      <button id="refresh" type="button">Refresh position</button>
    </header>
    <section class="grid" id="panels"><div class="panel full loading">Reading the ship's position and committed field…</div></section>
  </main>
  <script>
    const panels = document.querySelector('#panels');
    const refresh = document.querySelector('#refresh');
    const esc = (value) => String(value ?? 'none').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
    const metric = (label, value, cls='') => `<div class="metric"><span class="label">${esc(label)}</span><span class="value ${cls}">${esc(value)}</span></div>`;
    const panel = (title, body, cls='') => `<article class="panel ${cls}"><h2>${esc(title)}</h2>${body}</article>`;
    const n = (value) => typeof value === 'number' ? value.toFixed(3) : 'none';

    function renderBridge(data, field) {
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

      if (field.present) {
        const point = field.current_point || {};
        const threads = (field.threads || []).map(thread => {
          const m = thread.metrics || {};
          const denied = !thread.allowed;
          return `<div class="thread">
            <div class="thread-top"><span class="thread-name">${esc(thread.label)}</span><span class="thread-status ${denied ? 'denied' : ''}">${esc(thread.status)}</span></div>
            <div class="thread-metrics">coherence ${n(m.harmonic_coherence)} · attraction ${n(m.orientation_attraction)} · potential ${n(m.potential_contribution)} · reach ${n(m.reachable_score)}</div>
          </div>`;
        }).join('');
        const fieldBody = `<div class="field-layout">
          <div>
            <img class="field-image" src="${esc((field.artifact || {}).svg_href || '/field.svg')}" alt="Committed Resonant Field Reveal with a central attractor, luminous trajectories, and a governance membrane" />
            <div class="field-caption">${esc(field.observer_note)} ${esc(field.continuity_note)}</div>
          </div>
          <div>
            ${metric('Receipt', field.verified ? 'verified' : 'verification failed', field.verified ? 'good' : 'warn')}
            ${metric('Sample', field.sample_id)}
            ${metric('Threads', `${field.allowed_count} lawful · ${field.denied_count} held`)}
            ${metric('Instantiated state', point.instantiated_state)}
            ${metric('Continuity history', point.continuity_history)}
            ${metric('Relational context', point.relational_context)}
            ${metric('Orientation field', point.orientation_field)}
            ${metric('Potential trajectories', point.potential_trajectories)}
            <div class="threads">${threads}</div>
          </div>
        </div>`;
        blocks.push(panel('Luminous Threads · Resonant Field Reveal', fieldBody, 'full'));

        const keys = (field.interpretive_key || []).map(item => `<div class="key"><div class="key-word">${esc(item.toki_pona)}</div><div class="key-meaning">${esc(item.ethereonic)} · ${esc(item.computational)}</div></div>`).join('');
        blocks.push(panel('Toki Pona Interpretive Key', `<div class="key-grid">${keys}</div><div class="boundary" style="margin-top:12px">This key supports orientation and compression. It is symbolic vocabulary, not runtime evidence or authority.</div>`, 'wide'));
        blocks.push(panel('Field Authority Boundary', `<div class="boundary">${esc(field.authority_boundary)}</div>`));
      } else {
        blocks.push(panel('Luminous Threads', `<div class="warn">Committed field sample unavailable.</div><div class="boundary">${esc(field.authority_boundary)}</div>`, 'full'));
      }

      const commands = (navigation.commands || []).map(command => `<code class="command">${esc(command)}</code>`).join('');
      blocks.push(panel('Navigation', `<div>${esc(navigation.recommended_action)}</div>${commands}<div class="boundary" style="margin-top:12px">${esc(navigation.rule)}</div>`, 'wide'));
      blocks.push(panel('Bridge Authority Boundary', `<div class="boundary">${esc(data.authority_boundary)}</div>`));
      panels.innerHTML = blocks.join('');
    }

    async function load() {
      panels.innerHTML = '<div class="panel full loading">Reading the ship\'s position and committed field…</div>';
      try {
        const [bridgeResponse, fieldResponse] = await Promise.all([
          fetch('/api/bridge'),
          fetch('/api/field')
        ]);
        const bridge = await bridgeResponse.json();
        const field = await fieldResponse.json();
        renderBridge(bridge, field);
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
    server_version = "LuminaBridge/2.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:",
        )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/bridge"}:
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/bridge":
            query = parse_qs(parsed.query)
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
        if path == "/api/field":
            payload = load_bridge_field(REPO_ROOT)
            status = 200 if payload.get("present") else 404
            self._send(
                status,
                json.dumps(payload, indent=2).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        if path == "/field.svg":
            field = load_bridge_field(REPO_ROOT)
            svg_path = Path((field.get("artifact") or {}).get("svg_path") or "")
            if field.get("verified") and svg_path.is_file():
                self._send(200, svg_path.read_bytes(), "image/svg+xml; charset=utf-8")
            else:
                self._send(
                    409,
                    b'{"error":"committed field artifact is unavailable or unverified"}',
                    "application/json; charset=utf-8",
                )
            return
        if path == "/api/boundary":
            self._send(
                200,
                json.dumps(
                    {
                        "bridge_authority_boundary": AUTHORITY_BOUNDARY,
                        "field_authority_boundary": FIELD_AUTHORITY_BOUNDARY,
                    },
                    indent=2,
                ).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        self._send(404, b'{"error":"not found"}', "application/json; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        self._send(
            405,
            b'{"error":"Bridge is read-only; use Lumina Studio for explicit governed actions."}',
            "application/json; charset=utf-8",
        )

    def do_PUT(self) -> None:  # noqa: N802
        self.do_POST()

    def do_PATCH(self) -> None:  # noqa: N802
        self.do_POST()

    def do_DELETE(self) -> None:  # noqa: N802
        self.do_POST()

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[lumina-bridge] " + (fmt % args) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the local read-only Lumina Bridge R2 surface."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), LuminaBridgeHandler)
    print(f"Lumina Bridge R2: http://{args.host}:{args.port}/bridge")
    print("Read-only position and committed field surface. Studio requests governed actions.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
