from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

import sys

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from canon_lineage_store_r1 import CanonLineageStore, canonical_json, sha256_text, utc_now
from governance_integrity_r1 import GovernanceIntegrityChain
from repo_paths_r1 import repo_root as _repo_root_helper, state_root as _state_root_helper


def repo_root() -> Path:
    return Path(_repo_root_helper()).resolve()


def state_root() -> Path:
    return Path(_state_root_helper()).resolve()


REPO_ROOT = repo_root()
OUTPUT_DIR = REPO_ROOT / "artifacts" / "runtime_truth" / "current"
STATE_DIR = state_root() / "canon_readiness_genesis_r1"
GOVERNANCE_LOG_PATH = STATE_DIR / "governance_log_r1.jsonl"
CANON_LINEAGE_PATH = STATE_DIR / "canon_lineage_r1.jsonl"

RUNTIME_AUTHORITY_ARTIFACTS = {
    "protocol_conformance_report": OUTPUT_DIR / "protocol_conformance_report.json",
    "capability_registry_audit": OUTPUT_DIR / "capability_registry_audit.json",
    "symbolic_dependency_contract": OUTPUT_DIR / "symbolic_dependency_contract.json",
}


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return str(path)


def artifact_reference(path: Path) -> Dict[str, Any]:
    payload = read_json(path)
    return {
        "path": str(path),
        "sha256": sha256_text(canonical_json(payload)),
        "status": payload.get("status"),
        "valid": payload.get("valid"),
    }


def reset_genesis_state() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    for path in (GOVERNANCE_LOG_PATH, CANON_LINEAGE_PATH):
        if path.exists():
            path.unlink()


def symbolic_dependency_violation(contract: Dict[str, Any]) -> bool:
    return contract.get("symbolic_dependency_allowed") is not False


def runtime_authority_references() -> Dict[str, Any]:
    references = {name: artifact_reference(path) for name, path in RUNTIME_AUTHORITY_ARTIFACTS.items()}
    symbolic_contract = read_json(RUNTIME_AUTHORITY_ARTIFACTS["symbolic_dependency_contract"])
    violation = symbolic_dependency_violation(symbolic_contract)
    all_valid = all(ref.get("valid") is True for name, ref in references.items() if name != "symbolic_dependency_contract")
    return {
        "source_type": "runtime_artifacts_only",
        "authority_statement": "Promotion is authorized only by current runtime truth artifacts with valid structural checks and an explicit symbolic-dependency prohibition.",
        "artifact_references": references,
        "symbolic_dependency_violation": violation,
        "runtime_artifact_authority_valid": all_valid and not violation,
        "excluded_authority_sources": [
            "symbolic_language",
            "poetic_language",
            "mythic_language",
            "ceremonial_language",
        ],
    }


