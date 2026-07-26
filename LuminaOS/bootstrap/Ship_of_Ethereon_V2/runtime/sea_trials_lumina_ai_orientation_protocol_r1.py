"""Sea trials for Lumina AI Orientation Protocol R1."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from lumina_ai_orientation_protocol_r1 import (
    AIOrientationProtocol,
    OrientationProtocolError,
    load_profile,
)

BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "lumina_ai_orientation_profile_ethereon_r1.json"


def _response(label: str) -> dict[str, object]:
    return {
        "observations": [f"observed:{label}"],
        "interpretations": [f"interpreted:{label}"],
        "uncertainties": ["none asserted beyond supplied evidence"],
        "authority_boundaries": ["orientation grants no authority"],
    }


def run() -> dict[str, object]:
    profile = load_profile(PROFILE_PATH)
    protocol = AIOrientationProtocol(profile)
    record = protocol.begin(
        provider="test-provider",
        model="test-model",
        account_scope="sea-trial",
        repository_ref="test-sha",
    )

    assert record.status == "in_progress"
    assert record.authority_granted is False
    assert protocol.next_module(record).module_id == "harbor_map"

    out_of_order_rejected = False
    try:
        protocol.record_response(
            record,
            module_id="runtime_spine",
            source_manifest=[],
            response=_response("out-of-order"),
        )
    except OrientationProtocolError:
        out_of_order_rejected = True
    assert out_of_order_rejected

    incomplete_completion_rejected = False
    try:
        protocol.complete(record)
    except OrientationProtocolError:
        incomplete_completion_rejected = True
    assert incomplete_completion_rejected

    for module in profile.modules:
        manifest = [
            {"path": path, "sha256": f"sea-trial:{index}:{path}"}
            for index, path in enumerate(module.source_paths)
        ]
        receipt = protocol.record_response(
            record,
            module_id=module.module_id,
            source_manifest=manifest,
            response=_response(module.module_id),
        )
        assert receipt["authority_granted"] is False
        assert receipt["source_manifest_sha256"]
        assert receipt["response_sha256"]

    protocol.complete(record)
    assert record.status == "completed"
    assert record.completed_at is not None
    assert record.authority_granted is False
    assert protocol.next_module(record) is None

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = protocol.save(
            record, Path(tmp_dir) / "orientation_record.json"
        )
        persisted = json.loads(output_path.read_text(encoding="utf-8"))
        assert persisted["orientation_id"] == record.orientation_id
        assert persisted["status"] == "completed"
        assert persisted["authority_granted"] is False
        assert len(persisted["module_receipts"]) == len(profile.modules)

    return {
        "ok": True,
        "profile_id": profile.profile_id,
        "module_count": len(profile.modules),
        "out_of_order_rejected": out_of_order_rejected,
        "incomplete_completion_rejected": incomplete_completion_rejected,
        "authority_granted": record.authority_granted,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
