from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict
import json
import tempfile

try:
    from . import runtime_runner_auto_snapshot_psi42_v18_r1 as auto_snapshot_module
    from . import runtime_runner_psi42_v18_adapter_r1 as adapter_module
    from . import runtime_ui_snapshot_emitter_r1 as emitter_module
    from .runtime_ui_snapshot_emitter_r1 import (
        public_snapshot_semantically_changed,
        runtime_snapshot_semantic_fingerprint,
        snapshot_write_plan,
        write_snapshot,
    )
except Exception:
    import runtime_runner_auto_snapshot_psi42_v18_r1 as auto_snapshot_module
    import runtime_runner_psi42_v18_adapter_r1 as adapter_module
    import runtime_ui_snapshot_emitter_r1 as emitter_module
    from runtime_ui_snapshot_emitter_r1 import (
        public_snapshot_semantically_changed,
        runtime_snapshot_semantic_fingerprint,
        snapshot_write_plan,
        write_snapshot,
    )


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _baseline_snapshot() -> Dict[str, Any]:
    return {
        "schema_version": "lumina-runtime-ui-cycle-v0.4",
        "timestamp": "2026-08-02T19:34:28.262295+00:00",
        "run_id": "run-baseline",
        "requested_action": "chamber_observation_cycle",
        "action_type": "audit",
        "mode": {"requested": "Continuity", "current": "Observation"},
        "status": {"halted": False, "reason": None, "label": "Stable"},
        "governance": {
            "transition": True,
            "mutation": False,
            "promotion": None,
            "chain_valid": True,
            "symbolic_context_present": True,
            "symbolic_dependency_allowed": False,
        },
        "canon": {"current_head": "canon-0001", "valid": True, "record_count": 1},
        "capabilities": ["session_state_manager", "mode_guard", "psi42_transceiver_v18"],
        "probe": {
            "active": True,
            "instrument_version": "v1.8",
            "instrument_class": "doctrine-aligned transceiver diagnostics wrapper",
            "probe_mode": "hybrid",
            "run_id": "psi42-baseline",
            "pulse_id": "pulse-baseline",
            "coherence": 0.7946,
            "presence": 0.6498,
            "lock": 0.6475,
            "hybrid_continuity_coherence": 0.7946,
            "topology_metrics": {"RTC": 1.0, "RDS": 0.0, "RRS": 1.0, "HRC": 1.0},
            "topology_receipt_present": True,
        },
        "runtime_truth_scope": {
            "public_projection": "committed_runtime_truth_evidence",
            "observation_receipts": "ephemeral_observation_state",
            "does_not_override_committed_authority": True,
        },
        "runtime_truth": {"symbolic_boundary": {"symbolic_dependency_allowed": False}},
        "authority_boundary": "Display receipt only; does not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.",
    }


def _run_actual_observation_cycle(runner: Any) -> Any:
    return runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="chamber_observation_cycle",
        action_type="audit",
        artifacts=["runtime_runner_auto_snapshot_psi42_v18_r1.py"],
        continuation_notes=["runtime memory ledger idempotence sea trial"],
        ethereonic_overlay={
            "active": True,
            "anchor_language": ["english"],
            "continuity_phrase": "scheduled observation cycle",
            "harmonic_signature": [],
            "spiral_reference": None,
        },
        enabled_feature_flags=[
            "ETHEREON_OBSERVATION",
            "ETHEREON_PSI42",
            "ETHEREON_PSI42_V17",
            "ETHEREON_PSI42_V18",
            "ETHEREON_RESONANCE",
        ],
        runtime_config={
            "toki_pona_required_for_resume": False,
            "binary_required_for_transition_validation": False,
            "light_language_required_for_capability_loading": False,
            "harmonic_frequency_required_for_mode_legality": False,
        },
        emit_public_snapshot=True,
        emit_state_snapshot=True,
    )