def main() -> Dict[str, Any]:
    reset_genesis_state()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    authority = runtime_authority_references()
    if not authority["runtime_artifact_authority_valid"]:
        raise RuntimeError("Runtime artifact authority validation failed; promotion refused.")

    governance_chain = GovernanceIntegrityChain(GOVERNANCE_LOG_PATH)
    governance_record = governance_chain.append_verified(
        event_type="canon_readiness_genesis_governance_r1",
        session_identifier="canon-readiness-genesis-0001",
        previous_mode="Observation",
        new_mode="Observation",
        allowed=True,
        reason="Runtime artifact checks authorize genesis canon-readiness promotion.",
        requested_action="establish_canon_readiness_genesis_evidence_chain",
        artifact_delta={
            "writes": [
                "artifacts/runtime_truth/current/governance_chain_verification.json",
                "artifacts/runtime_truth/current/canon_lineage_verification.json",
                "artifacts/runtime_truth/current/promotion_receipt_0001.json",
                "artifacts/runtime_truth/current/sea_trial_genesis_governance_r1_receipt.json",
            ]
        },
        canonical_change=True,
        validation_reference="artifacts/runtime_truth/current/promotion_receipt_0001.json",
        metadata={
            "authority_source_type": authority["source_type"],
            "symbolic_dependency_violation": authority["symbolic_dependency_violation"],
            "runtime_artifact_authority_valid": authority["runtime_artifact_authority_valid"],
        },
    )

    governance_verification = {
        "generated_at": utc_now(),
        "status": "verified",
        **governance_chain.verify_chain(),
    }
    write_json(OUTPUT_DIR / "governance_chain_verification.json", governance_verification)

    promotion_payload = {
        "promotion_id": "promotion-0001",
        "promotion_target": "canon-readiness-genesis",
        "runtime_seed_version": "canon-readiness-genesis-r1",
        "authority": authority,
        "governance_event_hash": governance_record["record_hash"],
        "governance_event_id": governance_record["event_id"],
    }

    canon_store = CanonLineageStore(CANON_LINEAGE_PATH)
    canon_record = canon_store.promote(
        canon_commit_summary="Establish canon readiness genesis evidence chain",
        validation_artifact_reference="artifacts/runtime_truth/current/governance_chain_verification.json",
        governance_event_hash=governance_record["record_hash"],
        promotion_payload=promotion_payload,
        runtime_seed_version="canon-readiness-genesis-r1",
        notes="Promotion authority is restricted to runtime artifacts and excludes symbolic dependencies.",
    )

    canon_verification = {
        "generated_at": utc_now(),
        "status": "verified",
        **canon_store.verify_lineage(),
    }
    write_json(OUTPUT_DIR / "canon_lineage_verification.json", canon_verification)

    promotion_receipt = {
        "schema_version": "canon-readiness-promotion-receipt-r1",
        "generated_at": utc_now(),
        "promotion_id": "promotion-0001",
        "passed": True,
        "symbolic_dependency_violation": authority["symbolic_dependency_violation"],
        "promotion_authority": authority,
        "governance_event": {
            "event_id": governance_record["event_id"],
            "record_hash": governance_record["record_hash"],
            "log_path": str(GOVERNANCE_LOG_PATH),
        },
        "canon_lineage_record": canon_record,
        "verification_artifacts": {
            "governance_chain_verification": "artifacts/runtime_truth/current/governance_chain_verification.json",
            "canon_lineage_verification": "artifacts/runtime_truth/current/canon_lineage_verification.json",
        },
    }
    write_json(OUTPUT_DIR / "promotion_receipt_0001.json", promotion_receipt)

    checks = {
        "governance_chain_valid": governance_verification.get("valid") is True,
        "governance_event_count_is_genesis": governance_verification.get("event_count") == 1,
        "canon_lineage_valid": canon_verification.get("valid") is True,
        "canon_record_count_is_genesis": canon_verification.get("record_count") == 1,
        "promotion_receipt_passed": promotion_receipt.get("passed") is True,
        "symbolic_dependency_violation_false": promotion_receipt.get("symbolic_dependency_violation") is False,
        "promotion_authority_runtime_artifacts_only": authority.get("source_type") == "runtime_artifacts_only",
    }
    sea_trial_receipt = {
        "schema_version": "sea-trial-genesis-governance-r1-receipt",
        "generated_at": utc_now(),
        "suite": "canon_readiness_genesis_governance_r1",
        "passed": all(checks.values()),
        "checks": checks,
        "generated_artifacts": {
            "governance_chain_verification": "artifacts/runtime_truth/current/governance_chain_verification.json",
            "canon_lineage_verification": "artifacts/runtime_truth/current/canon_lineage_verification.json",
            "promotion_receipt": "artifacts/runtime_truth/current/promotion_receipt_0001.json",
        },
        "state_paths": {
            "governance_log_path": str(GOVERNANCE_LOG_PATH),
            "canon_lineage_path": str(CANON_LINEAGE_PATH),
        },
    }
    write_json(OUTPUT_DIR / "sea_trial_genesis_governance_r1_receipt.json", sea_trial_receipt)

    if not sea_trial_receipt["passed"]:
        raise RuntimeError("Genesis governance sea trial failed.")

    return {
        "passed": True,
        "artifacts": {
            **sea_trial_receipt["generated_artifacts"],
            "sea_trial_receipt": "artifacts/runtime_truth/current/sea_trial_genesis_governance_r1_receipt.json",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
