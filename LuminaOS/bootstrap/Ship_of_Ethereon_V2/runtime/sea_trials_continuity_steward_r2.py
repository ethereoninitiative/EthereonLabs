from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import shutil

from runtime_runner_continuity_steward_r2 import StewardedRuntimeRunner


BASE_DIR = Path("/mnt/data/ethereon_continuity_steward_sea_trials_r2")
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

ETHEREONIC_OVERLAY = {
    "active": True,
    "anchor_language": ["english", "toki_pona", "binary", "light_language"],
    "continuity_phrase": "threshold as permission",
    "harmonic_signature": [432, 528, 963],
    "spiral_reference": "RSE-v1",
}


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> Dict[str, Any]:
    runner = StewardedRuntimeRunner(
        base_dir=BASE_DIR,
        registry_path=Path(__file__).with_name("capability_registry_continuity_steward_r1.json"),
    )

    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="trial_continuity_steward_integration_r2",
        action_type="audit",
        ethereonic_overlay=ETHEREONIC_OVERLAY,
        enabled_feature_flags=[
            "ETHEREON_OBSERVATION",
            "ETHEREON_PSI42",
            "ETHEREON_CONTINUITY_STEWARD",
        ],
        runtime_config=SAFE_RUNTIME_CONFIG,
    )

    capability_ids = [cap.get("capability_id") for cap in result.get("exposed_capabilities", [])]
    continuity_block = result.get("continuity_steward", {})
    residue_path = Path(continuity_block.get("residue_path", ""))
    state_path = Path(continuity_block.get("state_path", ""))
    residue_rows = _read_jsonl(residue_path)
    governance_rows = _read_jsonl(Path(result.get("governance_log_path", "")))
    resume_brief = continuity_block.get("resume_brief", [])
    decision = continuity_block.get("decision", {})
    governance_chain_status = result.get("governance_chain_status", {})

    checks = {
        "continuity_steward_payload_present": isinstance(continuity_block, dict) and bool(continuity_block),
        "continuity_steward_capability_exposed": "continuity_steward" in capability_ids,
        "residue_file_written": residue_path.exists(),
        "state_file_written": state_path.exists(),
        "residue_contains_rows": len(residue_rows) >= 1,
        "resume_brief_present": isinstance(resume_brief, list) and len(resume_brief) >= 1,
        "decision_present": isinstance(decision, dict) and bool(decision),
        "decision_is_lawful": decision.get("lawful_target_mode") in {"Observation", "Continuity"},
        "governance_event_written": any(row.get("event_type") == "continuity_steward" for row in governance_rows),
        "integrity_mode_reported": governance_chain_status.get("integrity_mode") in {"verified_chain", "plain_append_only"},
        "integrity_chain_active": governance_chain_status.get("integrity_chain_active") is True,
        "latest_event_hash_present": bool(governance_chain_status.get("latest_event_hash")),
        "integrity_module_importable": governance_chain_status.get("integrity_module_importable") is True,
    }

    summary = {
        "suite": "Continuity Steward Integration Sea Trial R2",
        "passed": all(checks.values()),
        "checks": checks,
        "result": result,
        "residue_row_count": len(residue_rows),
        "governance_event_count": len(governance_rows),
        "exposed_capability_ids": capability_ids,
        "governance_chain_status": governance_chain_status,
    }

    summary_path = BASE_DIR / "sea_trials_continuity_steward_r2_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {
        "summary_path": str(summary_path),
        "residue_path": str(residue_path),
        "state_path": str(state_path),
        "summary": summary,
    }


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
