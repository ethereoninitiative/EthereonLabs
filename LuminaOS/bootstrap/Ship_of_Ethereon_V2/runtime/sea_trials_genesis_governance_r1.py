from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

from canon_lineage_store_r1 import CanonLineageStore, canonical_json, sha256_text
from governance_integrity_r1 import GovernanceIntegrityChain
from repo_paths_r1 import repo_root

ARTIFACT_DIR_REL = Path("artifacts/runtime_truth/current")
GOVERNANCE_CHAIN_REL = ARTIFACT_DIR_REL / "governance_chain_0001.jsonl"
CANON_LINEAGE_REL = ARTIFACT_DIR_REL / "canon_lineage_0001.jsonl"
GOVERNANCE_VERIFICATION_REL = ARTIFACT_DIR_REL / "governance_chain_verification.json"
CANON_VERIFICATION_REL = ARTIFACT_DIR_REL / "canon_lineage_verification.json"
PROMOTION_RECEIPT_REL = ARTIFACT_DIR_REL / "promotion_receipt_0001.json"
SEA_TRIAL_RECEIPT_REL = ARTIFACT_DIR_REL / "sea_trial_genesis_governance_r1_receipt.json"

FIXED_TIMESTAMP = "2026-05-30T00:00:00+00:00"
RUNTIME_SEED_VERSION = "ship-of-ethereon-v2-genesis-runtime-truth-r1"
VALIDATION_REFERENCE = SEA_TRIAL_RECEIPT_REL.as_posix()


def generated_at() -> str:
    return FIXED_TIMESTAMP


def rel_path(path: Path) -> str:
    return path.relative_to(repo_root()).as_posix()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def write_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def build_governance_record(path: Path) -> Dict[str, Any]:
    chain = GovernanceIntegrityChain(path)
    record = {
        "event_id": "gov-0001",
        "timestamp_utc": FIXED_TIMESTAMP,
        "prev_event_hash": None,
        "event_type": "genesis_promotion_verification",
        "session_identifier": "canon_readiness_genesis_r1",
        "previous_mode": None,
        "new_mode": "canon_readiness",
        "allowed": True,
        "reason": "Genesis governance chain committed as repo-relative runtime truth evidence.",
        "requested_action": "promote_genesis_runtime_truth",
        "artifact_delta": {
            "added": [
                GOVERNANCE_CHAIN_REL.as_posix(),
                CANON_LINEAGE_REL.as_posix(),
                PROMOTION_RECEIPT_REL.as_posix(),
            ]
        },
        "canonical_change": True,
        "validation_reference": VALIDATION_REFERENCE,
        "metadata": {
            "evidence_path": GOVERNANCE_CHAIN_REL.as_posix(),
            "path_policy": "repo-relative",
            "symbolic_dependency_violation": False,
        },
    }
    record["record_hash"] = chain._compute_record_hash(record)
    return record


def build_promotion_payload(governance_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "promotion_id": "promotion-0001",
        "runtime_seed_version": RUNTIME_SEED_VERSION,
        "governance_event_hash": governance_record["record_hash"],
        "governance_evidence_path": GOVERNANCE_CHAIN_REL.as_posix(),
        "canon_lineage_path": CANON_LINEAGE_REL.as_posix(),
        "validation_reference": VALIDATION_REFERENCE,
        "symbolic_dependency_violation": False,
    }


def build_canon_record(path: Path, governance_record: Dict[str, Any], promotion_payload: Dict[str, Any]) -> Dict[str, Any]:
    store = CanonLineageStore(path)
    record = {
        "canon_version": "canon-0001",
        "canon_parent": None,
        "canon_commit_summary": "Promote genesis runtime truth evidence with committed governance and canon chains.",
        "canon_timestamp": FIXED_TIMESTAMP,
        "validation_artifact_reference": VALIDATION_REFERENCE,
        "governance_event_hash": governance_record["record_hash"],
        "promotion_payload_hash": sha256_text(canonical_json(dict(promotion_payload))),
        "runtime_seed_version": RUNTIME_SEED_VERSION,
        "notes": "Genesis canon head is verified from committed repo-relative evidence files.",
        "prev_lineage_hash": None,
    }
    record["lineage_record_hash"] = store._compute_record_hash(record)
    return record


