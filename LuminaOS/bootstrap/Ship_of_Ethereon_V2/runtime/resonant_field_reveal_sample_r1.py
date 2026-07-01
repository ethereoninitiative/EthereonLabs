from __future__ import annotations

"""Committed sample generator for Resonant Field Reveal R1."""

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from resonant_field_reveal_r1 import AUTHORITY_BOUNDARY, emit_reveal_artifacts
from resonant_manifold_r1 import AXES, ManifoldPoint, PotentialTrajectory

SAMPLE_ID = "resonant-field-reveal-sample-0001"
SOURCE_MODEL_ID = "resonant-manifold-r1"
REVEAL_ID = "resonant-field-reveal-r1"
SAMPLE_DIR = Path(__file__).resolve().parents[1] / "artifacts" / "resonant_field_reveal" / "sample_0001"
INPUT_FILE = "resonant_field_reveal_r1_input.json"
REVEAL_JSON_FILE = "resonant_field_reveal_r1.json"
REVEAL_SVG_FILE = "resonant_field_reveal_r1.svg"
RECEIPT_FILE = "resonant_field_reveal_r1_receipt.json"
SAMPLE_FILES = (
    INPUT_FILE,
    REVEAL_JSON_FILE,
    REVEAL_SVG_FILE,
    RECEIPT_FILE,
)


def _validate_point(payload: Mapping[str, Any], field_name: str) -> None:
    if set(payload) != set(AXES):
        raise ValueError(f"{field_name} must contain exactly the five Resonant Manifold axes")
    for axis in AXES:
        value = payload[axis]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field_name}.{axis} must be numeric")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{field_name}.{axis} must be bounded from 0.0 through 1.0")


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    """Reject malformed fixtures before generating committed evidence."""
    if manifest.get("sample_id") != SAMPLE_ID:
        raise ValueError("unexpected sample_id")
    if manifest.get("source_model_id") != SOURCE_MODEL_ID:
        raise ValueError("unexpected source_model_id")
    if manifest.get("reveal_id") != REVEAL_ID:
        raise ValueError("unexpected reveal_id")

    canvas = manifest.get("canvas")
    if not isinstance(canvas, Mapping):
        raise ValueError("canvas must be an object")
    width = canvas.get("width")
    height = canvas.get("height")
    if not isinstance(width, int) or isinstance(width, bool) or width < 480:
        raise ValueError("canvas.width must be an integer of at least 480")
    if not isinstance(height, int) or isinstance(height, bool) or height < 360:
        raise ValueError("canvas.height must be an integer of at least 360")

    current = manifest.get("current_point")
    if not isinstance(current, Mapping):
        raise ValueError("current_point must be an object")
    _validate_point(current, "current_point")

    trajectories = manifest.get("trajectories")
    if not isinstance(trajectories, list) or not trajectories:
        raise ValueError("trajectories must be a non-empty list")

    ids = []
    for index, item in enumerate(trajectories):
        if not isinstance(item, Mapping):
            raise ValueError(f"trajectories[{index}] must be an object")
        trajectory_id = item.get("trajectory_id")
        label = item.get("label")
        vector = item.get("vector")
        if not isinstance(trajectory_id, str) or not trajectory_id.strip():
            raise ValueError(f"trajectories[{index}].trajectory_id must be non-empty")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"trajectories[{index}].label must be non-empty")
        if not isinstance(vector, Mapping):
            raise ValueError(f"trajectories[{index}].vector must be an object")
        _validate_point(vector, f"trajectories[{index}].vector")
        ids.append(trajectory_id)

    if len(ids) != len(set(ids)):
        raise ValueError("trajectory_id values must be unique")

    denied_ids = manifest.get("denied_ids")
    if not isinstance(denied_ids, list) or any(not isinstance(item, str) for item in denied_ids):
        raise ValueError("denied_ids must be a list of trajectory ids")
    if len(denied_ids) != len(set(denied_ids)):
        raise ValueError("denied_ids must be unique")
    unknown_denials = set(denied_ids) - set(ids)
    if unknown_denials:
        raise ValueError(f"denied_ids reference unknown trajectories: {sorted(unknown_denials)}")

    authority_note = manifest.get("authority_note", "")
    required_phrases = ("not runtime truth", "identity proof", "governance authority")
    if not isinstance(authority_note, str) or not all(phrase in authority_note for phrase in required_phrases):
        raise ValueError("authority_note must preserve the fixture authority boundary")


def generate_sample(output_dir: Path = SAMPLE_DIR) -> dict:
    manifest = json.loads((SAMPLE_DIR / INPUT_FILE).read_text(encoding="utf-8"))
    validate_manifest(manifest)
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / INPUT_FILE).write_text(manifest_text, encoding="utf-8")

    current = ManifoldPoint(**manifest["current_point"])
    trajectories = [
        PotentialTrajectory(
            trajectory_id=item["trajectory_id"],
            label=item["label"],
            vector=ManifoldPoint(**item["vector"]),
        )
        for item in manifest["trajectories"]
    ]
    receipt = emit_reveal_artifacts(
        output_dir,
        current,
        trajectories,
        denied_ids=manifest["denied_ids"],
        width=manifest["canvas"]["width"],
        height=manifest["canvas"]["height"],
    )
    receipt.update(
        {
            "sample_id": SAMPLE_ID,
            "reproducible": True,
            "input_artifact": {INPUT_FILE: sha256(manifest_text.encode("utf-8")).hexdigest()},
            "generator": "runtime/resonant_field_reveal_sample_r1.py",
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
    )
    (output_dir / RECEIPT_FILE).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


if __name__ == "__main__":
    print(json.dumps(generate_sample(), indent=2, sort_keys=True))
