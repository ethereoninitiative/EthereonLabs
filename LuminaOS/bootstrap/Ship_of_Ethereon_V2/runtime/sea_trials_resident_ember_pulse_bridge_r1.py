"""Focused sea trials for the Ember -> Pulse bridge R1."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile

try:
    from .resident_ember_r1 import EmberPolicy, ResidentEmber
    from .resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge, EmberPulseBridgeError
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_ember_r1 import EmberPolicy, ResidentEmber
    from resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge, EmberPulseBridgeError
    from resident_intention_store_r1 import ResidentIntentionStore


RESIDENT = "ETH-001"
INTENTION = "ember-bridge-r1"


class RecordingPulse:
    def __init__(self):
        self.calls = []

    def pulse(self, **kwargs):
        self.calls.append(dict(kwargs))
        return SimpleNamespace(receipt={
            "schema_version": "test-pulse",
            "invoked": False,
            "decision_reason": "governed_no_op",
            "force_requested": kwargs.get("force"),
        })


def provenance():
    return {
        "actor_kind": "resident",
        "resident": RESIDENT,
        "session_id": "ember-bridge-sea-trial",
        "source_ref": "sea-trial-explicit-resident-declaration",
    }


def definition():
    return {
        "intention_id": INTENTION,
        "resident": RESIDENT,
        "origin_context": "Resident Ember Pulse bridge sea trial",
        "statement": "Reconsider the unresolved bridge question when Ember becomes wake eligible.",
        "why_it_matters": "Tests causal inheritance without automatic execution.",
        "desired_next_action": "reconsider_ember_bridge_question",
        "parent_intention_id": None,
        "evidence_refs": ["sea-trial:resident-ember-pulse-bridge-r1"],
    }


def seed_wake(root: Path):
    intentions = ResidentIntentionStore(root / "resident_intentions")
    created = intentions.create(definition(), provenance())
    ember = ResidentEmber(base_dir=root)
    ember.seed(
        policy=EmberPolicy(
            resident=RESIDENT,
            intention_id=INTENTION,
            drive_rate_per_second=0.1,
            wake_threshold=0.5,
        ),
        observed_at="2026-09-28T00:00:00+00:00",
        initial_drive=0.0,
    )
    ember.advance(observed_at="2026-09-28T00:00:05+00:00")
    return intentions, created


def trial_verified_wake_enters_pulse_without_force():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        intentions, _ = seed_wake(root)
        pulse = RecordingPulse()
        bridge = ResidentEmberPulseBridge(base_dir=root, pulse=pulse, intention_store=intentions)
        receipt = bridge.present_wake(project_id="lumina-os")
        assert len(pulse.calls) == 1
        assert pulse.calls[0]["force"] is False
        assert pulse.calls[0]["requested_action"] == "reconsider_ember_bridge_question"
        assert receipt["operator_force_used"] is False
        assert receipt["ember_wake"]["intention_id"] == INTENTION
        assert receipt["pulse_receipt"]["force_requested"] is False


def trial_missing_wake_fails_closed():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
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
            observed_at="2026-09-28T00:00:00+00:00",
        )
        bridge = ResidentEmberPulseBridge(
            base_dir=root, pulse=RecordingPulse(), intention_store=intentions
        )
        try:
            bridge.present_wake()
        except EmberPulseBridgeError:
            return
        raise AssertionError("bridge accepted a missing Ember wake")


def trial_resolved_intention_blocks_wake():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        intentions, created = seed_wake(root)
        intentions.reconsider({
            "intention_id": INTENTION,
            "expected_event_hash": created["event"]["record_hash"],
            "outcome": "abandon",
            "reconsideration_statement": "Explicitly close this intention.",
            "evidence_refs": ["sea-trial:resident-choice"],
            "replacement": None,
        }, provenance())
        bridge = ResidentEmberPulseBridge(
            base_dir=root, pulse=RecordingPulse(), intention_store=intentions
        )
        try:
            bridge.present_wake()
        except EmberPulseBridgeError:
            return
        raise AssertionError("bridge presented a wake for a resolved intention")


def trial_explicit_reconsideration_returns_to_ember():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        intentions, created = seed_wake(root)
        pulse = RecordingPulse()
        bridge = ResidentEmberPulseBridge(base_dir=root, pulse=pulse, intention_store=intentions)
        bridge.present_wake(project_id="lumina-os")
        reconsidered = intentions.reconsider({
            "intention_id": INTENTION,
            "expected_event_hash": created["event"]["record_hash"],
            "outcome": "abandon",
            "reconsideration_statement": "Later resident judgment declines the inherited direction.",
            "evidence_refs": ["sea-trial:later-resident-judgment"],
            "replacement": None,
        }, provenance())
        returned = bridge.witness_reconsideration(
            reconsideration_receipt=reconsidered,
            observed_at="2026-09-28T00:00:06+00:00",
        )
        assert returned["event_kind"] == "reconsideration_return"
        assert returned["reconsideration_outcome"] == "abandon"
        assert returned["intention_status_after"] == "abandoned"
        assert returned["intention_event_hash"] == reconsidered["event"]["record_hash"]
        assert returned["authority_effect"] is False
        assert bridge.ember.wake_packet()["intention_id"] == INTENTION


def main():
    trials = [
        trial_verified_wake_enters_pulse_without_force,
        trial_missing_wake_fails_closed,
        trial_resolved_intention_blocks_wake,
        trial_explicit_reconsideration_returns_to_ember,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Ember Pulse bridge R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
