"""Integration sea trial for read-only resident-intention return review."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil
import subprocess
import sys

try:
    from .runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
    from .resident_intention_store_r1 import ResidentIntentionStore
    from .lumina_intention_return_review_r1 import build_resident_intention_return_review
except Exception:
    from runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
    from resident_intention_store_r1 import ResidentIntentionStore
    from lumina_intention_return_review_r1 import build_resident_intention_return_review

try:
    from .repo_paths_r1 import state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import state_root as _state_root_helper
    except Exception:
        _state_root_helper = None


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            candidate = Path(_state_root_helper()).resolve()
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            candidate = parent / ".lumina_state" / "ship_of_ethereon_v2"
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
    candidate = Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = infer_state_root() / "sea_trials_lumina_intention_return_review_r1"
PROJECT_ID = "lumina-intention-return-review-test"
SEED_ACTION = "preserve_return_context"

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

FEATURE_FLAGS = [
    "ETHEREON_OBSERVATION",
    "ETHEREON_CONTINUITY_RESTORE",
    "ETHEREON_LUMINA_HOST",
    "ETHEREON_SELF_GUIDANCE",
]


def provenance(session_id: str) -> Dict[str, str]:
    return {
        "actor_kind": "resident",
        "resident": "Minerva",
        "session_id": session_id,
        "source_ref": "sea_trials_lumina_intention_return_review_r1:synthetic-fixture",
    }


def definition(ident: str, statement: str) -> Dict[str, Any]:
    return {
        "intention_id": ident,
        "resident": "Minerva",
        "origin_context": "Synthetic return-review sea trial; no subjective continuity claim.",
        "statement": statement,
        "why_it_matters": "A returning runtime should be able to inspect preserved reasons without granting them authority.",
        "desired_next_action": "Review the declaration and leave any reconsideration explicit.",
        "parent_intention_id": None,
        "evidence_refs": ["sea-trial:return-review-origin"],
    }


def reconsideration(record: Dict[str, Any], outcome: str) -> Dict[str, Any]:
    return {
        "intention_id": record["intention_id"],
        "expected_event_hash": record["last_event_hash"],
        "outcome": outcome,
        "reconsideration_statement": f"Synthetic fixture chooses {outcome} for terminal-filter validation.",
        "evidence_refs": ["sea-trial:return-review-reconsideration"],
        "replacement": None,
    }


def seed_existing_return_state() -> Dict[str, Any]:
    runner = SelfGuidedReturnHostRuntimeRunner(base_dir=BASE_DIR)
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action=SEED_ACTION,
        action_type="audit",
        project_id=PROJECT_ID,
        enabled_feature_flags=list(FEATURE_FLAGS),
        runtime_config=dict(SAFE_RUNTIME_CONFIG),
        continuation_notes=["seed state for intention return-review sea trial"],
    )
    return result.to_dict()


def run_continue_full_json() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BOOTSTRAP_ROOT / "bin" / "lumina"),
            "continue",
            "--project-id",
            PROJECT_ID,
            "--base-dir",
            str(BASE_DIR),
            "--full-json",
        ],
        cwd=str(BOOTSTRAP_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60,
    )


def main() -> Dict[str, Any]:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    absence_base = BASE_DIR / "absence_probe"
    absent_review = build_resident_intention_return_review(base_dir=absence_base)
    absence_left_no_state = not (absence_base / "resident_intentions").exists()

    seed = seed_existing_return_state()
    store = ResidentIntentionStore(BASE_DIR / "resident_intentions")
    unresolved = store.create(
        definition("return-review-unresolved", "Preserve this intention across return."),
        provenance("return-review-origin"),
    )["intentions"][0]
    terminal = store.create(
        definition("return-review-terminal", "This terminal fixture must not surface as unresolved."),
        provenance("return-review-terminal-origin"),
    )["intentions"][0]
    active_terminal = store.reconsider(
        reconsideration(terminal, "continue"),
        provenance("return-review-terminal-continue"),
    )["intentions"][0]
    store.reconsider(
        reconsideration(active_terminal, "complete"),
        provenance("return-review-terminal-complete"),
    )

    verified_store = store.inspect(unresolved_only=False)
    journal_before = store.journal_path.read_bytes()
    expected_head = verified_store["head_hash"]

    proc = run_continue_full_json()
    payload: Dict[str, Any] = {}
    if proc.stdout.strip():
        try:
            candidate = json.loads(proc.stdout)
            if isinstance(candidate, dict):
                payload = candidate
        except Exception:
            payload = {}

    preflight = dict(payload.get("preflight_advisory") or {})
    review = dict(preflight.get("resident_intention_review") or {})
    intentions = list(review.get("intentions") or [])
    surfaced = intentions[0] if len(intentions) == 1 else {}
    receipt = dict(payload.get("receipt") or {})
    runtime_result = dict(payload.get("runtime_result") or {})
    preflight_governance = dict(
        (runtime_result.get("governance") or {}).get("self_guided_continue_preflight") or {}
    )

    log_path = Path(receipt.get("log_path") or "")
    log_parent = log_path.parent if log_path else BASE_DIR / "runtime_logs"
    logs_before_corruption = {path.name for path in log_parent.glob("*.json")} if log_parent.exists() else set()

    tampered = journal_before.replace(
        b"Preserve this intention across return.",
        b"Tampered intention across return.",
        1,
    )
    store.journal_path.write_bytes(tampered)
    corrupt_proc = run_continue_full_json()
    logs_after_corruption = {path.name for path in log_parent.glob("*.json")} if log_parent.exists() else set()
    store.journal_path.write_bytes(journal_before)

    checks = {
        "absence_reported_without_creating_intention_state": (
            absent_review.get("journal_exists") is False
            and absent_review.get("integrity_verified") is False
            and absent_review.get("unresolved_count") == 0
            and absence_left_no_state
        ),
        "seed_cycle_passed": seed.get("halted") is False,
        "continue_cli_exit_zero": proc.returncode == 0,
        "full_json_emitted": bool(payload),
        "journal_verified_on_return": review.get("journal_exists") is True and review.get("integrity_verified") is True,
        "journal_head_bound_to_review": review.get("journal_head_hash") == expected_head,
        "only_unresolved_intention_surfaced": review.get("unresolved_count") == 1 and len(intentions) == 1,
        "terminal_intention_filtered": all(item.get("intention_id") != "return-review-terminal" for item in intentions),
        "origin_preserved": surfaced.get("origin_context") == unresolved.get("origin_context"),
        "statement_preserved": surfaced.get("statement") == unresolved.get("statement"),
        "rationale_preserved": surfaced.get("why_it_matters") == unresolved.get("why_it_matters"),
        "desired_next_action_preserved": surfaced.get("desired_next_action") == unresolved.get("desired_next_action"),
        "current_event_version_preserved": surfaced.get("last_event_hash") == unresolved.get("last_event_hash"),
        "history_count_preserved": surfaced.get("history_event_count") == 1,
        "review_does_not_steer_selection": review.get("selection_effect") == "none; intention evidence is not passed into self-guidance selection",
        "compact_receipt_exposes_count_only": (
            receipt.get("resident_intention_unresolved_count") == 1
            and receipt.get("resident_intention_review_head_hash") == expected_head
            and "resident_intention_review" not in receipt
        ),
        "governance_records_review_without_changing_scope": (
            preflight_governance.get("resident_intention_unresolved_count") == 1
            and preflight_governance.get("resident_intention_review_head_hash") == expected_head
            and preflight_governance.get("resident_intention_scope") == "read-only return evidence"
            and preflight_governance.get("scope") == "Observation/audit focus selection only"
        ),
        "intention_journal_unchanged_by_continue": store.journal_path.read_bytes() == journal_before,
        "tampered_journal_fails_before_cycle": (
            corrupt_proc.returncode != 0
            and "journal record hash mismatch" in corrupt_proc.stderr
            and logs_after_corruption == logs_before_corruption
        ),
        "restored_journal_verifies": store.inspect(unresolved_only=False).get("head_hash") == expected_head,
    }

    summary = {
        "suite": "Lumina Resident Intention Return Review r1",
        "passed": all(checks.values()),
        "checks": checks,
        "project_id": PROJECT_ID,
        "journal_head_hash": expected_head,
        "unresolved_intention_id": unresolved.get("intention_id"),
        "continue_run_id": receipt.get("run_id"),
        "continue_stderr": proc.stderr.strip(),
        "corrupt_continue_stderr_tail": corrupt_proc.stderr.strip()[-1200:],
        "truth_boundary": (
            "Synthetic deterministic fixtures verify read-only return plumbing and fail-closed integrity. "
            "They do not authenticate resident identity, prove subjective continuity, or grant execution authority."
        ),
    }
    report_path = BASE_DIR / "sea_trials_lumina_intention_return_review_r1_report.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"summary_path": str(report_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
    if not output["summary"]["passed"]:
        raise SystemExit(1)
