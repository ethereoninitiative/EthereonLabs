from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

try:
    from . import runtime_spine_r1 as spine
except Exception:
    import runtime_spine_r1 as spine


def _run_git(args: List[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


def _structural(builder: spine.ContextBundleBuilder, repo_path: Path) -> Dict[str, Any]:
    return builder.build(repo_path=repo_path).structural_context


def main() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="lumina-context-truth-") as temp_dir:
        root = Path(temp_dir)
        builder = spine.ContextBundleBuilder(root / "bundles")

        missing = _structural(builder, root / "missing")

        file_path = root / "not-a-directory.txt"
        file_path.write_text("not a repository", encoding="utf-8")
        not_directory = _structural(builder, file_path)

        non_git_path = root / "non-git"
        non_git_path.mkdir()
        non_git = _structural(builder, non_git_path)

        repo = root / "repo"
        repo.mkdir()
        _run_git(["init", "-b", "main"], repo)
        _run_git(["config", "user.email", "lumina-sea-trial@example.invalid"], repo)
        _run_git(["config", "user.name", "Lumina Sea Trial"], repo)
        tracked = repo / "tracked.txt"
        tracked.write_text("clean\n", encoding="utf-8")
        _run_git(["add", "tracked.txt"], repo)
        _run_git(["commit", "-m", "Create clean baseline"], repo)

        clean = _structural(builder, repo)
        tracked.write_text("dirty\n", encoding="utf-8")
        dirty = _structural(builder, repo)

        original_run_git_checked = spine._run_git_checked

        def fail_status(args: List[str], cwd: Path) -> spine.GitCommandResult:
            if args == ["status", "--short"]:
                return spine.GitCommandResult(
                    ok=False,
                    stderr="simulated status inspection failure",
                    returncode=71,
                    error_type="GitCommandError",
                )
            return original_run_git_checked(args, cwd)

        spine._run_git_checked = fail_status
        try:
            failed_inspection = _structural(builder, repo)
        finally:
            spine._run_git_checked = original_run_git_checked

        checks = {
            "missing_path_is_unavailable": (
                missing.get("repo_available") is False
                and missing.get("repo_validation_error", {}).get("code") == "repo_path_missing"
            ),
            "file_path_is_not_directory": (
                not_directory.get("repo_available") is False
                and not_directory.get("repo_validation_error", {}).get("code") == "repo_path_not_directory"
            ),
            "non_git_directory_is_unavailable": (
                non_git.get("repo_available") is False
                and non_git.get("repo_validation_error", {}).get("code") == "git_worktree_validation_failed"
            ),
            "valid_clean_repo_reports_clean_state": (
                clean.get("repo_available") is True
                and clean.get("changed_files") == []
                and clean.get("current_branch") == "main"
            ),
            "valid_dirty_repo_reports_changed_file": (
                dirty.get("repo_available") is True
                and any("tracked.txt" in item for item in dirty.get("changed_files", []))
            ),
            "failed_git_command_never_becomes_empty_truth": (
                failed_inspection.get("repo_available") is False
                and failed_inspection.get("repo_validation_error", {}).get("code") == "git_command_failed"
                and failed_inspection.get("repo_validation_error", {}).get("command") == "git status --short"
                and "changed_files" not in failed_inspection
            ),
        }
        report = {
            "passed": all(checks.values()),
            "checks": checks,
            "failed_inspection": failed_inspection,
        }
        print(json.dumps(report, indent=2))
        if not report["passed"]:
            raise SystemExit(1)
        return report


if __name__ == "__main__":
    main()
