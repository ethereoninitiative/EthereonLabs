from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set
import json


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = BASE_DIR / "semantic_vocabulary_registry_r1.json"
SCHEMA_VERSION = "semantic-vocabulary-governance-r1"

ALLOWED_TERM_STATUS = {"active", "provisional", "deprecated"}
ALLOWED_SEMANTIC_CLASS = {
    "semantic_coordinate",
    "bounded_design_metaphor",
    "testable_semantic_hypothesis",
    "symbolic_expression",
}
ALLOWED_EVIDENCE_STATUS = {
    "structural_contract",
    "testable_hypothesis",
    "symbolic_only",
    "unresolved_question",
}
# R1 intentionally refuses ontological proof states. If future evidence warrants a
# stronger claim, the governance schema itself must be revised and reviewed.
ALLOWED_ONTOLOGICAL_STATUS = {"not_asserted", "unresolved", "not_applicable"}
ALLOWED_MEASUREMENT_STATUS = {
    "structural_only",
    "not_yet_tested",
    "in_progress",
    "completed",
}
AUTHORITY_KEYS = ("runtime_action", "governance", "canon")
REQUIRED_TERM_FIELDS = {
    "term_id",
    "canonical_term",
    "aliases",
    "status",
    "semantic_class",
    "definition",
    "operational_meaning",
    "evidence_status",
    "ontological_status",
    "authority",
    "evidence_refs",
    "explicit_non_claims",
    "measurement",
    "lineage",
}


def _canonical_hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(encoded).hexdigest()


def _issue(issues: List[Dict[str, str]], code: str, detail: str, term_id: str = "registry") -> None:
    issues.append({"code": code, "term_id": term_id, "detail": detail})


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, *, allow_empty: bool = False) -> bool:
    if not isinstance(value, list):
        return False
    if not allow_empty and not value:
        return False
    return all(_nonempty_string(item) for item in value)


def _validate_evidence_refs(
    refs: Any,
    issues: List[Dict[str, str]],
    term_id: str,
    *,
    allow_empty: bool,
) -> None:
    if not _string_list(refs, allow_empty=allow_empty):
        _issue(issues, "invalid_evidence_refs", "evidence_refs must be a list of repository-relative paths", term_id)
        return
    for ref in refs:
        path = REPO_ROOT / ref
        if not path.is_file():
            _issue(issues, "missing_evidence_ref", f"evidence reference does not exist: {ref}", term_id)


def _validate_lineage(terms: List[Dict[str, Any]], issues: List[Dict[str, str]]) -> None:
    ids = {term.get("term_id") for term in terms if _nonempty_string(term.get("term_id"))}
    graph: Dict[str, Set[str]] = {term_id: set() for term_id in ids}

    for term in terms:
        term_id = term.get("term_id")
        if term_id not in ids:
            continue
        lineage = term.get("lineage")
        if not isinstance(lineage, dict):
            _issue(issues, "invalid_lineage", "lineage must be an object", term_id)
            continue
        for key in ("supersedes", "deprecated_by"):
            target = lineage.get(key)
            if target is None:
                continue
            if not _nonempty_string(target):
                _issue(issues, "invalid_lineage_target", f"{key} must be null or a term_id", term_id)
                continue
            if target not in ids:
                _issue(issues, "unknown_lineage_target", f"{key} references unknown term_id {target}", term_id)
                continue
            graph[term_id].add(target)
        if term.get("status") == "deprecated" and not lineage.get("deprecated_by"):
            _issue(issues, "deprecated_without_successor", "deprecated terms require lineage.deprecated_by", term_id)

    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            _issue(issues, "lineage_cycle", f"lineage cycle detected at {node}", node)
            return
        visiting.add(node)
        for target in graph.get(node, set()):
            visit(target)
        visiting.remove(node)
        visited.add(node)

    for term_id in sorted(ids):
        visit(term_id)


