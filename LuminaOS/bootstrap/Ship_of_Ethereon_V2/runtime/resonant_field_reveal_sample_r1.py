from __future__ import annotations

"""Committed sample generator for Resonant Field Reveal R1."""

import json
from pathlib import Path

from resonant_field_reveal_r1 import emit_reveal_artifacts
from resonant_manifold_r1 import ManifoldPoint, PotentialTrajectory

SAMPLE_ID = "resonant-field-reveal-sample-0001"
SAMPLE_DIR = Path(__file__).resolve().parents[1] / "artifacts" / "resonant_field_reveal" / "sample_0001"
INPUT_FILE = "resonant_field_reveal_r1_input.json"


def generate_sample(output_dir: Path = SAMPLE_DIR) -> dict:
    manifest = json.loads((SAMPLE_DIR / INPUT_FILE).read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / INPUT_FILE).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    current = ManifoldPoint(**manifest["current_point"])
    trajectories = [
        PotentialTrajectory(
            item["trajectory_id"],
            item["label"],
            ManifoldPoint(**item["vector"]),
        )
        for item in manifest["trajectories"]
    ]
    return emit_reveal_artifacts(
        output_dir,
        current,
        trajectories,
        denied_ids=manifest["denied_ids"],
        width=manifest["canvas"]["width"],
        height=manifest["canvas"]["height"],
    )


if __name__ == "__main__":
    print(json.dumps(generate_sample(), indent=2, sort_keys=True))
