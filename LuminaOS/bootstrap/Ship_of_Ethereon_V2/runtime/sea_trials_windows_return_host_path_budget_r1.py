from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable
import json
import shutil
import tempfile

try:
    from .runtime_runner_r1_merged import RuntimeRunner
    from .lumina_return_host_repo_native_bridge_r1 import PATH_BUDGET
except Exception:
    from runtime_runner_r1_merged import RuntimeRunner
    from lumina_return_host_repo_native_bridge_r1 import PATH_BUDGET


TARGET_WINDOWS_RUNTIME_BASE_LENGTH = 123
DEFAULT_STUDIO_ACTION = "studio_runtime_cycle_v0_3_2"
DEFAULT_STUDIO_PROJECT = "lumina-os"


def _windows_prefix_length_base(test_root: Path) -> Path:
    prefix = test_root / "installed_windows_runtime"
    padding_length = max(1, TARGET_WINDOWS_RUNTIME_BASE_LENGTH - len(str(prefix)) - 1)
    return prefix / ("x" * padding_length)


def _nested_values(node: Any, key: str) -> Iterable[Any]:
    if isinstance(node, dict):
        for item_key, value in node.items():
            if item_key == key:
                yield value
            yield from _nested_values(value, key)
    elif isinstance(node, list):
        for value in node:
            yield from _nested_values(value, key)


def main() -> Dict[str, Any]:
    test_root = Path(tempfile.gettempdir()) / "lumina_windows_return_host_path_budget_r1"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    runtime_base = _windows_prefix_length_base(test_root)
    runtime_base.mkdir(parents=True, exist_ok=True)

    legacy_projected_sessions_path = (
        runtime_base
        / "lumina_return_host_artifacts"
        / "4c7a7a99-640c-4b2e-a7f0-2c90a1904e4a"
        / f"{DEFAULT_STUDIO_PROJECT}_{DEFAULT_STUDIO_ACTION}_Observation"
        / "sessions"
    )

    runner = RuntimeRunner(
        base_dir=runtime_base,
        registry_path=Path(__file__).with_name("capability_registry_r1.json"),
    )
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action=DEFAULT_STUDIO_ACTION,
        action_type="audit",
        enabled_feature_flags=["ETHEREON_CONTINUITY_RESTORE", "ETHEREON_LUMINA_HOST"],
        runtime_config={
            "toki_pona_required_for_resume": False,
            "binary_required_for_transition_validation": False,
            "light_language_required_for_capability_loading": False,
            "harmonic_frequency_required_for_mode_legality": False,
        },
        raw_user_input="Review Lumina OS progress and produce the next governed action receipt.",
        project_id=DEFAULT_STUDIO_PROJECT,
    )
    payload = result.to_dict()

    return_host = payload.get("lumina_return_host_artifacts") or {}
    checkpoint_only = return_host.get("checkpoint_only") or {}
    checkpoint_plus_host = return_host.get("checkpoint_plus_host") or {}
    checkpoint_only_payload = checkpoint_only.get("payload") or {}
    checkpoint_plus_payload = checkpoint_plus_host.get("payload") or {}
    storage = checkpoint_plus_payload.get("storage") or checkpoint_only_payload.get("storage") or {}

    storage_base_dir = Path(str(storage.get("storage_base_dir", "")))
    written_paths = [
        Path(payload["checkpoint_path"]),
        Path(payload["session_path"]),
        Path(payload["log_path"]),
        Path(payload["governance_log_path"]),
        Path(str(checkpoint_only.get("checkpoint_path", ""))),
        Path(str(checkpoint_plus_host.get("checkpoint_path", ""))),
    ]
    written_paths.extend(path for path in storage_base_dir.rglob("*") if path.is_file())
    written_paths = [path for path in written_paths if str(path) not in {"", "."}]

    missing_paths = [str(path) for path in written_paths if not path.exists()]
    path_lengths = {str(path): len(str(path)) for path in written_paths}
    longest_path = max(path_lengths, key=path_lengths.get) if path_lengths else None
    longest_path_length = path_lengths.get(longest_path, 0) if longest_path else 0

    full_session_ids = list(_nested_values(checkpoint_plus_payload, "session_id"))
    checks = {
        "simulated_runtime_base_matches_physical_length": len(str(runtime_base)) >= TARGET_WINDOWS_RUNTIME_BASE_LENGTH,
        "legacy_projection_reproduces_windows_boundary": len(str(legacy_projected_sessions_path)) >= 248,
        "cycle_completed": payload.get("halted") is False and bool(payload.get("run_id")),
        "final_receipt_written": Path(payload["log_path"]).is_file(),
        "runtime_checkpoint_written": Path(payload["checkpoint_path"]).is_file(),
        "return_host_checkpoint_only_written": Path(str(checkpoint_only.get("checkpoint_path", ""))).is_file(),
        "return_host_checkpoint_plus_host_written": Path(str(checkpoint_plus_host.get("checkpoint_path", ""))).is_file(),
        "checkpoint_plus_host_resolved": checkpoint_plus_payload.get("return_strategy") == "checkpoint_plus_host",
        "storage_root_compacted": storage.get("storage_root_compacted") is True,
        "storage_root_is_bounded": storage_base_dir.is_dir() and len(str(storage_base_dir)) < len(str(legacy_projected_sessions_path)),
        "all_recorded_paths_exist": not missing_paths,
        "all_written_paths_within_budget": longest_path_length <= PATH_BUDGET,
        "full_session_identifier_preserved_in_payload": any(isinstance(value, str) and len(value) == 36 for value in full_session_ids),
        "governance_reached_checkpoint": payload.get("governance_chain_status", {}).get("valid") is True,
    }

    summary = {
        "suite": "Windows Return / Host Path Budget Sea Trial R1",
        "passed": all(checks.values()),
        "path_budget": PATH_BUDGET,
        "simulated_runtime_base": str(runtime_base),
        "simulated_runtime_base_length": len(str(runtime_base)),
        "legacy_projected_sessions_path": str(legacy_projected_sessions_path),
        "legacy_projected_sessions_path_length": len(str(legacy_projected_sessions_path)),
        "storage_base_dir": str(storage_base_dir),
        "storage_base_dir_length": len(str(storage_base_dir)),
        "longest_written_path": longest_path,
        "longest_written_path_length": longest_path_length,
        "missing_paths": missing_paths,
        "checks": checks,
        "run_id": payload.get("run_id"),
        "governance_log_path": payload.get("governance_log_path"),
    }

    report_path = test_root / "sea_trials_windows_return_host_path_budget_r1_report.json"
    report_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if not summary["passed"]:
        raise SystemExit(json.dumps(summary, indent=2))

    return {"summary_path": str(report_path), "summary": summary}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
