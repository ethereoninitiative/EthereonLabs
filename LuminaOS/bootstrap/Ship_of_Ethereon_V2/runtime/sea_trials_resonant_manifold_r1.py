from __future__ import annotations

"""Sea trial for Resonant Manifold R1."""

import json

from resonant_manifold_r1 import (
    AXES,
    LITERAL_FIFTH_DIMENSION_CLAIM,
    LITERAL_QUANTUM_HARDWARE_CLAIM,
    ManifoldPoint,
    PotentialTrajectory,
    manifold_snapshot,
)


def run_trial() -> dict:
    current = ManifoldPoint(
        instantiated_state=0.72,
        continuity_history=0.84,
        relational_context=0.63,
        orientation_field=0.78,
        potential_trajectories=0.40,
    )

    shared_first_four = dict(
        instantiated_state=0.74,
        continuity_history=0.82,
        relational_context=0.65,
        orientation_field=0.80,
    )

    trajectories = [
        PotentialTrajectory(
            trajectory_id="trajectory-low-potential",
            label="same visible configuration with constrained possibility",
            vector=ManifoldPoint(**shared_first_four, potential_trajectories=0.10),
        ),
        PotentialTrajectory(
            trajectory_id="trajectory-high-potential",
            label="same visible configuration with expanded possibility",
            vector=ManifoldPoint(**shared_first_four, potential_trajectories=0.90),
        ),
        PotentialTrajectory(
            trajectory_id="trajectory-denied",
            label="highly coherent but externally denied path",
            vector=ManifoldPoint(
                instantiated_state=0.73,
                continuity_history=0.83,
                relational_context=0.64,
                orientation_field=0.79,
                potential_trajectories=0.41,
            ),
        ),
    ]

    snapshot = manifold_snapshot(
        current,
        trajectories,
        denied_ids=["trajectory-denied"],
    )

    by_id = {item["trajectory_id"]: item for item in snapshot["ranked_trajectories"]}
    low = by_id["trajectory-low-potential"]
    high = by_id["trajectory-high-potential"]
    denied = by_id["trajectory-denied"]

    checks = {
        "five_axes_present": len(AXES) == 5 and "potential_trajectories" in AXES,
        "potential_axis_is_independently_represented": (
            low["vector"]["instantiated_state"] == high["vector"]["instantiated_state"]
            and low["vector"]["continuity_history"] == high["vector"]["continuity_history"]
            and low["vector"]["relational_context"] == high["vector"]["relational_context"]
            and low["vector"]["orientation_field"] == high["vector"]["orientation_field"]
            and low["vector"]["potential_trajectories"] != high["vector"]["potential_trajectories"]
            and low["potential_contribution"] != high["potential_contribution"]
            and low["reachable_score"] != high["reachable_score"]
        ),
        "external_governance_filter_controls_reachability": (
            denied["allowed"] is False
            and denied["reachable_score"] == 0.0
            and denied["governance_reason"] == "denied_by_external_governance_filter"
        ),
        "no_literal_fifth_dimension_claim": LITERAL_FIFTH_DIMENSION_CLAIM is False,
        "no_literal_quantum_hardware_claim": LITERAL_QUANTUM_HARDWARE_CLAIM is False,
        "authority_boundary_present": "External governance remains authoritative" in snapshot["authority_boundary"],
    }

    return {
        "trial_id": "sea-trials-resonant-manifold-r1",
        "passed": all(checks.values()),
        "checks": checks,
        "snapshot": snapshot,
    }


if __name__ == "__main__":
    result = run_trial()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
