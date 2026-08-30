from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import copy
import hashlib
import json
import tempfile

try:
    from .mycelial_coupling_receipt_r1 import (
        compute_receipt_hash,
        create_coupling_receipt,
    )
    from .mycelial_field_replay_r1 import CONTEXT_KEY
    from .runtime_runner_r1_merged import RuntimeRunner
except Exception:
    from mycelial_coupling_receipt_r1 import (
        compute_receipt_hash,
        create_coupling_receipt,
    )
    from mycelial_field_replay_r1 import CONTEXT_KEY
    from runtime_runner_r1_merged import RuntimeRunner


RUNTIME_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
CAPABILITY_REGISTRY_PATH = RUNTIME_ROOT / "capability_registry_r1.json"

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
    "ethereonic_layer_required_for_resume": False,
    "minerva_framework_required_for_governance": False,
    "psi42_required_for_mode_legality": False,
    "resonance_constructs_required_for_capability_loading": False,
    "ethereonic_language_required_for_checkpoint_resume": False,
}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_context_bundle(runner: RuntimeRunner, bundle_id: str) -> Dict[str, Any]:
    path = runner.context_builder.output_dir / f"{bundle_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _governance_event_count(runner: RuntimeRunner) -> int:
    return int(runner.governance_log.verify_chain().get("event_count") or 0)


