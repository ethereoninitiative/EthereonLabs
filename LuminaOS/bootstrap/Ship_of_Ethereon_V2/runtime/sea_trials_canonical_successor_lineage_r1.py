from __future__ import annotations

from pathlib import Path
import json
import shutil

try:
    from .canon_lineage_store_r1 import CanonLineageStore
    from .governance_integrity_r1 import GovernanceIntegrityChain
    from .repo_paths_r1 import repo_root
except Exception:
    from canon_lineage_store_r1 import CanonLineageStore
    from governance_integrity_r1 import GovernanceIntegrityChain
    from repo_paths_r1 import repo_root


GENESIS_GOVERNANCE_HASH = "690b249ef2388ac70f9714ef3bd649b6bd235f0e32840faefe7c3562563a00ab"
GENESIS_LINEAGE_HASH = "2664c65bdc3e37733d1262d436e2c615191dc69dc71b0b798d71227f283d5401"


def run() -> dict:
    root = repo_root()
    state_root = root / ".lumina_state/ship_of_ethereon_v2/sea_trials_canonical_successor_lineage_r1"
    if state_root.exists():
        shutil.rmtree(state_root)
    state_root.mkdir(parents=True, exist_ok=True)

    governance_path = state_root / "governance_log_r1.jsonl"
    lineage_path = state_root / "canon_lineage_r1.jsonl"

    governance = GovernanceIntegrityChain(governance_path)
    promotion_event = governance.append_verified(
        event_type="promotion",
        session_identifier="canonical-successor-lineage-r1",
        previous_mode="DryDock",
        new_mode="Canon",
        allowed=True,
        reason="sea-trial successor promotion",
        requested_action="verify_canonical_successor_lineage",
        canonical_change=True,
        validation_reference="canonical-successor-lineage-r1-validation",
        metadata={"action_type": "promotion"},
    )
    governance_status = governance.verify_chain()
    governance_rows = [json.loads(line) for line in governance_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    lineage = CanonLineageStore(lineage_path)
    successor = lineage.promote(
        canon_commit_summary="Verify local promotion extends committed canon.",
        validation_artifact_reference="canonical-successor-lineage-r1-validation",
        governance_event_hash=promotion_event["record_hash"],
        promotion_payload={"validation_artifact_id": "canonical-successor-lineage-r1-validation"},
        runtime_seed_version="0.4",
        notes="Sea-trial only.",
    )
    lineage_status = lineage.verify_lineage()
    lineage_rows = lineage.read_lineage()

    checks = {
        "governance_chain_seeded_from_committed_genesis": len(governance_rows) == 2 and governance_rows[0].get("record_hash") == GENESIS_GOVERNANCE_HASH,
        "promotion_governance_extends_genesis": promotion_event.get("prev_event_hash") == GENESIS_GOVERNANCE_HASH,
        "governance_chain_valid": governance_status.get("valid") is True and governance_status.get("event_count") == 2,
        "canon_lineage_seeded_from_committed_genesis": len(lineage_rows) == 2 and lineage_rows[0].get("lineage_record_hash") == GENESIS_LINEAGE_HASH,
        "successor_is_canon_0002": successor.get("canon_version") == "canon-0002",
        "successor_parent_is_committed_canon": successor.get("canon_parent") == "canon-0001",
        "successor_links_genesis_lineage_hash": successor.get("prev_lineage_hash") == GENESIS_LINEAGE_HASH,
        "successor_links_promotion_governance": successor.get("governance_event_hash") == promotion_event.get("record_hash"),
        "canon_lineage_valid": lineage_status.get("valid") is True and lineage_status.get("record_count") == 2 and lineage_status.get("current_head") == "canon-0002",
    }
    passed = all(checks.values())
    result = {
        "trial": "canonical_successor_lineage_r1",
        "passed": passed,
        "checks": checks,
        "governance_status": governance_status,
        "lineage_status": lineage_status,
        "successor": successor,
    }
    shutil.rmtree(state_root, ignore_errors=True)
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
