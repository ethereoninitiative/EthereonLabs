"""Exercise runtime promotion, prepared export, Git review, and rejection paths."""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from unittest.mock import patch

try:
    from . import runtime_runner_r1_merged as runner_module
    from .canonical_promotion_export_r1 import (
        PREPARED, PreparationError, layout, prepare, verify_prepared, write_json,
    )
    from .canon_lineage_store_r1 import CanonLineageStore
    from .governance_integrity_r1 import GovernanceIntegrityChain
    from .post_promotion_verifier_r2 import DEFAULT_ARTIFACT_DIR, verify
    from .repo_paths_r1 import repo_root
except ImportError:
    import runtime_runner_r1_merged as runner_module
    from canonical_promotion_export_r1 import (
        PREPARED, PreparationError, layout, prepare, verify_prepared, write_json,
    )
    from canon_lineage_store_r1 import CanonLineageStore
    from governance_integrity_r1 import GovernanceIntegrityChain
    from post_promotion_verifier_r2 import DEFAULT_ARTIFACT_DIR, verify
    from repo_paths_r1 import repo_root


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=Lumina sea trial", "-c", "user.email=sea-trial@example.invalid", *args],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()


def run() -> dict:
    source_root = repo_root()
    checks: dict[str, bool] = {}
    rejected: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="canonical-promotion-export-r1-") as temporary:
        root = Path(temporary).resolve()
        shutil.copytree(source_root / DEFAULT_ARTIFACT_DIR, root / DEFAULT_ARTIFACT_DIR)
        shutil.copyfile(source_root / ".gitignore", root / ".gitignore")
        (root / "candidate.txt").write_text("candidate runtime input\n", encoding="utf-8")
        git(root, "init", "-q")
        git(root, "add", ".")
        git(root, "commit", "-qm", "isolated committed genesis and candidate")
        candidate = git(root, "rev-parse", "HEAD")
        current = {p.name: p.read_bytes() for p in (root / DEFAULT_ARTIFACT_DIR).iterdir() if p.is_file()}
        target = root / PREPARED / "canon-0002"

        with ExitStack() as stack:
            stack.enter_context(patch.object(runner_module, "_repo_root", return_value=root))
            stack.enter_context(patch.object(GovernanceIntegrityChain, "_repo_root", return_value=root))
            stack.enter_context(patch.object(CanonLineageStore, "_repo_root", return_value=root))

            def promote(name: str, *, isolated: bool = False) -> Path:
                state = root / ".lumina_state" / name
                state.mkdir(parents=True)
                validation = state / "validation.json"
                write_json(validation, {"artifact_id": name, "repository_head": git(root, "rev-parse", "HEAD"),
                                        "passed": True, "authority_scope": "isolated_integration_trial"})
                payload = {
                    "validation_artifact_id": name,
                    "validation_artifact_path": validation.relative_to(root).as_posix(),
                    "validation_artifact_sha256": hashlib.sha256(validation.read_bytes()).hexdigest(),
                    "candidate_commit_sha": git(root, "rev-parse", "HEAD"),
                    "test_execution_log": "isolated integration candidate fixture established",
                    "change_summary": "exercise canonical evidence export",
                    "structural_impact_assessment": "isolated Git repository; no live canon authority",
                    "regression_check_confirmation": True,
                    "conceptual_layer_check_confirmation": True,
                    "runtime_requires_symbolic_interpretation": False,
                }
                runner = runner_module.RuntimeRunner(base_dir=state, seed_committed_canon=not isolated)
                result = runner.run_cycle(current_mode="DryDock", target_mode="Canon", action_type="promotion",
                                          requested_action="verify_canonical_promotion_export", promotion_payload=payload,
                                          repo_path=root).to_dict()
                assert result["halted"] is False, result
                assert runner.governance_log.verify_chain()["valid"] is True
                assert runner.canon_lineage_store.verify_lineage()["valid"] is True
                return state

            def rejects(name: str, state: Path) -> None:
                try:
                    prepare(root=root, state_dir=state)
                except (PreparationError, ValueError, KeyError, TypeError, OSError) as exc:
                    rejected[name] = str(exc)
                    checks[name] = not target.exists()
                else:
                    checks[name] = False
                    shutil.rmtree(target)

            state = promote("valid-successor")
            source_receipt = json.loads((state / "promotion_receipt_0002.json").read_text())
            result = prepare(root=root, state_dir=state)
            paths = layout(root, target)
            exported = json.loads(paths["promotion_receipt"].read_text())
            checks["real_runner_successor_export_passes"] = result["passed"] and result["canon_head"] == "canon-0002"
            checks["committed_genesis_parent_preserved"] = result["canon_parent"] == "canon-0001"
            checks["payload_and_hashes_preserved"] = all(exported[key] == source_receipt[key] for key in source_receipt)
            checks["append_only_chain_bytes_preserved"] = (
                paths["governance_chain"].read_bytes() == (state / "governance_log_r1.jsonl").read_bytes()
                and paths["canon_lineage"].read_bytes() == (state / "canon_lineage_r1.jsonl").read_bytes())
            checks["source_payload_sha_preserved"] = result["candidate_commit_sha"] == candidate
            validation_bytes = paths["validation_artifact"].read_bytes()
            paths["validation_artifact"].write_bytes(validation_bytes + b"\n")
            tampered_copy = verify(root=root, governance_path=paths["governance_chain"],
                                   lineage_path=paths["canon_lineage"], promotion_receipt_path=paths["promotion_receipt"])
            checks["relocated_validation_hash_still_enforced"] = (
                tampered_copy["passed"] is False and "validation_artifact_hash_linked" in tampered_copy["failed_checks"])
            paths["validation_artifact"].write_bytes(validation_bytes)
            redirected = dict(exported)
            redirected["evidence_paths"] = dict(exported["evidence_paths"], validation_artifact="../outside.json")
            write_json(paths["promotion_receipt"], redirected)
            outside = verify(root=root, governance_path=paths["governance_chain"], lineage_path=paths["canon_lineage"],
                             promotion_receipt_path=paths["promotion_receipt"])
            checks["relocated_validation_cannot_escape_repository"] = outside["passed"] is False
            write_json(paths["promotion_receipt"], exported)
            extra = target / "unexpected.json"
            extra.write_text("{}\n", encoding="utf-8")
            try:
                verify_prepared(root, target)
            except PreparationError:
                checks["unbounded_extra_export_file_rejected"] = True
            else:
                checks["unbounded_extra_export_file_rejected"] = False
            extra.unlink()
            before = {p.name: p.read_bytes() for p in target.iterdir()}
            try:
                prepare(root=root, state_dir=state)
            except PreparationError:
                checks["existing_target_not_overwritten"] = before == {p.name: p.read_bytes() for p in target.iterdir()}
            else:
                checks["existing_target_not_overwritten"] = False
            (state / "validation.json").unlink()
            checks["prepared_set_survives_local_validation_removal"] = verify_prepared(root, target)["passed"]

            # A later commit may contain only these prepared evidence files.
            git(root, "add", PREPARED.as_posix())
            git(root, "commit", "-qm", "review prepared successor evidence only")
            checks["prepared_evidence_commit_reverifies"] = verify_prepared(root, target)["passed"]
            (root / "candidate.txt").write_text("changed executable candidate\n", encoding="utf-8")
            git(root, "add", "candidate.txt")
            git(root, "commit", "-qm", "change candidate after validation")
            try:
                verify_prepared(root, target)
            except PreparationError as exc:
                rejected["changed_candidate_after_review_rejected"] = str(exc)
                checks["changed_candidate_after_review_rejected"] = True
            else:
                checks["changed_candidate_after_review_rejected"] = False
            git(root, "reset", "--hard", candidate)

            stale = promote("stale")
            (root / "candidate.txt").write_text("new head\n", encoding="utf-8")
            git(root, "add", "candidate.txt")
            git(root, "commit", "-qm", "move candidate before preparation")
            rejects("stale_sha_rejected", stale)
            git(root, "reset", "--hard", candidate)

            dirty = promote("dirty")
            (root / "candidate.txt").write_text("uncommitted candidate\n", encoding="utf-8")
            rejects("dirty_candidate_rejected", dirty)
            git(root, "restore", "candidate.txt")

            for name, filename, mutation in [
                ("tampered_governance_rejected", "governance_log_r1.jsonl", lambda text: text.replace("cycle initialized", "tampered cycle")),
                ("broken_lineage_rejected", "canon_lineage_r1.jsonl", lambda text: text.replace('"canon_parent": "canon-0001"', '"canon_parent": "canon-0999"')),
                ("validation_hash_mismatch_rejected", "validation.json", lambda text: text.replace("isolated_integration_trial", "tampered")),
                ("receipt_payload_mismatch_rejected", "promotion_receipt_0002.json", lambda text: text.replace("exercise canonical evidence export", "unapproved replacement")),
            ]:
                invalid = promote(name)
                path = invalid / filename
                original = path.read_text()
                changed = mutation(original)
                assert original != changed, name
                path.write_text(changed, encoding="utf-8")
                rejects(name, invalid)

            missing = promote("missing-validation")
            (missing / "validation.json").unlink()
            rejects("missing_validation_rejected", missing)
            parallel = promote("parallel-genesis", isolated=True)
            rejects("parallel_genesis_rejected", parallel)

            # Even a validly rehashed alternate genesis cannot replace committed history.
            alternate = promote("alternate-history")
            path = alternate / "canon_lineage_r1.jsonl"
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            rows[0]["canon_commit_summary"] = "alternate genesis"
            chain = CanonLineageStore(path, seed_committed_canon=False)
            for index, row in enumerate(rows):
                row["prev_lineage_hash"] = rows[index - 1]["lineage_record_hash"] if index else None
                row["lineage_record_hash"] = chain._compute_record_hash(row)
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            assert chain.verify_lineage()["valid"]
            rejects("rehashed_alternate_genesis_rejected", alternate)

            unanchored = root / ".lumina_state/unanchored"
            runner = runner_module.RuntimeRunner(base_dir=unanchored)
            runner.run_cycle(current_mode="Observation", target_mode="Observation", action_type="audit", repo_path=root)
            prior = (unanchored / "governance_log_r1.jsonl").read_bytes()
            try:
                runner.run_cycle(current_mode="DryDock", target_mode="Canon", action_type="promotion",
                                 promotion_payload=source_receipt["promotion_payload"], repo_path=root)
            except ValueError:
                checks["unanchored_existing_log_not_rewritten"] = (unanchored / "governance_log_r1.jsonl").read_bytes() == prior
            else:
                checks["unanchored_existing_log_not_rewritten"] = False

            final_state = promote("post-receipt-tamper")
            prepare(root=root, state_dir=final_state)
            post = paths["post_promotion_verification"]
            content = json.loads(post.read_text())
            content["candidate_commit_sha"] = "0" * 40
            write_json(post, content)
            try:
                verify_prepared(root, target)
            except PreparationError:
                checks["tampered_post_verification_receipt_rejected"] = True
            else:
                checks["tampered_post_verification_receipt_rejected"] = False
            shutil.rmtree(target)
            checks["current_canon_never_modified"] = current == {
                p.name: p.read_bytes() for p in (root / DEFAULT_ARTIFACT_DIR).iterdir() if p.is_file()}
            checks["current_canon_still_genesis"] = verify(root=root)["canon_head"] == "canon-0001"

    return {"trial": "canonical_promotion_export_r1", "passed": all(checks.values()), "checks": checks,
            "rejections": rejected, "failed_checks": [key for key, passed in checks.items() if not passed],
            "authority_boundary": "Isolated Git repository only. No prepared or active successor is committed to the live repository."}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
