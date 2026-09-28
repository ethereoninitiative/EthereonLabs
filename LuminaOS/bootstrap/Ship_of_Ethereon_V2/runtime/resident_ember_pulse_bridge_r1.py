"""Resident Ember -> Resident Pulse bridge R1.

Verifies the causal Ember wake against the local Ember journal and the durable
resident intention journal, then presents it to Resident Pulse without operator
force. A later explicit resident reconsideration can be witnessed back into
Ember evidence. The bridge grants no execution or identity authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    from .resident_ember_r1 import ResidentEmber, EmberError
    from .resident_intention_store_r1 import ResidentIntentionStore, IntentionError
    from .lumina_resident_pulse_r1 import LuminaResidentPulse
except ImportError:
    from resident_ember_r1 import ResidentEmber, EmberError
    from resident_intention_store_r1 import ResidentIntentionStore, IntentionError
    from lumina_resident_pulse_r1 import LuminaResidentPulse


class EmberPulseBridgeError(ValueError):
    pass


class ResidentEmberPulseBridge:
    """Narrow causal bridge; verification before attention, never force."""

    def __init__(
        self,
        *,
        base_dir: str | Path,
        pulse: Optional[LuminaResidentPulse] = None,
        intention_store: Optional[ResidentIntentionStore] = None,
    ):
        self.base_dir = Path(base_dir)
        self.ember = ResidentEmber(base_dir=self.base_dir)
        self.pulse = pulse or LuminaResidentPulse(base_dir=self.base_dir)
        self.intentions = intention_store or ResidentIntentionStore(
            self.base_dir / "resident_intentions"
        )

    def _verified_wake(self) -> tuple[dict, dict]:
        packet = self.ember.wake_packet()
        if packet is None:
            raise EmberPulseBridgeError("no Ember wake is available")
        rows = self.ember.store.read()
        matching = [
            row for row in rows
            if row.get("event_hash") == packet.get("ember_event_hash")
            and row.get("wake_requested") is True
        ]
        if len(matching) != 1:
            raise EmberPulseBridgeError("Ember wake packet is not backed by exactly one journal event")
        try:
            inspected = self.intentions.inspect(
                resident=str(packet.get("resident") or ""),
                intention_id=str(packet.get("intention_id") or ""),
                unresolved_only=False,
            )
        except IntentionError as exc:
            raise EmberPulseBridgeError("Ember wake intention is not present in verified intention history") from exc
        records = list(inspected.get("intentions") or [])
        if len(records) != 1:
            raise EmberPulseBridgeError("Ember wake intention did not resolve uniquely")
        intention = records[0]
        if intention.get("status") not in {"proposed", "active", "suspended"}:
            raise EmberPulseBridgeError("Ember wake intention is already resolved")
        return packet, intention

    def present_wake(
        self,
        *,
        project_id: Optional[str] = None,
    ) -> dict[str, Any]:
        packet, intention = self._verified_wake()
        requested_action = str(intention.get("desired_next_action") or "").strip()
        if not requested_action:
            raise EmberPulseBridgeError("verified intention has no desired_next_action")
        result = self.pulse.pulse(
            project_id=project_id,
            requested_action=requested_action,
            force=False,
        )
        return {
            "schema_version": "resident-ember-pulse-bridge-r1",
            "ember_wake": packet,
            "intention_event_hash": intention.get("last_event_hash"),
            "intention_status_at_wake": intention.get("status"),
            "requested_action": requested_action,
            "operator_force_used": False,
            "pulse_receipt": result.receipt,
            "authority": (
                "verified attention handoff only; Pulse and downstream governance retain "
                "all execution authority, and explicit resident reconsideration remains separate"
            ),
        }

    def witness_reconsideration(
        self,
        *,
        reconsideration_receipt: dict,
        observed_at: str,
    ) -> dict:
        packet, _ = self._verified_wake()
        event = dict(reconsideration_receipt.get("event") or {})
        request = dict(event.get("request") or {})
        provenance = dict(event.get("provenance") or {})
        if event.get("operation") != "reconsider":
            raise EmberPulseBridgeError("receipt is not an intention reconsideration")
        if request.get("intention_id") != packet.get("intention_id"):
            raise EmberPulseBridgeError("reconsideration targets a different intention")
        if provenance.get("resident") != packet.get("resident"):
            raise EmberPulseBridgeError("reconsideration resident does not match Ember wake")
        record_hash = event.get("record_hash")
        if not record_hash:
            raise EmberPulseBridgeError("reconsideration receipt has no record hash")
        current = self.intentions.inspect(
            resident=str(packet["resident"]),
            intention_id=str(packet["intention_id"]),
            unresolved_only=False,
        )
        records = list(current.get("intentions") or [])
        if len(records) != 1 or records[0].get("last_event_hash") != record_hash:
            raise EmberPulseBridgeError("reconsideration receipt is not current verified intention state")
        return self.ember.record_reconsideration(
            observed_at=observed_at,
            intention_event_hash=str(record_hash),
            outcome=str(request.get("outcome") or ""),
            status_after=str(records[0].get("status") or ""),
        )