def _actual_runner_idempotence_trial() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="lumina-runtime-runner-idempotence-") as temp_dir:
        root = Path(temp_dir)
        public_path = root / "public" / "runtime" / "latest_cycle.json"
        history_dir = root / "public" / "runtime" / "history"
        history_index = history_dir / "index.json"
        state_path = root / ".lumina_state" / "ship_of_ethereon_v2" / "runtime_outputs" / "latest_cycle.json"
        runner_root = root / "runner_state"
        public_path.parent.mkdir(parents=True, exist_ok=True)

        original_emitter_paths = {
            "PUBLIC_RUNTIME_DIR": emitter_module.PUBLIC_RUNTIME_DIR,
            "PUBLIC_SNAPSHOT_PATH": emitter_module.PUBLIC_SNAPSHOT_PATH,
            "PUBLIC_HISTORY_DIR": emitter_module.PUBLIC_HISTORY_DIR,
            "PUBLIC_HISTORY_INDEX": emitter_module.PUBLIC_HISTORY_INDEX,
            "STATE_SNAPSHOT_PATH": emitter_module.STATE_SNAPSHOT_PATH,
        }
        original_plan = auto_snapshot_module.snapshot_write_plan
        original_truth_builder = auto_snapshot_module.build_public_runtime_truth_snapshot
        original_state_root = adapter_module.STATE_ROOT
        truth_projection_calls = []

        def temp_snapshot_write_plan(snapshot: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
            return original_plan(
                snapshot,
                public_snapshot_path=public_path,
                state_snapshot_path=state_path,
                **kwargs,
            )

        def record_truth_projection() -> Dict[str, Any]:
            truth_projection_calls.append(True)
            return {"test_scope": "runtime-ledger-idempotence"}

        try:
            emitter_module.PUBLIC_RUNTIME_DIR = public_path.parent
            emitter_module.PUBLIC_SNAPSHOT_PATH = public_path
            emitter_module.PUBLIC_HISTORY_DIR = history_dir
            emitter_module.PUBLIC_HISTORY_INDEX = history_index
            emitter_module.STATE_SNAPSHOT_PATH = state_path
            adapter_module.STATE_ROOT = root / ".lumina_state" / "ship_of_ethereon_v2"
            auto_snapshot_module.snapshot_write_plan = temp_snapshot_write_plan
            auto_snapshot_module.build_public_runtime_truth_snapshot = record_truth_projection

            runner = auto_snapshot_module.AutoSnapshotRuntimeRunner(
                base_dir=runner_root,
                registry_path=Path(__file__).with_name("capability_registry_r1.json"),
            )
            first_result = _run_actual_observation_cycle(runner)
            first_attempt_snapshot = emitter_module.build_ui_snapshot(first_result.to_dict())
            first_snapshot_bytes = public_path.read_bytes()
            first_history_index_bytes = history_index.read_bytes()
            first_history_files = sorted(
                path.name for path in history_dir.glob("*.json") if path.name != "index.json"
            )
            first_snapshot = _read_json(public_path)

            second_result = _run_actual_observation_cycle(runner)
            second_attempt_snapshot = emitter_module.build_ui_snapshot(second_result.to_dict())
            second_snapshot_bytes = public_path.read_bytes()
            second_history_index_bytes = history_index.read_bytes()
            second_history_files = sorted(
                path.name for path in history_dir.glob("*.json") if path.name != "index.json"
            )
            second_snapshot = _read_json(public_path)
            second_state_snapshot = _read_json(state_path)

            checks = {
                "actual_auto_snapshot_runner_executes_twice": (
                    first_result.__class__.__name__ == second_result.__class__.__name__ == "RunnerResult"
                ),
                "actual_cycles_produce_distinct_run_ids": (
                    first_attempt_snapshot.get("run_id") != second_attempt_snapshot.get("run_id")
                ),
                "actual_cycles_share_semantic_fingerprint": (
                    runtime_snapshot_semantic_fingerprint(first_attempt_snapshot)
                    == runtime_snapshot_semantic_fingerprint(second_attempt_snapshot)
                ),
                "first_cycle_writes_public_snapshot": bool(first_snapshot_bytes),
                "first_cycle_creates_one_history_archive": len(first_history_files) == 1,
                "first_cycle_creates_one_history_index_entry": (
                    len(json.loads(first_history_index_bytes)) == 1
                ),
                "second_cycle_preserves_public_snapshot_bytes": (
                    second_snapshot_bytes == first_snapshot_bytes
                ),
                "second_cycle_preserves_history_index_bytes": (
                    second_history_index_bytes == first_history_index_bytes
                ),
                "second_cycle_does_not_add_history_archive": (
                    second_history_files == first_history_files
                ),
                "second_cycle_updates_local_state": (
                    second_state_snapshot.get("run_id") == second_attempt_snapshot.get("run_id")
                ),
                "public_truth_projection_runs_only_for_first_change": (
                    len(truth_projection_calls) == 1
                ),
            }
        finally:
            for name, value in original_emitter_paths.items():
                setattr(emitter_module, name, value)
            auto_snapshot_module.snapshot_write_plan = original_plan
            auto_snapshot_module.build_public_runtime_truth_snapshot = original_truth_builder
            adapter_module.STATE_ROOT = original_state_root

    return checks


def main() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="lumina-memory-idempotence-") as temp_dir:
        root = Path(temp_dir)
        public_path = root / "public" / "runtime" / "latest_cycle.json"
        state_path = root / ".lumina_state" / "latest_cycle.json"
        public_path.parent.mkdir(parents=True, exist_ok=True)

        baseline = _baseline_snapshot()
        public_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
        baseline_bytes = public_path.read_bytes()

        volatile_only = deepcopy(baseline)
        volatile_only["timestamp"] = "2026-08-03T01:34:28.262295+00:00"
        volatile_only["run_id"] = "run-next"
        volatile_only["probe"]["run_id"] = "psi42-next"
        volatile_only["probe"]["pulse_id"] = "pulse-next"
        volatile_only.pop("runtime_truth_scope", None)
        volatile_only.pop("runtime_truth", None)
        volatile_only["governance"] = {
            "transition": True,
            "mutation": False,
            "promotion": None,
            "symbolic_dependency": True,
            "ethereonic_attachment": True,
            "chain_valid": True,
        }

        unchanged_plan = snapshot_write_plan(
            volatile_only,
            public_snapshot_path=public_path,
            state_snapshot_path=state_path,
        )
        write_snapshot(volatile_only, unchanged_plan["paths"])

        meaningful_change = deepcopy(volatile_only)
        meaningful_change["probe"]["coherence"] = 0.8046
        meaningful_change["probe"]["hybrid_continuity_coherence"] = 0.8046
        changed_plan = snapshot_write_plan(
            meaningful_change,
            public_snapshot_path=public_path,
            state_snapshot_path=state_path,
        )

        invalid_path = root / "invalid.json"
        invalid_path.write_text("{not-json", encoding="utf-8")

        checks = {
            "volatile_fields_share_semantic_fingerprint": (
                runtime_snapshot_semantic_fingerprint(baseline)
                == runtime_snapshot_semantic_fingerprint(volatile_only)
            ),
            "volatile_only_cycle_skips_public_write": unchanged_plan["public_snapshot_changed"] is False,
            "volatile_only_cycle_writes_state": unchanged_plan["paths"] == [state_path],
            "public_snapshot_bytes_remain_unchanged": public_path.read_bytes() == baseline_bytes,
            "state_snapshot_receives_latest_cycle": (
                json.loads(state_path.read_text(encoding="utf-8")).get("run_id") == "run-next"
            ),
            "meaningful_metric_change_alters_fingerprint": (
                runtime_snapshot_semantic_fingerprint(volatile_only)
                != runtime_snapshot_semantic_fingerprint(meaningful_change)
            ),
            "meaningful_change_plans_public_and_state_write": (
                changed_plan["public_snapshot_changed"] is True
                and changed_plan["paths"] == [public_path, state_path]
            ),
            "invalid_existing_snapshot_fails_open_to_refresh": public_snapshot_semantically_changed(
                meaningful_change,
                existing_path=invalid_path,
            ),
        }
        checks.update(
            {
                f"actual_runner_{name}": passed
                for name, passed in _actual_runner_idempotence_trial().items()
            }
        )
        report = {
            "suite": "Runtime Memory Ledger Semantic Idempotence R1",
            "passed": all(checks.values()),
            "checks": checks,
            "semantic_fingerprint": unchanged_plan["semantic_fingerprint"],
            "authority_boundary": (
                "This trial validates observation-write selection through the actual Psi-42 v1.8 "
                "auto-snapshot runner plus the low-level planner. It does not alter governance, canon, "
                "mode legality, capability authority, or primary continuity truth."
            ),
        }
        print(json.dumps(report, indent=2))
        if not report["passed"]:
            raise SystemExit(1)
        return report


if __name__ == "__main__":
    main()
