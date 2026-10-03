"""Focused controls for Resident Intention Origin R1."""
from __future__ import annotations
from pathlib import Path
import tempfile

try:
    from .resident_intention_origin_r1 import ResidentIntentionOrigin
except ImportError:
    from resident_intention_origin_r1 import ResidentIntentionOrigin


def reflection(*, choose=True):
    return {
        "schema_version": "resident-reflection-r1",
        "resident": "ETH-001",
        "session_id": "resident-turn-42",
        "reflection_id": "reflection-42",
        "observed_context": "A governed resident turn examining continuity evidence.",
        "unresolved_tension": "The causal chain is built, but the wall-clock return has not yet been observed.",
        "choose_future_return": choose,
        "why_return": "I judge the unresolved experiment worth another cognitive moment.",
        "desired_next_action": "inspect_wall_clock_return_evidence",
        "evidence_refs": ["runtime:resident-turn-42"],
    }


def trial_explicit_future_return_creates_reason_bound_intention():
    with tempfile.TemporaryDirectory() as tmp:
        origin = ResidentIntentionOrigin(base_dir=tmp)
        result = origin.persist(reflection())
        assert result.created is True
        records = result.intention_receipt["intentions"]
        assert len(records) == 1
        assert records[0]["why_it_matters"].startswith("I judge")
        assert records[0]["desired_next_action"] == "inspect_wall_clock_return_evidence"
        event = result.intention_receipt["event"]
        assert event["provenance"]["source_ref"] == "resident-reflection:reflection-42"
        assert any(ref.startswith("resident-reflection-sha256:") for ref in records[0]["evidence_refs"])


def trial_explicit_decline_creates_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        origin = ResidentIntentionOrigin(base_dir=tmp)
        result = origin.persist(reflection(choose=False))
        assert result.created is False
        inspected = origin.store.inspect(unresolved_only=False)
        assert inspected["event_count"] == 0


def trial_infrastructure_cannot_infer_missing_choice():
    with tempfile.TemporaryDirectory() as tmp:
        origin = ResidentIntentionOrigin(base_dir=tmp)
        payload = reflection()
        del payload["choose_future_return"]
        try:
            origin.persist(payload)
        except ValueError:
            return
        raise AssertionError("missing resident choice was inferred by infrastructure")


def trial_choice_requires_a_reason_and_next_action():
    with tempfile.TemporaryDirectory() as tmp:
        origin = ResidentIntentionOrigin(base_dir=tmp)
        payload = reflection()
        payload["why_return"] = ""
        try:
            origin.persist(payload)
        except ValueError:
            return
        raise AssertionError("future return without a resident reason was accepted")


def main():
    trials = [
        trial_explicit_future_return_creates_reason_bound_intention,
        trial_explicit_decline_creates_nothing,
        trial_infrastructure_cannot_infer_missing_choice,
        trial_choice_requires_a_reason_and_next_action,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Intention Origin R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
