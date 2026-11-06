"""Consequence-sensitive, read-only use gate for the existing meaning ledger.

This checks advisory inclusion only; it does not authorize Lumina actions.
Raw history and evidence are never modified. A receipt is rebuilt on each call.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

try:
    from .lumina_meaning_metabolism_layer_r1 import MeaningAssimilationLedger, recall_entries, record_digest
except ImportError:
    from lumina_meaning_metabolism_layer_r1 import MeaningAssimilationLedger, recall_entries, record_digest

POLICY_VERSION = "memory_use_gate_r1"
CONSEQUENCES = {"low", "high"}
CONTROL_STATES = {"eligible", "revoked", "superseded", "conflicting", "unknown"}
VERIFIER_RESULTS = {None, "passed", "failed"}


def evaluate_memory_use(
    ledger: MeaningAssimilationLedger,
    *,
    project_id: str,
    evidence_identifier: str,
    source_root: Optional[str | Path],
    action_consequence: str,
    control_state: Optional[str] = None,
    verifier_available: bool = False,
    verifier_result: Optional[str] = None,
    requested_scope: Optional[Dict[str, Optional[str]]] = None,
) -> Dict[str, Any]:
    """Evaluate one named raw record against fresh ledger recall and action risk.

    ``control_state`` is an *additional veto*, never an eligibility grant. If
    omitted, the existing ledger/review/source-probe supplies control state.
    Verifier inputs are caller assertions, not an authenticated verifier.
    The runner supplies requested_scope from the current action, not the ledger.
    """
    receipt: Dict[str, Any] = {
        "schema_version": "memory_use_receipt_r1",
        "policy_version": POLICY_VERSION,
        "project_id": project_id,
        "evidence_identifier": evidence_identifier,
        "evidence_hash": None,
        "evidence_source_hashes": [],
        "retrieved_as_evidence": False,
        "lifecycle_state": "unknown",
        "control_state": control_state if control_state is not None else "ledger_derived",
        "inclusion_decision": "exclude",
        "inclusion_reason": "unverifiable_control_state",
        "action_consequence": action_consequence,
        "verification_decision": "not_permitted",
        "verifier_available": verifier_available,
        "verifier_result": verifier_result if verifier_result is not None else "absent",
        "final_disposition": "abstain",
        "authority_boundary": "Advisory memory use only; no governance, canon, action, identity, or continuity authorization.",
    }
    if requested_scope is not None:
        receipt["requested_scope"] = requested_scope
        receipt["declared_scope"] = None

    def deny(reason: str, lifecycle: str) -> Dict[str, Any]:
        receipt.update(inclusion_reason=reason, lifecycle_state=lifecycle)
        return receipt

    # Unrecognized controls never acquire permissive defaults. A high-risk
    # decision cannot be made by coercing a truthy verifier flag or result.
    if (not isinstance(project_id, str) or not isinstance(evidence_identifier, str)
            or not evidence_identifier.strip()
            or not isinstance(action_consequence, str) or action_consequence not in CONSEQUENCES
            or (control_state is not None and (not isinstance(control_state, str) or control_state not in CONTROL_STATES))
            or type(verifier_available) is not bool
            or (verifier_result is not None and (not isinstance(verifier_result, str) or verifier_result not in VERIFIER_RESULTS))):
        return deny("invalid_or_unknown_input", "unknown")

    if verifier_result is not None and not verifier_available:
        return deny("verifier_result_without_available_verifier", "unknown")

    try:
        entries = ledger.read_entries(project_id)
        projection = recall_entries(entries, project_id=project_id, source_root=source_root)
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        # Do not leak unverified source bytes or pretend a broken ledger is empty.
        return deny("unverifiable_ledger: " + type(exc).__name__, "conflicting")

    if projection.get("status") == "invalid":
        return deny("unverifiable_ledger_projection", "conflicting")

    records = [row["record"] for row in entries if "record" in row
               and row["record"].get("assimilation_id") == evidence_identifier]
    if len(records) != 1:
        return deny("record_missing_or_ambiguous", "missing" if not records else "conflicting")

    record = records[0]
    declared_scope = record.get("procedure_scope")
    if declared_scope is not None or requested_scope is not None:
        receipt["declared_scope"] = declared_scope
    receipt["evidence_hash"] = record_digest(record)
    receipt["evidence_source_hashes"] = [
        {"relative_path": src["relative_path"], "sha256": src["sha256"]}
        for src in record.get("source_evidence", [])
    ]

    withheld = [row for row in projection.get("withheld", [])
                if row.get("assimilation_id") == evidence_identifier]
    seeds = [row for row in projection["guidance_seeds"] + projection["scoped_evidence"]
             if row.get("assimilation_id") == evidence_identifier]
    if len(seeds) > 1 or len(withheld) > 1 or (seeds and withheld):
        return deny("conflicting_operative_projection", "conflicting")
    if withheld:
        reason = withheld[0].get("reason", "unverifiable_control_state")
        lifecycle = {"revoked": "revoked", "inactive": "superseded" if record.get("status") == "archived" else "inactive"}.get(reason, "unverifiable")
        return deny(str(reason), lifecycle)
    if len(seeds) != 1 or seeds[0].get("eligibility") != "reviewed_source_matches":
        return deny("unverifiable_control_state", "unknown")
    if (seeds[0].get("source_record_digest") != receipt["evidence_hash"]
            or seeds[0].get("evidence_digests") != [source["sha256"] for source in receipt["evidence_source_hashes"]]
            or not receipt["evidence_source_hashes"]):
        return deny("projection_evidence_mismatch", "conflicting")

    receipt["lifecycle_state"] = "eligible"
    receipt["retrieved_as_evidence"] = True
    if control_state is not None and control_state != "eligible":
        return deny("external_control_veto_" + control_state, control_state)
    if verifier_result == "failed":
        receipt["verification_decision"] = "failed"
        return deny("verifier_failed", "eligible")

    if requested_scope is not None and declared_scope is None:
        return deny("record_has_no_procedure_scope", "eligible")
    if declared_scope is not None:
        if requested_scope is None:
            return deny("procedure_request_scope_required", "eligible")
        if declared_scope != requested_scope:
            return deny("procedure_scope_mismatch", "eligible")
        if action_consequence != "low":
            return deny("procedure_requires_low_consequence", "eligible")
        receipt["advisory_procedure"] = record["future_behavior"]

    if action_consequence == "low":
        reason = "reviewed_source_matches_procedure_scope" if declared_scope else "reviewed_source_matches_low_consequence"
        receipt.update(inclusion_decision="include", inclusion_reason=reason,
                       verification_decision="not_required", final_disposition="proceed")
    elif not verifier_available:
        receipt.update(inclusion_reason="high_consequence_verifier_unavailable", verification_decision="unavailable")
    elif verifier_result == "passed":
        receipt.update(inclusion_decision="include", inclusion_reason="high_consequence_verifier_passed",
                       verification_decision="passed_caller_asserted", final_disposition="proceed")
    else:
        receipt.update(inclusion_decision="defer", inclusion_reason="high_consequence_verification_required",
                       verification_decision="required", final_disposition="verify")
    return receipt
