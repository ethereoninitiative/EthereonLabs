from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import hashlib
import json
import re
import subprocess

try:
    from .canon_lineage_store_r1 import CanonLineageStore, canonical_json, sha256_text
    from .governance_integrity_r1 import GovernanceIntegrityChain
    from .repo_paths_r1 import repo_root
except Exception:
    from canon_lineage_store_r1 import CanonLineageStore, canonical_json, sha256_text
    from governance_integrity_r1 import GovernanceIntegrityChain
    from repo_paths_r1 import repo_root


DEFAULT_ARTIFACT_DIR = Path("artifacts/runtime_truth/current")
DEFAULT_GOVERNANCE = DEFAULT_ARTIFACT_DIR / "governance_chain_0001.jsonl"
DEFAULT_LINEAGE = DEFAULT_ARTIFACT_DIR / "canon_lineage_0001.jsonl"
DEFAULT_PROMOTION = DEFAULT_ARTIFACT_DIR / "promotion_receipt_0001.json"


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def read_jsonl(path: Path) -> list[Dict[str, Any]]:
    rows: list[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"expected JSON object row: {path}")
            rows.append(payload)
    return rows


def resolve_evidence_path(root: Path, reference: Any) -> Optional[Path]:
    if not isinstance(reference, str) or not reference.strip():
        return None
    relative = Path(reference)
    if relative.is_absolute():
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def git_commit_is_ancestor(root: Path, candidate_sha: Any) -> bool:
    if not isinstance(candidate_sha, str) or re.fullmatch(r"[0-9a-f]{40}", candidate_sha) is None:
        return False
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", candidate_sha, "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def verify(
    *,
    root: Optional[Path] = None,
    governance_path: Path = DEFAULT_GOVERNANCE,
    lineage_path: Path = DEFAULT_LINEAGE,
    promotion_receipt_path: Path = DEFAULT_PROMOTION,
    expected_head: Optional[str] = None,
) -> Dict[str, Any]:
    root = (root or repo_root()).resolve()
    governance_path = governance_path if governance_path.is_absolute() else root / governance_path
    lineage_path = lineage_path if lineage_path.is_absolute() else root / lineage_path
    promotion_receipt_path = (
        promotion_receipt_path if promotion_receipt_path.is_absolute() else root / promotion_receipt_path
    )

    required = {
        "governance_chain": governance_path.is_file(),
        "canon_lineage": lineage_path.is_file(),
        "promotion_receipt": promotion_receipt_path.is_file(),
    }
    if not all(required.values()):
        return {
            "verifier": "post_promotion_verifier_r2",
            "passed": False,
            "valid": False,
            "checks": {f"{name}_exists": exists for name, exists in required.items()},
            "errors": ["required post-promotion evidence is missing"],
        }

    try:
        governance_rows = read_jsonl(governance_path)
        lineage_rows = read_jsonl(lineage_path)
        promotion = read_json(promotion_receipt_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return {
            "verifier": "post_promotion_verifier_r2",
            "passed": False,
            "valid": False,
            "checks": {"evidence_is_valid_json": False},
            "errors": [str(exc)],
        }

    governance_verification = GovernanceIntegrityChain(governance_path).verify_chain()
    lineage_verification = CanonLineageStore(lineage_path).verify_lineage()
    head = lineage_rows[-1] if lineage_rows else {}
    head_name = head.get("canon_version")
    promotion_payload = promotion.get("promotion_payload")
    promotion_payload = promotion_payload if isinstance(promotion_payload, dict) else {}
    governance_hash = head.get("governance_event_hash")
    governance_event = next(
        (row for row in governance_rows if row.get("record_hash") == governance_hash),
        {},
    )
    metadata = governance_event.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}

    validation_id = promotion_payload.get("validation_artifact_id")
    if validation_id:
        validation_reference = promotion_payload.get("validation_artifact_path")
        reference_links = (
            head.get("validation_artifact_reference") == validation_id
            and governance_event.get("validation_reference") == validation_id
            and metadata.get("validation_artifact_id") in {None, validation_id}
        )
    else:
        validation_reference = promotion_payload.get("validation_reference")
        reference_links = (
            head.get("validation_artifact_reference") == validation_reference
            and governance_event.get("validation_reference") == validation_reference
        )

    validation_path = resolve_evidence_path(root, validation_reference)
    validation_exists = validation_path is not None and validation_path.is_file()
    validation_receipt: Dict[str, Any] = {}
    if validation_exists and validation_path is not None:
        try:
            validation_receipt = read_json(validation_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            validation_receipt = {}

    candidate_sha = promotion_payload.get("candidate_commit_sha")
    sha_bound_promotion = candidate_sha is not None
    legacy_genesis = head_name == "canon-0001" and not sha_bound_promotion
    validation_hash = hashlib.sha256(validation_path.read_bytes()).hexdigest() if validation_exists and validation_path else None
    expected_validation_hash = promotion_payload.get("validation_artifact_sha256")

    checks = {
        "governance_chain_valid": governance_verification.get("valid") is True,
        "governance_event_count_positive": int(governance_verification.get("event_count") or 0) > 0,
        "canon_lineage_valid": lineage_verification.get("valid") is True,
        "canon_record_count_positive": int(lineage_verification.get("record_count") or 0) > 0,
        "head_matches_lineage_verification": head_name == lineage_verification.get("current_head"),
        "expected_head_matches": expected_head is None or head_name == expected_head,
        "promotion_receipt_valid": promotion.get("valid") is True,
        "promotion_receipt_passed": promotion.get("passed") is True,
        "promotion_payload_hash_valid": promotion.get("promotion_payload_hash")
        == sha256_text(canonical_json(promotion_payload)),
        "lineage_payload_hash_linked": head.get("promotion_payload_hash") == promotion.get("promotion_payload_hash"),
        "governance_event_linked": bool(governance_event),
        "governance_event_allowed": governance_event.get("allowed") is True,
        "governance_event_is_canonical_change": governance_event.get("canonical_change") is True,
        "promotion_governance_hash_linked": promotion.get("governance_event_hash") == governance_hash,
        "promotion_lineage_hash_linked": promotion.get("canon_lineage_hash") == head.get("lineage_record_hash"),
        "validation_reference_linked": reference_links,
        "validation_artifact_exists": validation_exists,
        "validation_artifact_passed": validation_receipt.get("passed") is True,
        "symbolic_dependency_separated": (
            promotion_payload.get("symbolic_dependency_violation") is False
            if legacy_genesis
            else promotion_payload.get("runtime_requires_symbolic_interpretation") is False
        ),
        "successor_requires_sha_binding": legacy_genesis or sha_bound_promotion,
        "candidate_commit_is_ancestor": legacy_genesis or git_commit_is_ancestor(root, candidate_sha),
        "validation_artifact_hash_linked": legacy_genesis or validation_hash == expected_validation_hash,
        "validation_artifact_commit_linked": legacy_genesis or validation_receipt.get("repository_head") == candidate_sha,
        "governance_metadata_commit_linked": legacy_genesis or metadata.get("candidate_commit_sha") == candidate_sha,
        "governance_metadata_hash_linked": legacy_genesis or metadata.get("validation_artifact_sha256") == expected_validation_hash,
    }
    passed = all(checks.values())
    return {
        "verifier": "post_promotion_verifier_r2",
        "passed": passed,
        "valid": passed,
        "checks": checks,
        "canon_head": head_name,
        "canon_parent": head.get("canon_parent"),
        "governance_event_hash": governance_hash,
        "candidate_commit_sha": candidate_sha,
        "legacy_genesis_exception": legacy_genesis,
        "evidence_paths": {
            "governance_chain": governance_path.relative_to(root).as_posix(),
            "canon_lineage": lineage_path.relative_to(root).as_posix(),
            "promotion_receipt": promotion_receipt_path.relative_to(root).as_posix(),
            "validation_artifact": validation_reference,
        },
        "governance_chain_verification": governance_verification,
        "canon_lineage_verification": lineage_verification,
        "failed_checks": [name for name, value in checks.items() if not value],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify current or successor canon after promotion.")
    parser.add_argument("--governance", default=DEFAULT_GOVERNANCE.as_posix())
    parser.add_argument("--lineage", default=DEFAULT_LINEAGE.as_posix())
    parser.add_argument("--promotion-receipt", default=DEFAULT_PROMOTION.as_posix())
    parser.add_argument("--expected-head", default=None)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = verify(
        governance_path=Path(args.governance),
        lineage_path=Path(args.lineage),
        promotion_receipt_path=Path(args.promotion_receipt),
        expected_head=args.expected_head,
    )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
