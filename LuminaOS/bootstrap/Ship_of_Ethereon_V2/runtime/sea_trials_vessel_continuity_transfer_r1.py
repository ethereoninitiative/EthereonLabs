from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import shutil

try:
    from .lumina_continue_controller_r1 import LuminaContinueController
    from .lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
    from .repo_paths_r1 import state_root
    from .vessel_continuity_transfer_r1 import (
        VesselContinuityTransfer,
        VesselTransferCollisionError,
        VesselTransferIntegrityError,
        continuity_projection,
    )
except Exception:
    from lumina_continue_controller_r1 import LuminaContinueController
    from lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
    from repo_paths_r1 import state_root
    from vessel_continuity_transfer_r1 import (
        VesselContinuityTransfer,
        VesselTransferCollisionError,
        VesselTransferIntegrityError,
        continuity_projection,
    )


BASE_DIR = state_root() / "sea_trials_vessel_continuity_transfer_r1"
PROJECT_ID = "lumina-vessel-transfer-r1"

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


def _seed_source(surface_root: Path) -> Dict[str, Any]:
    continuity = ContinuityRestoreStore(surface_root)
    host = LuminaWorkspaceHost(surface_root)
    artifacts = [
        "docs/LUMINA_HABITAT_CREATION_CHECKLIST.md",
        "runtime/vessel_continuity_transfer_r1.py",
        "runtime/sea_trials_vessel_continuity_transfer_r1.py",
    ]
    notes = [
        "continuity evidence may cross vessels without becoming an identity verdict",
        "unfinished intention remains visible and non-authorizing",
    ]
    session = continuity.create_session(
        project_id=PROJECT_ID,
        mode="Continuity",
        artifacts_in_scope=artifacts,
        workspace_state={
            "active_lane": "vessel-portability",
            "open_panels": ["return-evidence", "transfer-receipt"],
        },
        continuation_notes=notes,
    )
    session.pending_next_action = "inspect transfer evidence before choosing new work"
    session.last_completed_action = "prepare bounded vessel transfer capsule"
    continuity.save_session(session)
    checkpoint = continuity.write_checkpoint(session.session_id, "portable project return")

    host_session = host.create_host_session(
        project_id=PROJECT_ID,
        mode="Continuity",
        active_layout_id="vessel-transfer-focus",
        focus_target="cross-vessel-continuity-evidence",
        artifacts_in_scope=artifacts,
        linked_restore_checkpoint=str(checkpoint),
        continuation_notes=notes,
    )
    host.upsert_panel(
        host_session.host_session_id,
        panel_id="transfer-receipt",
        panel_type="receipt-view",
        title="Vessel Transfer Receipt",
        zone="center",
        priority=10,
        payload={"authority": "evidence-only"},
    )
    host.attach_reference(
        host_session.host_session_id,
        reference_id="habitat-checklist",
        label="Lumina Habitat Creation Checklist",
        source="docs/LUMINA_HABITAT_CREATION_CHECKLIST.md",
        kind="planning-reference",
        metadata={"authority": "roadmap-only"},
    )
    host.write_host_snapshot(host_session.host_session_id)

    transfer = VesselContinuityTransfer(surface_root)
    return {
        "transfer": transfer,
        "session_id": session.session_id,
        "checkpoint": checkpoint,
        "project_return": transfer.project_return_payload(PROJECT_ID),
    }


