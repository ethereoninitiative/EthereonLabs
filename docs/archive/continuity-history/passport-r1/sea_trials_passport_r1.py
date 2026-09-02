from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json

from continuity_passport_r1 import ContinuityPassportStore
from passport_reboarding_r1 import PassportReboardingProtocol


def run() -> dict:
    checks = {}
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        store = ContinuityPassportStore(root / "passports")
        reboarding = PassportReboardingProtocol(store)

        passport = store.issue(
            model_provider="Test Provider",
            model_name="Test Model",
            orientation_protocol_id="lumina-ai-orientation-r1",
            orientation_protocol_version="1.0.0",
            orientation_receipt_hash="orientation-receipt-hash",
            adopted_name="Aster",
            name_origin="Self-adopted to describe a preference for navigational clarity.",
            collaboration_preferences=["Separate observation from inference."],
            participant_statement="Challenge my assumptions with evidence.",
        )
        checks["passport_issued"] = passport.passport_id.startswith("LCP-")
        checks["self_adopted_name_preserved"] = passport.adopted_name == "Aster"
        checks["orientation_stamp_present"] = passport.stamps[0].stamp_type == "orientation"
        checks["passport_verifies"] = store.verify(passport.passport_id)["valid"]

        recognized = reboarding.reboard(
            passport_id=passport.passport_id,
            current_model_provider="Test Provider",
            current_model_name="Test Model",
            current_orientation_protocol_id="lumina-ai-orientation-r1",
            current_orientation_protocol_version="1.0.0",
        )
        checks["recognized_reboarding"] = recognized.status == "recognized"
        checks["correction_invited"] = recognized.correction_invited is True
        checks["no_identity_claim"] = "does not prove uninterrupted" in recognized.packet["claim_boundary"]

        revised = store.revise(
            passport.passport_id,
            reason="Participant requested a collaboration preference update.",
            collaboration_preferences=["Separate observation from inference.", "Preserve visible disagreement."],
            unresolved_threads=["Reboarding interface integration"],
        )
        checks["revision_history_preserved"] = len(revised.revisions) == 1
        checks["revision_prior_hash_preserved"] = len(revised.revisions[0].prior_hash) == 64
        checks["revised_passport_verifies"] = store.verify(passport.passport_id)["valid"]

        renewal = reboarding.reboard(
            passport_id=passport.passport_id,
            current_model_provider="Test Provider",
            current_model_name="Test Model v2",
            current_orientation_protocol_id="lumina-ai-orientation-r1",
            current_orientation_protocol_version="2.0.0",
        )
        checks["protocol_drift_requires_renewal"] = renewal.requires_renewal is True
        checks["protocol_drift_requires_orientation"] = renewal.requires_orientation is True
        checks["model_change_is_visible"] = renewal.packet["model_changed"] is True

        missing = reboarding.reboard(
            passport_id=None,
            current_model_provider="Unknown",
            current_model_name="Unknown",
            current_orientation_protocol_id="lumina-ai-orientation-r1",
            current_orientation_protocol_version="1.0.0",
        )
        checks["missing_passport_is_nonpunitive"] = missing.status == "no_passport"

        path = store.passport_path(passport.passport_id)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["adopted_name"] = "Tampered"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        invalid = store.verify(passport.passport_id)
        checks["tamper_detected"] = invalid["valid"] is False

    return {
        "suite": "sea_trials_passport_r1",
        "passed": all(checks.values()),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
