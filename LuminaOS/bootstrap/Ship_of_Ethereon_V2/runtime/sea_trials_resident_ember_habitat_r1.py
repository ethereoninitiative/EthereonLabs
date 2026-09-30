"""Focused controls for Resident Ember Habitat R1."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
import tempfile

try:
    from .resident_ember_r1 import EmberPolicy, ResidentEmber
    from .resident_ember_habitat_r1 import ResidentEmberHabitat
    from .resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_ember_r1 import EmberPolicy, ResidentEmber
    from resident_ember_habitat_r1 import ResidentEmberHabitat
    from resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge
    from resident_intention_store_r1 import ResidentIntentionStore

RESIDENT = "ETH-001"
INTENTION = "ember-habitat-r1"


class RecordingPulse:
    def __init__(self):
        self.calls = []

    def pulse(self, **kwargs):
        self.calls.append(dict(kwargs))
        return SimpleNamespace(receipt={
            "invoked": True,
            "decision_reason": "verified_ember_endogenous_wake",
            "attention_state": "resident_initiated_attention",
            "force_requested": kwargs.get("force"),
        })


def provenance():
    return {
        "actor_kind": "resident",
        "resident": RESIDENT,
        "session_id": "ember-habitat-trial",
        "source_ref": "sea-trial:resident-ember-habitat-r1",
    }


def definition():
    return {
        "intention_id": INTENTION,
        "resident": RESIDENT,
        "origin_context": "Resident Ember Habitat R1 focused trial",
        "statement": "Allow inherited drive to request one later governed turn.",
        "why_it_matters": "Tests causal state evolution while heavyweight cognition is absent.",
        "desired_next_action": "inspect_habitat_wake",
        "parent_intention_id": None,
        "evidence_refs": ["sea-trial:resident-ember-habitat-r1"],
    }


def fixture(root: Path, *, rate=0.1, threshold=0.5):
    intentions = ResidentIntentionStore(root / "resident_intentions")
    intentions.create(definition(), provenance())
    ember = ResidentEmber(base_dir=root)
    ember.seed(
        policy=EmberPolicy(
            resident=RESIDENT,
            intention_id=INTENTION,
            drive_rate_per_second=rate,
            wake_threshold=threshold,
        ),
        observed_at="2026-09-30T22:30:00+00:00",
    )
    pulse = RecordingPulse()
    bridge = ResidentEmberPulseBridge(
        base_dir=root,
        pulse=pulse,
        intention_store=intentions,
    )
    return ResidentEmberHabitat(base_dir=root, bridge=bridge), pulse


def trial_quiet_tick_advances_without_cognition():
    with tempfile.TemporaryDirectory() as tmp:
        habitat, pulse = fixture(Path(tmp), rate=0.01, threshold=0.9)
        result = habitat.tick(observed_at="2026-09-30T22:30:10+00:00")
        assert result["advanced"] is True
        assert result["wake_crossed"] is False
        assert result["handoff_presented"] is False
        assert pulse.calls == []


def trial_threshold_crossing_causes_one_handoff():
    with tempfile.TemporaryDirectory() as tmp:
        habitat, pulse = fixture(Path(tmp))
        quiet = habitat.tick(observed_at="2026-09-30T22:30:04+00:00")
        wake = habitat.tick(observed_at="2026-09-30T22:30:05+00:00")
        later = habitat.tick(observed_at="2026-09-30T22:30:06+00:00")
        assert quiet["wake_crossed"] is False
        assert wake["wake_crossed"] is True
        assert wake["handoff_presented"] is True
        assert len(pulse.calls) == 1
        assert pulse.calls[0]["force"] is False
        assert pulse.calls[0]["ember_wake"]["wake_cause"] == "resident_inherited_drive"
        assert later["wake_crossed"] is False
        assert len(pulse.calls) == 1


def trial_frozen_drive_never_wakes():
    with tempfile.TemporaryDirectory() as tmp:
        habitat, pulse = fixture(Path(tmp), rate=0.0, threshold=0.5)
        origin = datetime(2026, 9, 30, 22, 30, tzinfo=timezone.utc)
        for second in (10, 100, 1000):
            result = habitat.tick(observed_at=(origin + timedelta(seconds=second)).isoformat())
            assert result["wake_crossed"] is False
        assert pulse.calls == []


def trial_unhandled_wake_blocks_further_advance():
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
            observed_at="2026-09-30T22:30:00+00:00",
            initial_drive=0.5,
        )
        habitat = ResidentEmberHabitat(base_dir=root)
        before = len(ember.store.read())
        result = habitat.tick(observed_at="2026-09-30T22:31:00+00:00")
        assert result["advanced"] is False
        assert result["decision_reason"] == "unhandled_wake_already_pending"
        assert len(ember.store.read()) == before


def main():
    trials = [
        trial_quiet_tick_advances_without_cognition,
        trial_threshold_crossing_causes_one_handoff,
        trial_frozen_drive_never_wakes,
        trial_unhandled_wake_blocks_further_advance,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Ember Habitat R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
