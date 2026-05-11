from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .runtime.runtime_runner_reflective_self_guided_bridge_r1 import (
        ReflectiveSelfGuidedReturnHostRuntimeRunner,
    )
except Exception:
    try:
        from runtime.runtime_runner_reflective_self_guided_bridge_r1 import (
            ReflectiveSelfGuidedReturnHostRuntimeRunner,
        )
    except Exception:
        from runtime_runner_reflective_self_guided_bridge_r1 import (
            ReflectiveSelfGuidedReturnHostRuntimeRunner,
        )


BASE_DIR = Path(__file__).resolve().parent / "_sea_trials_state" / "lumina_reflective_autonomy_wiring_r1"

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}


def main() -> Dict[str, Any]:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    runner = ReflectiveSelfGuidedReturnHostRuntimeRunner(base_dir=BASE_DIR)
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="trial_reflection_before_self_guidance",
        action_type="audit",
        runtime_config=SAFE_RUNTIME_CONFIG,
        project_id="lumina-core",
    )
    payload = result.to_dict()
    gov = payload.get("governance", {})
    reflective = gov.get("reflective_autonomy_execution", {})
    guidance = gov.get("self_guidance_execution", {})

    checks = {
        "cycle_not_halted": payload.get("halted") is False,
        "reflection_trace_recorded": bool(reflective.get("trace_id")),
        "reflection_has_six_phases": reflective.get("phases") == [
            "perceive", "reflect", "recurse", "compare", "integrate", "emerge",
        ],
        "guidance_recorded": bool(guidance.get("recommended_next_action")),
        "guidance_references_reflection": guidance.get("reflective_autonomy_trace_id") == reflective.get("trace_id"),
        "reflection_before_guidance_in_receipt": "reflective_autonomy_execution" in gov and "self_guidance_execution" in gov,
    }

    report = {
        "suite": "Sea Trials - Lumina Reflective Autonomy Wiring r1",
        "passed": all(checks.values()),
        "checks": checks,
        "reflective_autonomy_execution": reflective,
        "self_guidance_execution": guidance,
        "boundary": "Reflection is recorded before self-guidance; existing runtime still governs execution.",
    }
    report_path = BASE_DIR / "sea_trials_lumina_reflective_autonomy_wiring_r1_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return {"summary_path": str(report_path), "summary": report}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
