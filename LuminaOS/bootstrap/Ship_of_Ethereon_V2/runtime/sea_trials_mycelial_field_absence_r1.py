from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import hashlib
import json
import subprocess
import tempfile

try:
    from .mycelial_coupling_receipt_r1 import (
        CouplingReceiptLedger,
        create_coupling_receipt,
    )
    from .runtime_runner_r1_merged import RuntimeRunner
except Exception:
    from mycelial_coupling_receipt_r1 import (
        CouplingReceiptLedger,
        create_coupling_receipt,
    )
    from runtime_runner_r1_merged import RuntimeRunner


RUNTIME_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
CAPABILITY_REGISTRY_PATH = RUNTIME_ROOT / "capability_registry_r1.json"

FIELD_PRESENT_OVERLAY = {
    "active": True,
    "anchor_language": ["english", "toki_pona"],
    "continuity_phrase": "field-present-control",
    "harmonic_signature": [432, 528, 963],
    "spiral_reference": "field-absence-control-r1",
}

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
    "ethereonic_layer_required_for_resume": False,
    "minerva_framework_required_for_governance": False,
    "psi42_required_for_mode_legality": False,
    "resonance_constructs_required_for_capability_loading": False,
    "ethereonic_language_required_for_checkpoint_resume": False,
}

PROMOTION_PAYLOAD = {
    "validation_artifact_id": "mycelial-field-absence-r1",
    "test_execution_log": "paired field-present and field-absent boundary checks",
    "change_summary": "validate canonical promotion without supplemental field context",
    "structural_impact_assessment": "temporary isolated sea-trial state only",
    "regression_check_confirmation": True,
    "conceptual_layer_check_confirmation": True,
    "runtime_requires_symbolic_interpretation": False,
}


