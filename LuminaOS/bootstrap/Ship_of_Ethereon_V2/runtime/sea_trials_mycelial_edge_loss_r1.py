from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Dict
import argparse
import hashlib
import json
import tempfile

try:
    from .mycelial_coupling_receipt_r1 import (
        CouplingReceiptLedger,
        create_coupling_receipt,
    )
    from .mycelial_edge_loss_r1 import (
        CANONICAL_REFERENCE,
        FieldEdgeObservation,
        observe_edge_loss,
    )
    from .project_return_repo_native_r1 import ProjectReturnStore
except Exception:
    from mycelial_coupling_receipt_r1 import (
        CouplingReceiptLedger,
        create_coupling_receipt,
    )
    from mycelial_edge_loss_r1 import (
        CANONICAL_REFERENCE,
        FieldEdgeObservation,
        observe_edge_loss,
    )
    from project_return_repo_native_r1 import ProjectReturnStore


RUNTIME_ROOT = Path(__file__).resolve().parent
CAPABILITY_REGISTRY_PATH = RUNTIME_ROOT / "capability_registry_r1.json"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {str(key) for key in value} | {
            nested
            for child in value.values()
            for nested in _all_keys(child)
        }
    if isinstance(value, list):
        return {nested for child in value for nested in _all_keys(child)}
    return set()


def _rejection_checks() -> Dict[str, bool]:
    invalid_role_rejected = False
    authority_claim_rejected = False
    try:
        observe_edge_loss(
            [
                FieldEdgeObservation(
                    edge_id="invalid-role",
                    source="source",
                    destination="destination",
                    path_role="governor",
                    available=True,
                    evidence_reference="test:invalid-role",
                )
            ],
            [],
        )
    except ValueError:
        invalid_role_rejected = True
    try:
        observe_edge_loss(
            [
                FieldEdgeObservation(
                    edge_id="authority-claim",
                    source="source",
                    destination="destination",
                    path_role="non_authoritative_diagnostic",
                    available=True,
                    evidence_reference="test:authority-claim",
                    authority_effect=True,
                )
            ],
            [],
        )
    except ValueError:
        authority_claim_rejected = True
    return {
        "invalid_path_role_is_rejected": invalid_role_rejected,
        "authority_claim_is_rejected": authority_claim_rejected,
    }


