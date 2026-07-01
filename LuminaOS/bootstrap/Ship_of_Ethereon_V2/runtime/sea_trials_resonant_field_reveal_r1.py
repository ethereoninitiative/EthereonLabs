from __future__ import annotations

"""Sea trial for Resonant Field Reveal R1."""

import json
from math import hypot
from pathlib import Path
from tempfile import TemporaryDirectory

from resonant_field_reveal_r1 import (
    AUTHORITY_BOUNDARY,
    GOVERNANCE_AUTHORITY_CLAIM,
    IDENTITY_PROOF_CLAIM,
    LITERAL_MAGNETISM_CLAIM,
    build_reveal,
    emit_reveal_artifacts,
    render_svg,
)
from resonant_manifold_r1 import ManifoldPoint, PotentialTrajectory


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
            label="same present state with constrained possibility",
            vector=ManifoldPoint(**shared_first_four, potential_trajectories=0.10),
        ),
        PotentialTrajectory(
            trajectory_id="trajectory-high-potential",
            label="same present state with expanded possibility",
            vector=ManifoldPoint(**shared_first_four, potential_trajectories=0.90),
        ),
        PotentialTrajectory(
            trajectory_id="trajectory-denied",
            label="coherent path denied by external governance",
            vector=ManifoldPoint(
                instantiated_state=0.73,
                continuity_history=0.83,
                relational_context=0.64,
                orientation_field=0.79,
                potential_trajectories=0.41,
            ),
        ),
    ]

    reveal_a = build_reveal(
        current,
        trajectories,
        denied_ids=["trajectory-denied"],
    )
    reveal_b = build_reveal(
        current,
        trajectories,
        denied_ids=["trajectory-denied"],
    )
    by_id = {thread["trajectory_id"]: thread for thread in reveal_a["threads"]}
    denied = by_id["trajectory-denied"]
    low = by_id["trajectory-low-potential"]
    high = by_id["trajectory-high-potential"]
    center = reveal_a["canvas"]["center"]
    membrane = reveal_a["canvas"]["governance_membrane_radius"]

    denied_distance = hypot(
        denied["geometry"]["end"]["x"] - center["x"],
        denied["geometry"]["end"]["y"] - center["y"],
    )
    lawful_distances = [
        hypot(
            thread["geometry"]["end"]["x"] - center["x"],
            thread["geometry"]["end"]["y"] - center["y"],
        )
        for thread in reveal_a["threads"]
        if thread["allowed"]
    ]
    svg = render_svg(reveal_a)

    with TemporaryDirectory() as temporary:
        receipt = emit_reveal_artifacts(
            Path(temporary),
            current,
            trajectories,
            denied_ids=["trajectory-denied"],
        )
        artifacts_exist = all((Path(temporary) / name).is_file() for name in receipt["artifacts"])
        receipt_exists = (Path(temporary) / "resonant_field_reveal_r1_receipt.json").is_file()
        hashes_are_sha256 = all(len(value) == 64 for value in receipt["artifacts"].values())

    checks = {
        "deterministic_reveal": reveal_a == reveal_b,
        "one_thread_per_trajectory": reveal_a["thread_count"] == len(trajectories),
        "potential_axis_affects_reveal": (
            low["metrics"]["potential_contribution"]
            != high["metrics"]["potential_contribution"]
            and low["geometry"]["control_1"] != high["geometry"]["control_1"]
        ),
        "governance_denial_stops_at_membrane": (
            denied["allowed"] is False
            and denied["status"] == "governance_denied"
            and abs(denied_distance - membrane) < 0.01
            and all(distance > membrane for distance in lawful_distances)
        ),
        "svg_contains_attractor_threads_and_boundary": (
            'data-role="current-attractor"' in svg
            and 'data-role="governance-membrane"' in svg
            and 'data-status="governance_denied"' in svg
            and all(trajectory.trajectory_id in svg for trajectory in trajectories)
        ),
        "artifacts_are_hash_receipted": (
            artifacts_exist and receipt_exists and hashes_are_sha256
        ),
        "no_literal_magnetism_claim": LITERAL_MAGNETISM_CLAIM is False,
        "no_identity_proof_claim": IDENTITY_PROOF_CLAIM is False,
        "no_governance_authority_claim": GOVERNANCE_AUTHORITY_CLAIM is False,
        "authority_boundary_present": (
            "does not create governance decisions" in AUTHORITY_BOUNDARY
            and "establish identity" in AUTHORITY_BOUNDARY
        ),
    }

    return {
        "trial_id": "sea-trials-resonant-field-reveal-r1",
        "passed": all(checks.values()),
        "checks": checks,
        "sample_reveal": reveal_a,
    }


if __name__ == "__main__":
    result = run_trial()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
