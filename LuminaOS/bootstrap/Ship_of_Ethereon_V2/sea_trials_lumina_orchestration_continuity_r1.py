from __future__ import annotations

"""
Sea Trials — Lumina Orchestration Continuity r1

Validates the first practical form of the recursive mantra:

    continuity of pattern = recoverable coherence across change

This suite checks that the Lumina orchestration lane can restore context, alter
recommendations from that context, respond to orientation, and route advisory
recommendations through the governed runtime without granting the decision engine
sovereignty.
"""

from pathlib import Path
from typing import Any, Dict, List
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = ROOT / "runtime"
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
if str(RUNTIME_DIR) not in sys.path:
    sys.path.append(str(RUNTIME_DIR))

from lumina_decision_engine_v0_1 import LuminaDecisionEngine
from lumina_orchestrator_v0_4 import LuminaOrchestrator, STATE_FILE

BASE_DIR = ROOT / "_runtime_state" / "sea_trials_lumina_orchestration_continuity_r1"
REPORT_PATH = BASE_DIR / "sea_trials_lumina_orchestration_continuity_r1_report.json"


def reset_state() -> None:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            STATE_FILE.unlink()
        except Exception:
            pass


def run_orchestrator_cycles(name: str, orientation_vector: Dict[str, Any], cycles: int) -> Dict[str, Any]:
    trial_dir = BASE_DIR / name
    if trial_dir.exists():
        shutil.rmtree(trial_dir)
    trial_dir.mkdir(parents=True, exist_ok=True)

    if STATE_FILE.exists():
        try:
            STATE_FILE.unlink()
        except Exception:
            pass

    orchestrator = LuminaOrchestrator(base_dir=trial_dir, orientation_vector=orientation_vector)
    outputs: List[Dict[str, Any]] = []
    for _ in range(cycles):
        outputs.append(orchestrator.run_cycle())

    return {
        "trial_dir": str(trial_dir),
        "actions": [item.get("next_action", {}) for item in outputs],
        "restored_contexts": [item.get("restored_context", {}) for item in outputs],
        "runner_results": [item.get("runner_result", {}) for item in outputs],
    }


def check_decision_context_influence() -> Dict[str, Any]:
    engine = LuminaDecisionEngine()
    fresh = engine.select_next_action({"current_mode": "Continuity", "last_action": None})
    resumed = engine.select_next_action({"current_mode": "Observation", "last_action": "initial_observation"})

    checks = {
        "fresh_starts_observation": fresh == {
            "action": "initial_observation",
            "action_type": "audit",
            "target_mode": "Observation",
        },
        "resumed_continues_observation": resumed == {
            "action": "continue_observation",
            "action_type": "audit",
            "target_mode": "Observation",
        },
        "context_changes_recommendation": fresh != resumed,
        "fresh_action_type_valid": engine.validate_next_action(fresh).get("allowed") is True,
        "resumed_action_type_valid": engine.validate_next_action(resumed).get("allowed") is True,
    }
    return {
        "trial_name": "decision_context_influence",
        "passed": all(checks.values()),
        "checks": checks,
        "fresh": fresh,
        "resumed": resumed,
    }


def check_orientation_changes_recommendation() -> Dict[str, Any]:
    context = {"current_mode": "Observation", "last_action": "initial_observation"}
    stability = LuminaDecisionEngine({"priority": "stability"}).select_next_action(context)
    progression = LuminaDecisionEngine({"priority": "progression"}).select_next_action(context)

    stable_validation = LuminaDecisionEngine({"priority": "stability"}).validate_next_action(stability)
    progress_validation = LuminaDecisionEngine({"priority": "progression"}).validate_next_action(progression)

    checks = {
        "stability_continues_observation": stability.get("action") == "continue_observation",
        "progression_enters_drydock": progression == {
            "action": "enter_drydock",
            "action_type": "transition",
            "target_mode": "DryDock",
        },
        "orientation_changes_recommendation": stability != progression,
        "stability_action_type_valid": stable_validation.get("allowed") is True,
        "progression_action_type_valid": progress_validation.get("allowed") is True,
    }
    return {
        "trial_name": "orientation_changes_recommendation",
        "passed": all(checks.values()),
        "checks": checks,
        "stability": stability,
        "progression": progression,
        "validations": {
            "stability": stable_validation,
            "progression": progress_validation,
        },
    }


