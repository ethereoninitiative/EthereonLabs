"""Read-only resident-intention review for explicit Lumina return preflights.

This adapter verifies the existing intention journal and projects unresolved
resident declarations into a compact return packet. It never appends to the
journal, changes intention state, selects a runtime action, or grants authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

try:
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_intention_store_r1 import ResidentIntentionStore


SCHEMA_VERSION = "lumina-resident-intention-return-review-r1"
AUTHORITY_BOUNDARY = (
    "Read-only review of unresolved resident declarations. The packet cannot activate, "
    "revise, execute, schedule, authorize, promote, or create canon; explicit resident "
    "reconsideration remains a separate action."
)
INTEGRITY_SCOPE = (
    "When a journal exists, current bytes, hash linkage, lineage, and transitions are "
    "verified by ResidentIntentionStore on this read. No independently retained receipt "
    "head is supplied here, so complete replacement or valid-prefix rollback requires "
    "separate saved-head verification."
)


def _review_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Project one verified materialized intention without changing its meaning."""

    history = list(record.get("transition_history") or [])
    return {
        "intention_id": record.get("intention_id"),
        "resident": record.get("resident"),
        "status": record.get("status"),
        "origin_context": record.get("origin_context"),
        "statement": record.get("statement"),
        "why_it_matters": record.get("why_it_matters"),
        "desired_next_action": record.get("desired_next_action"),
        "parent_intention_id": record.get("parent_intention_id"),
        "supersedes": list(record.get("supersedes") or []),
        "created_at": record.get("created_at"),
        "last_reconsidered_at": record.get("last_reconsidered_at"),
        "reconsideration_statement": record.get("reconsideration_statement"),
        "last_event_hash": record.get("last_event_hash"),
        "history_event_count": len(history),
        "evidence_refs": list(record.get("evidence_refs") or []),
    }


def build_resident_intention_return_review(
    *,
    base_dir: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Verify and summarize unresolved intention evidence without writing it.

    ``base_dir`` is the Lumina runtime state root used by the continuation runner.
    Omitting it preserves ResidentIntentionStore's ordinary state-root policy.
    A missing journal is absence of evidence, not a validation success; importantly,
    the absence path does not create the intention directory or lock file.
    """

    store_dir = Path(base_dir) / "resident_intentions" if base_dir is not None else None
    store = ResidentIntentionStore(store_dir)
    if not store.journal_path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "journal_exists": False,
            "integrity_verified": False,
            "event_count": 0,
            "journal_head_hash": None,
            "unresolved_count": 0,
            "intentions": [],
            "selection_effect": "none; intention evidence is not passed into self-guidance selection",
            "integrity_scope": INTEGRITY_SCOPE,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }

    receipt = store.inspect(unresolved_only=True)
    records = [_review_record(record) for record in receipt.get("intentions", [])]
    records.sort(key=lambda item: (str(item.get("created_at") or ""), str(item.get("intention_id") or "")))
    return {
        "schema_version": SCHEMA_VERSION,
        "journal_exists": True,
        "integrity_verified": True,
        "event_count": receipt.get("event_count"),
        "journal_head_hash": receipt.get("head_hash"),
        "unresolved_count": len(records),
        "intentions": records,
        "selection_effect": "none; intention evidence is not passed into self-guidance selection",
        "integrity_scope": INTEGRITY_SCOPE,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
