"""Focused deterministic sea trials for Resident Ember R1."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

try:
    from .resident_ember_r1 import EmberPolicy, ResidentEmber, EmberError
except ImportError:
    from resident_ember_r1 import EmberPolicy, ResidentEmber, EmberError


T0 = datetime(2026, 9, 26, 23, 0, tzinfo=timezone.utc)


def ts(seconds: int) -> str:
    return (T0 + timedelta(seconds=seconds)).isoformat()


def trial_endogenous_wake():
    with tempfile.TemporaryDirectory() as tmp:
        ember = ResidentEmber(base_dir=tmp)
        policy = EmberPolicy(
            resident="ETH-001",
            intention_id="ember-r1-question",
            drive_rate_per_second=0.01,
            wake_threshold=0.80,
        )
        seed = ember.seed(policy=policy, observed_at=ts(0), initial_drive=0.10)
        quiet = ember.advance(observed_at=ts(60))
        wake = ember.advance(observed_at=ts(75))
        packet = ember.wake_packet()
        assert not seed["wake_requested"]
        assert not quiet["wake_requested"]
        assert wake["wake_requested"]
        assert wake["wake_cause"] == "resident_inherited_drive"
        assert packet["ember_event_hash"] == wake["event_hash"]
        assert packet["intention_id"] == "ember-r1-question"
        assert packet["authority"].startswith("attention request only")


def trial_frozen_drive_does_not_wake():
    with tempfile.TemporaryDirectory() as tmp:
        ember = ResidentEmber(base_dir=tmp)
        policy = EmberPolicy(
            resident="ETH-001",
            intention_id="frozen",
            drive_rate_per_second=0.0,
            wake_threshold=0.50,
        )
        ember.seed(policy=policy, observed_at=ts(0), initial_drive=0.10)
        event = ember.advance(observed_at=ts(100000))
        assert not event["wake_requested"]
        assert ember.wake_packet() is None


def trial_wake_is_single_transition():
    with tempfile.TemporaryDirectory() as tmp:
        ember = ResidentEmber(base_dir=tmp)
        policy = EmberPolicy(
            resident="ETH-001",
            intention_id="single",
            drive_rate_per_second=0.1,
            wake_threshold=0.50,
        )
        ember.seed(policy=policy, observed_at=ts(0))
        first = ember.advance(observed_at=ts(5))
        later = ember.advance(observed_at=ts(20))
        assert first["wake_requested"]
        assert not later["wake_requested"]
        assert ember.wake_packet()["ember_event_hash"] == first["event_hash"]


def trial_tamper_fails_closed():
    with tempfile.TemporaryDirectory() as tmp:
        ember = ResidentEmber(base_dir=tmp)
        policy = EmberPolicy(
            resident="ETH-001",
            intention_id="tamper",
            drive_rate_per_second=0.01,
            wake_threshold=0.80,
        )
        ember.seed(policy=policy, observed_at=ts(0))
        raw = ember.store.journal.read_text(encoding="utf-8")
        ember.store.journal.write_text(raw.replace('"drive_after":0.0', '"drive_after":0.4'), encoding="utf-8")
        try:
            ember.advance(observed_at=ts(10))
        except EmberError:
            return
        raise AssertionError("tampered Ember journal did not fail closed")


def trial_external_time_is_not_external_wake_cause():
    with tempfile.TemporaryDirectory() as tmp:
        ember = ResidentEmber(base_dir=tmp)
        policy = EmberPolicy(
            resident="ETH-001",
            intention_id="causal",
            drive_rate_per_second=0.01,
            wake_threshold=0.20,
        )
        ember.seed(policy=policy, observed_at=ts(0), initial_drive=0.10)
        wake = ember.advance(observed_at=ts(10))
        assert wake["wake_requested"]
        assert wake["wake_cause"] == "resident_inherited_drive"
        assert wake["authority_effect"] is False


def main():
    trials = [
        trial_endogenous_wake,
        trial_frozen_drive_does_not_wake,
        trial_wake_is_single_transition,
        trial_tamper_fails_closed,
        trial_external_time_is_not_external_wake_cause,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Ember R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
