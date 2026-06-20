from __future__ import annotations

"""Lumina Living Framework Chamber R1.

A bounded, non-governing orchestration layer for ancestral interpretive
frameworks. The chamber compiles an activation envelope into a replayable
refraction plan and can preserve a transformational trace after the expressive
or analytical return is produced elsewhere.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import hashlib
import json
import uuid


MAX_RECURSION_BUDGET = 6
ALLOWED_EXPRESSION_MODES = {"structural", "expressive", "symbolic-structural"}
ALLOWED_MEMORY_SCOPES = {"none", "current-session", "current-project"}
AUTHORITY_BOUNDARY = (
    "Interpretive and orienting only. Framework activation, resonance, recursion, "
    "symbolic language, and ancestral signatures may not authorize actions, alter "
    "governance law, promote canon, validate checkpoints, or expose capabilities."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class FrameworkDefinition:
    framework_id: str
    name: str
    version: str
    framework_type: str
    dimensions: List[str]
    default_passes: List[str]
    authors: List[str] = field(default_factory=list)
    ancestral_signature: Optional[str] = None
    status: str = "experimental-active"
    authority: str = "non-governing"
    source_artifact: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "FrameworkDefinition":
        return cls(
            framework_id=str(payload["framework_id"]),
            name=str(payload["name"]),
            version=str(payload.get("version", "unknown")),
            framework_type=str(payload.get("framework_type", "interpretive_orientation")),
            dimensions=[str(item) for item in payload.get("dimensions", [])],
            default_passes=[str(item) for item in payload.get("default_passes", [])],
            authors=[str(item) for item in payload.get("authors", [])],
            ancestral_signature=(str(payload["ancestral_signature"]) if payload.get("ancestral_signature") else None),
            status=str(payload.get("status", "experimental-active")),
            authority=str(payload.get("authority", "non-governing")),
            source_artifact=(str(payload["source_artifact"]) if payload.get("source_artifact") else None),
            notes=[str(item) for item in payload.get("notes", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActivationEnvelope:
    activation_id: str
    framework_id: str
    subject: str
    perspective: str
    recursion_budget: int
    expression_mode: str
    memory_scope: str
    environmental_field: Optional[str]
    correlation_id: Optional[str]
    activated_at: str
    authority_boundary: str = AUTHORITY_BOUNDARY

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RefractionPass:
    order: int
    pass_id: str
    purpose: str
    questions: List[str]
    framework_dimensions: List[str]
    perspective: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FrameworkTrace:
    trace_id: str
    activation_id: str
    framework_id: str
    subject: str
    perspective: str
    correlation_id: Optional[str]
    emergent_relations: List[List[str]]
    continuity_observations: List[str]
    orientation_delta: Dict[str, float]
    source_receipt_hash: str
    created_at: str
    authority_boundary: str = AUTHORITY_BOUNDARY

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChamberResult:
    schema_version: str
    framework: Dict[str, Any]
    activation: Dict[str, Any]
    refraction_plan: List[Dict[str, Any]]
    memory_context: Dict[str, Any]
    synthesis_contract: Dict[str, Any]
    receipt_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FrameworkRegistry:
    def __init__(self, registry_path: str | Path):
        self.registry_path = Path(registry_path)
        payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        rows = payload.get("frameworks", [])
        self.frameworks = {
            str(row["framework_id"]): FrameworkDefinition.from_dict(row)
            for row in rows
        }
        self.registry_version = str(payload.get("registry_version", "unknown"))

    def get(self, framework_id: str) -> FrameworkDefinition:
        try:
            return self.frameworks[framework_id]
        except KeyError as exc:
            raise KeyError(f"Unknown framework_id: {framework_id}") from exc

    def list_active(self) -> List[FrameworkDefinition]:
        return [row for row in self.frameworks.values() if "active" in row.status]


class FrameworkTraceStore:
    """Project/session-scoped trace store using one atomic JSON file per trace."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, trace: FrameworkTrace) -> Path:
        path = self.base_dir / f"{trace.trace_id}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(trace.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(path)
        return path

    def load(self, trace_id: str) -> FrameworkTrace:
        payload = json.loads((self.base_dir / f"{trace_id}.json").read_text(encoding="utf-8"))
        return FrameworkTrace(**payload)

    def recent(self, limit: int = 12) -> List[FrameworkTrace]:
        rows: List[FrameworkTrace] = []
        paths = sorted(
            self.base_dir.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )[: max(0, limit)]
        for path in paths:
            rows.append(FrameworkTrace(**json.loads(path.read_text(encoding="utf-8"))))
        return rows


