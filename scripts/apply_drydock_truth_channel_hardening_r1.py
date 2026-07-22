from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime"
SHIP_ROOT = RUNTIME_ROOT.parent
STUDIO_ROOT = SHIP_ROOT / "studio"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "lumina-drydock-gate.yml"
REGISTRY_PATH = ROOT / "docs" / "ACTIVE_SURFACE_REGISTRY_R1.json"
INDEX_PATH = SHIP_ROOT / "ACTIVE_RUNTIME_INDEX.md"
OPERATING_MAP_PATH = ROOT / "CURRENT_OPERATING_MAP.md"


def replace_exact(path: Path, old: str, new: str, *, expected_count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected_count:
        raise RuntimeError(f"{path}: expected {expected_count} occurrences, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


runtime_spine = RUNTIME_ROOT / "runtime_spine_r1.py"
replace_exact(
    runtime_spine,
    '''    if explicit_repo_path:\n        candidate = Path(explicit_repo_path).resolve()\n        return candidate if candidate.exists() else None\n''',
    '''    if explicit_repo_path is not None:\n        return Path(explicit_repo_path).expanduser().resolve()\n''',
)

replace_exact(
    runtime_spine,
    '''def _run_git(args: List[str], cwd: Path) -> Optional[str]:\n    try:\n        proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True)\n        return proc.stdout.strip()\n    except Exception:\n        return None\n''',
    '''@dataclass(frozen=True)\nclass GitCommandResult:\n    ok: bool\n    stdout: str = ""\n    stderr: str = ""\n    returncode: Optional[int] = None\n    error_type: Optional[str] = None\n\n\ndef _bounded_git_text(value: Any, max_length: int = 400) -> str:\n    compact = " ".join(str(value or "").split())\n    if len(compact) <= max_length:\n        return compact\n    return compact[: max_length - 3] + "..."\n\n\ndef _run_git_checked(args: List[str], cwd: Path) -> GitCommandResult:\n    try:\n        proc = subprocess.run(\n            ["git", *args],\n            cwd=str(cwd),\n            capture_output=True,\n            text=True,\n            check=False,\n        )\n    except Exception as exc:\n        return GitCommandResult(\n            ok=False,\n            stderr=_bounded_git_text(exc),\n            returncode=None,\n            error_type=type(exc).__name__,\n        )\n    if proc.returncode != 0:\n        return GitCommandResult(\n            ok=False,\n            stdout=proc.stdout.strip(),\n            stderr=_bounded_git_text(proc.stderr),\n            returncode=proc.returncode,\n            error_type="GitCommandError",\n        )\n    return GitCommandResult(\n        ok=True,\n        stdout=proc.stdout.strip(),\n        stderr=_bounded_git_text(proc.stderr),\n        returncode=proc.returncode,\n        error_type=None,\n    )\n\n\ndef _run_git(args: List[str], cwd: Path) -> Optional[str]:\n    result = _run_git_checked(args, cwd)\n    return result.stdout if result.ok else None\n\n\ndef _git_validation_error(\n    code: str,\n    message: str,\n    *,\n    command: Optional[List[str]] = None,\n    result: Optional[GitCommandResult] = None,\n) -> Dict[str, Any]:\n    payload: Dict[str, Any] = {"code": code, "message": message}\n    if command:\n        payload["command"] = "git " + " ".join(command)\n    if result is not None:\n        payload["returncode"] = result.returncode\n        payload["error_type"] = result.error_type\n        if result.stderr:\n            payload["stderr"] = result.stderr\n    return payload\n''',
)

replace_exact(
    runtime_spine,
    '''    def _collect_structural_context(self, repo_path: Optional[Path]) -> Dict[str, Any]:\n        if not repo_path or not repo_path.exists():\n            return {"repo_available": False}\n        branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)\n        status = _run_git(["status", "--short"], repo_path)\n        commits = _run_git(["log", "--oneline", "-5"], repo_path)\n        return {\n            "repo_available": True,\n            "repo_path": str(repo_path),\n            "runtime_root": str(infer_runtime_root()) if infer_runtime_root() is not None else None,\n            "current_branch": branch,\n            "changed_files": status.splitlines() if status else [],\n            "recent_commits": commits.splitlines() if commits else [],\n        }\n''',
    '''    def _collect_structural_context(self, repo_path: Optional[Path]) -> Dict[str, Any]:\n        runtime_root = infer_runtime_root()\n        unavailable: Dict[str, Any] = {\n            "repo_available": False,\n            "repo_path": str(repo_path) if repo_path is not None else None,\n            "runtime_root": str(runtime_root) if runtime_root is not None else None,\n        }\n        if repo_path is None:\n            unavailable["repo_validation_error"] = _git_validation_error(\n                "repo_path_unavailable",\n                "No repository path could be resolved.",\n            )\n            return unavailable\n        if not repo_path.exists():\n            unavailable["repo_validation_error"] = _git_validation_error(\n                "repo_path_missing",\n                "The requested repository path does not exist.",\n            )\n            return unavailable\n        if not repo_path.is_dir():\n            unavailable["repo_validation_error"] = _git_validation_error(\n                "repo_path_not_directory",\n                "The requested repository path is not a directory.",\n            )\n            return unavailable\n\n        worktree_command = ["rev-parse", "--is-inside-work-tree"]\n        worktree = _run_git_checked(worktree_command, repo_path)\n        if not worktree.ok:\n            unavailable["repo_validation_error"] = _git_validation_error(\n                "git_worktree_validation_failed",\n                "The repository path could not be validated as a Git worktree.",\n                command=worktree_command,\n                result=worktree,\n            )\n            return unavailable\n        if worktree.stdout.strip().lower() != "true":\n            unavailable["repo_validation_error"] = _git_validation_error(\n                "not_git_worktree",\n                "The repository path is not inside a Git worktree.",\n                command=worktree_command,\n                result=worktree,\n            )\n            return unavailable\n\n        commands = {\n            "current_branch": ["rev-parse", "--abbrev-ref", "HEAD"],\n            "changed_files": ["status", "--short"],\n            "recent_commits": ["log", "--oneline", "-5"],\n        }\n        results: Dict[str, GitCommandResult] = {}\n        for field_name, command in commands.items():\n            result = _run_git_checked(command, repo_path)\n            if not result.ok:\n                unavailable["repo_validation_error"] = _git_validation_error(\n                    "git_command_failed",\n                    f"Git inspection failed while collecting {field_name}.",\n                    command=command,\n                    result=result,\n                )\n                return unavailable\n            results[field_name] = result\n\n        return {\n            "repo_available": True,\n            "repo_path": str(repo_path),\n            "runtime_root": str(runtime_root) if runtime_root is not None else None,\n            "current_branch": results["current_branch"].stdout,\n            "changed_files": results["changed_files"].stdout.splitlines(),\n            "recent_commits": results["recent_commits"].stdout.splitlines(),\n        }\n''',
)

studio_server = STUDIO_ROOT / "lumina_studio_server.py"
replace_exact(
    studio_server,
    '''def _query_limit(path: str, default: int = 20) -> int:\n    query = parse_qs(urlparse(path).query)\n    try:\n        return max(1, min(int(_single(query, "limit", str(default))), 100))\n    except Exception:\n        return default\n\n\nclass LuminaStudioHandler(BaseHTTPRequestHandler):\n''',
    '''def _query_limit(path: str, default: int = 20) -> int:\n    query = parse_qs(urlparse(path).query)\n    try:\n        return max(1, min(int(_single(query, "limit", str(default))), 100))\n    except Exception:\n        return default\n\n\nPORTABLE_PATH_BUDGET = 240\nMAX_OPERATOR_ERROR_LENGTH = 240\n\n\ndef _bounded_operator_error(exc: Exception) -> str:\n    message = " ".join(str(exc).split()) or type(exc).__name__\n    if len(message) <= MAX_OPERATOR_ERROR_LENGTH:\n        return message\n    return message[: MAX_OPERATOR_ERROR_LENGTH - 3] + "..."\n\n\ndef _classify_studio_error(exc: Exception) -> tuple[int, Dict[str, Any]]:\n    message = _bounded_operator_error(exc)\n    payload: Dict[str, Any] = {\n        "ok": False,\n        "error_code": "runtime_cycle_failed",\n        "error": message,\n        "recoverable": False,\n    }\n    status = 500\n\n    if isinstance(exc, json.JSONDecodeError):\n        status = 400\n        payload["error_code"] = "invalid_request_payload"\n        payload["recoverable"] = True\n    elif isinstance(exc, (ValueError, TypeError)):\n        status = 400\n        payload["error_code"] = "invalid_operator_input"\n        payload["recoverable"] = True\n    elif isinstance(exc, OSError):\n        filename = getattr(exc, "filename", None)\n        path_length = len(str(filename)) if filename else None\n        lower_message = message.lower()\n        path_budget_exceeded = (\n            getattr(exc, "winerror", None) == 206\n            or getattr(exc, "errno", None) == 206\n            or "filename or extension is too long" in lower_message\n            or "file name too long" in lower_message\n            or (path_length is not None and path_length > PORTABLE_PATH_BUDGET)\n        )\n        if path_budget_exceeded:\n            status = 422\n            payload["error_code"] = "path_budget_exceeded"\n            payload["recoverable"] = True\n            payload["path_length"] = path_length\n            payload["path_budget"] = PORTABLE_PATH_BUDGET\n        else:\n            payload["error_code"] = "artifact_write_failed"\n            payload["recoverable"] = True\n\n    payload["error_class"] = type(exc).__name__\n    return status, payload\n\n\ndef _record_studio_error(payload: Dict[str, Any]) -> None:\n    print(\n        f"Lumina Studio diagnostic [{payload['error_code']}] "\n        f"{payload.get('error_class', 'Exception')}: {payload['error']}",\n        file=sys.stderr,\n    )\n\n\nclass LuminaStudioHandler(BaseHTTPRequestHandler):\n''',
)

replace_exact(
    studio_server,
    '''        except Exception as exc:  # pragma: no cover - operator feedback path\n            body = json.dumps({"ok": False, "error": str(exc)}, indent=2).encode("utf-8")\n            self._send(500, body, "application/json")\n''',
    '''        except Exception as exc:  # pragma: no cover - exercised by focused handler sea trial\n            status, error_payload = _classify_studio_error(exc)\n            _record_studio_error(error_payload)\n            body = json.dumps(error_payload, indent=2).encode("utf-8")\n            self._send(status, body, "application/json")\n''',
)

context_trial = r'''from __future__ import annotations

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
'''
(RUNTIME_ROOT / "sea_trials_context_bundle_repo_truth_r1.py").write_text(context_trial, encoding="utf-8")

studio_trial = r'''from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SHIP_ROOT = Path(__file__).resolve().parent
STUDIO_ROOT = SHIP_ROOT / "studio"
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

import lumina_studio_server as studio


def _invoke_handler(
    *,
    raised: Optional[Exception] = None,
    body: bytes = b"{}",
    content_type: str = "application/json",
) -> Dict[str, Any]:
    captured: Dict[str, Any] = {}
    handler = studio.LuminaStudioHandler.__new__(studio.LuminaStudioHandler)
    handler.path = "/run"
    handler.headers = {
        "Content-Length": str(len(body)),
        "Content-Type": content_type,
    }
    handler.rfile = io.BytesIO(body)
    handler._send = lambda status, response_body, response_type: captured.update(
        {
            "status": status,
            "body": response_body,
            "content_type": response_type,
        }
    )

    original_run = studio.run_lumina_cycle
    if raised is not None:
        def raise_error(_args: Any) -> Any:
            raise raised
        studio.run_lumina_cycle = raise_error
    try:
        handler.do_POST()
    finally:
        studio.run_lumina_cycle = original_run

    captured["payload"] = json.loads(captured["body"].decode("utf-8"))
    return captured


def main() -> Dict[str, Any]:
    long_path = "C:\\Lumina\\" + ("segment\\" * 40) + "receipt.json"
    path_error = OSError(206, "The filename or extension is too long", long_path)
    path_result = _invoke_handler(raised=path_error)
    os_result = _invoke_handler(raised=OSError(5, "simulated artifact write failure"))
    runtime_result = _invoke_handler(raised=RuntimeError("simulated runtime failure"))
    invalid_json_result = _invoke_handler(body=b"{not-json")

    required_keys = {"ok", "error_code", "error", "recoverable", "error_class"}
    checks = {
        "path_budget_error_classified": (
            path_result["status"] == 422
            and path_result["payload"].get("error_code") == "path_budget_exceeded"
            and path_result["payload"].get("recoverable") is True
            and path_result["payload"].get("path_budget") == studio.PORTABLE_PATH_BUDGET
            and path_result["payload"].get("path_length", 0) > studio.PORTABLE_PATH_BUDGET
        ),
        "generic_os_error_classified": (
            os_result["status"] == 500
            and os_result["payload"].get("error_code") == "artifact_write_failed"
            and os_result["payload"].get("recoverable") is True
        ),
        "runtime_error_has_bounded_fallback": (
            runtime_result["status"] == 500
            and runtime_result["payload"].get("error_code") == "runtime_cycle_failed"
            and runtime_result["payload"].get("recoverable") is False
        ),
        "invalid_json_is_operator_correctable": (
            invalid_json_result["status"] == 400
            and invalid_json_result["payload"].get("error_code") == "invalid_request_payload"
            and invalid_json_result["payload"].get("recoverable") is True
        ),
        "responses_share_bounded_shape": all(
            required_keys.issubset(result["payload"])
            and result["payload"].get("ok") is False
            and len(result["payload"].get("error", "")) <= studio.MAX_OPERATOR_ERROR_LENGTH
            and result["content_type"] == "application/json"
            for result in (path_result, os_result, runtime_result, invalid_json_result)
        ),
    }
    report = {
        "passed": all(checks.values()),
        "checks": checks,
        "samples": {
            "path_budget": path_result["payload"],
            "artifact_write": os_result["payload"],
            "runtime": runtime_result["payload"],
            "invalid_json": invalid_json_result["payload"],
        },
    }
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    main()
'''
(SHIP_ROOT / "sea_trials_lumina_studio_diagnostics_r1.py").write_text(studio_trial, encoding="utf-8")

replace_exact(
    WORKFLOW_PATH,
    '''      - "docs/ACTIVE_SURFACE_REGISTRY_R1.json"\n      - "docs/ARTIFACT_TRUTH_CONTRACT.md"\n''',
    '''      - "README.md"\n      - "docs/LUMINA_EMBODIMENT_BEACON_R1.md"\n      - "docs/LUMINA_HABITAT_CREATION_CHECKLIST.md"\n      - "docs/ACTIVE_SURFACE_REGISTRY_R1.json"\n      - "docs/ARTIFACT_TRUTH_CONTRACT.md"\n''',
    expected_count=2,
)
replace_exact(
    WORKFLOW_PATH,
    '''          python sea_trials_set_one_r1_merged.py\n          python sea_trials_lumina_return_host_r1.py\n''',
    '''          python sea_trials_set_one_r1_merged.py\n          python sea_trials_context_bundle_repo_truth_r1.py\n          python sea_trials_lumina_return_host_r1.py\n''',
)
replace_exact(
    WORKFLOW_PATH,
    '''      - name: Host command smoke checks\n''',
    '''      - name: Studio diagnostics sea trial\n        working-directory: LuminaOS/bootstrap/Ship_of_Ethereon_V2\n        run: python sea_trials_lumina_studio_diagnostics_r1.py\n\n      - name: Host command smoke checks\n''',
)

registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
if any(surface.get("surface_id") == "lumina_embodiment_horizon" for surface in registry["surfaces"]):
    raise RuntimeError("lumina_embodiment_horizon already exists")
public_index = next(
    index
    for index, surface in enumerate(registry["surfaces"])
    if surface.get("surface_id") == "ethereon_public_site"
)
registry["surfaces"].insert(
    public_index,
    {
        "surface_id": "lumina_embodiment_horizon",
        "name": "Lumina embodiment architectural horizon",
        "status": "architectural-horizon",
        "default_wiring": False,
        "paths": [
            "README.md",
            "docs/LUMINA_EMBODIMENT_BEACON_R1.md",
            "docs/LUMINA_HABITAT_CREATION_CHECKLIST.md",
        ],
        "validation_paths": [
            ".github/workflows/lumina-drydock-gate.yml",
            "scripts/repository_truth_reconciliation_gate_r1.py",
        ],
        "authority_boundary": (
            "Guides long-term prioritization and stationary-habitation sequencing. "
            "It does not create current robotics capability, runtime authority, "
            "physical agency, or safety certification."
        ),
    },
)
markers = registry["claim_markers"]
markers["README.md"] = [
    "Lumina's long-term horizon includes **governed embodied intelligence**",
    "This is future direction, not a claim of current robotics capability or embodied readiness.",
]
markers["docs/LUMINA_EMBODIMENT_BEACON_R1.md"] = [
    "Embodiment begins with stable inhabitation, not movement.",
    "Presence must precede movement.",
    "Continuity is not permission",
]
markers["docs/LUMINA_HABITAT_CREATION_CHECKLIST.md"] = [
    "Before adding mobile physical capability, prove that a resident intelligence can meaningfully inhabit a stationary host.",
    "borrow proven wheels -> inhabit the stationary cart -> test the actual terrain -> redesign only what the evidence shows does not fit.",
]
REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

replace_exact(
    INDEX_PATH,
    '''The Ethereonic registry JSON is runtime-generated state, not a committed source file beside the module. Its generated location follows the active runner or test `base_dir`.\n''',
    '''The Ethereonic registry JSON is runtime-generated state, not a committed source file beside the module. Its generated location follows the active runner or test `base_dir`.\n\nStructural repository context validates the Git worktree before reporting branch, status, or history. Failed inspection is reported as bounded unavailable state and may not become an apparently clean repository snapshot.\n''',
)
replace_exact(
    INDEX_PATH,
    '''| Core runtime / governance / canon | `runtime/sea_trials_set_one_r1_merged.py` |\n''',
    '''| Core runtime / governance / canon | `runtime/sea_trials_set_one_r1_merged.py` |\n| Structural repository-context truth | `runtime/sea_trials_context_bundle_repo_truth_r1.py` |\n''',
)
replace_exact(
    INDEX_PATH,
    '''| Studio | `sea_trials_lumina_studio_v0_1.py` |\n''',
    '''| Studio | `sea_trials_lumina_studio_v0_1.py` |\n| Studio bounded diagnostics | `sea_trials_lumina_studio_diagnostics_r1.py` |\n''',
)
replace_exact(
    OPERATING_MAP_PATH,
    '''- Runtime work belongs in the Lumina OS substrate lane.\n''',
    '''- Runtime work belongs in the Lumina OS substrate lane.\n- Structural repository inspection must fail closed: an invalid or unverifiable Git worktree may not be rendered as a clean repository.\n''',
)

# These files exist only to perform this one-time branch transformation.
Path(__file__).unlink()
(ROOT / ".github" / "workflows" / "agent-drydock-hardening-apply.yml").unlink()
