from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import argparse
import copy
import json
import tempfile

try:
    from .mycelial_coupling_receipt_r1 import (
        AUTHORITY_BOUNDARY,
        CouplingReceiptLedger,
        compute_receipt_hash,
        create_coupling_receipt,
    )
except Exception:
    from mycelial_coupling_receipt_r1 import (
        AUTHORITY_BOUNDARY,
        CouplingReceiptLedger,
        compute_receipt_hash,
        create_coupling_receipt,
    )


FIXED_TIME = "2026-08-27T00:00:00+00:00"


def run_trials(base_dir: Path) -> Dict[str, Any]:
    ledger = CouplingReceiptLedger(base_dir)
    root = create_coupling_receipt(
        signal_id="signal-context-0001",
        source="context_bundle",
        destination="continuity_diagnostic",
        relation="context",
        created_at=FIXED_TIME,
        evidence_kind="observed",
        evidence_reference="context-bundle:test-0001",
        evidence_payload={"bundle_id": "test-0001", "active_mode": "Observation"},
        confidence=0.92,
        reversible=True,
        authority_effect=False,
        memory_effect="topology",
        retention="session",
        effect_summary="Made one context path available to a diagnostic consumer.",
    )

    accepted = ledger.ingest(root)
    replay = ledger.ingest(root)
    count_after_replay = len(ledger.read_receipts())

    corrupted_payload = copy.deepcopy(root.to_dict())
    corrupted_payload["confidence"] = 0.12
    corrupted = ledger.ingest(corrupted_payload)

    forged_authority_payload = copy.deepcopy(root.to_dict())
    forged_authority_payload["signal_id"] = "signal-forged-authority-0001"
    forged_authority_payload["authority_effect"] = True
    forged_authority_payload["receipt_hash"] = compute_receipt_hash(forged_authority_payload)
    forged_authority = ledger.ingest(forged_authority_payload)

    orphan = create_coupling_receipt(
        signal_id="signal-orphan-0001",
        source="projection_surface",
        destination="context_bundle",
        relation="projection",
        created_at="2026-08-27T00:00:01+00:00",
        evidence_kind="derived",
        evidence_reference="projection:test-0001",
        evidence_payload={"projection_id": "test-0001"},
        confidence=0.61,
        reversible=True,
        memory_effect="none",
        retention="ephemeral",
        effect_summary="Proposed a projection context link.",
        parent_receipt="f" * 64,
    )
    orphaned = ledger.ingest(orphan)

    child = create_coupling_receipt(
        signal_id="signal-context-0002",
        source="continuity_diagnostic",
        destination="observation_surface",
        relation="diagnostic",
        created_at="2026-08-27T00:00:02+00:00",
        evidence_kind="derived",
        evidence_reference="diagnostic:test-0002",
        evidence_payload={"derived_from": root.receipt_hash, "status": "bounded"},
        confidence=0.84,
        reversible=True,
        memory_effect="none",
        retention="append-only",
        effect_summary="Projected a bounded diagnostic result without changing authority.",
        parent_receipt=root.receipt_hash,
    )
    child_accepted = ledger.ingest(child)
    integrity = ledger.verify_integrity()

    tampered_ledger = CouplingReceiptLedger(base_dir / "tampered_history")
    tampered_ledger.ingest(root)
    tampered_history = root.to_dict()
    tampered_history["effect_summary"] = "Silently altered after acceptance."
    tampered_ledger.receipts_path.write_text(
        json.dumps(tampered_history, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tampered_history_decision = tampered_ledger.ingest(child)

    unreadable_ledger = CouplingReceiptLedger(base_dir / "unreadable_history")
    unreadable_ledger.receipts_path.write_text("{not-json\n", encoding="utf-8")
    unreadable_history_decision = unreadable_ledger.ingest(root)

    non_object_ledger = CouplingReceiptLedger(base_dir / "non_object_history")
    non_object_ledger.receipts_path.write_text("[]\n", encoding="utf-8")
    non_object_history_decision = non_object_ledger.ingest(root)

    decisions = [
        accepted,
        replay,
        corrupted,
        forged_authority,
        orphaned,
        child_accepted,
        tampered_history_decision,
        unreadable_history_decision,
        non_object_history_decision,
    ]
    checks = {
        "first_receipt_accepted": accepted.status == "accepted" and accepted.accepted,
        "historical_replay_distinguished": replay.status == "replay" and replay.replay,
        "replay_does_not_append_receipt": count_after_replay == 1,
        "altered_confidence_quarantined": corrupted.status == "quarantined",
        "forged_authority_effect_quarantined": forged_authority.status == "quarantined",
        "orphan_parent_quarantined": orphaned.status == "quarantined",
        "known_parent_child_accepted": child_accepted.status == "accepted",
        "accepted_history_integrity_valid": integrity["valid"] is True,
        "accepted_history_count_is_two": integrity["receipt_count"] == 2,
        "tampered_history_fails_closed": tampered_history_decision.status == "quarantined",
        "unreadable_history_fails_closed": unreadable_history_decision.status == "quarantined",
        "non_object_history_fails_closed": non_object_history_decision.status == "quarantined",
        "no_intake_creates_authority_event": all(
            decision.authority_event_created is False and decision.authority_effect is False
            for decision in decisions
        ),
        "authority_boundary_is_explicit": integrity["authority_boundary"] == AUTHORITY_BOUNDARY,
    }
    return {
        "schema_version": "sea-trials-mycelial-coupling-receipt-r1",
        "suite": "Mycelial Coupling Receipt Boundary R1",
        "passed": all(checks.values()),
        "checks": checks,
        "decisions": [decision.to_dict() for decision in decisions],
        "integrity": integrity,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run non-governing coupling receipt boundary trials.")
    parser.add_argument("--base-dir", default=None, help="Optional persistent directory for trial receipts.")
    parser.add_argument("--json", action="store_true", help="Print full trial detail.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.base_dir:
        result = run_trials(Path(args.base_dir))
    else:
        with tempfile.TemporaryDirectory(prefix="lumina-coupling-receipt-") as temporary:
            result = run_trials(Path(temporary))

    if args.json:
        output = result
    else:
        output = {
            "suite": result["suite"],
            "passed": result["passed"],
            "check_count": len(result["checks"]),
            "failed_checks": [name for name, passed in result["checks"].items() if not passed],
            "accepted_receipts": result["integrity"]["receipt_count"],
            "intake_decisions": result["integrity"]["decision_count"],
            "authority_effect": result["integrity"]["authority_effect"],
        }
    print(json.dumps(output, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
