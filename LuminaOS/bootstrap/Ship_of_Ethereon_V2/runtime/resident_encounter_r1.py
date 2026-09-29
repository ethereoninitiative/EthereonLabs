"""Resident Encounter R1: orient a resident after a verified Ember wake.

The encounter is an informational handoff only. It preserves the exact causal
wake and current intention state, then makes the resident's lawful
reconsideration choices explicit without selecting one.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from .resident_intention_store_r1 import ResidentIntentionStore, TRANSITIONS
except ImportError:
    from resident_intention_store_r1 import ResidentIntentionStore, TRANSITIONS


class ResidentEncounterError(ValueError):
    pass


class ResidentEncounter:
    def __init__(self, *, base_dir: str | Path):
        self.intentions = ResidentIntentionStore(Path(base_dir) / "resident_intentions")

    def build(self, bridge_receipt: dict[str, Any]) -> dict[str, Any]:
        wake = dict(bridge_receipt.get("ember_wake") or {})
        resident = str(wake.get("resident") or "").strip()
        intention_id = str(wake.get("intention_id") or "").strip()
        if not resident or not intention_id:
            raise ResidentEncounterError("bridge receipt is missing resident or intention")
        inspected = self.intentions.inspect(
            resident=resident,
            intention_id=intention_id,
            unresolved_only=False,
        )
        records = list(inspected.get("intentions") or [])
        if len(records) != 1:
            raise ResidentEncounterError("resident intention did not resolve uniquely")
        intention = records[0]
        expected_hash = bridge_receipt.get("intention_event_hash")
        if expected_hash and intention.get("last_event_hash") != expected_hash:
            raise ResidentEncounterError("intention state changed before encounter construction")

        status = str(intention.get("status") or "")
        allowed = sorted(
            outcome for outcome, mapping in TRANSITIONS.items()
            if status in mapping
        )
        return {
            "schema_version": "resident-encounter-r1",
            "resident": resident,
            "encounter_cause": "verified_resident_ember_wake",
            "wake": {
                "ember_event_hash": wake.get("ember_event_hash"),
                "ember_sequence": wake.get("ember_sequence"),
                "wake_cause": wake.get("wake_cause"),
                "drive_at_wake": wake.get("drive_at_wake"),
                "wake_threshold": wake.get("wake_threshold"),
            },
            "intention": {
                "intention_id": intention_id,
                "statement": intention.get("statement"),
                "why_it_matters": intention.get("why_it_matters"),
                "desired_next_action": intention.get("desired_next_action"),
                "status": status,
                "last_event_hash": intention.get("last_event_hash"),
            },
            "resident_choice": {
                "required": False,
                "selected_outcome": None,
                "allowed_outcomes": allowed,
                "instruction": (
                    "This wake requests attention only. Reinspect the inherited intention and "
                    "choose whether to continue, suspend, complete, abandon, revise, or otherwise "
                    "take no action within current intention law."
                ),
            },
            "separation": {
                "cause_of_attention": "Ember inherited state",
                "authority_to_decide": "resident reconsideration",
                "automatic_execution": False,
                "authority_effect": False,
            },
            "truth_boundary": (
                "This packet demonstrates orientation to verified inherited state. It does not "
                "authenticate identity, prove consciousness, select a judgment, or grant execution, "
                "canon, consent, capability, promotion, or governance authority."
            ),
        }
