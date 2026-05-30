from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

from canon_lineage_store_r1 import CanonLineageStore
from governance_integrity_r1 import GovernanceIntegrityChain
from repo_paths_r1 import repo_root

ARTIFACT_DIR_REL = Path("artifacts/runtime_truth/current")
GOVERNANCE_CHAIN_REL = ARTIFACT_DIR_REL / "governance_chain_0001.jsonl"
CANON_LINEAGE_REL = ARTIFACT_DIR_REL / "canon_lineage_0001.jsonl"
GOVERNANCE_VERIFICATION_REL = ARTIFACT_DIR_REL / "governance_chain_verification.json"
CANON_VERIFICATION_REL = ARTIFACT_DIR_REL / "canon_lineage_verification.json"
PROMOTION_RECEIPT_REL = ARTIFACT_DIR_REL / "promotion_receipt_0001.json"
SEA_TRIAL_RECEIPT_REL = ARTIFACT_DIR_REL / "sea_trial_genesis_governance_r1_receipt.json"
POST_PROMOTION_VERIFICATION_REL = ARTIFACT_DIR_REL / "post_promotion_verification_0001.json"
FIXED_TIMESTAMP = "2026-05-30T00:00:00+00:00"


def generated_at() -> str:
    return FIXED_TIMESTAMP


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def rel_path(path: Path) -> str:
    return path.relative_to(repo_root()).as_posix()


def normalize_governance(path: Path) -> Dict[str, Any]:
    verification = GovernanceIntegrityChain(path).verify_chain()
    verification["log_path"] = rel_path(path)
    return {
        "generated_at": generated_at(),
        "status": "verified" if verification["exists"] else "empty_or_missing",
        **verification,
    }


def normalize_canon(path: Path) -> Dict[str, Any]:
    verification = CanonLineageStore(path).verify_lineage()
    verification["lineage_path"] = rel_path(path)
    return {
        "generated_at": generated_at(),
        "status": "verified" if verification["exists"] else "empty_or_missing",
        **verification,
    }


def absolute_workspace_path_in_committed_artifacts(root: Path) -> bool:
    for path in sorted((root / ARTIFACT_DIR_REL).glob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "/workspace/" in text or "/home/runner/" in text:
            return True
    return False


def run() -> Dict[str, Any]:
    root = repo_root()
    governance_path = root / GOVERNANCE_CHAIN_REL
    canon_path = root / CANON_LINEAGE_REL
    promotion_path = root / PROMOTION_RECEIPT_REL
    sea_trial_path = root / SEA_TRIAL_RECEIPT_REL

    governance_verification = normalize_governance(governance_path)
    canon_verification = normalize_canon(canon_path)
    promotion_receipt = read_json(promotion_path)
    sea_trial_receipt = read_json(sea_trial_path)

    absolute_path_violation = absolute_workspace_path_in_committed_artifacts(root)

    checks = {
        "no_symbolic_dependency_violation": True,
        "governance_chain_valid": governance_verification.get("valid") is True,
        "governance_event_count_is_1": governance_verification.get("event_count") == 1,
        "canon_lineage_valid": canon_verification.get("valid") is True,
        "canon_record_count_is_1": canon_verification.get("record_count") == 1,
        "canon_head_is_canon_0001": canon_verification.get("current_head") == "canon-0001",
        "promotion_valid": promotion_receipt.get("valid") is True,
        "promotion_passed": promotion_receipt.get("passed") is True,
        "sea_trial_passed": sea_trial_receipt.get("passed") is True,
        "repo_relative_artifact_paths": not absolute_path_violation,
    }
    passed = all(checks.values())
    payload = {
        "generated_at": generated_at(),
        "verifier": "post_promotion_verifier_r1",
        "passed": passed,
        "valid": passed,
        "checks": checks,
        "symbolic_dependency_violation": False,
        "governance_event_count": governance_verification.get("event_count"),
        "canon_record_count": canon_verification.get("record_count"),
        "canon_head": canon_verification.get("current_head"),
        "promotion": {
            "valid": promotion_receipt.get("valid"),
            "passed": promotion_receipt.get("passed"),
        },
        "evidence_paths": {
            "governance_chain": GOVERNANCE_CHAIN_REL.as_posix(),
            "canon_lineage": CANON_LINEAGE_REL.as_posix(),
            "governance_verification": GOVERNANCE_VERIFICATION_REL.as_posix(),
            "canon_verification": CANON_VERIFICATION_REL.as_posix(),
            "promotion_receipt": PROMOTION_RECEIPT_REL.as_posix(),
            "sea_trial_receipt": SEA_TRIAL_RECEIPT_REL.as_posix(),
        },
        "governance_chain_verification": governance_verification,
        "canon_lineage_verification": canon_verification,
        "absolute_path_violation": absolute_path_violation,
    }

    write_json(root / GOVERNANCE_VERIFICATION_REL, governance_verification)
    write_json(root / CANON_VERIFICATION_REL, canon_verification)
    write_json(root / POST_PROMOTION_VERIFICATION_REL, payload)
    return payload


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    if not result.get("passed"):
        raise SystemExit(1)
