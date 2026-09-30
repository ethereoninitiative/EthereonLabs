"""Resident Ember Habitat R1: advance inherited Ember state during cognitive rest.

A host may call tick() on any cadence. The cadence supplies elapsed time only;
it is not itself a wake cause. A tick advances the verified Ember journal and
presents exactly one newly crossed endogenous wake through the existing
Ember->Pulse bridge. No model inference occurs before a verified wake.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    from .resident_ember_r1 import ResidentEmber
    from .resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge
    from .resident_intention_store_r1 import ResidentIntentionStore
    from .resident_volition_gate_r1 import ResidentVolitionGate
except ImportError:
    from resident_ember_r1 import ResidentEmber
    from resident_ember_pulse_bridge_r1 import ResidentEmberPulseBridge
    from resident_intention_store_r1 import ResidentIntentionStore
    from resident_volition_gate_r1 import ResidentVolitionGate


class ResidentEmberHabitat:
    """Minimal foreground habitat; scheduling remains an external host concern."""

    def __init__(
        self,
        *,
        base_dir: str | Path,
        bridge: Optional[ResidentEmberPulseBridge] = None,
    ):
        self.base_dir = Path(base_dir)
        self.ember = ResidentEmber(base_dir=self.base_dir)
        self.bridge = bridge or ResidentEmberPulseBridge(base_dir=self.base_dir)
        self.volition = ResidentVolitionGate(
            ResidentIntentionStore(self.base_dir / "resident_intentions")
        )

    @staticmethod
    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def tick(
        self,
        *,
        observed_at: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Advance one causal Ember transition and hand off only a new wake."""
        at = observed_at or self.utc_now()
        before = self.ember.wake_packet()
        if before is not None:
            # Fail closed: a prior unhandled wake must be consumed before time
            # can advance again. This preserves one wake -> one governed turn.
            return {
                "schema_version": "resident-ember-habitat-r1",
                "observed_at": at,
                "advanced": False,
                "wake_crossed": False,
                "handoff_presented": False,
                "decision_reason": "unhandled_wake_already_pending",
                "pending_ember_event_hash": before["ember_event_hash"],
                "authority_effect": False,
            }

        event = self.ember.advance(observed_at=at)
        if event.get("wake_requested") is not True:
            return {
                "schema_version": "resident-ember-habitat-r1",
                "observed_at": at,
                "advanced": True,
                "ember_event_hash": event.get("event_hash"),
                "wake_crossed": False,
                "handoff_presented": False,
                "decision_reason": "ember_advanced_without_wake",
                "authority_effect": False,
            }

        volition = self.volition.evaluate(
            resident=event["resident"],
            intention_id=event["intention_id"],
        )
        if not volition.continue_next_moment:
            return {
                "schema_version": "resident-ember-habitat-r1",
                "observed_at": at,
                "advanced": True,
                "ember_event_hash": event.get("event_hash"),
                "wake_crossed": True,
                "handoff_presented": False,
                "decision_reason": "endogenous_wake_inhibited_by_resident_intention_state",
                "volition": volition.to_dict(),
                "authority_effect": False,
            }

        receipt = self.bridge.present_wake(project_id=project_id, observed_at=at)
        return {
            "schema_version": "resident-ember-habitat-r1",
            "observed_at": at,
            "advanced": True,
            "ember_event_hash": event.get("event_hash"),
            "wake_crossed": True,
            "handoff_presented": True,
            "decision_reason": "new_endogenous_wake_presented",
            "volition": volition.to_dict(),
            "bridge_receipt": receipt,
            "authority_effect": False,
        }
