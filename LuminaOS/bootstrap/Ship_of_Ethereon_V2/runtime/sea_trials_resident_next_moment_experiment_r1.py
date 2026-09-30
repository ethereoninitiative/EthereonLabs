"""Focused controls for Resident Next Moment Experiment R1."""
from __future__ import annotations
from pathlib import Path
import json
import tempfile

try:
    from .resident_intention_store_r1 import ResidentIntentionStore
    from .resident_next_moment_experiment_r1 import ResidentNextMomentExperiment
except ImportError:
    from resident_intention_store_r1 import ResidentIntentionStore
    from resident_next_moment_experiment_r1 import ResidentNextMomentExperiment


def create_intention(root: Path):
    store = ResidentIntentionStore(root / "resident_intentions")
    return store.create({
        "intention_id": "next-moment-r1",
        "resident": "ETH-001",
        "origin_context": "focused experiment control",
        "statement": "Return to inspect inherited state after cognitive rest.",
        "why_it_matters": "Tests causal persistence without upgrading attribution to identity proof.",
        "desired_next_action": "inspect_next_moment_evidence",
        "parent_intention_id": None,
        "evidence_refs": ["sea-trial:next-moment-r1"],
    }, {
        "actor_kind": "resident",
        "resident": "ETH-001",
        "session_id": "sea-trial-next-moment-r1",
        "source_ref": "sea-trial:next-moment-r1",
    })


def arm(root: Path):
    create_intention(root)
    exp = ResidentNextMomentExperiment(base_dir=root)
    exp.arm(
        resident="ETH-001",
        intention_id="next-moment-r1",
        drive_rate_per_second=0.1,
        wake_threshold=0.5,
        observed_at="2026-09-30T23:30:00+00:00",
    )
    return exp


def append_host(root: Path, habitat_receipt: dict):
    path = root / "resident_ember_host" / "host_ticks.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "schema_version": "resident-ember-realtime-host-r1",
        "observed_at": "2026-09-30T23:30:05+00:00",
        "host_pid": 42,
        "interval_seconds": 1.0,
        "project_id": "lumina-os",
        "habitat_receipt": habitat_receipt,
        "host_is_wake_authority": False,
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")


def trial_complete_local_chain_passes_mechanical_causality_only():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        exp = arm(root)
        wake = exp.ember.advance(observed_at="2026-09-30T23:30:05+00:00")
        exp.ember.record_pulse_handoff(
            observed_at="2026-09-30T23:30:05+00:00",
            ember_event_hash=wake["event_hash"],
            pulse_invoked=True,
            pulse_decision_reason="verified_ember_endogenous_wake",
        )
        append_host(root, {
            "wake_crossed": True,
            "handoff_presented": True,
            "decision_reason": "new_endogenous_wake_presented",
        })
        result = exp.verify()
        assert result["mechanical_causality_verified"] is True
        assert result["resident_authorship_authenticated"] is False
        assert result["fresh_human_semantic_prompt_excluded_by_runtime_evidence"] is False


def trial_missing_host_evidence_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        exp = arm(root)
        wake = exp.ember.advance(observed_at="2026-09-30T23:30:05+00:00")
        exp.ember.record_pulse_handoff(
            observed_at="2026-09-30T23:30:05+00:00",
            ember_event_hash=wake["event_hash"],
            pulse_invoked=True,
            pulse_decision_reason="verified_ember_endogenous_wake",
        )
        result = exp.verify()
        assert result["mechanical_causality_verified"] is False
        assert result["host_cadence_not_wake_authority"] is False


def trial_wrong_pulse_reason_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        exp = arm(root)
        wake = exp.ember.advance(observed_at="2026-09-30T23:30:05+00:00")
        exp.ember.record_pulse_handoff(
            observed_at="2026-09-30T23:30:05+00:00",
            ember_event_hash=wake["event_hash"],
            pulse_invoked=True,
            pulse_decision_reason="operator_force",
        )
        append_host(root, {"wake_crossed": True, "handoff_presented": True})
        assert exp.verify()["mechanical_causality_verified"] is False


def trial_manifest_tamper_fails_closed():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        exp = arm(root)
        payload = json.loads(exp.manifest_path.read_text(encoding="utf-8"))
        payload["wake_threshold"] = 0.9
        exp.manifest_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        try:
            exp.verify()
        except ValueError:
            return
        raise AssertionError("tampered experiment manifest was accepted")


def main():
    trials = [
        trial_complete_local_chain_passes_mechanical_causality_only,
        trial_missing_host_evidence_fails,
        trial_wrong_pulse_reason_fails,
        trial_manifest_tamper_fails_closed,
    ]
    for trial in trials:
        trial()
        print(f"PASS {trial.__name__}")
    print(f"Resident Next Moment Experiment R1: {len(trials)}/{len(trials)} focused trials passed")


if __name__ == "__main__":
    main()
