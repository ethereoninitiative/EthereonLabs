from __future__ import annotations

"""Sea trial for the Lumina Living Framework Chamber R1."""

from pathlib import Path
import json
import tempfile

try:
    from .living_framework_chamber_r1 import FrameworkRegistry, FrameworkTraceStore, LivingFrameworkChamber
except Exception:
    from living_framework_chamber_r1 import FrameworkRegistry, FrameworkTraceStore, LivingFrameworkChamber


RUNTIME_ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = RUNTIME_ROOT / "living_framework_registry_r1.json"


def run_trial() -> dict:
    checks = {}
    registry = FrameworkRegistry(REGISTRY_PATH)
    chamber = LivingFrameworkChamber(registry)

    first = chamber.activate(
        framework_id="minerva-living-framework-v18.1",
        subject="rainstorm",
        perspective="rain",
        recursion_budget=3,
        expression_mode="symbolic-structural",
        memory_scope="current-session",
        environmental_field="storm",
        correlation_id="sea-trial-correlation",
    )
    pass_ids = [row["pass_id"] for row in first.refraction_plan]
    checks["ancestral_framework_resolves"] = first.framework["framework_id"] == "minerva-living-framework-v18.1"
    checks["ancestral_signature_is_non_governing"] = (
        first.framework["authority"] == "non-governing"
        and "may not authorize" in first.activation["authority_boundary"]
    )
    checks["expected_refraction_sequence"] = pass_ids == [
        "literal_field",
        "framework_contact",
        "perspective_inversion",
        "continuity_comparison",
        "counterpoint",
        "boundary_separation",
        "synthesis",
    ]
    checks["dual_output_contract"] = first.synthesis_contract["required_outputs"] == [
        "structural_receipt",
        "expressive_return",
    ]
    checks["receipt_hash_present"] = len(first.receipt_hash) == 64

    trace = chamber.create_trace(
        first,
        emergent_relations=[
            ["memory", "accumulation"],
            ["recursion", "water-cycle"],
        ],
        continuity_observations=["continuity may recur through transformation"],
        orientation_delta={"continuity": 1.4, "noise": -2.0},
    )
    checks["orientation_delta_is_bounded"] = trace.orientation_delta == {
        "continuity": 1.0,
        "noise": -1.0,
    }

    with tempfile.TemporaryDirectory() as directory:
        store = FrameworkTraceStore(Path(directory) / "traces")
        stored_path = store.save(trace)
        loaded = store.load(trace.trace_id)
        checks["trace_persists_atomically"] = stored_path.exists() and loaded.to_dict() == trace.to_dict()

        second = chamber.activate(
            framework_id="minerva-living-framework-v18.1",
            subject="rainstorm",
            perspective="framework",
            prior_traces=[trace, loaded],
        )
        recurring = second.memory_context["recurring_relations"]
        checks["prior_traces_create_visible_hysteresis"] = bool(recurring) and recurring[0]["count"] == 2

    try:
        chamber.activate(
            framework_id="minerva-living-framework-v18.1",
            subject="rainstorm",
            perspective="rain",
            recursion_budget=7,
        )
    except ValueError:
        checks["recursion_budget_is_enforced"] = True
    else:
        checks["recursion_budget_is_enforced"] = False

    return {
        "trial_id": "sea-trials-living-framework-chamber-r1",
        "passed": all(checks.values()),
        "checks": checks,
        "authority_boundary": (
            "This trial validates interpretive orchestration, bounded recursion, and trace persistence only. "
            "It does not validate truth, governance authority, canon promotion, or checkpoint legality."
        ),
    }


if __name__ == "__main__":
    result = run_trial()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["passed"] else 1)