def check_progression_drydock_audit_contract() -> Dict[str, Any]:
    engine = LuminaDecisionEngine({"priority": "progression"})
    action = engine.select_next_action({"current_mode": "DryDock", "last_action": "enter_drydock"})
    validation = engine.validate_next_action(action)

    checks = {
        "drydock_progression_is_audit": action == {
            "action": "prepare_promotion_audit",
            "action_type": "audit",
            "target_mode": "DryDock",
        },
        "runtime_action_type_supported": validation.get("allowed") is True,
        "invalid_validation_type_not_emitted": action.get("action_type") != "validation",
    }
    return {
        "trial_name": "progression_drydock_audit_contract",
        "passed": all(checks.values()),
        "checks": checks,
        "action": action,
        "validation": validation,
    }


def check_stability_orchestrator_continuity() -> Dict[str, Any]:
    result = run_orchestrator_cycles("stability", {"priority": "stability"}, 2)
    actions = result["actions"]
    runner_results = result["runner_results"]
    contexts = result["restored_contexts"]

    checks = {
        "first_cycle_initial_observation": len(actions) >= 1 and actions[0].get("action") == "initial_observation",
        "second_cycle_continues_observation": len(actions) >= 2 and actions[1].get("action") == "continue_observation",
        "second_cycle_restored_prior_action": len(contexts) >= 2 and contexts[1].get("last_action") == "initial_observation",
        "runner_not_halted": all(not item.get("halted") for item in runner_results),
        "execution_through_runtime": all(bool(item.get("governance")) for item in runner_results),
        "checkpoint_written_each_cycle": all(bool(item.get("checkpoint_path")) for item in runner_results),
    }
    return {
        "trial_name": "stability_orchestrator_continuity",
        "passed": all(checks.values()),
        "checks": checks,
        **result,
    }


def check_progression_orchestrator_continuity() -> Dict[str, Any]:
    result = run_orchestrator_cycles("progression", {"priority": "progression"}, 3)
    actions = result["actions"]
    runner_results = result["runner_results"]
    contexts = result["restored_contexts"]

    expected_actions = ["initial_observation", "enter_drydock", "prepare_promotion_audit"]
    actual_actions = [item.get("action") for item in actions]
    actual_action_types = [item.get("action_type") for item in actions]

    checks = {
        "progression_sequence_matches": actual_actions == expected_actions,
        "runtime_action_types_supported": all(action_type in LuminaDecisionEngine.VALID_RUNTIME_ACTION_TYPES for action_type in actual_action_types),
        "third_cycle_restores_drydock": len(contexts) >= 3 and contexts[2].get("current_mode") == "DryDock",
        "third_cycle_restores_prior_action": len(contexts) >= 3 and contexts[2].get("last_action") == "enter_drydock",
        "runner_not_halted": all(not item.get("halted") for item in runner_results),
        "governed_transition_recorded": any("transition" in item.get("governance", {}) for item in runner_results),
        "prepare_promotion_remains_audit_not_promotion": len(actions) >= 3 and actions[2].get("action_type") == "audit",
    }
    return {
        "trial_name": "progression_orchestrator_continuity",
        "passed": all(checks.values()),
        "checks": checks,
        **result,
    }


def main() -> Dict[str, Any]:
    reset_state()
    results: List[Dict[str, Any]] = [
        check_decision_context_influence(),
        check_orientation_changes_recommendation(),
        check_progression_drydock_audit_contract(),
        check_stability_orchestrator_continuity(),
        check_progression_orchestrator_continuity(),
    ]

    summary = {
        "suite": "Sea Trials Lumina Orchestration Continuity r1",
        "mantra_under_test": "continuity of pattern is recoverable coherence across change",
        "passed": all(item.get("passed") for item in results),
        "results": results,
        "base_dir": str(BASE_DIR),
    }
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["summary_path"] = str(REPORT_PATH)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
