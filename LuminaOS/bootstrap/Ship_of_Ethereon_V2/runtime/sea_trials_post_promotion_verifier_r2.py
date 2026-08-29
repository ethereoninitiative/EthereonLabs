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
    from .post_promotion_verifier_r2 import verify
    from .repo_paths_r1 import repo_root
except Exception:
    from canon_lineage_store_r1 import CanonLineageStore, canonical_json, sha256_text
    from governance_integrity_r1 import GovernanceIntegrityChain
    from post_promotion_verifier_r2 import verify
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


def build_successor_fixture(root: Path, fixture: Path) -> Dict[str, Path]:
    governance_path = fixture / "governance_chain.jsonl"
    lineage_path = fixture / "canon_lineage.jsonl"
    promotion_path = fixture / "promotion_receipt_0002.json"
    validation_path = fixture / "validation_artifact_0002.json"
    head_sha = repository_head(root)

    write_json(
        validation_path,
        {
            "artifact_id": "successor-validation-0002",
            "repository_head": head_sha,
            "passed": True,
            "authority_scope": "isolated_successor_sea_trial_only",
        },
    )
    validation_hash = hashlib.sha256(validation_path.read_bytes()).hexdigest()
    validation_relative = validation_path.relative_to(root).as_posix()

    governance = GovernanceIntegrityChain(governance_path)
    lineage = CanonLineageStore(lineage_path)
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
        "regression_check_confirmation": True,
        "conceptual_layer_check_confirmation": True,
        "runtime_requires_symbolic_interpretation": False,
    }
    successor_event = governance.append_verified(
        event_type="promotion",
        session_identifier="synthetic-successor",
        previous_mode="DryDock",
        new_mode="Canon",
        allowed=True,
        canonical_change=True,
        validation_reference="successor-validation-0002",
        metadata={
            "action_type": "promotion",
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
        paths = build_successor_fixture(root, fixture)
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
        checks = {
            "successor_canon_0002_passes": valid.get("passed") is True,
            "successor_parent_is_canon_0001": valid.get("canon_parent") == "canon-0001",
            "successor_is_sha_bound": valid.get("candidate_commit_sha") == repository_head(root),
            "tampered_validation_fails": tampered.get("passed") is False,
            "wrong_expected_head_fails": wrong_head.get("passed") is False,
            "fixture_reference_was_repo_relative": not Path(original_reference).is_absolute(),
        }
        return {
            "suite": "Sea Trials Post-Promotion Verifier R2",
            "passed": all(checks.values()),
            "checks": checks,
            "valid_successor": valid,
            "tampered_failed_checks": tampered.get("failed_checks", []),
            "wrong_head_failed_checks": wrong_head.get("failed_checks", []),
            "authority_boundary": "Synthetic isolated lineage only; does not alter committed canon authority.",
        }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result.get("passed") else 1)
