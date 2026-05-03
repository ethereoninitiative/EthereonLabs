#!/usr/bin/env python3
"""Lumina Studio State Browser v0.2.

Read-only helpers for inspecting Lumina runtime receipts and governance events.
This module does not write state and does not own governance truth. It only
summarizes files already emitted by the governed runtime runner.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
STATE_ROOT = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2"
DEFAULT_RUNTIME_BASE = STATE_ROOT / "runtime_runner_r1_actiontype_logging"


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _read_jsonl(path: Path, *, limit: int = 50) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if isinstance(payload, dict):
                    rows.append(payload)
    except Exception:
        return []
    return rows[-limit:]


def _safe_stat_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except Exception:
        return 0.0


def _capability_ids(payload: Dict[str, Any]) -> List[str]:
    exposed = payload.get("exposed_capabilities", []) or []
    if not isinstance(exposed, list):
        return []
    out: List[str] = []
    for item in exposed:
        if isinstance(item, dict) and item.get("capability_id"):
            out.append(str(item["capability_id"]))
    return out


def compact_run_summary(payload: Dict[str, Any], *, path: Optional[Path] = None) -> Dict[str, Any]:
    governance = payload.get("governance", {}) or {}
    if not isinstance(governance, dict):
        governance = {}
    input_integrity = governance.get("input_integrity", {}) or {}
    if not isinstance(input_integrity, dict):
        input_integrity = {}
    return {
        "run_id": payload.get("run_id"),
        "created_at": payload.get("created_at"),
        "requested_action": payload.get("requested_action"),
        "action_type": payload.get("action_type"),
        "requested_mode": payload.get("requested_mode"),
        "target_mode": payload.get("target_mode"),
        "halted": payload.get("halted"),
        "halt_reason": payload.get("halt_reason"),
        "session_id": payload.get("session_id"),
        "context_bundle_id": payload.get("context_bundle_id"),
        "checkpoint_path": payload.get("checkpoint_path"),
        "log_path": payload.get("log_path") or (str(path) if path else None),
        "governance_log_path": payload.get("governance_log_path"),
        "governance_chain_valid": (payload.get("governance_chain_status") or {}).get("valid"),
        "canon_head": (payload.get("canon_lineage") or {}).get("current_head"),
        "exposed_capability_ids": _capability_ids(payload),
        "governance_keys": sorted(governance.keys()),
        "input_confidence": input_integrity.get("confidence_label"),
        "input_behavior": input_integrity.get("recommended_behavior"),
        "probe_run_id": (payload.get("probe_artifacts") or {}).get("run_id"),
        "lumina_project_id": (payload.get("lumina_return_host_artifacts") or {}).get("project_id"),
        "source_path": str(path) if path else None,
    }


def iter_result_logs(base_dir: Path = DEFAULT_RUNTIME_BASE) -> Iterable[Path]:
    logs_dir = base_dir / "logs"
    if not logs_dir.exists():
        return []
    return sorted(logs_dir.glob("*.json"), key=_safe_stat_mtime, reverse=True)


def list_run_receipts(*, base_dir: Path = DEFAULT_RUNTIME_BASE, limit: int = 20) -> List[Dict[str, Any]]:
    receipts: List[Dict[str, Any]] = []
    for path in iter_result_logs(base_dir):
        payload = _read_json(path)
        if payload is None:
            continue
        receipts.append(compact_run_summary(payload, path=path))
        if len(receipts) >= limit:
            break
    return receipts


def governance_event_summary(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    event_types: Dict[str, int] = {}
    action_types: Dict[str, int] = {}
    for event in events:
        event_type = str(event.get("event_type") or "unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1
        metadata = event.get("metadata", {}) or {}
        if isinstance(metadata, dict) and metadata.get("action_type"):
            action_type = str(metadata["action_type"])
            action_types[action_type] = action_types.get(action_type, 0) + 1
    return {
        "event_count": len(events),
        "event_types": dict(sorted(event_types.items())),
        "action_types": dict(sorted(action_types.items())),
        "latest_event_type": events[-1].get("event_type") if events else None,
        "latest_event_hash": events[-1].get("record_hash") if events else None,
    }


def state_snapshot(*, base_dir: Path = DEFAULT_RUNTIME_BASE, limit: int = 20) -> Dict[str, Any]:
    governance_log_path = base_dir / "governance_log_r1.jsonl"
    canon_lineage_path = base_dir / "canon_lineage_r1.jsonl"
    receipts = list_run_receipts(base_dir=base_dir, limit=limit)
    governance_events = _read_jsonl(governance_log_path, limit=500)
    canon_records = _read_jsonl(canon_lineage_path, limit=50)
    return {
        "schema_version": "lumina-studio-state-browser-v0.2",
        "read_only": True,
        "state_root": str(STATE_ROOT),
        "runtime_base_dir": str(base_dir),
        "runtime_base_exists": base_dir.exists(),
        "logs_dir": str(base_dir / "logs"),
        "receipt_count_returned": len(receipts),
        "latest_runs": receipts,
        "governance_log_path": str(governance_log_path),
        "governance": governance_event_summary(governance_events),
        "canon_lineage_path": str(canon_lineage_path),
        "canon_record_count": len(canon_records),
        "canon_head": canon_records[-1].get("canon_version") if canon_records else None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read Lumina Studio runtime receipts without mutating state.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--base-dir", default=None, help="Override runtime base dir. Defaults to .lumina_state/ship_of_ethereon_v2/runtime_runner_r1_actiontype_logging")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir).expanduser().resolve() if args.base_dir else DEFAULT_RUNTIME_BASE
    print(json.dumps(state_snapshot(base_dir=base_dir, limit=args.limit), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
