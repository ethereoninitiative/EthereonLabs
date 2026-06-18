#!/usr/bin/env python3
"""Lumina Studio State Browser v0.4.

Read-only helpers for inspecting Lumina runtime receipts, governance events,
and host-layer state schema status. This module does not write state and does
not own governance truth. It only summarizes files already emitted by the
governed runtime runner and host-layer schema helper.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
INSTALL_ROOT = BOOTSTRAP_ROOT / "install"
if str(INSTALL_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTALL_ROOT))

try:
    from lumina_state_schema import inspect_state_schema
except Exception:  # pragma: no cover - state browser reports unavailable helper
    inspect_state_schema = None

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


def _as_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _metric_text(label: str, value: Optional[float]) -> Optional[str]:
    if value is None:
        return None
    return f"{label} {value:.2f}"


def state_schema_summary() -> Dict[str, Any]:
    if inspect_state_schema is None:
        return {
            "available": False,
            "compatible": False,
            "reason": "lumina_state_schema helper unavailable",
        }
    status = inspect_state_schema(ensure=False, migrate=False).to_dict()
    status["available"] = True
    return status


def harmonic_witness_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    governance = payload.get("governance", {}) or {}
    if not isinstance(governance, dict):
        governance = {}
    input_integrity = governance.get("input_integrity", {}) or {}
    if not isinstance(input_integrity, dict):
        input_integrity = {}
    probe = payload.get("probe_artifacts", {}) or {}
    if not isinstance(probe, dict):
        probe = {}
    metrics = probe.get("metrics", {}) or {}
    if not isinstance(metrics, dict):
        metrics = {}

    chain_valid = bool((payload.get("governance_chain_status") or {}).get("valid"))
    recommended_behavior = input_integrity.get("recommended_behavior")
    confidence_label = input_integrity.get("confidence_label")
    chosen_interpretation = input_integrity.get("chosen_interpretation")

    crs = _as_float(metrics.get("CRS"))
    rf = _as_float(metrics.get("RF"))
    lock = _as_float(metrics.get("alignment_strength") or metrics.get("lock"))
    presence = _as_float(metrics.get("presence"))

    if payload.get("halted"):
        continuity_shape = "halted_before_return"
    elif crs is not None:
        if crs >= 0.75 and chain_valid:
            continuity_shape = "strong_return"
        elif crs >= 0.45:
            continuity_shape = "partial_return"
        else:
            continuity_shape = "fragile_return"
    elif chain_valid and recommended_behavior in {"clarify", "accept_softly"}:
        continuity_shape = "listened_return"
    elif chain_valid:
        continuity_shape = "lawful_return"
    else:
        continuity_shape = "unverified_return"

    if not input_integrity:
        input_listening_note = "No special listening event recorded."
    elif recommended_behavior == "halt_for_confirmation":
        input_listening_note = (
            f"Load-bearing listening gate halted for confirmation"
            f" ({confidence_label or 'unknown confidence'})."
        )
    elif recommended_behavior == "clarify":
        input_listening_note = (
            f"Listening pressure detected ambiguity"
            f" ({confidence_label or 'unknown confidence'}); clarification preferred."
        )
    elif recommended_behavior == "accept_softly":
        chosen = f" chosen interpretation: {chosen_interpretation}." if chosen_interpretation else ""
        input_listening_note = (
            f"Listening pass accepted a soft repair"
            f" ({confidence_label or 'unknown confidence'}).{chosen}"
        )
    else:
        input_listening_note = (
            f"Input passed without special intervention"
            f" ({confidence_label or 'clear'})."
        )

    metric_parts = [
        _metric_text("CRS", crs),
        _metric_text("RF", rf),
        _metric_text("lock", lock),
        _metric_text("presence", presence),
    ]
    metric_text = ", ".join(part for part in metric_parts if part)
    if metric_text:
        recomposition_summary = f"Lawful probe witness: {metric_text}."
    elif probe:
        recomposition_summary = "Lawful Psi-42 probe ran without recomposition summary metrics."
    else:
        recomposition_summary = "No lawful Psi-42 probe witness for this run."

    recurrence_note = "Single-run witness only. Compare across recent runs for recurrence and drift."

    return {
        "continuity_shape": continuity_shape,
        "input_listening_note": input_listening_note,
        "recomposition_summary": recomposition_summary,
        "recurrence_note": recurrence_note,
    }


def compact_run_summary(payload: Dict[str, Any], *, path: Optional[Path] = None) -> Dict[str, Any]:
    governance = payload.get("governance", {}) or {}
    if not isinstance(governance, dict):
        governance = {}
    input_integrity = governance.get("input_integrity", {}) or {}
    if not isinstance(input_integrity, dict):
        input_integrity = {}
    harmonic_witness = harmonic_witness_from_payload(payload)
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
        "harmonic_witness": harmonic_witness,
        "continuity_shape": harmonic_witness.get("continuity_shape"),
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


def harmonic_state_summary(receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not receipts:
        return {
            "latest_continuity_shape": None,
            "drift_note": "No runs yet.",
            "recurrence_note": "No recurrence available yet.",
            "recent_shape_counts": {},
        }

    latest = receipts[0]
    latest_witness = latest.get("harmonic_witness") or {}
    recent_shapes: Dict[str, int] = {}
    route_counts: Dict[str, int] = {}
    for item in receipts:
        shape = str((item.get("harmonic_witness") or {}).get("continuity_shape") or "unknown")
        recent_shapes[shape] = recent_shapes.get(shape, 0) + 1
        route = f"{item.get('requested_mode') or '?'}->{item.get('target_mode') or '?'}:{item.get('action_type') or '?'}"
        route_counts[route] = route_counts.get(route, 0) + 1

    recurrence_route = max(route_counts.items(), key=lambda pair: pair[1])[0] if route_counts else None
    recurrence_note = (
        f"Recent recurrence favors {recurrence_route}."
        if recurrence_route
        else "No recurrence pattern available yet."
    )

    if len(receipts) < 2:
        drift_note = "Baseline established. Run Lumina again to compare pattern return."
    else:
        previous = receipts[1]
        previous_witness = previous.get("harmonic_witness") or {}
        drift_parts: List[str] = []
        if latest_witness.get("continuity_shape") != previous_witness.get("continuity_shape"):
            drift_parts.append(
                f"continuity shape shifted from {previous_witness.get('continuity_shape')} to {latest_witness.get('continuity_shape')}"
            )
        if latest.get("input_behavior") != previous.get("input_behavior"):
            drift_parts.append(
                f"input behavior shifted from {previous.get('input_behavior') or 'none'} to {latest.get('input_behavior') or 'none'}"
            )
        if bool(latest.get("probe_run_id")) != bool(previous.get("probe_run_id")):
            drift_parts.append("probe witness availability changed")
        latest_caps = set(latest.get("exposed_capability_ids") or [])
        previous_caps = set(previous.get("exposed_capability_ids") or [])
        if latest_caps != previous_caps:
            drift_parts.append("exposed capability set changed")
        drift_note = "; ".join(drift_parts) if drift_parts else "Recent runs hold a stable witness shape."

    return {
        "latest_continuity_shape": latest_witness.get("continuity_shape"),
        "latest_input_listening_note": latest_witness.get("input_listening_note"),
        "latest_recomposition_summary": latest_witness.get("recomposition_summary"),
        "drift_note": drift_note,
        "recurrence_note": recurrence_note,
        "recent_shape_counts": dict(sorted(recent_shapes.items())),
    }


def state_snapshot(*, base_dir: Path = DEFAULT_RUNTIME_BASE, limit: int = 20) -> Dict[str, Any]:
    governance_log_path = base_dir / "governance_log_r1.jsonl"
    canon_lineage_path = base_dir / "canon_lineage_r1.jsonl"
    receipts = list_run_receipts(base_dir=base_dir, limit=limit)
    governance_events = _read_jsonl(governance_log_path, limit=500)
    canon_records = _read_jsonl(canon_lineage_path, limit=50)
    return {
        "schema_version": "lumina-studio-state-browser-v0.4",
        "read_only": True,
        "state_root": str(STATE_ROOT),
        "state_schema": state_schema_summary(),
        "runtime_base_dir": str(base_dir),
        "runtime_base_exists": base_dir.exists(),
        "logs_dir": str(base_dir / "logs"),
        "receipt_count_returned": len(receipts),
        "latest_runs": receipts,
        "harmonic_summary": harmonic_state_summary(receipts),
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
