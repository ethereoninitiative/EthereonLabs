#!/usr/bin/env python3
"""Lumina Bridge State R1.

Read-only aggregation for the Ship of Ethereon bridge surface.

This module joins host/workspace orientation, local continuity witness, the
public Observation receipt, and committed runtime truth. It does not mutate
state, authorize actions, alter governance, or decide canon.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Optional

STUDIO_ROOT = Path(__file__).resolve().parent
BOOTSTRAP_ROOT = STUDIO_ROOT.parent
REPO_ROOT = Path(__file__).resolve().parents[4]
STATE_ROOT = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2"
DEFAULT_RUNTIME_BASE = STATE_ROOT / "runtime_runner_r1_actiontype_logging"

try:
    from lumina_state_browser import state_snapshot
except ImportError:  # pragma: no cover - package-style import fallback
    from .lumina_state_browser import state_snapshot

SCHEMA_VERSION = "lumina-bridge-state-r1"
AUTHORITY_BOUNDARY = (
    "Bridge R1 is a read-only orientation surface. It may summarize existing "
    "workspace markers, runtime receipts, and committed evidence; it may not "
    "authorize action, alter governance, mutate canon, change mode legality, "
    "expose capabilities, or execute a governed cycle."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _active_workspace(state_root: Path) -> Dict[str, Any]:
    project = _read_json(state_root / "active_project.json")
    session = _read_json(state_root / "active_session.json")
    return {
        "project": {
            "slug": project.get("active_project_slug"),
            "name": project.get("active_project_name"),
            "project_root": project.get("project_root"),
            "set_at": project.get("set_at"),
            "present": bool(project),
        },
        "harbor_session": {
            "session_id": session.get("active_session_id"),
            "title": session.get("active_session_title"),
            "project_slug": session.get("project_slug"),
            "session_root": session.get("session_root"),
            "set_at": session.get("set_at"),
            "present": bool(session),
        },
    }


def _runtime_witness(latest_cycle: Dict[str, Any]) -> Dict[str, Any]:
    mode = _safe_dict(latest_cycle.get("mode"))
    status = _safe_dict(latest_cycle.get("status"))
    probe = _safe_dict(latest_cycle.get("probe"))
    return {
        "run_id": latest_cycle.get("run_id"),
        "timestamp": latest_cycle.get("timestamp"),
        "requested_action": latest_cycle.get("requested_action"),
        "action_type": latest_cycle.get("action_type"),
        "requested_mode": mode.get("requested"),
        "current_mode": mode.get("current"),
        "status": status.get("label"),
        "halted": status.get("halted"),
        "halt_reason": status.get("reason"),
        "probe": {
            "active": probe.get("active"),
            "instrument_version": probe.get("instrument_version"),
            "coherence": probe.get("coherence"),
            "presence": probe.get("presence"),
            "lock": probe.get("lock"),
        },
        "capabilities": list(latest_cycle.get("capabilities") or []),
    }


def _authority_snapshot(public_truth: Dict[str, Any]) -> Dict[str, Any]:
    runtime_truth = _safe_dict(public_truth.get("runtime_truth"))
    committed = _safe_dict(runtime_truth.get("committed_authority"))
    observed = _safe_dict(runtime_truth.get("observed_runtime_state"))
    return {
        "public_truth_schema": public_truth.get("schema_version"),
        "source_run_id": public_truth.get("latest_cycle_run_id"),
        "source_timestamp": public_truth.get("latest_cycle_timestamp"),
        "scope": _safe_dict(public_truth.get("runtime_truth_scope")),
        "committed": {
            "governance_chain": _safe_dict(committed.get("governance_chain")),
            "canon_lineage": _safe_dict(committed.get("canon_lineage")),
            "promotion": _safe_dict(committed.get("promotion")),
            "post_promotion_verification": _safe_dict(
                committed.get("post_promotion_verification")
            ),
            "evidence_paths": _safe_dict(committed.get("evidence_paths")),
        },
        "observed": {
            "scope": observed.get("scope"),
            "does_not_override_committed_authority": observed.get(
                "does_not_override_committed_authority"
            ),
            "governance_chain": _safe_dict(observed.get("governance_chain")),
            "canon_lineage": _safe_dict(observed.get("canon_lineage")),
        },
        "protocol_conformance": _safe_dict(runtime_truth.get("protocol_conformance")),
        "capability_registry": _safe_dict(runtime_truth.get("capability_registry")),
        "symbolic_boundary": _safe_dict(runtime_truth.get("symbolic_boundary")),
    }


def _correlation_snapshot(
    workspace: Dict[str, Any], local_state: Dict[str, Any]
) -> Dict[str, Any]:
    latest_runs = local_state.get("latest_runs") or []
    latest_run = latest_runs[0] if latest_runs and isinstance(latest_runs[0], dict) else {}
    project = _safe_dict(workspace.get("project"))
    harbor_session = _safe_dict(workspace.get("harbor_session"))
    references = {
        "project_slug": project.get("slug"),
        "harbor_session_id": harbor_session.get("session_id"),
        "runtime_session_id": latest_run.get("session_id"),
        "lumina_project_id": latest_run.get("lumina_project_id"),
        "context_bundle_id": latest_run.get("context_bundle_id"),
    }
    visible_count = sum(1 for value in references.values() if value)
    return {
        "status": "references_visible" if visible_count else "not_available",
        "typed_envelope_verified": False,
        "references": references,
        "note": (
            "Bridge R1 surfaces identifiers without inferring identity equivalence. "
            "A typed correlation envelope remains the authority for verified linkage."
        ),
    }


def _navigation(workspace: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    project = _safe_dict(workspace.get("project"))
    session = _safe_dict(workspace.get("harbor_session"))
    if not project.get("present"):
        recommended = "Establish a Harbor project before beginning governed work."
        primary = "lumina project create EthereonLabs --open"
    elif not session.get("present"):
        recommended = "Open a Harbor session so local continuity has a named return point."
        primary = 'lumina session create "Initial Harbor session" --open'
    elif runtime.get("halted"):
        recommended = "Inspect the halted receipt before requesting another maneuver."
        primary = "lumina state --limit 3"
    else:
        recommended = "Enter Lumina Studio for an explicit governed action."
        primary = "lumina studio"
    return {
        "recommended_action": recommended,
        "primary_command": primary,
        "commands": [
            primary,
            "lumina dashboard",
            "lumina compare",
            "lumina state --limit 3",
            "lumina observe",
        ],
        "rule": "Bridge orients; Studio acts through the governed runtime path.",
    }


def build_bridge_state(
    *,
    repo_root: Path = REPO_ROOT,
    state_root: Path = STATE_ROOT,
    runtime_base: Optional[Path] = None,
    limit: int = 12,
) -> Dict[str, Any]:
    """Build a read-only ship-position snapshot from existing artifacts."""
    runtime_base = runtime_base or (state_root / "runtime_runner_r1_actiontype_logging")
    workspace = _active_workspace(state_root)
    try:
        local_state = state_snapshot(base_dir=runtime_base, limit=limit)
    except Exception as exc:  # bridge should degrade rather than invent state
        local_state = {
            "read_only": True,
            "error": str(exc),
            "latest_runs": [],
            "harmonic_summary": {},
            "governance": {},
            "canon_head": None,
        }

    latest_cycle_path = repo_root / "public" / "runtime" / "latest_cycle.json"
    public_truth_path = repo_root / "public" / "runtime" / "runtime_truth_snapshot.json"
    latest_cycle = _read_json(latest_cycle_path)
    public_truth = _read_json(public_truth_path)
    runtime = _runtime_witness(latest_cycle)
    authority = _authority_snapshot(public_truth)

    latest_run_id = latest_cycle.get("run_id")
    truth_run_id = public_truth.get("latest_cycle_run_id")
    latest_timestamp = latest_cycle.get("timestamp")
    truth_timestamp = public_truth.get("latest_cycle_timestamp")
    alignment = {
        "latest_cycle_present": bool(latest_cycle),
        "public_truth_present": bool(public_truth),
        "run_id_matches": bool(latest_run_id and latest_run_id == truth_run_id),
        "timestamp_matches": bool(
            latest_timestamp and latest_timestamp == truth_timestamp
        ),
    }
    alignment["aligned"] = all(
        [
            alignment["latest_cycle_present"],
            alignment["public_truth_present"],
            alignment["run_id_matches"],
            alignment["timestamp_matches"],
        ]
    )

    harmonic = _safe_dict(local_state.get("harmonic_summary"))
    continuity = {
        "latest_shape": harmonic.get("latest_continuity_shape"),
        "drift_note": harmonic.get("drift_note"),
        "recurrence_note": harmonic.get("recurrence_note"),
        "input_listening_note": harmonic.get("latest_input_listening_note"),
        "local_receipt_count": local_state.get("receipt_count_returned"),
        "local_governance": _safe_dict(local_state.get("governance")),
        "local_canon_head": local_state.get("canon_head"),
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "read_only": True,
        "vessel": {
            "name": "Ship of Ethereon",
            "habitat": "Lumina",
            "position_surface": "Bridge R1",
            "spatial_frame": "ship / orbital habitat / planetary realm",
        },
        "workspace": workspace,
        "continuity": continuity,
        "runtime_witness": runtime,
        "runtime_truth_alignment": alignment,
        "authority": authority,
        "correlation": _correlation_snapshot(workspace, local_state),
        "navigation": _navigation(workspace, runtime),
        "sources": {
            "active_project": str(state_root / "active_project.json"),
            "active_session": str(state_root / "active_session.json"),
            "local_runtime_base": str(runtime_base),
            "latest_cycle": str(latest_cycle_path),
            "public_runtime_truth": str(public_truth_path),
        },
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


if __name__ == "__main__":
    print(json.dumps(build_bridge_state(), indent=2))
