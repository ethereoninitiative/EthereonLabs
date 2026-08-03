from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict
import json
import tempfile

try:
    from .runtime_ui_snapshot_emitter_r1 import (
        public_snapshot_semantically_changed,
        runtime_snapshot_semantic_fingerprint,
        snapshot_write_plan,
        write_snapshot,
    )
except Exception:
    from runtime_ui_snapshot_emitter_r1 import (
        public_snapshot_semantically_changed,
        runtime_snapshot_semantic_fingerprint,
        snapshot_write_plan,
        write_snapshot,
    )


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
        report = {
            "suite": "Runtime Memory Ledger Semantic Idempotence R1",
            "passed": all(checks.values()),
            "checks": checks,
            "semantic_fingerprint": unchanged_plan["semantic_fingerprint"],
            "authority_boundary": (
                "This trial validates observation-write selection only. It does not alter governance, "
                "canon, mode legality, capability authority, or primary continuity truth."
            ),
        }
        print(json.dumps(report, indent=2))
        return report


if __name__ == "__main__":
    main()