def main() -> Dict[str, Any]:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    source_runtime_root = BASE_DIR / "source_vessel_runtime"
    target_runtime_root = BASE_DIR / "target_vessel_runtime"
    tamper_runtime_root = BASE_DIR / "tamper_target_runtime"
    source_surface_root = source_runtime_root / "lumina_project_surface"
    target_surface_root = target_runtime_root / "lumina_project_surface"
    tamper_surface_root = tamper_runtime_root / "lumina_project_surface"
    capsule_path = BASE_DIR / "transport" / "lumina-vessel-transfer-r1.json"
    tampered_path = BASE_DIR / "transport" / "lumina-vessel-transfer-r1-tampered.json"

    seeded = _seed_source(source_surface_root)
    source_before = seeded["project_return"]
    source_projection = continuity_projection(source_before)
    source_checkpoint = str(seeded["checkpoint"])
    source_session_before = seeded["transfer"].load_session(seeded["session_id"])

    export_result = seeded["transfer"].export_project(
        project_id=PROJECT_ID,
        capsule_path=capsule_path,
        source_vessel_id="station-alpha",
    )
    verified = VesselContinuityTransfer.verify_capsule(capsule_path)

    importer = VesselContinuityTransfer(target_surface_root)
    import_result = importer.import_project(
        capsule_path=capsule_path,
        target_vessel_id="station-beta",
    )
    target_before_continue = importer.project_return_payload(PROJECT_ID)
    target_session_before = importer.load_session(seeded["session_id"])
    target_restore = target_before_continue["latest_restore"]
    target_checkpoint = str(target_restore["checkpoint_path"])
    target_host = dict(target_before_continue.get("host_bundle") or {})

    collision_rejected = False
    collision_checkpoint_before = Path(target_checkpoint).read_bytes()
    try:
        importer.import_project(
            capsule_path=capsule_path,
            target_vessel_id="station-beta",
        )
    except VesselTransferCollisionError:
        collision_rejected = True
    collision_checkpoint_after = Path(target_checkpoint).read_bytes()

    tampered = json.loads(capsule_path.read_text(encoding="utf-8"))
    tampered["payload"]["session_state"]["pending_next_action"] = "tampered action"
    tampered_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
    tamper_rejected = False
    tamper_importer = VesselContinuityTransfer(tamper_surface_root)
    try:
        tamper_importer.import_project(
            capsule_path=tampered_path,
            target_vessel_id="station-gamma",
        )
    except VesselTransferIntegrityError:
        tamper_rejected = True
    tamper_files = [path for path in tamper_importer.storage_root.rglob("*") if path.is_file()]

    controller = LuminaContinueController(base_dir=target_runtime_root)
    preflight = controller.preflight(project_id=PROJECT_ID)
    continued = controller.continue_cycle(project_id=PROJECT_ID)
    source_after = seeded["transfer"].project_return_payload(PROJECT_ID)
    source_session_after = seeded["transfer"].load_session(seeded["session_id"])

    receipt_forbidden = _forbidden_key_paths(import_result.receipt)
    return_forbidden = _forbidden_key_paths(target_before_continue)
    checks = {
        "capsule_written": capsule_path.is_file(),
        "capsule_schema_verified": verified.get("schema_version") == "lumina-vessel-continuity-capsule-r1",
        "capsule_declares_no_authority": verified.get("authority_effect") is False,
        "capsule_declares_no_identity": verified.get("identity_claimed") is False,
        "source_and_target_vessels_are_distinct": (
            import_result.receipt.get("source_vessel_id") == "station-alpha"
            and import_result.receipt.get("target_vessel_id") == "station-beta"
        ),
        "continuity_projection_matches_across_vessels": (
            continuity_projection(target_before_continue) == source_projection
        ),
        "import_receipt_projection_hashes_match": (
            import_result.receipt.get("projection_match") is True
            and import_result.receipt.get("source_continuity_projection_hash")
            == import_result.receipt.get("target_continuity_projection_hash")
        ),
        "checkpoint_rebased_to_target_vessel": (
            target_checkpoint != source_checkpoint
            and target_checkpoint.startswith(str(importer.storage_root))
            and Path(target_checkpoint).is_file()
        ),
        "host_checkpoint_rebased_to_target_vessel": (
            target_host.get("linked_restore_checkpoint") == target_checkpoint
        ),
        "import_did_not_invoke_continuation": (
            import_result.receipt.get("continuation_invoked") is False
            and target_session_before == verified["payload"]["session_state"] | {
                "last_checkpoint": target_checkpoint,
                "linked_host_bundle": import_result.receipt["imported_paths"]["host_bundle"],
            }
        ),
        "explicit_continue_reads_imported_intention": (
            preflight.get("guidance_strategy") in {
                "pending_next_action",
                "pending_next_action_history_aligned",
            }
            and "inspect transfer evidence" in str(preflight.get("recommended_next_action") or "")
        ),
        "explicit_continue_runs_governed_cycle": (
            continued.runtime_result.get("halted") is False
            and continued.runtime_result.get("target_mode") == "Observation"
            and continued.runtime_result.get("action_type") == "audit"
            and (continued.runtime_result.get("governance_chain_status") or {}).get("valid") is True
        ),
        "source_session_unchanged": source_session_after == source_session_before,
        "source_projection_unchanged": continuity_projection(source_after) == source_projection,
        "repeat_import_fails_closed": collision_rejected,
        "collision_did_not_overwrite_checkpoint": (
            collision_checkpoint_after == collision_checkpoint_before
        ),
        "tampered_capsule_rejected": tamper_rejected,
        "tampered_capsule_wrote_no_project_files": not tamper_files,
        "import_receipt_declares_no_authority": import_result.receipt.get("authority_effect") is False,
        "import_receipt_declares_no_identity": import_result.receipt.get("identity_claimed") is False,
        "import_receipt_contains_no_authority_keys": not receipt_forbidden,
        "project_return_contains_no_authority_keys": not return_forbidden,
    }
    report = {
        "schema_version": "sea-trials-vessel-continuity-transfer-r1",
        "suite": "Lumina Vessel Continuity Transfer R1",
        "passed": all(checks.values()),
        "checks": checks,
        "scope": {
            "proves": [
                "one active repo-native project-return surface can move between distinct state roots",
                "path-independent continuity evidence matches after checkpoint and host links are rebased",
                "import is explicit, non-overwriting, integrity-checked, and does not invoke continuation",
                "a later explicit lumina continue cycle reads the imported intention through governed runtime",
                "transport receipts distinguish evidence preservation from an identity claim",
            ],
            "does_not_prove": [
                "resident identity across model, process, account, or hardware replacement",
                "complete runtime-state migration",
                "governance or canon transfer",
                "operating-system reboot, power-loss recovery, or application upgrade",
                "autonomous permission to export or import state",
            ],
        },
        "project_id": PROJECT_ID,
        "source_checkpoint": source_checkpoint,
        "target_checkpoint": target_checkpoint,
        "capsule_path": str(capsule_path),
        "export_receipt": export_result.receipt,
        "import_receipt": import_result.receipt,
        "explicit_continue_receipt": continued.compact_receipt(),
        "forbidden_key_paths": {
            "import_receipt": receipt_forbidden,
            "project_return": return_forbidden,
        },
        "authority_effect": False,
        "identity_claimed": False,
    }
    report_path = BASE_DIR / "vessel_continuity_transfer_r1_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return {"summary_path": str(report_path), "summary": report}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output["summary"]["passed"] else 1)
