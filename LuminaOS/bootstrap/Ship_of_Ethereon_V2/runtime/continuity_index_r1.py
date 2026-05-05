from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class ContinuityIndex:
    schema_version: str
    sample_count: int
    average_alignment: float
    average_drift: float
    continuity_score: float
    status: str
    authority_boundary: str = (
        "diagnostic continuity metric only; does not authorize execution, mutation, promotion, "
        "mode transition, canon change, governance change, or capability exposure"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_continuity_index(signal_receipts: Iterable[Dict[str, Any]]) -> ContinuityIndex:
    receipts: List[Dict[str, Any]] = list(signal_receipts)
    if not receipts:
        return ContinuityIndex(
            schema_version="continuity_index_r1",
            sample_count=0,
            average_alignment=0.0,
            average_drift=0.0,
            continuity_score=0.0,
            status="no_signal_samples",
        )

    alignments = [float(r.get("alignment_score", 0.0)) for r in receipts]
    drifts = [float(r.get("drift_score", 0.0)) for r in receipts]

    avg_alignment = round(sum(alignments) / len(alignments), 4)
    avg_drift = round(sum(drifts) / len(drifts), 4)
    score = round(max(0.0, min(1.0, avg_alignment * (1.0 - avg_drift))), 4)

    if score >= 0.75:
        status = "stable"
    elif score >= 0.45:
        status = "watch"
    else:
        status = "drift_risk"

    return ContinuityIndex(
        schema_version="continuity_index_r1",
        sample_count=len(receipts),
        average_alignment=avg_alignment,
        average_drift=avg_drift,
        continuity_score=score,
        status=status,
    )