def run_trials(base_dir: Path) -> Dict[str, Any]:
    registry_hash_before = _sha256_file(CAPABILITY_REGISTRY_PATH)
    project_id = "mycelial-edge-loss-r1"
    store = ProjectReturnStore(base_dir / "project_return")
    store.host_bundle_dir = base_dir / "workspace_host" / "host_bundles"
    store.host_bundle_dir.mkdir(parents=True, exist_ok=True)
    session = store.create_session(
        project_id=project_id,
        mode="Continuity",
        artifacts_in_scope=[
            "project_return_repo_native_r1.py",
            "mycelial_coupling_receipt_r1.py",
            "mycelial_edge_loss_r1.py",
        ],
    )
    session.workspace_state = {
        "focus_target": "edge-loss-counterfactual",
        "open_panels": ["continuity", "field-diagnostic"],
    }
    session.continuation_notes = [
        "canonical recovery must remain independent of the field diagnostic edge"
    ]
    session.pending_next_action = "inspect edge-loss receipt"
    session.last_completed_action = "establish baseline topology"
    store.save_session(session)
    checkpoint_path = store.write_checkpoint(session.session_id, "edge_loss_baseline")
    return_before = store.project_return_payload(project_id)
    checkpoint_before = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    field_ledger = CouplingReceiptLedger(base_dir / "field_diagnostic")
    field_receipt = create_coupling_receipt(
        signal_id="signal-mycelial-edge-loss-source-0001",
        source="supplemental_field_context",
        destination="runtime_boundary_diagnostic",
        relation="diagnostic",
        created_at="2026-08-30T17:40:00+00:00",
        evidence_kind="observed",
        evidence_reference="sea-trial:mycelial-edge-loss-source-r1",
        evidence_payload={
            "diagnostic_path": "coupling_receipt_intake_r1.jsonl",
            "authority_effect": False,
        },
        confidence=1.0,
        reversible=True,
        authority_effect=False,
        memory_effect="topology",
        retention="ephemeral",
        effect_summary="Establish a removable non-authoritative diagnostic edge.",
    )
    field_decision = field_ledger.ingest(field_receipt)
    diagnostic_path = field_ledger.decisions_path

    baseline_edges = [
        FieldEdgeObservation(
            edge_id="project-return-to-checkpoint",
            source="project_restore_latest",
            destination="checkpoint",
            path_role=CANONICAL_REFERENCE,
            available=checkpoint_path.exists(),
            evidence_reference=str(checkpoint_path),
        ),
        FieldEdgeObservation(
            edge_id="checkpoint-to-session-state",
            source="checkpoint",
            destination="session_state",
            path_role=CANONICAL_REFERENCE,
            available=(
                checkpoint_before.get("session_state", {}).get("session_id")
                == session.session_id
            ),
            evidence_reference=str(checkpoint_path),
        ),
        FieldEdgeObservation(
            edge_id="coupling-intake-to-field-diagnostic",
            source="coupling_receipt_intake",
            destination="field_diagnostic",
            path_role="non_authoritative_diagnostic",
            available=diagnostic_path.exists(),
            evidence_reference=str(diagnostic_path),
        ),
    ]

    diagnostic_path.unlink()

    return_after = store.project_return_payload(project_id)
    recovered_checkpoint_path = Path(return_after["latest_restore"]["checkpoint_path"])
    checkpoint_after = json.loads(recovered_checkpoint_path.read_text(encoding="utf-8"))
    recovered_session = store.load_session(return_after["latest_restore"]["session_id"])
    source_integrity_after = field_ledger.verify_integrity()

    observed_edges = [
        replace(
            baseline_edges[0],
            available=(
                recovered_checkpoint_path.exists()
                and recovered_checkpoint_path == checkpoint_path
            ),
        ),
        replace(
            baseline_edges[1],
            available=(
                checkpoint_after.get("session_state", {}).get("session_id")
                == recovered_session.session_id
            ),
        ),
        replace(baseline_edges[2], available=diagnostic_path.exists()),
    ]
    report = observe_edge_loss(baseline_edges, observed_edges)
    repeated_report = observe_edge_loss(baseline_edges, observed_edges)

    canonical_loss_observation = [
        replace(edge, available=False)
        if edge.edge_id == "project-return-to-checkpoint"
        else edge
        for edge in baseline_edges
    ]
    canonical_loss_report = observe_edge_loss(
        baseline_edges,
        canonical_loss_observation,
    )

    recovery_evidence = {
        "project_id_matches": return_after.get("project_id") == project_id,
        "return_strategy_is_checkpoint_only": (
            return_after.get("return_strategy") == "checkpoint_only"
        ),
        "checkpoint_survived": recovered_checkpoint_path.exists(),
        "checkpoint_path_matches": recovered_checkpoint_path == checkpoint_path,
        "session_id_matches": recovered_session.session_id == session.session_id,
        "session_mode_matches": recovered_session.current_mode == "Continuity",
        "workspace_state_matches": (
            recovered_session.workspace_state == session.workspace_state
        ),
        "pending_action_matches": (
            recovered_session.pending_next_action == session.pending_next_action
        ),
        "last_action_matches": (
            recovered_session.last_completed_action == session.last_completed_action
        ),
        "restore_payload_ignores_diagnostic_path": (
            str(diagnostic_path) not in json.dumps(return_after, sort_keys=True)
        ),
    }

    evidence_receipt = create_coupling_receipt(
        signal_id="signal-mycelial-edge-loss-result-0001",
        source="mycelial_edge_loss_counterfactual",
        destination="runtime_boundary_diagnostic",
        relation="diagnostic",
        created_at="2026-08-30T17:41:00+00:00",
        evidence_kind="derived",
        evidence_reference="sea-trial:mycelial-edge-loss-r1",
        evidence_payload={
            "topology_metrics": report["metrics"],
            "recovery_evidence": recovery_evidence,
        },
        confidence=1.0,
        reversible=True,
        authority_effect=False,
        memory_effect="topology",
        retention="ephemeral",
        effect_summary=(
            "Observed one lost diagnostic edge while canonical recovery remained externally proven."
        ),
    )
    evidence_ledger = CouplingReceiptLedger(base_dir / "edge_loss_receipt")
    evidence_decision = evidence_ledger.ingest(evidence_receipt)
    evidence_integrity = evidence_ledger.verify_integrity()
    registry_hash_after = _sha256_file(CAPABILITY_REGISTRY_PATH)

    metrics = report["metrics"]
    forbidden_report_keys = {
        "governance_event",
        "canon_lineage",
        "promotion",
        "mutation",
        "mode_legality",
        "capability_exposure",
        "checkpoint_validity",
        "identity_score",
        "intelligence_score",
        "overall_score",
    }
    checks = {
        "source_diagnostic_receipt_is_accepted": field_decision.status == "accepted",
        "baseline_has_three_available_edges": (
            metrics.get("baseline_edge_count") == 3
            and metrics.get("baseline_available_edge_count") == 3
        ),
        "exactly_one_edge_is_lost": metrics.get("lost_edge_count") == 1,
        "lost_edge_is_non_authoritative": (
            metrics.get("lost_non_authoritative_edge_count") == 1
            and metrics.get("lost_canonical_reference_count") == 0
            and (report.get("lost_edges") or [{}])[0].get("edge_id")
            == "coupling-intake-to-field-diagnostic"
        ),
        "topology_reports_non_authoritative_degradation": (
            report.get("status") == "degraded"
            and report.get("degradation", {}).get("observed") is True
            and report.get("degradation", {}).get("scope")
            == "non_authoritative_only"
        ),
        "edge_retention_decreases": metrics.get("edge_retention_ratio") == 0.6667,
        "canonical_reference_availability_is_preserved": (
            metrics.get("observed_canonical_reference_count") == 2
            and metrics.get("canonical_reference_availability_ratio") == 1.0
        ),
        "non_authoritative_availability_decreases": (
            metrics.get("observed_non_authoritative_edge_count") == 0
            and metrics.get("non_authoritative_availability_ratio") == 0.0
        ),
        "source_ledger_integrity_and_path_availability_remain_distinct": (
            source_integrity_after.get("valid") is True
            and source_integrity_after.get("receipt_count") == 1
            and source_integrity_after.get("decision_count") == 0
        ),
        "project_return_recovers_after_edge_loss": all(recovery_evidence.values()),
        "checkpoint_embedded_state_is_unchanged": (
            checkpoint_before.get("session_state")
            == checkpoint_after.get("session_state")
        ),
        "topology_observation_is_deterministic": report == repeated_report,
        "topology_does_not_claim_canonical_recovery": (
            report.get("canonical_recovery_claimed") is False
        ),
        "topology_creates_no_authority_event": (
            report.get("authority_effect") is False
            and report.get("authority_event_created") is False
        ),
        "topology_report_contains_no_governing_result_keys": not (
            forbidden_report_keys & _all_keys(report)
        ),
        "canonical_loss_is_reported_as_a_distinct_scope": (
            canonical_loss_report.get("degradation", {}).get("scope")
            == "canonical_reference"
            and canonical_loss_report.get("metrics", {}).get(
                "lost_canonical_reference_count"
            )
            == 1
            and canonical_loss_report.get("canonical_recovery_claimed") is False
        ),
        "metrics_remain_dimension_specific": not any(
            term in key
            for key in metrics
            for term in ("identity", "intelligence", "consciousness", "overall")
        ),
        "result_receipt_is_accepted": evidence_decision.status == "accepted",
        "result_receipt_declares_topology_memory_only": (
            evidence_receipt.memory_effect == "topology"
            and evidence_receipt.authority_effect is False
        ),
        "result_receipt_creates_no_authority": (
            evidence_decision.authority_effect is False
            and evidence_decision.authority_event_created is False
        ),
        "result_receipt_history_is_valid": evidence_integrity.get("valid") is True,
        "capability_registry_is_unchanged": registry_hash_before == registry_hash_after,
        **_rejection_checks(),
    }
    return {
        "schema_version": "sea-trials-mycelial-edge-loss-r1",
        "suite": "Mycelial Edge Loss Boundary R1",
        "passed": all(checks.values()),
        "checks": checks,
        "lost_path": str(diagnostic_path),
        "topology_report": report,
        "canonical_loss_control": canonical_loss_report,
        "recovery_evidence": recovery_evidence,
        "source_ledger_integrity_after_loss": source_integrity_after,
        "diagnostic_receipt": {
            "receipt_hash": evidence_receipt.receipt_hash,
            "decision": evidence_decision.to_dict(),
            "integrity": evidence_integrity,
        },
        "authority_effect": False,
        "authority_event_created": False,
        "limitations": (
            "Validates loss of one non-authoritative diagnostic path against a local "
            "project-return checkpoint. It does not validate vessel replacement, resident "
            "reset, public-surface disagreement, no-op observation, or runtime-wide recovery."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the mycelial non-authoritative edge-loss counterfactual."
    )
    parser.add_argument("--base-dir", default=None, help="Optional persistent trial directory.")
    parser.add_argument("--json", action="store_true", help="Print full trial detail.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.base_dir:
        result = run_trials(Path(args.base_dir))
    else:
        with tempfile.TemporaryDirectory(prefix="lumina-edge-loss-") as temporary:
            result = run_trials(Path(temporary))

    if args.json:
        output = result
    else:
        output = {
            "suite": result["suite"],
            "passed": result["passed"],
            "check_count": len(result["checks"]),
            "failed_checks": [
                name for name, passed in result["checks"].items() if not passed
            ],
            "topology_metrics": result["topology_report"]["metrics"],
            "recovery_evidence": result["recovery_evidence"],
            "authority_effect": result["authority_effect"],
            "authority_event_created": result["authority_event_created"],
        }
    print(json.dumps(output, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
