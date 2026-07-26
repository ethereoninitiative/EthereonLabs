from __future__ import annotations

from pathlib import Path
import json
import shutil

try:
    from .ai_orientation_protocol_r1 import AIOrientationProtocol
except Exception:
    from ai_orientation_protocol_r1 import AIOrientationProtocol


BASE_DIR = Path(__file__).resolve().parent / "_runtime_state" / "sea_trials_ai_orientation_r1"
MANIFEST = Path(__file__).resolve().parent / "ai_orientation_manifest_r1.json"


def main():
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    protocol = AIOrientationProtocol(MANIFEST, BASE_DIR / "records")
    record = protocol.begin(
        model_provider="test-provider",
        model_name="test-model",
        account_label="sea-trial",
    )

    presented = []
    while record.status != "completed":
        packet = protocol.next_packet(record.record_id)
        stage_id = packet["stage"]["stage_id"]
        presented.append(stage_id)
        record = protocol.record_response(
            record.record_id,
            response=f"Observed evidence and unresolved questions for {stage_id}.",
            self_assessment={"distinguished_evidence_from_inference": True},
        )

    summary = protocol.verification_summary(record.record_id)
    checks = {
        "all_stages_presented_in_manifest_order": presented == [
            "baseline",
            "authority",
            "runtime",
            "orientation",
            "transfer_probe",
        ],
        "record_completed": summary["status"] == "completed",
        "all_responses_hashed": len(summary["stage_response_hashes"]) == 5,
        "authority_is_supplemental": summary["authority"].startswith(
            "supplemental orientation only"
        ),
        "claim_boundary_rejects_identity_proof": (
            "does not prove identity transfer" in summary["claim_boundary"]
        ),
    }
    report = {
        "suite": "Sea Trials AI Orientation r1",
        "passed": all(checks.values()),
        "checks": checks,
        "summary": summary,
    }
    report_path = BASE_DIR / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
