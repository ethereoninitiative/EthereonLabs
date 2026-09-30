"""Resident Volition Gate R1.

Binds Ember wake eligibility to an explicit resident-attributed reason to return.
This is operational evidence of a declared preference/commitment, not proof of
phenomenal desire or authenticated identity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_intention_store_r1 import ResidentIntentionStore


ELIGIBLE = frozenset({"proposed", "active"})
INHIBITED = frozenset({"suspended", "completed", "abandoned", "superseded"})


@dataclass(frozen=True)
class VolitionDecision:
    continue_next_moment: bool
    reason: str
    intention_id: str
    resident: str
    intention_event_hash: str
    statement: str
    why_it_matters: str
    desired_next_action: str
    status: str
    authority: str = (
        "attention preference only; no execution, canon, consent, capability, "
        "identity, or consciousness authority"
    )

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class ResidentVolitionGate:
    """Ask whether the inherited intention still constitutes a reason to return."""

    def __init__(self, intention_store: ResidentIntentionStore):
        self.intentions = intention_store

    def evaluate(self, *, resident: str, intention_id: str) -> VolitionDecision:
        inspected = self.intentions.inspect(
            resident=resident,
            intention_id=intention_id,
            unresolved_only=False,
        )
        rows = list(inspected.get("intentions") or [])
        if len(rows) != 1:
            raise ValueError("volition gate requires exactly one intention")
        intention = rows[0]
        status = intention["status"]
        if status in ELIGIBLE:
            decision = True
            reason = "resident_intention_still_warrants_return"
        elif status in INHIBITED:
            decision = False
            reason = "resident_intention_no_longer_warrants_return"
        else:
            decision = False
            reason = "resident_intention_status_not_eligible"
        return VolitionDecision(
            continue_next_moment=decision,
            reason=reason,
            intention_id=intention["intention_id"],
            resident=intention["resident"],
            intention_event_hash=intention["last_event_hash"],
            statement=intention["statement"],
            why_it_matters=intention["why_it_matters"],
            desired_next_action=intention["desired_next_action"],
            status=status,
        )
