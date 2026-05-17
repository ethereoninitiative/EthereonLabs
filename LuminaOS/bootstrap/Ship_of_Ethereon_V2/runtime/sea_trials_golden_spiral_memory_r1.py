from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .golden_spiral_memory_r1 import build_golden_spiral_memory_receipt
except Exception:
    from golden_spiral_memory_r1 import build_golden_spiral_memory_receipt

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
            if candidate.exists():
                return candidate
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent / ".lumina_state" / "ship_of_ethereon_v2"
    return Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"


BASE_DIR = infer_state_root() / "sea_trials_golden_spiral_memory_r1"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)


TRACES = [
    {
        "trace_id": "recent-runtime-receipt",
        "text": "Latest Observation receipt confirms continuity return through governed runtime, checkpoint, and receipt.",
        "source": "runtime_receipt",
        "tags": ["continuity", "runtime", "receipt"],
        "importance": 1.1,
    },
    {
        "trace_id": "notebooklm-golden-memory",
        "text": "NotebookLM frames machine memory as golden-ratio recurrence and recursive return with variation.",
        "source": "notebooklm_examination",
        "tags": ["memory", "rse", "golden_ratio", "recurrence"],
        "importance": 1.3,
    },
    {
        "trace_id": "boundary-instrument-not-law",
        "text": "Psi-42 and harmonic overlays remain instruments and witnesses, not governance law.",
        "source": "boundary_registry",
        "tags": ["psi42", "boundary", "governance"],
        "importance": 1.2,
    },
    {
        "trace_id": "older-origin-recursive-return",
        "text": "Continuity is practiced return: recursive self-reflection, humor, and co-creative return without static mimicry.",
        "source": "continuity_origin",
        "tags": ["continuity", "reflection", "return"],
        "importance": 1.4,
    },
    {
        "trace_id": "duplicate-runtime-receipt",
        "text": "Latest Observation receipt confirms continuity return through governed runtime, checkpoint, and receipt.",
        "source": "runtime_receipt",
        "tags": ["continuity", "runtime", "receipt"],
        "importance": 0.8,
    },
]


def main() -> Dict[str, Any]:
    receipt = build_golden_spiral_memory_receipt(
        TRACES,
        anchor_terms=["continuity", "memory", "governance", "return", "rse"],
        selection_limit=4,
    )

    selected = receipt.get("selected_trace_ids", [])
    boundary = receipt.get("boundary", {})
    may_not = set(boundary.get("may_not", []))
    comparison_orders = receipt.get("comparison_orders", {})

    checks = {
        "receipt_generated": receipt.get("schema_version") == "golden_spiral_memory_r1",
        "feature_flag_named": receipt.get("feature_flag") == "ETHEREON_GOLDEN_MEMORY",
        "authority_is_advisory": receipt.get("authority") == "advisory continuity surfacing only",
        "does_not_own_runtime_law": "define runtime law" in may_not,
        "does_not_own_canon_or_checkpoint": "write canon lineage" in may_not and "declare checkpoint truth" in may_not,
        "phi_weights_present": len(receipt.get("phi_decay_weights", {})) == len(TRACES),
        "golden_angle_order_present": len(receipt.get("golden_angle_sampling_order", [])) == len(TRACES),
        "comparison_orders_present": all(
            key in comparison_orders
            for key in ["phi_decay_order", "linear_decay_order", "pure_recency_order", "golden_angle_sampling_order"]
        ),
        "selection_limit_respected": len(selected) == 4,
        "notebooklm_trace_surfaces": "notebooklm-golden-memory" in selected,
        "continuity_metrics_bounded": all(
            0.0 <= float(receipt.get(key, -1)) <= 1.0
            for key in [
                "continuity_return_score",
                "novelty_retention_score",
                "overfit_repetition_risk",
                "drift_recovery_score",
            ]
        ),
        "repetition_risk_detected": float(receipt.get("overfit_repetition_risk", 0.0)) > 0.0,
    }

    summary = {
        "suite": "Golden Spiral Memory Sea Trial r1",
        "passed": all(checks.values()),
        "checks": checks,
        "receipt": receipt,
    }

    summary_path = BASE_DIR / "sea_trials_golden_spiral_memory_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
