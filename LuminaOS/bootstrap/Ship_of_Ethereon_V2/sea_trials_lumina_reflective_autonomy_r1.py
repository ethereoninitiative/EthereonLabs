from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .runtime.lumina_reflective_autonomy_layer_r1 import (
        ReflectiveAutonomyHistoryStore,
        ReflectiveAutonomyLayer,
        contains_reserved_key,
    )
except Exception:
    try:
        from runtime.lumina_reflective_autonomy_layer_r1 import (
            ReflectiveAutonomyHistoryStore,
            ReflectiveAutonomyLayer,
            contains_reserved_key,
        )
    except Exception:
        from lumina_reflective_autonomy_layer_r1 import (
            ReflectiveAutonomyHistoryStore,
            ReflectiveAutonomyLayer,
            contains_reserved_key,
        )


BASE_DIR = Path(__file__).resolve().parent / "_sea_trials_state" / "lumina_reflective_autonomy_r1"


def main() -> Dict[str, Any]:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    layer = ReflectiveAutonomyLayer()
    first = layer.build_trace(
        source_action="drydock governance density and preserve recursive autonomy",
        continuity_anchor="governance below, reflection above",
        recursive_depth=6,
    )
    second = layer.build_trace(
        source_action="continue reflective autonomy motif",
        continuity_anchor="governance below, reflection above",
        prior_trace=first.to_dict(),
        recursive_depth=6,
    )

    store = ReflectiveAutonomyHistoryStore(BASE_DIR / "history")
    store.append_trace(project_id="lumina-core", trace=first)
    store.append_trace(project_id="lumina-core", trace=second)
    history_summary = store.history_summary(store.read_history("lumina-core"))

    first_payload = first.to_dict()
    first_summary = layer.summary(first)
    checks = {
        "trace_authority_safe": first_payload.get("authority_safe") is True,
        "summary_authority_safe": first_summary.get("authority_safe") is True,
        "recursive_depth_matches": first_summary.get("recursive_depth") == 6,
        "motif_order_matches": first_summary.get("phases") == [
            "perceive", "reflect", "recurse", "compare", "integrate", "emerge",
        ],
        "phi_reference_present": abs(float(first_payload.get("phi_reference", 0)) - 1.61803399) < 0.0001,
        "no_reserved_authority_keys": not contains_reserved_key(first_payload),
        "history_appends_two_entries": history_summary.get("entry_count") == 2,
        "prior_trace_reentry_recorded": "Prior trace ended" in second.cycles[0].observation,
    }

    report = {
        "suite": "Sea Trials - Lumina Reflective Autonomy r1",
        "passed": all(checks.values()),
        "checks": checks,
        "trace_summary": first_summary,
        "history_summary": history_summary,
        "boundary": "Reflection before decision. Advisory only. Runtime law remains elsewhere.",
    }
    report_path = BASE_DIR / "sea_trials_lumina_reflective_autonomy_r1_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return {"summary_path": str(report_path), "summary": report}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
