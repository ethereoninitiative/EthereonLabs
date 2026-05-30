from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

import sys

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from canon_lineage_store_r1 import CanonLineageStore, utc_now
from governance_integrity_r1 import GovernanceIntegrityChain
from repo_paths_r1 import repo_root as _repo_root_helper


REPO_ROOT = Path(_repo_root_helper()).resolve()
OUTPUT_DIR = REPO_ROOT / "artifacts" / "runtime_truth" / "current"


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Dict[str, Any]) -> str:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return str(path)


def main() -> Dict[str, Any]:
    governance_verification = read_json(OUTPUT_DIR / "governance_chain_verification.json")
    canon_verification = read_json(OUTPUT_DIR / "canon_lineage_verification.json")
    promotion_receipt = read_json(OUTPUT_DIR / "promotion_receipt_0001.json")
    sea_trial_receipt = read_json(OUTPUT_DIR / "sea_trial_genesis_governance_r1_receipt.json")

    governance_chain = GovernanceIntegrityChain(governance_verification["log_path"])
    governance_recheck = governance_chain.verify_chain()
    canon_store = CanonLineageStore(canon_verification["lineage_path"])
    canon_recheck = canon_store.verify_lineage()

    authority = promotion_receipt.get("promotion_authority", {})
    checks = {
        "governance_chain_artifact_valid": governance_verification.get("valid") is True,
        "governance_chain_recheck_valid": governance_recheck.get("valid") is True,
        "governance_latest_hash_matches_receipt": governance_recheck.get("latest_event_hash") == promotion_receipt.get("governance_event", {}).get("record_hash"),
        "canon_lineage_artifact_valid": canon_verification.get("valid") is True,
        "canon_lineage_recheck_valid": canon_recheck.get("valid") is True,
        "canon_head_is_genesis": canon_recheck.get("current_head") == "canon-0001",
        "promotion_receipt_passed": promotion_receipt.get("passed") is True,
        "sea_trial_receipt_passed": sea_trial_receipt.get("passed") is True,
        "symbolic_dependency_violation_false": promotion_receipt.get("symbolic_dependency_violation") is False,
        "promotion_authority_runtime_artifacts_only": authority.get("source_type") == "runtime_artifacts_only",
        "promotion_authority_runtime_artifact_valid": authority.get("runtime_artifact_authority_valid") is True,
    }

    payload = {
        "schema_version": "post-promotion-verification-r1",
        "generated_at": utc_now(),
        "verification_id": "post-promotion-verification-0001",
        "passed": all(checks.values()),
        "symbolic_dependency_violation": promotion_receipt.get("symbolic_dependency_violation"),
        "checks": checks,
        "rechecked_with_repo_native_utilities": {
            "governance_integrity_chain": governance_recheck,
            "canon_lineage_store": canon_recheck,
        },
        "verified_artifacts": {
            "governance_chain_verification": "artifacts/runtime_truth/current/governance_chain_verification.json",
            "canon_lineage_verification": "artifacts/runtime_truth/current/canon_lineage_verification.json",
            "promotion_receipt": "artifacts/runtime_truth/current/promotion_receipt_0001.json",
            "sea_trial_receipt": "artifacts/runtime_truth/current/sea_trial_genesis_governance_r1_receipt.json",
        },
    }
    write_json(OUTPUT_DIR / "post_promotion_verification_0001.json", payload)

    if not payload["passed"]:
        raise RuntimeError("Post-promotion verification failed.")

    return {
        "passed": True,
        "artifact": "artifacts/runtime_truth/current/post_promotion_verification_0001.json",
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
