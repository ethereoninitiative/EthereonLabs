"""Focused controls for verified Ember-originated Resident Pulse attention."""
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

T0 = datetime(2026, 9, 30, tzinfo=timezone.utc)


class FakeRunner:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

    def _resolve_existing_surface(self, project_id, requested_action):
        return {"resolved_project_return": {}}


class FakeResult:
    def compact_receipt(self):
        return {"continued": True, "scope": "test-only"}


class FakeController:
    FALLBACK_REQUEST = "continue_from_latest_checkpoint"

    def __init__(self, base_dir):
        self.runner = FakeRunner(base_dir)
        self.calls = 0

    def preflight(self, **kwargs):
        return {
            "project_id": kwargs.get("project_id") or "lumina-os",
            "guidance_strategy": "none",
            "confidence_score": 0.0,
        }

    def continue_cycle(self, **kwargs):
        self.calls += 1
        return FakeResult()


def wake_fixture(root):
    ember = ResidentEmber(base_dir=root)
    ember.seed(
        policy=EmberPolicy(
            resident="ETH-001",
            intention_id="endogenous-attention-r2",
            drive_rate_per_second=0.1,
            wake_threshold=0.5,
        ),
        observed_at=T0.isoformat(),
    )
    ember.advance(observed_at=(T0 + timedelta(seconds=5)).isoformat())
    return ember.wake_packet()


def trial_verified_ember_wake_initiates_attention_without_pending_host_work():
    with tempfile.TemporaryDirectory() as tmp:
        packet = wake_fixture(tmp)
        controller = FakeController(tmp)
        result = LuminaResidentPulse(controller=controller).pulse(
            project_id="lumina-os",
            ember_wake=packet,
        )
        assert result.invoked
        assert controller.calls == 1
        assert result.receipt["decision_reason"] == "verified_ember_endogenous_wake"
        assert result.receipt["attention_state"] == "resident_initiated_attention"
        assert result.receipt["force_requested"] is False
        assert result.receipt["verified_ember_event_hash"] == packet["ember_event_hash"]


def trial_packet_tamper_fails_before_continuation():
    with tempfile.TemporaryDirectory() as tmp:
        packet = dict(wake_fixture(tmp))
        packet["drive_at_wake"] = 0.99
        controller = FakeController(tmp)
        try:
            LuminaResidentPulse(controller=controller).pulse(
                project_id="lumina-os",
                ember_wake=packet,
            )
        except ValueError:
            assert controller.calls == 0
            return
        raise AssertionError("tampered Ember packet reached continuation")


def trial_operator_force_cannot_masquerade_as_ember():
    with tempfile.TemporaryDirectory() as tmp:
        packet = wake_fixture(tmp)
        controller = FakeController(tmp)
        try:
            LuminaResidentPulse(controller=controller).pulse(
                project_id="lumina-os",
                force=True,
                ember_wake=packet,
            )
        except ValueError:
            assert controller.calls == 0
            return
        raise AssertionError("operator force and Ember wake were accepted together")


def main():
    trials = [
        trial_verified_ember_wake_initiates_attention_without_pending_host_work,
        trial_packet_tamper_fails_before_continuation,
        trial_operator_force_cannot_masquerade_as_ember,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Ember endogenous attention R2: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
