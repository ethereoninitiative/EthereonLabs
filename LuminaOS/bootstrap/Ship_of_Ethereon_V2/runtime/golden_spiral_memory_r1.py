"""Golden Spiral Memory r1.

Advisory continuity surfacing through phi-damped return-with-variation.
This module emits receipts only. It does not govern mode legality, canon, or checkpoints.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from math import cos, pi
from typing import Any, Dict, Iterable, List, Optional, Sequence
import hashlib
import json

PHI = (1 + 5 ** 0.5) / 2
GOLDEN_ANGLE_DEGREES = 360 * (1 - (1 / PHI))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(text: str, source: str = "unknown") -> str:
    return hashlib.sha256(f"{source}|{text}".encode("utf-8")).hexdigest()[:12]


def _tokenize(text: str) -> List[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return [token for token in cleaned.split() if len(token) >= 3]


def _safe_float(value: Any, default: float = 1.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


@dataclass
class MemoryTrace:
    text: str
    source: str = "unknown"
    trace_id: Optional[str] = None
    timestamp_utc: Optional[str] = None
    importance: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> "MemoryTrace":
        text = str(payload.get("text") or payload.get("summary") or payload.get("content") or "").strip()
        source = str(payload.get("source") or payload.get("kind") or payload.get("type") or "unknown").strip() or "unknown"
        tags = payload.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        trace = MemoryTrace(
            text=text,
            source=source,
            trace_id=payload.get("trace_id") or payload.get("id"),
            timestamp_utc=payload.get("timestamp_utc") or payload.get("created_at") or payload.get("timestamp"),
            importance=_safe_float(payload.get("importance"), 1.0),
            tags=[str(tag) for tag in tags],
            metadata=dict(metadata),
        )
        if not trace.trace_id:
            trace.trace_id = _stable_id(trace.text, trace.source)
        return trace

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["trace_id"] = self.trace_id or _stable_id(self.text, self.source)
        return payload


@dataclass
class ScoredMemoryTrace:
    trace: MemoryTrace
    recency_rank: int
    phi_decay_weight: float
    golden_angle_degrees: float
    rotation_boost: float
    anchor_overlap: float
    novelty_weight: float
    final_score: float
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace": self.trace.to_dict(),
            "recency_rank": self.recency_rank,
            "phi_decay_weight": round(self.phi_decay_weight, 6),
            "golden_angle_degrees": round(self.golden_angle_degrees, 6),
            "rotation_boost": round(self.rotation_boost, 6),
            "anchor_overlap": round(self.anchor_overlap, 6),
            "novelty_weight": round(self.novelty_weight, 6),
            "final_score": round(self.final_score, 6),
            "reasons": list(self.reasons),
        }


class GoldenSpiralMemoryAdvisor:
    FEATURE_FLAG = "ETHEREON_GOLDEN_MEMORY"
    AUTHORITY = "advisory continuity surfacing only"
    BOUNDARY = {
        "may": [
            "rank bounded memory traces for review",
            "emit selection receipts",
            "compare phi decay with linear and pure-recency ordering",
            "surface continuity-return and novelty-retention metrics",
        ],
        "may_not": [
            "define runtime law",
            "authorize structural changes",
            "write canon lineage",
            "declare checkpoint truth",
            "load capabilities",
        ],
        "attachment_rule": "receipt may be attached as artifact context; it is not structural law",
    }

    def __init__(self, *, phi: float = PHI, golden_angle_degrees: float = GOLDEN_ANGLE_DEGREES):
        self.phi = float(phi)
        self.golden_angle_degrees = float(golden_angle_degrees)

    def build_receipt(
        self,
        traces: Sequence[Dict[str, Any] | MemoryTrace],
        *,
        anchor_terms: Optional[Iterable[str]] = None,
        selection_limit: int = 5,
    ) -> Dict[str, Any]:
        memory_traces = [t if isinstance(t, MemoryTrace) else MemoryTrace.from_payload(t) for t in traces]
        memory_traces = [t for t in memory_traces if t.text.strip()]
        selection_limit = max(1, min(selection_limit, max(1, len(memory_traces) or 1)))
        anchors = {token.lower() for term in (anchor_terms or []) for token in _tokenize(str(term))}

        scored = self.score_traces(memory_traces, anchors)
        selected = scored[:selection_limit]
        comparison = self.compare_decay_orders(memory_traces)
        continuity_return_score = self._continuity_return_score(selected, anchors)
        novelty_retention_score = self._novelty_retention_score(selected)
        overfit_repetition_risk = self._overfit_repetition_risk(selected)
        drift_recovery_score = max(
            0.0,
            min(1.0, 0.50 * continuity_return_score + 0.35 * novelty_retention_score + 0.15 * (1.0 - overfit_repetition_risk)),
        )

        return {
            "generated_at": utc_now(),
            "schema_version": "golden_spiral_memory_r1",
            "authority": self.AUTHORITY,
            "feature_flag": self.FEATURE_FLAG,
            "selection_limit": selection_limit,
            "input_trace_count": len(memory_traces),
            "selected_trace_ids": [item.trace.trace_id for item in selected],
            "phi_decay_weights": {item.trace.trace_id: round(item.phi_decay_weight, 6) for item in scored},
            "golden_angle_sampling_order": comparison["golden_angle_sampling_order"],
            "continuity_return_score": round(continuity_return_score, 6),
            "novelty_retention_score": round(novelty_retention_score, 6),
            "overfit_repetition_risk": round(overfit_repetition_risk, 6),
            "drift_recovery_score": round(drift_recovery_score, 6),
            "comparison_orders": comparison,
            "scored_traces": [item.to_dict() for item in scored],
            "boundary": dict(self.BOUNDARY),
        }

    def score_traces(self, memory_traces: Sequence[MemoryTrace], anchors: set[str]) -> List[ScoredMemoryTrace]:
        seen_tokens: set[str] = set()
        scored: List[ScoredMemoryTrace] = []
        for index, trace in enumerate(memory_traces):
            trace.trace_id = trace.trace_id or _stable_id(trace.text, trace.source)
            tokens = set(_tokenize(" ".join([trace.text, " ".join(trace.tags)])))
            anchor_hits = len(tokens & anchors)
            anchor_overlap = anchor_hits / max(1, len(anchors)) if anchors else 0.0
            new_tokens = tokens - seen_tokens
            novelty_weight = len(new_tokens) / max(1, len(tokens)) if tokens else 0.0
            seen_tokens |= tokens
            phi_decay_weight = self.phi ** (-index)
            angle = (index * self.golden_angle_degrees) % 360.0
            rotation_boost = 0.92 + 0.08 * ((cos(angle * pi / 180.0) + 1.0) / 2.0)
            importance = max(0.0, min(trace.importance, 3.0)) / 3.0
            final_score = 0.34 * phi_decay_weight + 0.24 * anchor_overlap + 0.18 * novelty_weight + 0.14 * importance + 0.10 * rotation_boost
            reasons: List[str] = []
            if index == 0:
                reasons.append("strongest recency position")
            if anchor_hits:
                reasons.append("returns to anchor terms")
            if novelty_weight >= 0.5:
                reasons.append("preserves variation rather than repetition")
            if trace.importance > 1.0:
                reasons.append("importance weighting supplied by caller")
            if not reasons:
                reasons.append("kept as low-authority continuity context")
            scored.append(ScoredMemoryTrace(trace, index, phi_decay_weight, angle, rotation_boost, anchor_overlap, novelty_weight, final_score, reasons))
        scored.sort(key=lambda item: item.final_score, reverse=True)
        return scored

    def compare_decay_orders(self, memory_traces: Sequence[MemoryTrace]) -> Dict[str, List[str]]:
        indexed = list(enumerate(memory_traces))
        def tid(trace: MemoryTrace) -> str:
            return trace.trace_id or _stable_id(trace.text, trace.source)
        angle_order = sorted(indexed, key=lambda pair: ((pair[0] * self.golden_angle_degrees) % 360.0))
        return {
            "phi_decay_order": [tid(trace) for _, trace in sorted(indexed, key=lambda pair: self.phi ** (-pair[0]), reverse=True)],
            "linear_decay_order": [tid(trace) for _, trace in sorted(indexed, key=lambda pair: max(0.0, 1.0 - pair[0] / max(1, len(indexed) - 1)), reverse=True)],
            "pure_recency_order": [tid(trace) for _, trace in indexed],
            "golden_angle_sampling_order": [tid(trace) for _, trace in angle_order],
        }

    def _continuity_return_score(self, selected: Sequence[ScoredMemoryTrace], anchors: set[str]) -> float:
        if not selected:
            return 0.0
        if not anchors:
            return sum(item.phi_decay_weight for item in selected) / len(selected)
        return sum(item.anchor_overlap for item in selected) / len(selected)

    def _novelty_retention_score(self, selected: Sequence[ScoredMemoryTrace]) -> float:
        if not selected:
            return 0.0
        sources = {item.trace.source for item in selected}
        tags = {tag for item in selected for tag in item.trace.tags}
        source_component = len(sources) / max(1, len(selected))
        tag_component = min(1.0, len(tags) / max(1, len(selected)))
        novelty_component = sum(item.novelty_weight for item in selected) / len(selected)
        return 0.40 * source_component + 0.25 * tag_component + 0.35 * novelty_component

    def _overfit_repetition_risk(self, selected: Sequence[ScoredMemoryTrace]) -> float:
        if not selected:
            return 0.0
        normalized_texts = [" ".join(_tokenize(item.trace.text)) for item in selected]
        duplicate_count = len(normalized_texts) - len(set(normalized_texts))
        sources = [item.trace.source for item in selected]
        dominant_source_count = max((sources.count(source) for source in set(sources)), default=0)
        return min(1.0, 0.62 * (duplicate_count / max(1, len(selected))) + 0.38 * (dominant_source_count / max(1, len(selected))))


def build_golden_spiral_memory_receipt(
    traces: Sequence[Dict[str, Any] | MemoryTrace],
    *,
    anchor_terms: Optional[Iterable[str]] = None,
    selection_limit: int = 5,
) -> Dict[str, Any]:
    return GoldenSpiralMemoryAdvisor().build_receipt(traces, anchor_terms=anchor_terms, selection_limit=selection_limit)


if __name__ == "__main__":
    sample = [
        {"text": "Latest runtime receipt confirms governed return path.", "source": "checkpoint", "tags": ["continuity", "runtime"], "importance": 1.2},
        {"text": "Recursive memory should return with variation, not repeat blindly.", "source": "notebooklm", "tags": ["rse", "memory"], "importance": 1.1},
        {"text": "Psi-42 remains an instrument and never owns governance.", "source": "probe", "tags": ["psi42", "boundary"], "importance": 1.0},
    ]
    print(json.dumps(build_golden_spiral_memory_receipt(sample, anchor_terms=["continuity", "memory", "governance"]), indent=2))
