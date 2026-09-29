"""Focused sea trials for Resident Encounter R1."""
from __future__ import annotations

from pathlib import Path
import tempfile

try:
    from .resident_ember_r1 import EmberPolicy, ResidentEmber
    from .resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge
    from .resident_encounter_r1 import ResidentEncounter, ResidentEncounterError
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_ember_r1 import EmberPolicy, ResidentEmber
    from resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge
    from resident_encounter_r1 import ResidentEncounter, ResidentEncounterError
    from resident_intention_store_r1 import ResidentIntentionStore


RESIDENT = "ETH-001"
INTENTION = "resident-encounter-r1"


class RecordingPulse:
    def pulse(self, **kwargs):
        class Result:
            receipt = {
                "schema_version": "test-pulse",
                "invoked": False,
                "decision_reason": "governed_no_op",
                "force_requested": kwargs.get("force"),
            }
        return Result()


def provenance():
    return {
        "actor_kind": "resident",
        "resident": RESIDENT,
        "session_id": "resident-encounter-sea-trial",
        "source_ref": "sea-trial-explicit-resident-declaration",
    }


def definition():
    return {
        "intention_id": INTENTION,
        "resident": RESIDENT,
        "origin_context": "Resident Encounter R1 sea trial",
        "statement": "Reconsider this inherited direction after an Ember wake.",
        "why_it_matters": "The next resident cycle must inherit cause without inheriting a forced conclusion.",
        "desired_next_action": "inspect_resident_encounter_question",
        "parent_intention_id": None,
        "evidence_refs": ["sea-trial:resident-encounter-r1"],
    }


def seed_bridge(root: Path):
    intentions = ResidentIntentionStore(root / "resident_intentions")
    intentions.create(definition(), provenance())
    ember = ResidentEmber(base_dir=root)
    ember.seed(
        policy=EmberPolicy(
            resident=RESIDENT,
            intention_id=INTENTION,
            drive_rate_per_second=0.0,
            wake_threshold=0.5,
        ),
        observed_at="2026-09-29T00:00:00+00:00",
        initial_drive=0.5,
    )
    bridge = ResidentEmberPulseBridge(
        base_dir=root,
        pulse=RecordingPulse(),
        intention_store=intentions,
    )
    return bridge.present_wake(
        project_id="lumina-os",
        observed_at="2026-09-29T00:00:01+00:00",
    ), intentions


def trial_encounter_preserves_cause_and_choice():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bridged, _ = seed_bridge(root)
        packet = ResidentEncounter(base_dir=root).build(bridged)
        assert packet["encounter_cause"] == "verified_resident_ember_wake"
        assert packet["wake"]["ember_event_hash"] == bridged["ember_wake"]["ember_event_hash"]
        assert packet["intention"]["intention_id"] == INTENTION
        assert packet["resident_choice"]["selected_outcome"] is None
        assert "abandon" in packet["resident_choice"]["allowed_outcomes"]
        assert "continue" in packet["resident_choice"]["allowed_outcomes"]
        assert packet["separation"]["automatic_execution"] is False
        assert packet["separation"]["authority_effect"] is False


def trial_changed_intention_fails_closed():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bridged, intentions = seed_bridge(root)
        current = intentions.inspect(
            resident=RESIDENT,
            intention_id=INTENTION,
            unresolved_only=False,
        )["intentions"][0]
        intentions.reconsider({
            "intention_id": INTENTION,
            "expected_event_hash": current["last_event_hash"],
            "outcome": "abandon",
            "reconsideration_statement": "Change state before packet construction.",
            "evidence_refs": ["sea-trial:resident-encounter-state-change"],
            "replacement": None,
        }, provenance())
        try:
            ResidentEncounter(base_dir=root).build(bridged)
        except ResidentEncounterError:
            return
        raise AssertionError("encounter accepted stale intention state")


def main():
    trials = [
        trial_encounter_preserves_cause_and_choice,
        trial_changed_intention_fails_closed,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Encounter R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