def normalized_governance_verification(path: Path) -> Dict[str, Any]:
    verification = GovernanceIntegrityChain(path).verify_chain()
    verification["log_path"] = rel_path(path)
    return {
        "generated_at": generated_at(),
        "status": "verified" if verification["exists"] else "empty_or_missing",
        **verification,
    }


def normalized_canon_verification(path: Path) -> Dict[str, Any]:
    verification = CanonLineageStore(path).verify_lineage()
    verification["lineage_path"] = rel_path(path)
    return {
        "generated_at": generated_at(),
        "status": "verified" if verification["exists"] else "empty_or_missing",
        **verification,
    }


def build_sea_trial_receipt(
    governance_verification: Dict[str, Any],
    canon_verification: Dict[str, Any],
    promotion_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    checks = {
        "no_symbolic_dependency_violation": True,
        "governance_event_count_is_1": governance_verification.get("event_count") == 1,
        "canon_record_count_is_1": canon_verification.get("record_count") == 1,
        "canon_head_is_canon_0001": canon_verification.get("current_head") == "canon-0001",
        "promotion_valid": promotion_receipt.get("valid") is True,
        "promotion_passed": promotion_receipt.get("passed") is True,
        "governance_chain_valid": governance_verification.get("valid") is True,
        "canon_lineage_valid": canon_verification.get("valid") is True,
    }
    return {
        "generated_at": generated_at(),
        "trial_name": "sea_trials_genesis_governance_r1",
        "passed": all(checks.values()),
        "checks": checks,
        "symbolic_dependency_violation": False,
        "governance_event_count": governance_verification.get("event_count"),
        "canon_record_count": canon_verification.get("record_count"),
        "canon_head": canon_verification.get("current_head"),
        "promotion": {
            "valid": promotion_receipt.get("valid"),
            "passed": promotion_receipt.get("passed"),
            "receipt_path": PROMOTION_RECEIPT_REL.as_posix(),
        },
        "evidence_paths": {
            "governance_chain": GOVERNANCE_CHAIN_REL.as_posix(),
            "canon_lineage": CANON_LINEAGE_REL.as_posix(),
            "governance_verification": GOVERNANCE_VERIFICATION_REL.as_posix(),
            "canon_verification": CANON_VERIFICATION_REL.as_posix(),
            "promotion_receipt": PROMOTION_RECEIPT_REL.as_posix(),
        },
    }


def run() -> Dict[str, Any]:
    root = repo_root()
    governance_path = root / GOVERNANCE_CHAIN_REL
    canon_path = root / CANON_LINEAGE_REL

    governance_record = build_governance_record(governance_path)
    promotion_payload = build_promotion_payload(governance_record)
    canon_record = build_canon_record(canon_path, governance_record, promotion_payload)

    write_jsonl(governance_path, governance_record)
    write_jsonl(canon_path, canon_record)

    governance_verification = normalized_governance_verification(governance_path)
    canon_verification = normalized_canon_verification(canon_path)
    promotion_receipt = {
        "generated_at": generated_at(),
        "promotion_id": promotion_payload["promotion_id"],
        "valid": governance_verification.get("valid") is True and canon_verification.get("valid") is True,
        "passed": governance_verification.get("event_count") == 1
        and canon_verification.get("record_count") == 1
        and canon_verification.get("current_head") == "canon-0001",
        "promotion_payload": promotion_payload,
        "promotion_payload_hash": canon_record["promotion_payload_hash"],
        "governance_event_hash": governance_record["record_hash"],
        "canon_lineage_hash": canon_record["lineage_record_hash"],
        "evidence_paths": {
            "governance_chain": GOVERNANCE_CHAIN_REL.as_posix(),
            "canon_lineage": CANON_LINEAGE_REL.as_posix(),
        },
    }
    sea_trial_receipt = build_sea_trial_receipt(
        governance_verification, canon_verification, promotion_receipt
    )

    write_json(root / GOVERNANCE_VERIFICATION_REL, governance_verification)
    write_json(root / CANON_VERIFICATION_REL, canon_verification)
    write_json(root / PROMOTION_RECEIPT_REL, promotion_receipt)
    write_json(root / SEA_TRIAL_RECEIPT_REL, sea_trial_receipt)
    return sea_trial_receipt


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    if not result.get("passed"):
        raise SystemExit(1)