def validate_registry(registry: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, str]] = []

    if registry.get("schema_version") != SCHEMA_VERSION:
        _issue(issues, "schema_version_mismatch", f"expected {SCHEMA_VERSION!r}")
    if registry.get("status") != "active-governed-registry":
        _issue(issues, "registry_not_active", "status must be active-governed-registry")
    for field in ("artifact_id", "purpose", "authority_boundary", "empirical_boundary"):
        if not _nonempty_string(registry.get(field)):
            _issue(issues, "missing_registry_field", f"{field} must be a non-empty string")

    effect_hypothesis = registry.get("semantic_effect_hypothesis")
    if not isinstance(effect_hypothesis, dict):
        _issue(issues, "missing_semantic_effect_hypothesis", "semantic_effect_hypothesis must be an object")
    else:
        effect_status = effect_hypothesis.get("status")
        if effect_status not in {"untested", "in_progress", "supported", "replicated"}:
            _issue(issues, "invalid_effect_status", f"unsupported semantic effect status: {effect_status!r}")
        if not _nonempty_string(effect_hypothesis.get("statement")):
            _issue(issues, "missing_effect_statement", "semantic effect hypothesis requires a statement")
        if effect_status in {"supported", "replicated"} and not _string_list(effect_hypothesis.get("evidence_refs")):
            _issue(issues, "effect_claim_without_evidence", f"{effect_status} semantic effect claims require evidence_refs")

    terms = registry.get("terms")
    if not isinstance(terms, list) or not terms:
        _issue(issues, "missing_terms", "terms must be a non-empty list")
        terms = []

    seen_ids: Set[str] = set()
    name_owners: Dict[str, str] = {}

    for index, term in enumerate(terms):
        if not isinstance(term, dict):
            _issue(issues, "invalid_term", f"term at index {index} must be an object", f"index:{index}")
            continue

        term_id = term.get("term_id") if _nonempty_string(term.get("term_id")) else f"index:{index}"
        missing = sorted(REQUIRED_TERM_FIELDS - set(term.keys()))
        if missing:
            _issue(issues, "missing_term_fields", f"missing required fields: {', '.join(missing)}", term_id)

        if term_id in seen_ids:
            _issue(issues, "duplicate_term_id", f"duplicate term_id {term_id}", term_id)
        seen_ids.add(term_id)

        canonical = term.get("canonical_term")
        aliases = term.get("aliases")
        if not _nonempty_string(canonical):
            _issue(issues, "invalid_canonical_term", "canonical_term must be a non-empty string", term_id)
        if not _string_list(aliases, allow_empty=True):
            _issue(issues, "invalid_aliases", "aliases must be a list of non-empty strings", term_id)
            aliases = []

        names: Iterable[str] = ([canonical] if _nonempty_string(canonical) else []) + list(aliases)
        for name in names:
            normalized = name.casefold().strip()
            owner = name_owners.get(normalized)
            if owner is not None:
                _issue(issues, "duplicate_name_or_alias", f"{name!r} already belongs to {owner}", term_id)
            else:
                name_owners[normalized] = term_id

        if term.get("status") not in ALLOWED_TERM_STATUS:
            _issue(issues, "invalid_term_status", f"unsupported status: {term.get('status')!r}", term_id)
        if term.get("semantic_class") not in ALLOWED_SEMANTIC_CLASS:
            _issue(issues, "invalid_semantic_class", f"unsupported semantic_class: {term.get('semantic_class')!r}", term_id)
        if term.get("evidence_status") not in ALLOWED_EVIDENCE_STATUS:
            _issue(issues, "invalid_evidence_status", f"unsupported evidence_status: {term.get('evidence_status')!r}", term_id)
        if term.get("ontological_status") not in ALLOWED_ONTOLOGICAL_STATUS:
            _issue(
                issues,
                "ontological_overclaim",
                "R1 permits only not_asserted, unresolved, or not_applicable; ontological proof claims require schema revision and independent evidence",
                term_id,
            )

        for field in ("definition", "operational_meaning"):
            if not _nonempty_string(term.get(field)):
                _issue(issues, "missing_term_text", f"{field} must be a non-empty string", term_id)

        authority = term.get("authority")
        if not isinstance(authority, dict):
            _issue(issues, "invalid_authority", "authority must be an object", term_id)
        else:
            for key in AUTHORITY_KEYS:
                if authority.get(key) is not False:
                    _issue(issues, "semantic_authority_leak", f"authority.{key} must be false in R1", term_id)

        evidence_refs = term.get("evidence_refs")
        _validate_evidence_refs(
            evidence_refs,
            issues,
            term_id,
            allow_empty=term.get("evidence_status") not in {"structural_contract"},
        )

        non_claims = term.get("explicit_non_claims")
        if not _string_list(non_claims) or len(non_claims) < 2:
            _issue(issues, "insufficient_non_claims", "explicit_non_claims must contain at least two bounded non-claims", term_id)

        measurement = term.get("measurement")
        if not isinstance(measurement, dict):
            _issue(issues, "invalid_measurement", "measurement must be an object", term_id)
        else:
            measurement_status = measurement.get("status")
            if measurement_status not in ALLOWED_MEASUREMENT_STATUS:
                _issue(issues, "invalid_measurement_status", f"unsupported measurement status: {measurement_status!r}", term_id)
            if term.get("evidence_status") == "testable_hypothesis":
                if measurement_status == "structural_only":
                    _issue(issues, "hypothesis_without_measurement_path", "testable hypotheses may not use structural_only measurement status", term_id)
                if not _nonempty_string(measurement.get("hypothesis")):
                    _issue(issues, "missing_measurement_hypothesis", "testable hypotheses require measurement.hypothesis", term_id)
                if not _string_list(measurement.get("metrics")):
                    _issue(issues, "missing_measurement_metrics", "testable hypotheses require at least one metric", term_id)
            if measurement_status == "completed":
                refs = measurement.get("evidence_refs")
                if not _string_list(refs):
                    _issue(issues, "completed_measurement_without_evidence", "completed measurement requires evidence_refs", term_id)
                else:
                    _validate_evidence_refs(refs, issues, term_id, allow_empty=False)

    _validate_lineage([term for term in terms if isinstance(term, dict)], issues)

    return {
        "schema_version": SCHEMA_VERSION,
        "passed": not issues,
        "registry_sha256": _canonical_hash(registry),
        "term_count": len(terms),
        "active_term_count": sum(1 for term in terms if isinstance(term, dict) and term.get("status") == "active"),
        "issues": issues,
        "truth_boundary": (
            "A passing report verifies registry structure, evidence-reference presence, lineage consistency, explicit non-claims, "
            "and absence of semantic authority leakage. It does not prove that the vocabulary improves cognition, continuity, "
            "identity, consciousness, sentience, subjective persistence, metaphysical status, or any physical resonance mechanism."
        ),
    }


def load_registry(path: Path = REGISTRY_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("semantic vocabulary registry must be a JSON object")
    return payload


def validate_registry_path(path: Path = REGISTRY_PATH) -> Dict[str, Any]:
    return validate_registry(load_registry(path))


if __name__ == "__main__":
    report = validate_registry_path()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)
