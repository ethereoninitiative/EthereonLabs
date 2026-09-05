from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import hashlib
import json
import shutil
import subprocess
import tempfile

try:
    from .canon_lineage_store_r1 import CanonLineageStore, canonical_json, sha256_text
    from .governance_integrity_r1 import GovernanceIntegrityChain
    from .post_promotion_verifier_r2 import (
        DEFAULT_GOVERNANCE,
        DEFAULT_LINEAGE,
        DEFAULT_PROMOTION,
        verify,
    )
    from .repo_paths_r1 import repo_root
except Exception:
    from canon_lineage_store_r1 import CanonLineageStore, canonical_json, sha256_text
    from governance_integrity_r1 import GovernanceIntegrityChain
    from post_promotion_verifier_r2 import (
        DEFAULT_GOVERNANCE,
        DEFAULT_LINEAGE,
        DEFAULT_PROMOTION,
        verify,
    )
    from repo_paths_r1 import repo_root


def repository_head(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_successor_fixture(
    root: Path,
    fixture: Path,
    *,
    successor_event_type: str = "promotion",
    successor_action_type: str = "promotion",
    successor_previous_mode: str = "DryDock",
    validation_receipt_artifact_id: str = "successor-validation-0002",
    regression_check_confirmation: bool = True,
) -> Dict[str, Path]:
    governance_path = fixture / "governance_chain.jsonl"
    lineage_path = fixture / "canon_lineage.jsonl"
    promotion_path = fixture / "promotion_receipt_0002.json"
    validation_path = fixture / "validation_artifact_0002.json"
    head_sha = repository_head(root)

    write_json(
        validation_path,
        {
            "artifact_id": validation_receipt_artifact_id,
            "repository_head": head_sha,
            "passed": True,
            "authority_scope": "isolated_successor_sea_trial_only",
        },
    )
    validation_hash = hashlib.sha256(validation_path.read_bytes()).hexdigest()
    validation_relative = validation_path.relative_to(root).as_posix()

    governance = GovernanceIntegrityChain(governance_path, seed_committed_canon=False)
    lineage = CanonLineageStore(lineage_path, seed_committed_canon=False)
    genesis_payload = {
        "validation_artifact_id": "synthetic-genesis",
        "runtime_requires_symbolic_interpretation": False,
    }
    genesis_event = governance.append_verified(
        event_type="promotion",
        session_identifier="synthetic-genesis",
        previous_mode="DryDock",
        new_mode="Canon",
        allowed=True,
        canonical_change=True,
        validation_reference="synthetic-genesis",
        metadata={"action_type": "promotion"},
    )
    lineage.promote(
        canon_commit_summary="synthetic predecessor",
        validation_artifact_reference="synthetic-genesis",
        governance_event_hash=genesis_event["record_hash"],
        promotion_payload=genesis_payload,
        runtime_seed_version="sea-trial",
    )

    successor_payload = {
        "validation_artifact_id": "successor-validation-0002",
        "validation_artifact_path": validation_relative,
        "validation_artifact_sha256": validation_hash,
        "candidate_commit_sha": head_sha,
        "test_execution_log": "isolated successor verification passed",
        "change_summary": "exercise successor-capable post-promotion verification",
        "structural_impact_assessment": "temporary sea-trial state only",
        "regression_check_confirmation": regression_check_confirmation,
        "conceptual_layer_check_confirmation": True,
        "runtime_requires_symbolic_interpretation": False,
    }
    successor_event = governance.append_verified(
        event_type=successor_event_type,
        session_identifier="synthetic-successor",
        previous_mode=successor_previous_mode,
        new_mode="Canon",
        allowed=True,
        canonical_change=True,
        validation_reference="successor-validation-0002",
        metadata={
            "action_type": successor_action_type,
            "validation_artifact_id": "successor-validation-0002",
            "validation_artifact_path": validation_relative,
            "validation_artifact_sha256": validation_hash,
            "candidate_commit_sha": head_sha,
        },
    )
    successor = lineage.promote(
        canon_commit_summary="synthetic successor",
        validation_artifact_reference="successor-validation-0002",
        governance_event_hash=successor_event["record_hash"],
        promotion_payload=successor_payload,
        runtime_seed_version="sea-trial",
    )
    payload_hash = sha256_text(canonical_json(successor_payload))
    write_json(
        promotion_path,
        {
            "promotion_id": "promotion-0002",
            "valid": True,
            "passed": True,
            "promotion_payload": successor_payload,
            "promotion_payload_hash": payload_hash,
            "governance_event_hash": successor_event["record_hash"],
            "canon_lineage_hash": successor["lineage_record_hash"],
        },
    )
    return {
        "governance": governance_path,
        "lineage": lineage_path,
        "promotion": promotion_path,
        "validation": validation_path,
    }


def run() -> Dict[str, Any]:
    root = repo_root().resolve()
    state_root = root / ".lumina_state/ship_of_ethereon_v2"
    state_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="post-promotion-r2-", dir=state_root) as temporary:
        fixture = Path(temporary)
        paths = build_successor_fixture(root, fixture / "valid")
        valid = verify(
            root=root,
            governance_path=paths["governance"],
            lineage_path=paths["lineage"],
            promotion_receipt_path=paths["promotion"],
            expected_head="canon-0002",
        )

        tampered_dir = fixture / "tampered"
        tampered_dir.mkdir()
        tampered_validation = tampered_dir / paths["validation"].name
        shutil.copy2(paths["validation"], tampered_validation)
        tampered_payload = json.loads(tampered_validation.read_text(encoding="utf-8"))
        tampered_payload["authority_scope"] = "tampered"
        write_json(tampered_validation, tampered_payload)
        original_reference = paths["validation"].relative_to(root).as_posix()
        tampered_reference = tampered_validation.relative_to(root).as_posix()
        promotion_payload = json.loads(paths["promotion"].read_text(encoding="utf-8"))
        promotion_payload["promotion_payload"]["validation_artifact_path"] = tampered_reference
        promotion_payload["promotion_payload_hash"] = sha256_text(canonical_json(promotion_payload["promotion_payload"]))
        tampered_promotion = tampered_dir / "promotion_receipt_0002.json"
        write_json(tampered_promotion, promotion_payload)
        tampered = verify(
            root=root,
            governance_path=paths["governance"],
            lineage_path=paths["lineage"],
            promotion_receipt_path=tampered_promotion,
            expected_head="canon-0002",
        )

        wrong_head = verify(
            root=root,
            governance_path=paths["governance"],
            lineage_path=paths["lineage"],
            promotion_receipt_path=paths["promotion"],
            expected_head="canon-0003",
        )

        committed_genesis = verify(root=root, expected_head="canon-0001")

        relocated_dir = fixture / "relocated-genesis"
        relocated_dir.mkdir()
        relocated_paths = {
            "governance": relocated_dir / DEFAULT_GOVERNANCE.name,
            "lineage": relocated_dir / DEFAULT_LINEAGE.name,
            "promotion": relocated_dir / DEFAULT_PROMOTION.name,
        }
        shutil.copy2(root / DEFAULT_GOVERNANCE, relocated_paths["governance"])
        shutil.copy2(root / DEFAULT_LINEAGE, relocated_paths["lineage"])
        shutil.copy2(root / DEFAULT_PROMOTION, relocated_paths["promotion"])
        relocated_genesis = verify(
            root=root,
            governance_path=relocated_paths["governance"],
            lineage_path=relocated_paths["lineage"],
            promotion_receipt_path=relocated_paths["promotion"],
            expected_head="canon-0001",
        )

        non_promotion_paths = build_successor_fixture(
            root,
            fixture / "non-promotion-event",
            successor_event_type="audit",
        )
        non_promotion = verify(
            root=root,
            governance_path=non_promotion_paths["governance"],
            lineage_path=non_promotion_paths["lineage"],
            promotion_receipt_path=non_promotion_paths["promotion"],
            expected_head="canon-0002",
        )

        wrong_action_paths = build_successor_fixture(
            root,
            fixture / "wrong-action-type",
            successor_action_type="audit",
        )
        wrong_action = verify(
            root=root,
            governance_path=wrong_action_paths["governance"],
            lineage_path=wrong_action_paths["lineage"],
            promotion_receipt_path=wrong_action_paths["promotion"],
            expected_head="canon-0002",
        )

        wrong_mode_paths = build_successor_fixture(
            root,
            fixture / "wrong-source-mode",
            successor_previous_mode="Sandbox",
        )
        wrong_mode = verify(
            root=root,
            governance_path=wrong_mode_paths["governance"],
            lineage_path=wrong_mode_paths["lineage"],
            promotion_receipt_path=wrong_mode_paths["promotion"],
            expected_head="canon-0002",
        )

        identity_mismatch_paths = build_successor_fixture(
            root,
            fixture / "validation-identity-mismatch",
            validation_receipt_artifact_id="different-validation-artifact",
        )
        identity_mismatch = verify(
            root=root,
            governance_path=identity_mismatch_paths["governance"],
            lineage_path=identity_mismatch_paths["lineage"],
            promotion_receipt_path=identity_mismatch_paths["promotion"],
            expected_head="canon-0002",
        )

        false_confirmation_paths = build_successor_fixture(
            root,
            fixture / "false-regression-confirmation",
            regression_check_confirmation=False,
        )
        false_confirmation = verify(
            root=root,
            governance_path=false_confirmation_paths["governance"],
            lineage_path=false_confirmation_paths["lineage"],
            promotion_receipt_path=false_confirmation_paths["promotion"],
            expected_head="canon-0002",
        )

        with tempfile.TemporaryDirectory(prefix="post-promotion-r2-external-") as external:
            external_governance = Path(external) / DEFAULT_GOVERNANCE.name
            shutil.copy2(root / DEFAULT_GOVERNANCE, external_governance)
            external_evidence = verify(
                root=root,
                governance_path=external_governance,
                lineage_path=DEFAULT_LINEAGE,
                promotion_receipt_path=DEFAULT_PROMOTION,
                expected_head="canon-0001",
            )
        checks = {
            "committed_genesis_passes": committed_genesis.get("passed") is True,
            "committed_genesis_uses_narrow_exception": committed_genesis.get("legacy_genesis_exception") is True,
            "successor_canon_0002_passes": valid.get("passed") is True,
            "successor_parent_is_canon_0001": valid.get("canon_parent") == "canon-0001",
            "successor_is_sha_bound": valid.get("candidate_commit_sha") == repository_head(root),
            "tampered_validation_fails": tampered.get("passed") is False,
            "wrong_expected_head_fails": wrong_head.get("passed") is False,
            "relocated_genesis_fails": relocated_genesis.get("passed") is False,
            "relocated_genesis_cannot_claim_exception": relocated_genesis.get("legacy_genesis_exception") is False,
            "non_promotion_governance_event_fails": non_promotion.get("passed") is False,
            "non_promotion_failure_is_explicit": "governance_event_is_promotion"
            in non_promotion.get("failed_checks", []),
            "wrong_governance_action_fails": wrong_action.get("passed") is False,
            "wrong_governance_action_failure_is_explicit": "governance_action_is_promotion"
            in wrong_action.get("failed_checks", []),
            "wrong_governance_mode_fails": wrong_mode.get("passed") is False,
            "wrong_governance_mode_failure_is_explicit": "governance_modes_are_drydock_to_canon"
            in wrong_mode.get("failed_checks", []),
            "validation_identity_mismatch_fails": identity_mismatch.get("passed") is False,
            "validation_identity_failure_is_explicit": "validation_artifact_identity_linked"
            in identity_mismatch.get("failed_checks", []),
            "false_regression_confirmation_fails": false_confirmation.get("passed") is False,
            "false_confirmation_failure_is_explicit": "successor_regression_confirmed"
            in false_confirmation.get("failed_checks", []),
            "external_primary_evidence_fails_closed": external_evidence.get("passed") is False,
            "external_primary_evidence_failure_is_explicit": external_evidence.get("checks", {}).get(
                "governance_chain_within_repository"
            )
            is False,
            "fixture_reference_was_repo_relative": not Path(original_reference).is_absolute(),
        }
        return {
            "suite": "Sea Trials Post-Promotion Verifier R2",
            "passed": all(checks.values()),
            "checks": checks,
            "valid_successor": valid,
            "tampered_failed_checks": tampered.get("failed_checks", []),
            "wrong_head_failed_checks": wrong_head.get("failed_checks", []),
            "relocated_genesis_failed_checks": relocated_genesis.get("failed_checks", []),
            "non_promotion_failed_checks": non_promotion.get("failed_checks", []),
            "wrong_action_failed_checks": wrong_action.get("failed_checks", []),
            "wrong_mode_failed_checks": wrong_mode.get("failed_checks", []),
            "identity_mismatch_failed_checks": identity_mismatch.get("failed_checks", []),
            "false_confirmation_failed_checks": false_confirmation.get("failed_checks", []),
            "external_evidence_checks": external_evidence.get("checks", {}),
            "authority_boundary": "Synthetic isolated lineage only; does not alter committed canon authority.",
        }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result.get("passed") else 1)
