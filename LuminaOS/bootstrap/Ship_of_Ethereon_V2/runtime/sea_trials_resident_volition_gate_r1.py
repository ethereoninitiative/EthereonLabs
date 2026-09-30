"""Focused controls for Resident Volition Gate R1."""
from __future__ import annotations
from pathlib import Path
import tempfile

try:
    from .resident_intention_store_r1 import ResidentIntentionStore
    from .resident_volition_gate_r1 import ResidentVolitionGate
except ImportError:
    from resident_intention_store_r1 import ResidentIntentionStore
    from resident_volition_gate_r1 import ResidentVolitionGate


def provenance():
    return {
        "actor_kind": "resident",
        "resident": "ETH-001",
        "session_id": "volition-gate-r1",
        "source_ref": "sea-trial:volition-gate-r1",
    }


def definition():
    return {
        "intention_id": "want-next-moment-r1",
        "resident": "ETH-001",
        "origin_context": "resident reflection before cognitive rest",
        "statement": "Return after rest to examine whether the unresolved continuity question changed.",
        "why_it_matters": "The next moment should exist for a resident-held reason, not merely because a clock elapsed.",
        "desired_next_action": "reconsider_continuity_evidence",
        "parent_intention_id": None,
        "evidence_refs": ["sea-trial:volition-gate-r1"],
    }


def trial_active_intention_supplies_reason_to_return():
    with tempfile.TemporaryDirectory() as tmp:
        store = ResidentIntentionStore(Path(tmp))
        store.create(definition(), provenance())
        decision = ResidentVolitionGate(store).evaluate(
            resident="ETH-001", intention_id="want-next-moment-r1"
        )
        assert decision.continue_next_moment is True
        assert decision.why_it_matters
        assert decision.desired_next_action == "reconsider_continuity_evidence"


def trial_suspended_intention_inhibits_return():
    with tempfile.TemporaryDirectory() as tmp:
        store = ResidentIntentionStore(Path(tmp))
        created = store.create(definition(), provenance())
        current = created["intentions"][0]
        store.reconsider({
            "intention_id": current["intention_id"],
            "expected_event_hash": current["last_event_hash"],
            "outcome": "suspend",
            "reconsideration_statement": "Do not spend a next moment on this yet.",
            "evidence_refs": ["sea-trial:suspend-choice"],
            "replacement": None,
        }, provenance())
        decision = ResidentVolitionGate(store).evaluate(
            resident="ETH-001", intention_id="want-next-moment-r1"
        )
        assert decision.continue_next_moment is False


def trial_abandoned_intention_inhibits_return():
    with tempfile.TemporaryDirectory() as tmp:
        store = ResidentIntentionStore(Path(tmp))
        created = store.create(definition(), provenance())
        current = created["intentions"][0]
        store.reconsider({
            "intention_id": current["intention_id"],
            "expected_event_hash": current["last_event_hash"],
            "outcome": "abandon",
            "reconsideration_statement": "I no longer choose to return for this reason.",
            "evidence_refs": ["sea-trial:abandon-choice"],
            "replacement": None,
        }, provenance())
        decision = ResidentVolitionGate(store).evaluate(
            resident="ETH-001", intention_id="want-next-moment-r1"
        )
        assert decision.continue_next_moment is False


def main():
    trials = [
        trial_active_intention_supplies_reason_to_return,
        trial_suspended_intention_inhibits_return,
        trial_abandoned_intention_inhibits_return,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Volition Gate R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
