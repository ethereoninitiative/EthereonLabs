#!/usr/bin/env python3
"""
Lumina Runtime Daemon v0.1

Minimal heartbeat implementation.

This is not a full operating system, desktop shell, or autonomous agent.
It is a small persistent runtime surface for state, checkpoint, status,
and honest resume behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

DAEMON_NAME = "lumina-runtime-daemon"
DAEMON_VERSION = "0.1"
DEFAULT_MODE = "Continuity"


VALID_MODES = {"Continuity", "Sandbox", "DryDock", "Observation", "Canon"}
ALLOWED_TRANSITIONS = {
    "Continuity": {"Sandbox", "DryDock", "Observation"},
    "Sandbox": {"Continuity", "DryDock", "Observation"},
    "DryDock": {"Continuity", "Observation", "Canon"},
    "Observation": {"Continuity", "Sandbox", "DryDock"},
    "Canon": {"Continuity"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class DaemonState:
    daemon: str
    version: str
    session_id: str
    created_at: str
    updated_at: str
    current_mode: str
    last_checkpoint: Optional[str]
    cycle_count: int
    last_lifecycle_event: str
    state_source: str
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaDaemon:
    def __init__(self, state_dir: str | Path):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = self.state_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "daemon_state_v0_1.json"
        self.event_log_path = self.state_dir / "daemon_events_v0_1.jsonl"

    def _append_event(self, event_type: str, state: DaemonState, metadata: Optional[Dict[str, Any]] = None) -> None:
        event = {
            "timestamp_utc": utc_now(),
            "daemon": DAEMON_NAME,
            "version": DAEMON_VERSION,
            "event_type": event_type,
            "session_id": state.session_id,
            "current_mode": state.current_mode,
            "cycle_count": state.cycle_count,
            "metadata": metadata or {},
        }
        with self.event_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _write_state(self, state: DaemonState) -> None:
        state.updated_at = utc_now()
        with self.state_path.open("w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)

    def _read_state_payload(self) -> Optional[Dict[str, Any]]:
        if not self.state_path.exists():
            return None
        with self.state_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_or_create(self) -> DaemonState:
        payload = self._read_state_payload()
        if payload:
            state = DaemonState(**payload)
            state.state_source = "resumed"
            state.started_at = utc_now()
            state.stopped_at = None
            state.last_lifecycle_event = "resumed"
            state.cycle_count += 1
            self._write_state(state)
            self._append_event("resume", state)
            return state

        state = DaemonState(
            daemon=DAEMON_NAME,
            version=DAEMON_VERSION,
            session_id=str(uuid.uuid4()),
            created_at=utc_now(),
            updated_at=utc_now(),
            current_mode=DEFAULT_MODE,
            last_checkpoint=None,
            cycle_count=1,
            last_lifecycle_event="fresh_start",
            state_source="fresh",
            started_at=utc_now(),
            stopped_at=None,
        )
        self._write_state(state)
        self._append_event("fresh_start", state)
        return state

    def start(self) -> Dict[str, Any]:
        state = self.load_or_create()
        return self.status(state)

    def stop(self) -> Dict[str, Any]:
        state = self.require_state()
        state.stopped_at = utc_now()
        state.last_lifecycle_event = "stopped"
        self._write_state(state)
        self._append_event("stop", state)
        return self.status(state)

    def require_state(self) -> DaemonState:
        payload = self._read_state_payload()
        if not payload:
            raise RuntimeError("No daemon state found. Run `start` first.")
        return DaemonState(**payload)

    def status(self, state: Optional[DaemonState] = None) -> Dict[str, Any]:
        state = state or self.require_state()
        uptime_seconds = None
        if state.started_at and not state.stopped_at:
            try:
                started = datetime.fromisoformat(state.started_at)
                uptime_seconds = max(0, int((datetime.now(timezone.utc) - started).total_seconds()))
            except Exception:
                uptime_seconds = None

        return {
            "daemon": state.daemon,
            "version": state.version,
            "status": "stopped" if state.stopped_at else "running",
            "session_id": state.session_id,
            "current_mode": state.current_mode,
            "last_checkpoint": state.last_checkpoint,
            "uptime_seconds": uptime_seconds,
            "state_source": state.state_source,
            "governance_available": True,
            "cycle_count": state.cycle_count,
            "last_lifecycle_event": state.last_lifecycle_event,
            "state_path": str(self.state_path),
            "event_log_path": str(self.event_log_path),
        }

    def checkpoint(self, label: str = "manual") -> Dict[str, Any]:
        state = self.require_state()
        safe_label = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)[:80] or "checkpoint"
        checkpoint_path = self.checkpoint_dir / f"{state.session_id}__{safe_label}.json"

        payload = {
            "checkpoint_label": safe_label,
            "created_at": utc_now(),
            "daemon_state": state.to_dict(),
        }
        payload["checkpoint_hash"] = sha256_text(canonical_json(payload))

        with checkpoint_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        state.last_checkpoint = str(checkpoint_path)
        state.last_lifecycle_event = "checkpoint_written"
        state.cycle_count += 1
        self._write_state(state)
        self._append_event("checkpoint", state, {"checkpoint_path": str(checkpoint_path), "checkpoint_hash": payload["checkpoint_hash"]})

        return {
            "checkpoint_path": str(checkpoint_path),
            "checkpoint_hash": payload["checkpoint_hash"],
            "status": self.status(state),
        }

    def transition(self, target_mode: str) -> Dict[str, Any]:
        if target_mode not in VALID_MODES:
            return {"allowed": False, "reason": f"unknown mode: {target_mode}"}

        state = self.require_state()
        current = state.current_mode
        if target_mode == current:
            decision = {"allowed": True, "reason": "already in requested mode"}
        else:
            allowed = target_mode in ALLOWED_TRANSITIONS.get(current, set())
            decision = {
                "allowed": allowed,
                "reason": "transition allowed" if allowed else f"illegal transition: {current} -> {target_mode}",
            }

        if decision["allowed"]:
            state.current_mode = target_mode
            state.last_lifecycle_event = "mode_transition"
            state.cycle_count += 1
            self._write_state(state)

        self._append_event("mode_transition", state, {"target_mode": target_mode, **decision})
        return {**decision, "status": self.status(state)}


def default_state_dir() -> Path:
    env = os.environ.get("LUMINA_DAEMON_STATE_DIR")
    if env:
        return Path(env)
    return Path.home() / ".lumina" / "runtime_daemon_v0_1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lumina Runtime Daemon v0.1 minimal heartbeat")
    parser.add_argument("command", choices=["start", "status", "checkpoint", "stop", "transition"])
    parser.add_argument("--state-dir", default=str(default_state_dir()))
    parser.add_argument("--label", default="manual")
    parser.add_argument("--target-mode", default=DEFAULT_MODE)
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    daemon = LuminaDaemon(args.state_dir)

    try:
        if args.command == "start":
            result = daemon.start()
        elif args.command == "status":
            result = daemon.status()
        elif args.command == "checkpoint":
            result = daemon.checkpoint(args.label)
        elif args.command == "stop":
            result = daemon.stop()
        elif args.command == "transition":
            result = daemon.transition(args.target_mode)
        else:
            raise ValueError(f"Unhandled command: {args.command}")
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
