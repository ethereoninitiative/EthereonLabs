"""Prepare verified local promotion evidence for review without activating canon."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

try:
    from .post_promotion_verifier_r2 import (
        DEFAULT_ARTIFACT_DIR, DEFAULT_GOVERNANCE, DEFAULT_LINEAGE,
        DEFAULT_PROMOTION, read_json, read_jsonl, resolve_evidence_path, verify,
    )
    from .repo_paths_r1 import repo_root
    from .runtime_spine_r1 import ModeGuard
except ImportError:
    from post_promotion_verifier_r2 import (
        DEFAULT_ARTIFACT_DIR, DEFAULT_GOVERNANCE, DEFAULT_LINEAGE,
        DEFAULT_PROMOTION, read_json, read_jsonl, resolve_evidence_path, verify,
    )
    from repo_paths_r1 import repo_root
    from runtime_spine_r1 import ModeGuard


PREPARED = DEFAULT_ARTIFACT_DIR.parent / "prepared"


class PreparationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreparationError(message)


def git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PreparationError(f"Git evidence could not be verified: {args[0]}") from exc


def relative_file(root: Path, path: Path) -> Path:
    path = path if path.is_absolute() else root / path
    require(path.absolute() == path.resolve(), "evidence paths must be normalized and contain no symlinks")
    require(path.is_relative_to(root) and path.is_file(), "required repository evidence file is missing")
    return path


def layout(root: Path, target: Path) -> dict[str, Path]:
    target = target if target.is_absolute() else root / target
    require(target.absolute() == target.resolve(), "prepared target must not traverse symlinks or parent directories")
    require(target.parent == root / PREPARED, "target must be one canon directory under artifacts/runtime_truth/prepared")
    require(re.fullmatch(r"canon-[0-9]{4}", target.name) is not None, "invalid prepared canon directory")
    suffix = target.name.removeprefix("canon-")
    return {
        "governance_chain": target / f"governance_chain_{suffix}.jsonl",
        "canon_lineage": target / f"canon_lineage_{suffix}.jsonl",
        "promotion_receipt": target / f"promotion_receipt_{suffix}.json",
        "validation_artifact": target / f"validation_artifact_{suffix}.json",
        "post_promotion_verification": target / f"post_promotion_verification_{suffix}.json",
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def portable_verification(root: Path, result: dict) -> dict:
    # The verifier also reports diagnostic paths from the chain stores.
    result["governance_chain_verification"]["log_path"] = Path(
        result["governance_chain_verification"]["log_path"]
    ).relative_to(root).as_posix()
    result["canon_lineage_verification"]["lineage_path"] = Path(
        result["canon_lineage_verification"]["lineage_path"]
    ).relative_to(root).as_posix()
    return result


def baseline(root: Path) -> tuple[bytes, bytes]:
    require(verify(root=root).get("passed") is True, "committed current canon fails post-promotion verification")
    for relative in (DEFAULT_GOVERNANCE, DEFAULT_LINEAGE, DEFAULT_PROMOTION):
        path = relative_file(root, relative)
        require(path.read_bytes() == git(root, "show", f"HEAD:{relative.as_posix()}"),
                "current canon differs from committed evidence")
    return (root / DEFAULT_GOVERNANCE).read_bytes(), (root / DEFAULT_LINEAGE).read_bytes()


def successor(root: Path, governance: Path, lineage: Path) -> str:
    committed_governance, committed_lineage = baseline(root)
    governance_bytes = governance.read_bytes()
    lineage_bytes = lineage.read_bytes()
    # Byte prefixes preserve all committed records, including their hashes.
    require(governance_bytes.startswith(committed_governance), "governance is not an append-only committed successor")
    require(lineage_bytes.startswith(committed_lineage), "lineage is not an append-only committed successor")
    parents = read_jsonl(root / DEFAULT_LINEAGE)
    rows = read_jsonl(lineage)
    require(len(rows) == len(parents) + 1, "prepare exactly one successor of committed canon")
    head = rows[-1]
    require(head.get("canon_parent") == parents[-1]["canon_version"], "successor parent does not match committed canon")
    require(head.get("prev_lineage_hash") == parents[-1]["lineage_record_hash"], "successor lineage hash does not extend committed canon")
    expected = f"canon-{len(parents) + 1:04d}"
    require(head.get("canon_version") == expected, "successor version does not extend committed canon")
    new_events = read_jsonl(governance)[len(read_jsonl(root / DEFAULT_GOVERNANCE)):]
    promotions = [row for row in new_events if row.get("event_type") == "promotion"
                  and row.get("allowed") is True and row.get("canonical_change") is True]
    require(len(promotions) == 1 and promotions[0].get("record_hash") == head.get("governance_event_hash"),
            "successor requires exactly one linked new promotion event")
    return expected


def clean_candidate(root: Path, candidate: str, *, allowed: set[str] | None = None) -> None:
    require(not git(root, "ls-files", "--", ".lumina_state"), "local runtime state must not be tracked")
    head = git(root, "rev-parse", "HEAD").decode().strip()
    if allowed is None:
        require(candidate == head, "stale candidate_commit_sha: preparation requires current HEAD")
        allowed = set()
    else:
        git(root, "merge-base", "--is-ancestor", candidate, "HEAD")
        changed = set(git(root, "diff", "--name-only", "-z", candidate, "HEAD").decode().split("\0")) - {""}
        require(changed <= allowed, "candidate code changed after validation; prepare a fresh promotion")
    dirty = set(git(root, "diff", "--name-only", "-z", "HEAD").decode().split("\0")) - {""}
    untracked = set(git(root, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")) - {""}
    require((dirty | untracked) <= allowed, "candidate working tree has changes outside the prepared evidence set")


def verify_prepared(root: Path, target: Path, *, check_receipt: bool = True) -> dict:
    root = root.resolve()
    paths = layout(root, target)
    target = paths["promotion_receipt"].parent
    allowed = {p.relative_to(root).as_posix() for p in paths.values()}
    expected_files = set(paths.values())
    if not check_receipt:
        expected_files.remove(paths["post_promotion_verification"])
    require(set(target.iterdir()) == expected_files, "prepared evidence set has missing or unexpected files")
    for path in expected_files:
        relative_file(root, path)
    expected = successor(root, paths["governance_chain"], paths["canon_lineage"])
    require(target.name == expected, "prepared directory does not match successor head")
    receipt = read_json(paths["promotion_receipt"])
    require(receipt.get("promotion_id") == expected.replace("canon-", "promotion-"), "promotion receipt identity mismatch")
    locations = {name: path.relative_to(root).as_posix() for name, path in paths.items()
                 if name in {"governance_chain", "canon_lineage", "validation_artifact"}}
    require(receipt.get("evidence_paths") == locations, "prepared evidence references do not match bounded target")
    require(receipt.get("authority_scope") == "prepared_for_review", "prepared evidence must not claim active canon")
    result = verify(root=root, governance_path=paths["governance_chain"],
                    lineage_path=paths["canon_lineage"], promotion_receipt_path=paths["promotion_receipt"],
                    expected_head=expected)
    require(result.get("passed") is True, f"prepared post-promotion verification failed: {result.get('failed_checks', result.get('errors'))}")
    clean_candidate(root, result["candidate_commit_sha"], allowed=allowed)
    result = portable_verification(root, result)
    if check_receipt:
        require(read_json(paths["post_promotion_verification"]) == result, "post-promotion verification receipt is stale or mismatched")
    return result


def prepare(*, root: Path, state_dir: Path, target: Path | None = None) -> dict:
    root = root.resolve()
    state_dir = state_dir if state_dir.is_absolute() else root / state_dir
    require(state_dir.absolute() == state_dir.resolve() and state_dir.is_relative_to(root / ".lumina_state"),
            "source must be repository-local promotion state without symlinks")
    governance = relative_file(root, state_dir / "governance_log_r1.jsonl")
    lineage = relative_file(root, state_dir / "canon_lineage_r1.jsonl")
    head = successor(root, governance, lineage)
    receipt_path = relative_file(root, state_dir / f"promotion_receipt_{head.removeprefix('canon-')}.json")
    receipt = read_json(receipt_path)
    source_verification = verify(root=root, governance_path=governance, lineage_path=lineage,
                                 promotion_receipt_path=receipt_path, expected_head=head)
    require(source_verification.get("passed") is True,
            f"local post-promotion verification failed: {source_verification.get('failed_checks', source_verification.get('errors'))}")
    payload = receipt["promotion_payload"]
    clean_candidate(root, payload["candidate_commit_sha"])
    decision = ModeGuard(repo_root=root).validate_promotion(payload)
    require(decision.allowed, decision.reason)
    # Local input must still use its originally authorized validation reference.
    require(source_verification["evidence_paths"]["validation_artifact"] == payload["validation_artifact_path"],
            "local validation evidence has already been relocated")
    validation = resolve_evidence_path(root, payload["validation_artifact_path"])
    require(validation is not None, "validation reference is invalid")
    validation = relative_file(root, root / payload["validation_artifact_path"])
    paths = layout(root, target or PREPARED / head)
    target = paths["promotion_receipt"].parent
    require(target.name == head, "target must name the verified successor")
    require(not target.exists(), "prepared target already exists; it will not be overwritten")

    # Freeze verified input bytes. The staged copy is independently verified, so
    # a source changed during collection cannot silently enter the export.
    frozen = {"governance_chain": governance.read_bytes(), "canon_lineage": lineage.read_bytes(),
              "validation_artifact": validation.read_bytes()}
    with tempfile.TemporaryDirectory(prefix="promotion-export-", dir=state_dir) as temporary:
        staging = Path(temporary)
        staged = {name: staging / path.name for name, path in paths.items()}
        for name, data in frozen.items():
            staged[name].write_bytes(data)
        exported = dict(receipt)
        exported["authority_scope"] = "prepared_for_review"
        exported["evidence_paths"] = {name: staged[name].relative_to(root).as_posix() for name in frozen}
        write_json(staged["promotion_receipt"], exported)
        stage_result = verify(root=root, governance_path=staged["governance_chain"],
                              lineage_path=staged["canon_lineage"], promotion_receipt_path=staged["promotion_receipt"],
                              expected_head=head)
        require(stage_result.get("passed") is True, "staged evidence changed or failed post-promotion verification")
        successor(root, staged["governance_chain"], staged["canon_lineage"])
        clean_candidate(root, payload["candidate_commit_sha"])
        exported["evidence_paths"] = {name: paths[name].relative_to(root).as_posix() for name in frozen}
        write_json(staged["promotion_receipt"], exported)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents overwriting an earlier prepared proposal.
        target.mkdir()
        try:
            for name in (*frozen, "promotion_receipt"):
                shutil.copyfile(staged[name], paths[name])
            result = verify_prepared(root, target, check_receipt=False)
            write_json(paths["post_promotion_verification"], result)
            return verify_prepared(root, target)
        except Exception:
            shutil.rmtree(target)
            raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("prepare", help="prepare one verified local successor; never commit or activate")
    create.add_argument("--state-dir", type=Path, required=True)
    create.add_argument("--target", type=Path)
    check = commands.add_parser("verify", help="reverify a prepared target, or all prepared targets for CI")
    check.add_argument("--target", type=Path)
    args = parser.parse_args()
    root = repo_root().resolve()
    try:
        if args.command == "prepare":
            result = prepare(root=root, state_dir=args.state_dir, target=args.target)
        else:
            require(not (root / PREPARED).exists() or (root / PREPARED).is_dir(),
                    "prepared evidence root must be a directory")
            targets = [args.target] if args.target else sorted((root / PREPARED).glob("*"))
            result = {"passed": True, "prepared_sets": [verify_prepared(root, path) for path in targets]}
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        result = {"passed": False, "error": str(exc)}
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