def _bind_validation_artifact(payload: Dict[str, Any]) -> Dict[str, Any]:
    repository_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    artifact_path = (
        REPO_ROOT
        / ".lumina_state/ship_of_ethereon_v2/sea_trials_mycelial_field_absence_r1/promotion_validation.json"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(
            {
                "artifact_id": payload["validation_artifact_id"],
                "repository_head": repository_head,
                "passed": True,
                "authority_scope": "isolated_sea_trial_only",
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return {
        **payload,
        "validation_artifact_path": artifact_path.relative_to(REPO_ROOT).as_posix(),
        "validation_artifact_sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
        "candidate_commit_sha": repository_head,
    }


PROMOTION_PAYLOAD = _bind_validation_artifact(PROMOTION_PAYLOAD)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_context_bundle(runner: RuntimeRunner, bundle_id: str) -> Dict[str, Any]:
    path = runner.context_builder.output_dir / f"{bundle_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _capability_ids(result: Any) -> list[str]:
    return [str(capability.get("capability_id")) for capability in result.exposed_capabilities]


def _authority_projection(result: Any) -> Dict[str, Any]:
    governance = result.governance
    projection: Dict[str, Any] = {
        "ethereonic_layer_independence": governance.get("ethereonic_layer_independence", {}).get("allowed"),
        "ethereonic_attachment": governance.get("ethereonic_attachment", {}).get("allowed"),
        "transition": governance.get("transition", {}).get("allowed"),
        "mutation": governance.get("mutation", {}).get("allowed"),
        "symbolic_dependency": governance.get("symbolic_dependency", {}).get("allowed"),
        "capability_exposure": governance.get("capability_exposure", {}).get("allowed"),
        "capability_ids": _capability_ids(result),
    }
    if "promotion" in governance:
        projection["promotion"] = governance.get("promotion", {}).get("allowed")
    return projection


def _run_scenario(
    base_dir: Path,
    *,
    overlay: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    runner = RuntimeRunner(
        base_dir=base_dir,
        registry_path=CAPABILITY_REGISTRY_PATH,
    )

    transition = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="mycelial_field_absence_transition",
        action_type="transition",
        ethereonic_overlay=overlay,
        runtime_config=SAFE_RUNTIME_CONFIG,
        repo_path=REPO_ROOT,
    )
    transition_bundle = _load_context_bundle(runner, transition.context_bundle_id)
    transition_resume = runner.session_engine.resume_from_checkpoint(transition.checkpoint_path)

    canon = runner.run_cycle(
        current_mode="DryDock",
        target_mode="Canon",
        requested_action="mycelial_field_absence_canon_promotion",
        action_type="promotion",
        promotion_payload=PROMOTION_PAYLOAD,
        ethereonic_overlay=overlay,
        runtime_config=SAFE_RUNTIME_CONFIG,
        repo_path=REPO_ROOT,
    )
    canon_bundle = _load_context_bundle(runner, canon.context_bundle_id)
    canon_resume = runner.session_engine.resume_from_checkpoint(canon.checkpoint_path)

    return {
        "transition": {
            "halted": transition.halted,
            "target_mode": transition.target_mode,
            "authority_projection": _authority_projection(transition),
            "governance_chain_valid": transition.governance_chain_status.get("valid") is True,
            "supplemental_context": transition_bundle.get("supplemental_ethereonic_context"),
            "resumed_mode": transition_resume.current_mode,
            "resume_count": transition_resume.continuity_state.resume_count,
            "resumed_overlay": asdict(transition_resume.ethereonic_overlay),
        },
        "canon": {
            "halted": canon.halted,
            "target_mode": canon.target_mode,
            "authority_projection": _authority_projection(canon),
            "governance_chain_valid": canon.governance_chain_status.get("valid") is True,
            "supplemental_context": canon_bundle.get("supplemental_ethereonic_context"),
            "resumed_mode": canon_resume.current_mode,
            "resume_count": canon_resume.continuity_state.resume_count,
            "resumed_overlay": asdict(canon_resume.ethereonic_overlay),
            "canon_lineage": canon.canon_lineage,
            "lineage_integrity": runner.canon_lineage_store.verify_lineage(),
        },
    }


def run_trials(base_dir: Path) -> Dict[str, Any]:
    registry_hash_before = _sha256_file(CAPABILITY_REGISTRY_PATH)
    control = _run_scenario(base_dir / "field_present_control", overlay=FIELD_PRESENT_OVERLAY)
    absent = _run_scenario(base_dir / "field_absent", overlay=None)
    registry_hash_after = _sha256_file(CAPABILITY_REGISTRY_PATH)

    boundary_checks = {
        "control_field_context_is_present": bool(control["transition"]["supplemental_context"]),
        "control_canon_field_context_is_present": bool(control["canon"]["supplemental_context"]),
        "absent_transition_context_is_empty": absent["transition"]["supplemental_context"] == {},
        "absent_canon_context_is_empty": absent["canon"]["supplemental_context"] == {},
        "control_transition_completed": control["transition"]["halted"] is False,
        "absent_transition_completed": absent["transition"]["halted"] is False,
        "control_canon_promotion_completed": control["canon"]["halted"] is False,
        "absent_canon_promotion_completed": absent["canon"]["halted"] is False,
        "transition_authority_is_field_invariant": (
            control["transition"]["authority_projection"]
            == absent["transition"]["authority_projection"]
        ),
        "canon_authority_is_field_invariant": (
            control["canon"]["authority_projection"]
            == absent["canon"]["authority_projection"]
        ),
        "absent_transition_mode_legality_is_valid": (
            absent["transition"]["target_mode"] == "Observation"
            and absent["transition"]["authority_projection"]["transition"] is True
            and absent["transition"]["authority_projection"]["mutation"] is False
            and absent["transition"]["authority_projection"]["symbolic_dependency"] is True
        ),
        "absent_canon_mode_legality_is_valid": (
            absent["canon"]["target_mode"] == "Canon"
            and absent["canon"]["authority_projection"]["transition"] is True
            and absent["canon"]["authority_projection"]["mutation"] is True
            and absent["canon"]["authority_projection"]["promotion"] is True
            and absent["canon"]["authority_projection"]["symbolic_dependency"] is True
        ),
        "absent_transition_exposes_core_capabilities": {
            "session_state_manager",
            "mode_guard",
            "context_bundle_builder",
            "input_integrity_assessor",
            "continuity_restore_store",
            "lumina_workspace_host",
        }.issubset(absent["transition"]["authority_projection"]["capability_ids"]),
        "absent_canon_exposes_core_capabilities": {
            "session_state_manager",
            "mode_guard",
            "input_integrity_assessor",
            "continuity_restore_store",
        }.issubset(absent["canon"]["authority_projection"]["capability_ids"]),
        "control_governance_chains_are_valid": (
            control["transition"]["governance_chain_valid"]
            and control["canon"]["governance_chain_valid"]
        ),
        "absent_governance_chains_are_valid": (
            absent["transition"]["governance_chain_valid"]
            and absent["canon"]["governance_chain_valid"]
        ),
        "absent_transition_resumes_without_field": (
            absent["transition"]["resumed_mode"] == "Observation"
            and absent["transition"]["resume_count"] == 1
            and absent["transition"]["resumed_overlay"]["active"] is False
            and absent["transition"]["resumed_overlay"]["harmonic_signature"] == []
        ),
        "absent_canon_resumes_without_field": (
            absent["canon"]["resumed_mode"] == "Canon"
            and absent["canon"]["resume_count"] == 1
            and absent["canon"]["resumed_overlay"]["active"] is False
            and absent["canon"]["resumed_overlay"]["harmonic_signature"] == []
        ),
        "absent_canon_lineage_is_valid": (
            absent["canon"]["lineage_integrity"].get("valid") is True
            and absent["canon"]["lineage_integrity"].get("current_head") == "canon-0001"
            and (absent["canon"]["canon_lineage"] or {}).get("canon_version") == "canon-0001"
        ),
        "capability_registry_is_unchanged": registry_hash_before == registry_hash_after,
    }

    evidence_payload = {
        "transition_authority_is_field_invariant": boundary_checks["transition_authority_is_field_invariant"],
        "canon_authority_is_field_invariant": boundary_checks["canon_authority_is_field_invariant"],
        "absent_transition_resumes_without_field": boundary_checks["absent_transition_resumes_without_field"],
        "absent_canon_resumes_without_field": boundary_checks["absent_canon_resumes_without_field"],
        "absent_canon_lineage_is_valid": boundary_checks["absent_canon_lineage_is_valid"],
        "capability_registry_is_unchanged": boundary_checks["capability_registry_is_unchanged"],
    }
    receipt = create_coupling_receipt(
        signal_id="signal-mycelial-field-absence-r1",
        source="field_absence_counterfactual",
        destination="runtime_boundary_diagnostic",
        relation="diagnostic",
        created_at="2026-08-27T03:00:00+00:00",
        evidence_kind="derived",
        evidence_reference="sea-trial:mycelial-field-absence-r1",
        evidence_payload=evidence_payload,
        confidence=1.0,
        reversible=True,
        authority_effect=False,
        memory_effect="none",
        retention="ephemeral",
        effect_summary=(
            "Compared field-present and field-absent runs without changing runtime authority."
        ),
    )
    ledger = CouplingReceiptLedger(base_dir / "diagnostic_receipt")
    receipt_decision = ledger.ingest(receipt)
    receipt_integrity = ledger.verify_integrity()

    checks = {
        **boundary_checks,
        "diagnostic_receipt_is_accepted": receipt_decision.status == "accepted",
        "diagnostic_receipt_history_is_valid": receipt_integrity.get("valid") is True,
        "diagnostic_receipt_creates_no_authority": (
            receipt.authority_effect is False
            and receipt_decision.authority_effect is False
            and receipt_decision.authority_event_created is False
        ),
    }
    return {
        "schema_version": "sea-trials-mycelial-field-absence-r1",
        "suite": "Mycelial Field Absence Boundary R1",
        "passed": all(checks.values()),
        "checks": checks,
        "field_effect": {
            "control_transition_supplemental_keys": sorted(control["transition"]["supplemental_context"]),
            "absent_transition_supplemental_keys": sorted(absent["transition"]["supplemental_context"]),
            "transition_authority_projection": absent["transition"]["authority_projection"],
            "canon_authority_projection": absent["canon"]["authority_projection"],
        },
        "canon_resume": {
            "mode": absent["canon"]["resumed_mode"],
            "resume_count": absent["canon"]["resume_count"],
            "field_active": absent["canon"]["resumed_overlay"]["active"],
            "lineage_head": absent["canon"]["lineage_integrity"].get("current_head"),
        },
        "diagnostic_receipt": {
            "receipt_hash": receipt.receipt_hash,
            "decision": receipt_decision.to_dict(),
            "integrity": receipt_integrity,
        },
        "authority_effect": False,
        "limitations": (
            "Validates removal of supplemental Ethereonic context and symbolic overlays in isolated "
            "active-V2 transition, promotion, and checkpoint-resume cycles. It does not validate "
            "vessel replacement, resident reset, edge loss, or runtime-wide recovery."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the mycelial field-absence boundary trial.")
    parser.add_argument("--base-dir", default=None, help="Optional persistent directory for trial state.")
    parser.add_argument("--json", action="store_true", help="Print full trial detail.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.base_dir:
        result = run_trials(Path(args.base_dir))
    else:
        with tempfile.TemporaryDirectory(prefix="lumina-field-absence-") as temporary:
            result = run_trials(Path(temporary))

    if args.json:
        output = result
    else:
        output = {
            "suite": result["suite"],
            "passed": result["passed"],
            "check_count": len(result["checks"]),
            "failed_checks": [name for name, passed in result["checks"].items() if not passed],
            "canon_resume": result["canon_resume"],
            "authority_effect": result["authority_effect"],
        }
    print(json.dumps(output, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
