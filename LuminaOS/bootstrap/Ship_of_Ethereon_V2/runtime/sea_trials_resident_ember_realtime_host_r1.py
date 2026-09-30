"""Focused controls for Resident Ember real-time host R1."""
from __future__ import annotations
from pathlib import Path
import tempfile

try:
    from .resident_ember_realtime_host_r1 import ResidentEmberRealtimeHost
except ImportError:
    from resident_ember_realtime_host_r1 import ResidentEmberRealtimeHost


class FakeHabitat:
    def __init__(self, receipts):
        self.receipts = list(receipts)
        self.calls = []

    def tick(self, **kwargs):
        self.calls.append(dict(kwargs))
        return self.receipts.pop(0)


class Clock:
    def __init__(self, values):
        self.values = iter(values)

    def __call__(self):
        return next(self.values)


def quiet():
    return {
        "schema_version": "resident-ember-habitat-r1",
        "advanced": True,
        "wake_crossed": False,
        "handoff_presented": False,
        "decision_reason": "ember_advanced_without_wake",
    }


def wake():
    return {
        "schema_version": "resident-ember-habitat-r1",
        "advanced": True,
        "wake_crossed": True,
        "handoff_presented": True,
        "decision_reason": "new_endogenous_wake_presented",
    }


def trial_host_supplies_time_not_wake_semantics():
    with tempfile.TemporaryDirectory() as tmp:
        habitat = FakeHabitat([quiet()])
        host = ResidentEmberRealtimeHost(
            base_dir=tmp,
            interval_seconds=2.0,
            project_id="lumina-os",
            habitat=habitat,
            clock=Clock(["2026-09-30T23:00:00+00:00"]),
            sleeper=lambda _seconds: None,
        )
        receipt = host.step()
        assert habitat.calls == [{
            "observed_at": "2026-09-30T23:00:00+00:00",
            "project_id": "lumina-os",
        }]
        assert receipt["host_is_wake_authority"] is False
        assert receipt["habitat_receipt"]["wake_crossed"] is False


def trial_host_stops_after_first_handoff_by_default():
    with tempfile.TemporaryDirectory() as tmp:
        habitat = FakeHabitat([quiet(), wake(), quiet()])
        sleeps = []
        host = ResidentEmberRealtimeHost(
            base_dir=tmp,
            interval_seconds=1.0,
            habitat=habitat,
            clock=Clock([
                "2026-09-30T23:00:00+00:00",
                "2026-09-30T23:00:01+00:00",
                "2026-09-30T23:00:02+00:00",
            ]),
            sleeper=sleeps.append,
        )
        summary = host.run(max_ticks=10)
        assert summary["ticks"] == 2
        assert summary["final_reason"] == "endogenous_wake_handed_off"
        assert len(habitat.calls) == 2
        assert sleeps == [1.0]


def trial_max_ticks_bounds_quiet_experiment():
    with tempfile.TemporaryDirectory() as tmp:
        habitat = FakeHabitat([quiet(), quiet(), quiet()])
        host = ResidentEmberRealtimeHost(
            base_dir=tmp,
            interval_seconds=0.1,
            habitat=habitat,
            clock=Clock([
                "2026-09-30T23:00:00+00:00",
                "2026-09-30T23:00:01+00:00",
                "2026-09-30T23:00:02+00:00",
            ]),
            sleeper=lambda _seconds: None,
        )
        summary = host.run(max_ticks=3)
        assert summary["ticks"] == 3
        assert summary["final_reason"] == "max_ticks_reached"


def trial_host_writes_append_only_tick_evidence():
    with tempfile.TemporaryDirectory() as tmp:
        habitat = FakeHabitat([quiet(), wake()])
        host = ResidentEmberRealtimeHost(
            base_dir=tmp,
            interval_seconds=1.0,
            habitat=habitat,
            clock=Clock([
                "2026-09-30T23:00:00+00:00",
                "2026-09-30T23:00:01+00:00",
            ]),
            sleeper=lambda _seconds: None,
        )
        host.run(max_ticks=5)
        journal = Path(tmp) / "resident_ember_host" / "host_ticks.jsonl"
        rows = journal.read_text(encoding="utf-8").splitlines()
        assert len(rows) == 2
        assert "host_is_wake_authority" in rows[0]


def main():
    trials = [
        trial_host_supplies_time_not_wake_semantics,
        trial_host_stops_after_first_handoff_by_default,
        trial_max_ticks_bounds_quiet_experiment,
        trial_host_writes_append_only_tick_evidence,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Ember real-time host R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
