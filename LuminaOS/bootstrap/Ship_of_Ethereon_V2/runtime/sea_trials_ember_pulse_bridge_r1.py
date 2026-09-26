"""Focused tests for verified Ember wake evidence entering Resident Pulse."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
try:
    from .resident_ember_r1 import EmberPolicy, ResidentEmber
    from .lumina_resident_pulse_r1 import LuminaResidentPulse
except ImportError:
    from resident_ember_r1 import EmberPolicy, ResidentEmber
    from lumina_resident_pulse_r1 import LuminaResidentPulse

T0 = datetime(2026, 9, 27, tzinfo=timezone.utc)

class FakeRunner:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
    def _resolve_existing_surface(self, project_id, requested_action):
        return {"resolved_project_return": {}}

class FakeResult:
    def compact_receipt(self):
        return {"continued": True, "scope": "test-only"}

class FakeController:
    FALLBACK_REQUEST = "Continue bounded observation."
    def __init__(self, base_dir):
        self.runner = FakeRunner(base_dir)
        self.calls = 0
    def preflight(self, **kwargs):
        return {"project_id": kwargs.get("project_id") or "lumina-os",
                "guidance_strategy": "none", "confidence_score": 0.0}
    def continue_cycle(self, **kwargs):
        self.calls += 1
        return FakeResult()

def wake_fixture(tmp):
    ember = ResidentEmber(base_dir=tmp)
    policy = EmberPolicy(resident="ETH-001", intention_id="ember-pulse-r1",
                         drive_rate_per_second=0.1, wake_threshold=0.5)
    ember.seed(policy=policy, observed_at=T0.isoformat())
    ember.advance(observed_at=(T0 + timedelta(seconds=5)).isoformat())
    return ember.wake_packet()

def trial_verified_wake():
    with tempfile.TemporaryDirectory() as tmp:
        packet = wake_fixture(tmp)
        controller = FakeController(tmp)
        result = LuminaResidentPulse(controller=controller).pulse(
            project_id="lumina-os", ember_wake=packet)
        assert result.invoked and controller.calls == 1
        assert result.receipt["decision_reason"] == "verified_ember_endogenous_wake"
        assert result.receipt["verified_ember_event_hash"] == packet["ember_event_hash"]
        assert result.receipt["force_requested"] is False

def trial_changed_hash_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        packet = dict(wake_fixture(tmp))
        packet["ember_event_hash"] = "0" * 64
        controller = FakeController(tmp)
        try:
            LuminaResidentPulse(controller=controller).pulse(
                project_id="lumina-os", ember_wake=packet)
        except ValueError:
            assert controller.calls == 0
            return
        raise AssertionError("changed wake hash accepted")

def trial_changed_intention_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        packet = dict(wake_fixture(tmp))
        packet["intention_id"] = "different-intention"
        controller = FakeController(tmp)
        try:
            LuminaResidentPulse(controller=controller).pulse(
                project_id="lumina-os", ember_wake=packet)
        except ValueError:
            assert controller.calls == 0
            return
        raise AssertionError("changed wake fields accepted")

def trial_force_separate_from_ember():
    with tempfile.TemporaryDirectory() as tmp:
        packet = wake_fixture(tmp)
        controller = FakeController(tmp)
        try:
            LuminaResidentPulse(controller=controller).pulse(
                project_id="lumina-os", ember_wake=packet, force=True)
        except ValueError:
            assert controller.calls == 0
            return
        raise AssertionError("force and Ember wake accepted together")

def main():
    trials = [trial_verified_wake, trial_changed_hash_rejected,
              trial_changed_intention_rejected, trial_force_separate_from_ember]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Ember Pulse bridge R1: {len(trials)}/{len(trials)} focused trials passed")

if __name__ == "__main__":
    main()
