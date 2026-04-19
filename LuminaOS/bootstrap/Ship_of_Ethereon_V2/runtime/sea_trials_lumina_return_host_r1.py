from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .continuity_restore_spike_r1 import ContinuityRestoreStore
    from .lumina_workspace_host_spike_r1 import LuminaWorkspaceHost
except Exception:
    from continuity_restore_spike_r1 import ContinuityRestoreStore
    from lumina_workspace_host_spike_r1 import LuminaWorkspaceHost

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


BASE_DIR = infer_state_root() / "sea_trials_lumina_return_host_r1"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)

FORBIDDEN_AUTHORITY_KEYS = {
    "governance",
    "canon_lineage",
    "mode_guard",
    "promotion",
    "transition",
    "record_hash",
    "validation_reference",
    "allowed",
}


def main() -> Dict[str, Any]:
    continuity = ContinuityRestoreStore(BASE_DIR / "shared_runtime")
    host = LuminaWorkspaceHost(BASE_DIR / "shared_runtime")

    project_id = "lumina-core"

    session = continuity.create_session(
        project_id=project_id,
        mode="Continuity",
        artifacts_in_scope=[
            "continuity_restore_spike_r1.py",
            "lumina_workspace_host_spike_r1.py",
        ],
        workspace_state={"open_panels": ["notes"]},
        continuation_notes=["verify checkpoint-only return before host handshake"],
    )
    checkpoint_one = continuity.write_checkpoint(session.session_id, "checkpoint_only_probe")
    payload_one = continuity.project_return_payload(project_id)

    host_session = host.create_host_session(
        project_id=project_id,
        mode="Continuity",
        active_layout_id="studio-focus",
        focus_target="lumina-return-lane",
        artifacts_in_scope=[
            "continuity_restore_spike_r1.py",
            "lumina_workspace_host_spike_r1.py",
        ],
        linked_restore_checkpoint=str(checkpoint_one),
        continuation_notes=["host bundle should remain workspace-owned"],
    )
    host.upsert_panel(
        host_session.host_session_id,
        panel_id="notes",
        panel_type="text",
        title="Project Notes",
        zone="left",
        priority=10,
        payload={"open_document": "continuation_notes.md"},
    )
    host.bind_tool(
        host_session.host_session_id,
        tool_id="restore-latest",
        label="Restore Latest Project State",
        launch_target="continuity_restore_spike_r1.py::resume_project",
        context_keys=["project_id"],
        pinned=True,
    )
    host.attach_reference(
        host_session.host_session_id,
        reference_id="bootstrap-readme",
        label="Bootstrap README",
        source="LuminaOS/bootstrap/Ship_of_Ethereon_V2/README.md",
        kind="runtime-reference",
    )
    host_snapshot = host.write_host_snapshot(
        host_session.host_session_id,
        last_completed_action="write_host_snapshot",
    )
    host_bundle = host.emit_host_bundle(project_id)

    checkpoint_two = continuity.write_checkpoint(session.session_id, "checkpoint_plus_host_probe")
    payload_two = continuity.project_return_payload(project_id)

    payload_one_latest = payload_one.get("latest_restore", {})
    payload_two_latest = payload_two.get("latest_restore", {})

    checkpoint_only_checks = {
        "return_strategy_checkpoint_only": payload_one.get("return_strategy") == "checkpoint_only",
        "linked_host_bundle_absent": payload_one_latest.get("linked_host_bundle") in (None, ""),
    }

    handshake_checks = {
        "return_strategy_checkpoint_plus_host": payload_two.get("return_strategy") == "checkpoint_plus_host",
        "linked_host_bundle_present": bool(payload_two_latest.get("linked_host_bundle")),
        "host_bundle_linked_restore_matches_checkpoint_one": host_bundle.get("linked_restore_checkpoint") == str(checkpoint_one),
        "host_bundle_project_matches": host_bundle.get("project_id") == project_id,
        "mode_preserved_through_handshake": payload_two_latest.get("current_mode") == "Continuity",
    }

    governance_boundary_checks = {
        "host_bundle_has_no_governance_authority_keys": not any(key in host_bundle for key in FORBIDDEN_AUTHORITY_KEYS),
        "restore_payload_has_no_governance_authority_keys": not any(key in payload_two for key in FORBIDDEN_AUTHORITY_KEYS),
        "latest_restore_has_no_governance_authority_keys": not any(key in payload_two_latest for key in FORBIDDEN_AUTHORITY_KEYS),
    }

    summary = {
        "suite": "Lumina Return / Host Handshake Sea Trial r1",
        "passed": all(checkpoint_only_checks.values()) and all(handshake_checks.values()) and all(governance_boundary_checks.values()),
        "project_id": project_id,
        "checkpoint_one": str(checkpoint_one),
        "checkpoint_two": str(checkpoint_two),
        "host_snapshot_id": host_snapshot.snapshot_id,
        "checkpoint_only_checks": checkpoint_only_checks,
        "handshake_checks": handshake_checks,
        "governance_boundary_checks": governance_boundary_checks,
        "payload_one": payload_one,
        "payload_two": payload_two,
        "host_bundle": host_bundle,
    }

    summary_path = BASE_DIR / "sea_trials_lumina_return_host_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {
        "summary_path": str(summary_path),
        "summary": summary,
    }


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
