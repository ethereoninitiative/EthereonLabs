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

# The only evidence allowed to use the pre-SHA-binding compatibility path is the
# immutable, committed genesis set. A canon label or repo-relative location alone
# is not sufficient authority for the exception.
LEGACY_GENESIS_GOVERNANCE_HASH = "690b249ef2388ac70f9714ef3bd649b6bd235f0e32840faefe7c3562563a00ab"
LEGACY_GENESIS_LINEAGE_HASH = "2664c65bdc3e37733d1262d436e2c615191dc69dc71b0b798d71227f283d5401"
LEGACY_GENESIS_PAYLOAD_HASH = "fed4e6e257928a502355eaa18a81f8a1130a875c014da2c971c2ff49b5a60dbb"
LEGACY_GENESIS_VALIDATION_HASH = "c1601b2069ce3eb40081e3590bc3734ed5c9dbe8971e9f1a2f52c0b07e320d77"

SUCCESSOR_TEXT_FIELDS = (
    "validation_artifact_id",
    "validation_artifact_path",
    "validation_artifact_sha256",
    "candidate_commit_sha",
    "test_execution_log",
    "change_summary",
    "structural_impact_assessment",
)


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


def path_is_within(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


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
    governance_path = (governance_path if governance_path.is_absolute() else root / governance_path).resolve()
    lineage_path = (lineage_path if lineage_path.is_absolute() else root / lineage_path).resolve()
    promotion_receipt_path = (
        promotion_receipt_path if promotion_receipt_path.is_absolute() else root / promotion_receipt_path
    ).resolve()

    evidence_paths = {
        "governance_chain": governance_path,
        "canon_lineage": lineage_path,
        "promotion_receipt": promotion_receipt_path,
    }
    evidence_within_repo = {
        name: path_is_within(root, path)
        for name, path in evidence_paths.items()
    }
    if not all(evidence_within_repo.values()):
        return {
            "verifier": "post_promotion_verifier_r2",
            "passed": False,
            "valid": False,
            "checks": {
                f"{name}_within_repository": within
                for name, within in evidence_within_repo.items()
            },
            "errors": ["post-promotion evidence paths must remain within the repository"],
        }

    required = {
        name: path.is_file()
        for name, path in evidence_paths.items()
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
        )
    else:
        validation_reference = promotion_payload.get("validation_reference")
        reference_links = (
            head.get("validation_artifact_reference") == validation_reference
            and governance_event.get("validation_reference") == validation_reference
        )

    # A prepared receipt may relocate validation bytes. The original reference
    # stays in the hashed payload and governance metadata; the same required
    # SHA-256, artifact identity and candidate SHA bind the relocated bytes.
    locations = promotion.get("evidence_paths", {})
    locations = locations if isinstance(locations, dict) else {}
    effective_validation_reference = locations.get("validation_artifact", validation_reference)
    validation_path = resolve_evidence_path(root, effective_validation_reference)
    validation_exists = validation_path is not None and validation_path.is_file()
    validation_receipt: Dict[str, Any] = {}
    if validation_exists and validation_path is not None:
        try:
            validation_receipt = read_json(validation_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            validation_receipt = {}

    candidate_sha = promotion_payload.get("candidate_commit_sha")
    sha_bound_promotion = candidate_sha is not None
    validation_hash = hashlib.sha256(validation_path.read_bytes()).hexdigest() if validation_exists and validation_path else None
    legacy_genesis = (
        governance_path == (root / DEFAULT_GOVERNANCE).resolve()
        and lineage_path == (root / DEFAULT_LINEAGE).resolve()
        and promotion_receipt_path == (root / DEFAULT_PROMOTION).resolve()
        and len(governance_rows) == 1
        and len(lineage_rows) == 1
        and head_name == "canon-0001"
        and head.get("lineage_record_hash") == LEGACY_GENESIS_LINEAGE_HASH
        and governance_hash == LEGACY_GENESIS_GOVERNANCE_HASH
        and promotion.get("promotion_id") == "promotion-0001"
        and promotion.get("promotion_payload_hash") == LEGACY_GENESIS_PAYLOAD_HASH
        and validation_hash == LEGACY_GENESIS_VALIDATION_HASH
        and not sha_bound_promotion
    )
    expected_validation_hash = promotion_payload.get("validation_artifact_sha256")
    successor_text_evidence_present = all(
        isinstance(promotion_payload.get(field), str) and bool(promotion_payload[field].strip())
        for field in SUCCESSOR_TEXT_FIELDS
    )

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
        "governance_event_is_promotion": legacy_genesis or governance_event.get("event_type") == "promotion",
        "governance_action_is_promotion": legacy_genesis or metadata.get("action_type") == "promotion",
        "governance_modes_are_drydock_to_canon": legacy_genesis
        or (
            governance_event.get("previous_mode") == "DryDock"
            and governance_event.get("new_mode") == "Canon"
        ),
        "promotion_governance_hash_linked": promotion.get("governance_event_hash") == governance_hash,
        "promotion_lineage_hash_linked": promotion.get("canon_lineage_hash") == head.get("lineage_record_hash"),
        "validation_reference_linked": reference_links,
        "validation_relocation_requires_sha_binding": effective_validation_reference == validation_reference
        or sha_bound_promotion,
        "validation_original_reference_within_repository": resolve_evidence_path(root, validation_reference) is not None,
        "receipt_evidence_locations_linked": all(
            key not in locations or resolve_evidence_path(root, locations[key]) == path
            for key, path in evidence_paths.items() if key != "promotion_receipt"
        ),
        "validation_artifact_exists": validation_exists,
        "validation_artifact_passed": validation_receipt.get("passed") is True,
        "validation_artifact_identity_linked": legacy_genesis
        or validation_receipt.get("artifact_id") == validation_id,
        "symbolic_dependency_separated": (
            promotion_payload.get("symbolic_dependency_violation") is False
            if legacy_genesis
            else promotion_payload.get("runtime_requires_symbolic_interpretation") is False
        ),
        "successor_requires_sha_binding": legacy_genesis or sha_bound_promotion,
        "successor_text_evidence_present": legacy_genesis or successor_text_evidence_present,
        "successor_regression_confirmed": legacy_genesis
        or promotion_payload.get("regression_check_confirmation") is True,
        "successor_conceptual_layer_confirmed": legacy_genesis
        or promotion_payload.get("conceptual_layer_check_confirmation") is True,
        "candidate_commit_is_ancestor": legacy_genesis or git_commit_is_ancestor(root, candidate_sha),
        "validation_artifact_hash_linked": legacy_genesis or validation_hash == expected_validation_hash,
        "validation_artifact_commit_linked": legacy_genesis or validation_receipt.get("repository_head") == candidate_sha,
        "governance_metadata_validation_id_linked": legacy_genesis
        or metadata.get("validation_artifact_id") == validation_id,
        "governance_metadata_validation_path_linked": legacy_genesis
        or metadata.get("validation_artifact_path") == validation_reference,
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
            "validation_artifact": effective_validation_reference,
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
