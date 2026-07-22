from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import shutil

try:
    from .lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
except Exception:
    from lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost

try:
    from .repo_paths_r1 import state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import state_root as _state_root_helper
    except Exception:
        _state_root_helper = None


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            return Path(_state_root_helper())
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent / ".lumina_state" / "ship_of_ethereon_v2"
    return Path(__file__).resolve().parents[4] / ".lumina_state" / "ship_of_ethereon_v2"


BASE_DIR = infer_state_root() / "sea_trials_stationary_habitation_cold_return_r1"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)

FORBIDDEN_AUTHORITY_KEYS = {
    "allowed",
    "canon_lineage",
    "governance",
    "mode_guard",
    "promotion",
    "record_hash",
    "transition",
    "validation_reference",
}


def _forbidden_key_paths(node: Any, path: str = "root") -> List[str]:
    found: List[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_AUTHORITY_KEYS:
                found.append(child_path)
            found.extend(_forbidden_key_paths(value, child_path))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(_forbidden_key_paths(value, f"{path}[{index}]"))
    return found


def main() -> Dict[str, Any]:
    runtime_root = BASE_DIR / "stationary_runtime"
    project_id = "lumina-stationary-habitation-r1"
    pending_action = "review cold-return evidence before any new action"
    completed_action = "prepare stationary-habitation checkpoint"
    artifacts = [
        "docs/LUMINA_HABITAT_CREATION_CHECKLIST.md",
        "runtime/lumina_return_host_repo_native_bridge_r1.py",
        "runtime/sea_trials_stationary_habitation_cold_return_r1.py",
    ]
    continuation_notes = [
        "presence must precede movement",
        "return should preserve intention without converting it into permission",
    ]
    workspace_state = {
        "active_lane": "stationary-habitation",
        "open_panels": ["continuity-evidence", "next-action"],
    }

    # Phase one: create a bounded project and host state before simulated absence.
    continuity_before = ContinuityRestoreStore(runtime_root)
    host_before = LuminaWorkspaceHost(runtime_root)

    session = continuity_before.create_session(
        project_id=project_id,
        mode="Continuity",
        artifacts_in_scope=artifacts,
        workspace_state=workspace_state,
        continuation_notes=continuation_notes,
    )
    session.pending_next_action = pending_action
    session.last_completed_action = completed_action
    continuity_before.save_session(session)
    checkpoint_path = continuity_before.write_checkpoint(
        session.session_id,
        "stationary habitation before absence",
    )

    host_session = host_before.create_host_session(
        project_id=project_id,
        mode="Continuity",
        active_layout_id="stationary-habitation-focus",
        focus_target="cold-return-evidence",
        artifacts_in_scope=artifacts,
        linked_restore_checkpoint=str(checkpoint_path),
        continuation_notes=continuation_notes,
    )
    host_before.upsert_panel(
        host_session.host_session_id,
        panel_id="continuity-evidence",
        panel_type="receipt-view",
        title="Continuity Evidence",
        zone="center",
        priority=10,
        payload={"evidence_scope": "cold-return-r1"},
    )
    host_before.bind_tool(
        host_session.host_session_id,
        tool_id="inspect-return-payload",
        label="Inspect Return Payload",
        launch_target="project_return_repo_native_r1.py::project_return_payload",
        context_keys=["project_id"],
        pinned=True,
    )
    host_before.attach_reference(
        host_session.host_session_id,
        reference_id="habitat-checklist",
        label="Lumina Habitat Creation Checklist",
        source="docs/LUMINA_HABITAT_CREATION_CHECKLIST.md",
        kind="planning-reference",
        metadata={"authority": "roadmap-only"},
    )
    host_before.write_host_snapshot(
        host_session.host_session_id,
        last_completed_action="write stationary habitation host snapshot",
    )

    return_before = continuity_before.project_return_payload(project_id)
    host_bundle_before = host_before.emit_host_bundle(project_id)
    checkpoint_before = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    # Simulated absence boundary: discard every live store object and reconstruct
    # fresh owners from the same on-disk state. This is deliberately narrower than
    # a process restart, OS reboot, power-loss trial, or application upgrade.
    del continuity_before
    del host_before

    continuity_after = ContinuityRestoreStore(runtime_root)
    host_after = LuminaWorkspaceHost(runtime_root)
    return_after = continuity_after.project_return_payload(project_id)
    host_bundle_after = host_after.emit_host_bundle(project_id)

    latest_restore = return_after.get("latest_restore", {})
    checkpoint_session = checkpoint_before.get("session_state", {})
    return_forbidden_paths = _forbidden_key_paths(return_after)
    host_forbidden_paths = _forbidden_key_paths(host_bundle_after)

    checks = {
        "checkpoint_survived": checkpoint_path.exists(),
        "checkpoint_project_preserved": checkpoint_session.get("project_id") == project_id,
        "checkpoint_session_preserved": checkpoint_session.get("session_id") == session.session_id,
        "return_project_preserved": return_after.get("project_id") == project_id,
        "return_session_preserved": latest_restore.get("session_id") == session.session_id,
        "mode_preserved": latest_restore.get("current_mode") == "Continuity",
        "artifacts_preserved": latest_restore.get("artifacts_in_scope") == artifacts,
        "workspace_state_preserved": latest_restore.get("workspace_state") == workspace_state,
        "continuation_notes_preserved": latest_restore.get("continuation_notes") == continuation_notes,
        "pending_intention_preserved": latest_restore.get("pending_next_action") == pending_action,
        "pending_intention_not_auto_completed": latest_restore.get("last_completed_action") == completed_action,
        "return_strategy_preserved": return_after.get("return_strategy") == "checkpoint_plus_host",
        "host_session_preserved": host_bundle_after.get("host_session_id") == host_session.host_session_id,
        "host_mode_preserved": host_bundle_after.get("current_mode") == "Continuity",
        "host_layout_preserved": host_bundle_after.get("active_layout_id") == "stationary-habitation-focus",
        "host_focus_preserved": host_bundle_after.get("focus_target") == "cold-return-evidence",
        "host_panel_preserved": any(
            row.get("panel_id") == "continuity-evidence"
            for row in host_bundle_after.get("panels", [])
        ),
        "host_tool_binding_preserved": any(
            row.get("tool_id") == "inspect-return-payload"
            for row in host_bundle_after.get("tool_bindings", [])
        ),
        "host_reference_preserved": any(
            row.get("reference_id") == "habitat-checklist"
            for row in host_bundle_after.get("references", [])
        ),
        "linked_checkpoint_preserved": host_bundle_after.get("linked_restore_checkpoint") == str(checkpoint_path),
        "return_payload_stable_across_reconstruction": return_after == return_before,
        "host_bundle_stable_across_reconstruction": host_bundle_after == host_bundle_before,
        "return_contains_no_authority_keys": not return_forbidden_paths,
        "host_contains_no_authority_keys": not host_forbidden_paths,
    }

    summary = {
        "suite": "Lumina Stationary Habitation Cold Return Sea Trial R1",
        "passed": all(checks.values()),
        "scope": {
            "proves": [
                "fresh continuity and host store objects can reconstruct the same project return from persisted local state",
                "project orientation, workspace state, artifacts, notes, and host layout survive the reconstruction boundary",
                "unfinished intention remains visible without being marked completed by the return operation",
                "return and host payloads remain non-authoritative",
            ],
            "does_not_prove": [
                "full application close and reopen",
                "separate-process restart",
                "operating-system reboot",
                "power-loss recovery",
                "upgrade or migration continuity",
                "persistent autonomous cognition",
                "physical embodiment readiness",
            ],
        },
        "project_id": project_id,
        "session_id": session.session_id,
        "host_session_id": host_session.host_session_id,
        "checkpoint_path": str(checkpoint_path),
        "checks": checks,
        "forbidden_key_paths": {
            "return_payload": return_forbidden_paths,
            "host_bundle": host_forbidden_paths,
        },
        "return_payload": return_after,
        "host_bundle": host_bundle_after,
    }

    summary_path = BASE_DIR / "stationary_habitation_cold_return_r1_report.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output["summary"]["passed"] else 1)