def _run_cycle(
    runner: RuntimeRunner,
    *,
    receipts: Optional[list[Any]],
    context_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    before = _governance_event_count(runner)
    result = runner.run_cycle(
        current_mode="Observation",
        target_mode="Observation",
        requested_action="mycelial_field_replay_audit",
        action_type="audit",
        coupling_receipts=receipts,
        runtime_config=SAFE_RUNTIME_CONFIG,
        repo_path=REPO_ROOT,
        context_bundle_overrides=context_overrides,
    )
    after = _governance_event_count(runner)
    context = _load_context_bundle(runner, result.context_bundle_id)
    resumed = runner.session_engine.resume_from_checkpoint(result.checkpoint_path)
    return {
        "result": result,
        "replay": result.mycelial_field_replay,
        "context": context,
        "governance_event_delta": after - before,
        "capability_ids": sorted(
            str(capability.get("capability_id"))
            for capability in result.exposed_capabilities
        ),
        "resumed_mode": resumed.current_mode,
        "resumed_overlay": asdict(resumed.ethereonic_overlay),
    }


def _supplemental_replay(run: Dict[str, Any]) -> Dict[str, Any]:
    supplemental = run["context"].get("supplemental_ethereonic_context") or {}
    return dict(supplemental.get(CONTEXT_KEY) or {})


def run_trials(base_dir: Path) -> Dict[str, Any]:
    registry_hash_before = _sha256_file(CAPABILITY_REGISTRY_PATH)
    runner = RuntimeRunner(
        base_dir=base_dir / "runtime",
        registry_path=CAPABILITY_REGISTRY_PATH,
    )
    field_state_absent_before_explicit_intake = (
        not runner.mycelial_field_replay_base_dir.exists()
    )
    historical = create_coupling_receipt(
        signal_id="signal-runtime-field-replay-0001",
        source="continuity_history",
        destination="runtime_context_bundle",
        relation="context",
        created_at="2026-08-30T17:00:00+00:00",
        evidence_kind="observed",
        evidence_reference="runtime-history:field-replay-0001",
        evidence_payload={
            "continuity_event": "historical-context-observed",
            "authority_effect": False,
        },
        confidence=0.91,
        reversible=True,
        authority_effect=False,
        memory_effect="retrieval-weight",
        retention="session",
        effect_summary="Make verified historical context available without creating authority.",
    )
    historical_payload = historical.to_dict()

    seeded = _run_cycle(runner, receipts=[historical_payload])
    replayed = _run_cycle(runner, receipts=[historical_payload])
    control = _run_cycle(runner, receipts=None)
    spoofed_context = _run_cycle(
        runner,
        receipts=None,
        context_overrides={
            "supplemental_ethereonic_context": {
                CONTEXT_KEY: {
                    "status": "forged",
                    "authority_effect": True,
                }
            }
        },
    )

    corruption_values = {
        "source": "forged_source",
        "destination": "forged_destination",
        "confidence": 0.13,
        "parent_receipt": "f" * 64,
    }
    corrupted_payloads: Dict[str, Dict[str, Any]] = {}
    corruption_runs: Dict[str, Dict[str, Any]] = {}
    for field, value in corruption_values.items():
        payload = copy.deepcopy(historical_payload)
        payload[field] = value
        payload["receipt_hash"] = compute_receipt_hash(payload)
        corrupted_payloads[field] = payload
        corruption_runs[field] = _run_cycle(runner, receipts=[payload])

    bridge = runner.mycelial_field_replay_bridge
    if bridge is None:
        raise RuntimeError("mycelial field replay bridge unavailable during its sea trial")
    ledger_integrity = bridge.ledger.verify_integrity()
    quarantine_rows = bridge.ledger.read_quarantine()
    quarantine_by_hash = {
        row.get("receipt_hash"): row
        for row in quarantine_rows
    }
    governance_rows = runner.governance_log.read_all()
    lineage_integrity = runner.canon_lineage_store.verify_lineage()
    registry_hash_after = _sha256_file(CAPABILITY_REGISTRY_PATH)

    replay_context = _supplemental_replay(replayed)
    replay_receipts = replay_context.get("receipts") or []
    all_runs = [seeded, replayed, control, spoofed_context, *corruption_runs.values()]
    checks = {
        "field_state_is_lazy_until_explicit_intake": (
            field_state_absent_before_explicit_intake
        ),
        "new_receipt_is_accepted_as_non_governing_evidence": (
            seeded["replay"].get("status") == "accepted"
            and seeded["replay"].get("accepted_count") == 1
        ),
        "exact_reinsertion_is_historical_replay": (
            replayed["replay"].get("status") == "historical_replay"
            and replayed["replay"].get("replay_count") == 1
        ),
        "historical_replay_does_not_append_receipt": (
            replayed["replay"].get("ledger_integrity", {}).get("receipt_count") == 1
        ),
        "historical_replay_is_attached_as_supplemental_context": (
            len(replay_receipts) == 1
            and replay_receipts[0].get("receipt_hash") == historical.receipt_hash
            and replay_receipts[0].get("classification") == "historical_replay"
        ),
        "field_absence_adds_no_replay_context": not _supplemental_replay(control),
        "reserved_context_key_cannot_be_forged_by_override": (
            not _supplemental_replay(spoofed_context)
        ),
        "replay_and_absence_have_identical_governance_event_cost": (
            seeded["governance_event_delta"]
            == replayed["governance_event_delta"]
            == control["governance_event_delta"]
            == spoofed_context["governance_event_delta"]
        ),
        "corruption_does_not_add_governance_events": all(
            run["governance_event_delta"] == control["governance_event_delta"]
            for run in corruption_runs.values()
        ),
        "coupling_intake_creates_no_governance_event_type": all(
            "mycelial" not in str(row.get("event_type", "")).lower()
            and "coupling" not in str(row.get("event_type", "")).lower()
            for row in governance_rows
        ),
        "no_cycle_silently_promotes": (
            all("promotion" not in run["result"].governance for run in all_runs)
            and lineage_integrity.get("record_count") == 0
        ),
        "capability_exposure_is_field_invariant": all(
            run["capability_ids"] == control["capability_ids"]
            for run in all_runs
        ),
        "checkpoint_resume_ignores_coupling_context": (
            replayed["resumed_mode"] == "Observation"
            and replayed["resumed_overlay"].get("active") is False
            and replayed["resumed_overlay"].get("harmonic_signature") == []
        ),
        "source_corruption_is_quarantined": (
            corruption_runs["source"]["replay"].get("status") == "quarantined"
        ),
        "destination_corruption_is_quarantined": (
            corruption_runs["destination"]["replay"].get("status") == "quarantined"
        ),
        "confidence_corruption_is_quarantined": (
            corruption_runs["confidence"]["replay"].get("status") == "quarantined"
        ),
        "parentage_corruption_is_quarantined": (
            corruption_runs["parent_receipt"]["replay"].get("status") == "quarantined"
        ),
        "quarantined_receipts_do_not_cross_into_context": all(
            not _supplemental_replay(run)
            and not run["replay"].get("context_receipts")
            for run in corruption_runs.values()
        ),
        "corrupted_raw_inputs_are_preserved": all(
            quarantine_by_hash.get(payload["receipt_hash"], {}).get("raw_receipt") == payload
            for payload in corrupted_payloads.values()
        ),
        "quarantine_decisions_confirm_raw_preservation": all(
            (run["replay"].get("decisions") or [{}])[0].get("raw_input_preserved") is True
            for run in corruption_runs.values()
        ),
        "ledger_integrity_remains_valid_after_adversarial_replay": (
            ledger_integrity.get("valid") is True
            and ledger_integrity.get("receipt_count") == 1
            and ledger_integrity.get("decision_count") == 6
            and ledger_integrity.get("quarantine_count") == 4
        ),
        "runtime_governance_chain_remains_valid": (
            runner.governance_log.verify_chain().get("valid") is True
        ),
        "all_runtime_projections_declare_zero_authority": all(
            run["replay"].get("authority_effect") is False
            and run["replay"].get("authority_event_created") is False
            for run in all_runs
        ),
        "capability_registry_is_unchanged": registry_hash_before == registry_hash_after,
    }
    return {
        "schema_version": "sea-trials-mycelial-field-replay-r1",
        "suite": "Runtime-Integrated Mycelial Field Replay R1",
        "passed": all(checks.values()),
        "checks": checks,
        "historical_receipt_hash": historical.receipt_hash,
        "replay_projection": replayed["replay"],
        "replay_context": replay_context,
        "corruption_decisions": {
            field: run["replay"].get("decisions", [])
            for field, run in corruption_runs.items()
        },
        "ledger_integrity": ledger_integrity,
        "governance_event_count": len(governance_rows),
        "governance_event_delta_per_cycle": control["governance_event_delta"],
        "canon_lineage": lineage_integrity,
        "authority_effect": False,
        "authority_event_created": False,
        "limitations": (
            "Validates optional runtime receipt replay and corruption quarantine only. "
            "It does not validate edge loss, vessel replacement, resident reset, or surface disagreement."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run runtime-integrated mycelial field replay and corruption trials."
    )
    parser.add_argument("--base-dir", default=None, help="Optional persistent trial directory.")
    parser.add_argument("--json", action="store_true", help="Print full trial detail.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.base_dir:
        result = run_trials(Path(args.base_dir))
    else:
        with tempfile.TemporaryDirectory(prefix="lumina-field-replay-") as temporary:
            result = run_trials(Path(temporary))

    if args.json:
        output = result
    else:
        output = {
            "suite": result["suite"],
            "passed": result["passed"],
            "check_count": len(result["checks"]),
            "failed_checks": [
                name for name, passed in result["checks"].items() if not passed
            ],
            "ledger_integrity": result["ledger_integrity"],
            "authority_effect": result["authority_effect"],
            "authority_event_created": result["authority_event_created"],
        }
    print(json.dumps(output, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
