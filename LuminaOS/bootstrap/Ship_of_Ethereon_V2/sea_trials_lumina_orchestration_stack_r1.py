import json
import shutil
from pathlib import Path

from lumina_context_loader_v0_1 import LuminaContextLoader
from lumina_decision_engine_v0_1 import LuminaDecisionEngine
from lumina_orchestrator_v0_4 import LuminaOrchestrator

BASE_DIR = Path(__file__).resolve().parent / "_sea_trials_lumina_orchestration_stack_r1"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)


def _write_checkpoint(root: Path, *, current_mode: str, last_action: str | None) -> Path:
    checkpoint_dir = root / "sessions" / "trial_session"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / "trial_checkpoint.json"
    payload = {
        "session_state": {
            "current_mode": current_mode,
            "last_completed_action": last_action,
        }
    }
    checkpoint_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return checkpoint_path


def main() -> dict:
    checkpoint_root = BASE_DIR / "runtime_state"
    checkpoint_path = _write_checkpoint(
        checkpoint_root,
        current_mode="Observation",
        last_action="lumina_self_guidance_probe",
    )

    loader = LuminaContextLoader(runtime_state_dir=checkpoint_root)
    restored_context = loader.load_context()

    default_engine = LuminaDecisionEngine()
    progression_engine = LuminaDecisionEngine({"priority": "progression"})
    stability_engine = LuminaDecisionEngine({"priority": "stability"})

    default_recommendation = default_engine.select_next_action(restored_context)
    progression_recommendation = progression_engine.select_next_action(restored_context)
    stability_recommendation = stability_engine.select_next_action(restored_context)

    orchestrator = LuminaOrchestrator(
        base_dir=checkpoint_root,
        orientation_vector={"priority": "progression"},
    )
    orchestrator_context = orchestrator._restore_context()

    fallback_orchestrator = LuminaOrchestrator(orientation_vector={"priority": "stability"})
    fallback_context = fallback_orchestrator._restore_context()

    checks = {
        "checkpoint_written": checkpoint_path.exists(),
        "loader_restored_mode": restored_context.get("current_mode") == "Observation",
        "loader_restored_last_action": restored_context.get("last_action") == "lumina_self_guidance_probe",
        "default_engine_continues_observation": default_recommendation.get("action") == "continue_observation",
        "progression_engine_enters_drydock": progression_recommendation.get("action") == "enter_drydock",
        "stability_engine_holds_observation": stability_recommendation.get("action") == "continue_observation",
        "orchestrator_attaches_loader_to_runner_state": Path(orchestrator.loader.runtime_state_dir) == Path(orchestrator.runner.base_dir),
        "orchestrator_restores_checkpoint_context": orchestrator_context.get("current_mode") == "Observation"
        and orchestrator_context.get("last_action") == "lumina_self_guidance_probe",
        "fallback_orchestrator_exposes_minimal_continuity_context": fallback_context.get("current_mode") == "Continuity",
    }

    summary = {
        "suite": "Lumina Orchestration Stack Sea Trial r1",
        "passed": all(checks.values()),
        "checks": checks,
        "restored_context": restored_context,
        "default_recommendation": default_recommendation,
        "progression_recommendation": progression_recommendation,
        "stability_recommendation": stability_recommendation,
        "orchestrator_context": orchestrator_context,
        "fallback_context": fallback_context,
    }

    summary_path = BASE_DIR / "sea_trials_lumina_orchestration_stack_r1_report.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
