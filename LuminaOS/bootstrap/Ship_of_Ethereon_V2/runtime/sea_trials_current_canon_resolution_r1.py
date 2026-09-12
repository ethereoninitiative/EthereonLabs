"""Verify fail-closed resolution of numbered current-canon evidence sets."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile

try:
    from .post_promotion_verifier_r2 import (
        DEFAULT_ARTIFACT_DIR,
        resolve_current_evidence_set,
        verify,
    )
    from .repo_paths_r1 import repo_root
except ImportError:
    from post_promotion_verifier_r2 import (
        DEFAULT_ARTIFACT_DIR,
        resolve_current_evidence_set,
        verify,
    )
    from repo_paths_r1 import repo_root


def run() -> dict:
    source_root = repo_root()
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="current-canon-resolution-r1-") as temporary:
        root = Path(temporary).resolve()
        current = root / DEFAULT_ARTIFACT_DIR
        shutil.copytree(source_root / DEFAULT_ARTIFACT_DIR, current)

        governance, lineage, promotion, expected = resolve_current_evidence_set(root)
        checks["genesis_resolves_as_current"] = (
            governance.name == "governance_chain_0001.jsonl"
            and lineage.name == "canon_lineage_0001.jsonl"
            and promotion.name == "promotion_receipt_0001.json"
            and expected == "canon-0001"
            and verify(root=root).get("passed") is True
        )

        shutil.copyfile(current / "governance_chain_0001.jsonl", current / "governance_chain_0002.jsonl")
        governance, lineage, promotion, expected = resolve_current_evidence_set(root)
        incomplete = verify(root=root)
        checks["newer_partial_set_is_not_silently_ignored"] = (
            governance.name == "governance_chain_0002.jsonl"
            and lineage.name == "canon_lineage_0002.jsonl"
            and promotion.name == "promotion_receipt_0002.json"
            and expected == "canon-0002"
            and incomplete.get("passed") is False
            and incomplete.get("expected_head") == "canon-0002"
            and incomplete.get("checks", {}).get("canon_lineage_exists") is False
            and incomplete.get("checks", {}).get("promotion_receipt_exists") is False
        )

        shutil.copyfile(current / "canon_lineage_0001.jsonl", current / "canon_lineage_0002.jsonl")
        shutil.copyfile(current / "promotion_receipt_0001.json", current / "promotion_receipt_0002.json")
        masquerade = verify(root=root)
        checks["numbered_set_must_match_resolved_canon_head"] = (
            masquerade.get("passed") is False
            and masquerade.get("canon_head") == "canon-0001"
            and masquerade.get("checks", {}).get("expected_head_matches") is False
        )

        for path in (
            current / "governance_chain_0002.jsonl",
            current / "canon_lineage_0002.jsonl",
            current / "promotion_receipt_0002.json",
        ):
            path.unlink()
        checks["removing_incomplete_successor_restores_genesis_resolution"] = verify(root=root).get("passed") is True

    return {
        "trial": "current_canon_resolution_r1",
        "passed": all(checks.values()),
        "checks": checks,
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "authority_boundary": "Resolution only; this trial never creates, activates, or promotes successor canon.",
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