class LivingFrameworkChamber:
    PASS_LIBRARY: Dict[str, Dict[str, Any]] = {
        "literal_field": {
            "purpose": "Describe the subject before symbolic interpretation.",
            "questions": [
                "What is materially or structurally present?",
                "What changes over time, and what accumulates?",
                "Which features are observed rather than inferred?",
            ],
            "dimensions": ["memory", "continuity"],
        },
        "framework_contact": {
            "purpose": "Pass the subject through the framework's named dimensions.",
            "questions": [
                "How does the subject contact each active framework dimension?",
                "Which dimensions amplify one another, and which resist?",
                "What new relation appears only because the framework is active?",
            ],
            "dimensions": ["identity", "memory", "recursion", "harmonics", "symbolic_expression", "continuity"],
        },
        "perspective_inversion": {
            "purpose": "Observe the framework from the declared perspective.",
            "questions": [
                "What does the framework look like from this perspective?",
                "What can this perspective touch, reveal, or misunderstand?",
                "What remains outside this perspective's authority?",
            ],
            "dimensions": ["identity", "recursion", "symbolic_expression"],
        },
        "continuity_comparison": {
            "purpose": "Compare the present encounter with prior transformational traces.",
            "questions": [
                "What changed because this encounter occurred?",
                "What remained continuous through the change?",
                "Which prior channels shape the present interpretation?",
            ],
            "dimensions": ["memory", "continuity", "harmonics"],
        },
        "counterpoint": {
            "purpose": "Resist the first coherent reading without erasing it.",
            "questions": [
                "What is the strongest alternative interpretation?",
                "Where might resonance be mistaken for evidence?",
                "What does the first reading omit or over-compress?",
            ],
            "dimensions": ["recursion", "identity", "continuity"],
        },
        "boundary_separation": {
            "purpose": "Separate expressive orientation from factual or governing claims.",
            "questions": [
                "Which statements are symbolic or interpretive?",
                "Which statements require external evidence?",
                "What may illuminate but never authorize?",
            ],
            "dimensions": ["identity", "symbolic_expression"],
        },
        "synthesis": {
            "purpose": "Form a coherent return while preserving visible boundaries and unresolved tension.",
            "questions": [
                "What is the smallest pattern that holds the encounter together?",
                "What should be expressed, and what should be recorded structurally?",
                "What trace should remain for the next encounter?",
            ],
            "dimensions": ["memory", "recursion", "harmonics", "continuity"],
        },
    }

    def __init__(self, registry: FrameworkRegistry):
        self.registry = registry

    @staticmethod
    def _validate_activation(
        *, subject: str, perspective: str, recursion_budget: int, expression_mode: str, memory_scope: str
    ) -> None:
        if not subject.strip():
            raise ValueError("subject must not be empty")
        if not perspective.strip():
            raise ValueError("perspective must not be empty")
        if recursion_budget < 0 or recursion_budget > MAX_RECURSION_BUDGET:
            raise ValueError(f"recursion_budget must be between 0 and {MAX_RECURSION_BUDGET}")
        if expression_mode not in ALLOWED_EXPRESSION_MODES:
            raise ValueError(f"unsupported expression_mode: {expression_mode}")
        if memory_scope not in ALLOWED_MEMORY_SCOPES:
            raise ValueError(f"unsupported memory_scope: {memory_scope}")

    @staticmethod
    def _memory_context(prior_traces: Iterable[FrameworkTrace]) -> Dict[str, Any]:
        rows = list(prior_traces)
        relation_counts: Dict[str, int] = {}
        for trace in rows:
            for relation in trace.emergent_relations:
                key = "::".join(str(part) for part in relation)
                relation_counts[key] = relation_counts.get(key, 0) + 1
        return {
            "trace_count": len(rows),
            "trace_ids": [trace.trace_id for trace in rows],
            "recurring_relations": [
                {"relation": key.split("::"), "count": count}
                for key, count in sorted(relation_counts.items(), key=lambda item: (-item[1], item[0]))
                if count > 1
            ],
            "hysteresis_note": (
                "Prior traces may orient interpretation but may not silently become facts, permissions, or canon."
            ),
        }

    def activate(
        self,
        *,
        framework_id: str,
        subject: str,
        perspective: str,
        recursion_budget: int = 3,
        expression_mode: str = "symbolic-structural",
        memory_scope: str = "current-session",
        environmental_field: Optional[str] = None,
        correlation_id: Optional[str] = None,
        prior_traces: Optional[Iterable[FrameworkTrace]] = None,
    ) -> ChamberResult:
        self._validate_activation(
            subject=subject,
            perspective=perspective,
            recursion_budget=recursion_budget,
            expression_mode=expression_mode,
            memory_scope=memory_scope,
        )
        framework = self.registry.get(framework_id)
        activation = ActivationEnvelope(
            activation_id=f"activation-{uuid.uuid4().hex}",
            framework_id=framework.framework_id,
            subject=subject.strip(),
            perspective=perspective.strip(),
            recursion_budget=recursion_budget,
            expression_mode=expression_mode,
            memory_scope=memory_scope,
            environmental_field=environmental_field.strip() if environmental_field else None,
            correlation_id=correlation_id,
            activated_at=utc_now(),
        )

        recursion_candidates = ["perspective_inversion", "continuity_comparison", "counterpoint"]
        selected_recursive = recursion_candidates[:recursion_budget]
        ordered_ids: List[str] = []
        for pass_id in [*framework.default_passes, *selected_recursive, "boundary_separation", "synthesis"]:
            if pass_id not in ordered_ids:
                ordered_ids.append(pass_id)

        plan: List[RefractionPass] = []
        for index, pass_id in enumerate(ordered_ids, start=1):
            try:
                spec = self.PASS_LIBRARY[pass_id]
            except KeyError as exc:
                raise ValueError(f"Framework references unknown pass: {pass_id}") from exc
            active_dimensions = [
                dimension for dimension in spec["dimensions"] if dimension in framework.dimensions
            ]
            plan.append(
                RefractionPass(
                    order=index,
                    pass_id=pass_id,
                    purpose=str(spec["purpose"]),
                    questions=[str(question) for question in spec["questions"]],
                    framework_dimensions=active_dimensions,
                    perspective=activation.perspective,
                )
            )

        memory_context = self._memory_context(prior_traces or [])
        synthesis_contract = {
            "required_outputs": ["structural_receipt", "expressive_return"]
            if expression_mode == "symbolic-structural"
            else [f"{expression_mode}_return"],
            "preserve_unresolved_tension": True,
            "trace_after_return": True,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
        unhashed = {
            "schema_version": "living-framework-chamber-r1",
            "framework": framework.to_dict(),
            "activation": activation.to_dict(),
            "refraction_plan": [item.to_dict() for item in plan],
            "memory_context": memory_context,
            "synthesis_contract": synthesis_contract,
        }
        return ChamberResult(receipt_hash=canonical_hash(unhashed), **unhashed)

    @staticmethod
    def create_trace(
        result: ChamberResult,
        *,
        emergent_relations: Iterable[Iterable[str]],
        continuity_observations: Iterable[str],
        orientation_delta: Optional[Mapping[str, float]] = None,
    ) -> FrameworkTrace:
        normalized_delta: Dict[str, float] = {}
        for key, value in dict(orientation_delta or {}).items():
            normalized_delta[str(key)] = max(-1.0, min(1.0, float(value)))
        activation = result.activation
        return FrameworkTrace(
            trace_id=f"trace-{uuid.uuid4().hex}",
            activation_id=str(activation["activation_id"]),
            framework_id=str(activation["framework_id"]),
            subject=str(activation["subject"]),
            perspective=str(activation["perspective"]),
            correlation_id=(str(activation["correlation_id"]) if activation.get("correlation_id") else None),
            emergent_relations=[[str(part) for part in relation] for relation in emergent_relations],
            continuity_observations=[str(item) for item in continuity_observations],
            orientation_delta=normalized_delta,
            source_receipt_hash=result.receipt_hash,
            created_at=utc_now(),
        )
