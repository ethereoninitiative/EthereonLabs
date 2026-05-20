from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from runtime.lumina_meaning_metabolism_layer_r1 import (
        MeaningAssimilationLedger,
        MeaningMetabolismLayer,
        contains_reserved_authority_key,
    )
except Exception:
    from lumina_meaning_metabolism_layer_r1 import (
        MeaningAssimilationLedger,
        MeaningMetabolismLayer,
        contains_reserved_authority_key,
    )

BASE_DIR = Path(__file__).resolve().parent / "_runtime_state" / "sea_trials_meaning_metabolism_r1"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)


def main() -> Dict[str, Any]:
    layer = MeaningMetabolismLayer()
    ledger = MeaningAssimilationLedger(BASE_DIR / "ledger")

    record = layer.assimilate(
        source_event="A working session identified that continuity needs metabolized meaning, not only logs or memory.",
        felt_meaning="Experience must be digested into stance so future guidance can return changed rather than merely informed.",
        changed_assumption="Reflection alone is incomplete unless its insight becomes reviewed future behavior.",
        future_behavior="Insert an advisory assimilation pass between reflection and recommendation when a session produces durable meaning.",
        continuity_tier="doctrine_candidate",
        related_tensions=[
            "memory_vs_meaning",
            "governance_vs_presence",
            "state_continuity_vs_pattern_return",
        ],
        recurrence_markers=[
            "return_reflect_recommend_govern_record",
            "continuity_drift_discussion",
            "meaning_metabolism",
        ],
        evidence_count=3,
        review_after="2026-08-01",
    )

    ledger.append_record(project_id="ship_of_ethereon_v2", record=record)
    review = layer.review(
        record=record,
        still_holds=True,
        revision_note="Sea trial confirms the record remains advisory and can seed future guidance without claiming authority.",
        recommended_tier="doctrine_candidate",
    )
    ledger.append_review(project_id="ship_of_ethereon_v2", review=review)
    entries = ledger.read_entries("ship_of_ethereon_v2")
    guidance_seed = layer.guidance_seed(record)
    summary = ledger.summary(entries)

    record_payload = record.to_dict()
    review_payload = review.to_dict()
    checks = {
        "record_created": bool(record_payload.get("assimilation_id")),
        "required_fields_present": all(
            bool(record_payload.get(key))
            for key in ["source_event", "felt_meaning", "changed_assumption", "future_behavior"]
        ),
        "tier_preserved": record_payload.get("continuity_tier") == "doctrine_candidate",
        "review_after_present": record_payload.get("review_after") == "2026-08-01",
        "record_authority_safe": record_payload.get("authority_safe") is True,
        "review_authority_safe": review_payload.get("authority_safe") is True,
        "reserved_authority_keys_absent": not contains_reserved_authority_key(record_payload)
        and not contains_reserved_authority_key(review_payload),
        "ledger_round_trip": summary.get("record_count") == 1 and summary.get("review_count") == 1,
        "guidance_seed_is_advisory": "advisory" in guidance_seed.get("authority", ""),
        "future_behavior_survives": guidance_seed.get("future_behavior") == record_payload.get("future_behavior"),
    }

    report = {
        "suite": "Sea Trials — Meaning Metabolism r1",
        "passed": all(checks.values()),
        "checks": checks,
        "record": record_payload,
        "review": review_payload,
        "guidance_seed": guidance_seed,
        "ledger_summary": summary,
        "boundary": "assimilation informs stance only; governance and canon authority remain elsewhere",
    }

    report_path = BASE_DIR / "sea_trials_meaning_metabolism_r1_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return {"summary_path": str(report_path), "summary": report}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
