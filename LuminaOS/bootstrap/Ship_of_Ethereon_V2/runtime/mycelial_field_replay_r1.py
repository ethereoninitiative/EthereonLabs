from __future__ import annotations

"""Optional runtime bridge for non-governing mycelial receipt replay.

The bridge may attach validated coupling provenance to supplemental context. It
never writes governance events, changes action type, exposes capabilities,
promotes canon, or stores coupling context in a checkpoint.
"""

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

try:
    from .mycelial_coupling_receipt_r1 import (
        AUTHORITY_BOUNDARY,
        CouplingReceipt,
        CouplingReceiptLedger,
    )
except Exception:
    from mycelial_coupling_receipt_r1 import (
        AUTHORITY_BOUNDARY,
        CouplingReceipt,
        CouplingReceiptLedger,
    )


SCHEMA_VERSION = "lumina-mycelial-field-replay-v0.1"
CONTEXT_KEY = "mycelial_coupling_replay"
CONTEXT_FIELDS = (
    "schema_version",
    "signal_id",
    "source",
    "destination",
    "relation",
    "created_at",
    "evidence_kind",
    "evidence_reference",
    "evidence_digest",
    "confidence",
    "reversible",
    "authority_effect",
    "memory_effect",
    "retention",
    "effect_summary",
    "parent_receipt",
    "authority_boundary",
    "receipt_hash",
)


class MycelialFieldReplayBridge:
    """Classify optional receipt intake and emit bounded supplemental context."""

    def __init__(self, base_dir: str | Path):
        self.ledger = CouplingReceiptLedger(base_dir)

    @staticmethod
    def absent_result() -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "absent",
            "present": False,
            "input_count": 0,
            "accepted_count": 0,
            "replay_count": 0,
            "quarantine_count": 0,
            "decisions": [],
            "context_receipts": [],
            "authority_effect": False,
            "authority_event_created": False,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }

    @staticmethod
    def _payload(receipt: Any) -> Dict[str, Any]:
        if isinstance(receipt, CouplingReceipt):
            return receipt.to_dict()
        if isinstance(receipt, Mapping):
            return dict(receipt)
        return {}

    @classmethod
    def _context_projection(
        cls,
        payload: Mapping[str, Any],
        *,
        classification: str,
    ) -> Dict[str, Any]:
        projection = {field: payload.get(field) for field in CONTEXT_FIELDS}
        projection["classification"] = classification
        projection["authority_effect"] = False
        projection["authority_event_created"] = False
        return projection

    def ingest(self, receipts: Iterable[Any]) -> Dict[str, Any]:
        inputs = list(receipts)
        if not inputs:
            return self.absent_result()

        decisions: list[Dict[str, Any]] = []
        context_receipts: list[Dict[str, Any]] = []
        for receipt in inputs:
            decision = self.ledger.ingest(receipt)
            decision_payload = decision.to_dict()
            decisions.append(decision_payload)
            if decision.accepted or decision.replay:
                classification = (
                    "historical_replay"
                    if decision.replay
                    else "new_non_governing_evidence"
                )
                context_receipts.append(
                    self._context_projection(
                        self._payload(receipt),
                        classification=classification,
                    )
                )

        accepted_count = sum(1 for row in decisions if row.get("accepted") is True)
        replay_count = sum(1 for row in decisions if row.get("replay") is True)
        quarantine_count = sum(1 for row in decisions if row.get("quarantined") is True)
        if quarantine_count == len(decisions):
            status = "quarantined"
        elif quarantine_count:
            status = "partially_quarantined"
        elif replay_count and not accepted_count:
            status = "historical_replay"
        else:
            status = "accepted"

        return {
            "schema_version": SCHEMA_VERSION,
            "status": status,
            "present": True,
            "input_count": len(inputs),
            "accepted_count": accepted_count,
            "replay_count": replay_count,
            "quarantine_count": quarantine_count,
            "decisions": decisions,
            "context_receipts": context_receipts,
            "ledger_integrity": self.ledger.verify_integrity(),
            "authority_effect": False,
            "authority_event_created": False,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }

    @staticmethod
    def attach_to_context_bundle(
        context_bundle: Mapping[str, Any],
        replay_result: Mapping[str, Any],
    ) -> Dict[str, Any]:
        payload = dict(context_bundle)
        supplemental = dict(payload.get("supplemental_ethereonic_context") or {})

        # The key is reserved for validated bridge output. Caller-provided data
        # under this key is discarded rather than treated as field evidence.
        supplemental.pop(CONTEXT_KEY, None)
        context_receipts = list(replay_result.get("context_receipts") or [])
        if context_receipts:
            supplemental[CONTEXT_KEY] = {
                "schema_version": SCHEMA_VERSION,
                "status": replay_result.get("status"),
                "receipts": context_receipts,
                "authority_effect": False,
                "authority_event_created": False,
                "authority_boundary": AUTHORITY_BOUNDARY,
            }
        payload["supplemental_ethereonic_context"] = supplemental
        return payload
