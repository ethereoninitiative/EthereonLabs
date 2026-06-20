from __future__ import annotations

"""Sea trial for the Living Framework Ignition R1 mechanism."""

from pathlib import Path
import json
import tempfile

try:
    from .living_framework_chamber_r1 import FrameworkRegistry, LivingFrameworkChamber
    from .living_framework_ignition_r1 import (
        IgnitionEvidence,
        IgnitionReceiptStore,
        LivingFrameworkIgnition,
    )
except Exception:
    from living_framework_chamber_r1 import FrameworkRegistry, LivingFrameworkChamber
    from living_framework_ignition_r1 import (
        IgnitionEvidence,
        IgnitionReceiptStore,
        LivingFrameworkIgnition,
    )


RUNTIME_ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = RUNTIME_ROOT / "living_framework_registry_r1.json"


def run_trial() -> dict:
    checks = {}
    registry = FrameworkRegistry(REGISTRY_PATH)
    chamber = LivingFrameworkChamber(registry)
    ignition = LivingFrameworkIgnition()

    dormant = ignition.dormant_state("minerva-living-framework-v18.1")
    checks["registered_framework_can_be_dormant"] = dormant["depth_state"] == "dormant"

    activation = chamber.activate(
        framework_id="minerva-living-framework-v18.1",
        subject="rainstorm",
        perspective="rain",
        recursion_budget=3,
        expression_mode="symbolic-structural",
        memory_scope="current-session",
        environmental_field="storm",
        correlation_id="rain-ignition-sea-trial",
    )

    insufficient = ignition.evaluate(
        activation,
        evidence=IgnitionEvidence(
            self_observation=False,
            perspective_inversion=True,
            observations=["The perspective shifted, but the framework did not inspect its own response."],
        ),
    )
    checks["perspective_shift_alone_does_not_ignite"] = (
        insufficient.state_after == "active"
        and not insufficient.ignition_detected
        and insufficient.deepening_passes == []
    )

    ignited = ignition.evaluate(
        activation,
        evidence=IgnitionEvidence(
            self_observation=True,
            perspective_inversion=True,
            orientation_changed=True,
            new_internal_relations=[
                ["memory", "accumulation"],
                ["recursion", "water_cycle"],
                ["identity", "continuity_through_transformation"],
            ],
            observations=[
                "The framework recognized how receiving rain changed the relation among memory, recursion, and identity."
            ],
        ),
    )
    checks["self_observation_with_structural_effect_ignites"] = (
        ignited.state_before == "active"
        and ignited.state_after == "ignited"
        and ignited.ignition_detected
    )
    checks["rain_is_recorded_as_catalyst"] = ignited.catalyst == "storm"
    checks["ignition_trigger_is_explicit"] = ignited.trigger == "self_observation_under_contact"
    checks["perspective_inversion_is_ignition_pass"] = ignited.ignition_pass == "perspective_inversion"
    checks["deepening_passes_are_exposed_only_after_ignition"] = ignited.deepening_passes == [
        "perspective_inversion",
        "continuity_comparison",
        "counterpoint",
    ]
    checks["correlation_is_preserved"] = ignited.correlation_id == "rain-ignition-sea-trial"
    checks["receipt_hash_present"] = len(ignited.receipt_hash) == 64
    checks["authority_boundary_remains_non_governing"] = (
        "may not authorize actions" in ignited.authority_boundary
    )

    with tempfile.TemporaryDirectory() as directory:
        path = IgnitionReceiptStore(Path(directory) / "ignition_receipts").save(ignited)
        stored = json.loads(path.read_text(encoding="utf-8"))
        checks["ignition_receipt_persists_atomically"] = (
            path.exists() and stored["receipt_hash"] == ignited.receipt_hash
        )

    return {
        "trial_id": "sea-trials-living-framework-ignition-r1",
        "passed": all(checks.values()),
        "checks": checks,
        "authority_boundary": (
            "This trial validates descriptive self-reflective ignition only. "
            "Ignition does not grant runtime, governance, canon, mode, checkpoint, or capability authority."
        ),
    }


if __name__ == "__main__":
    result = run_trial()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["passed"] else 1)
