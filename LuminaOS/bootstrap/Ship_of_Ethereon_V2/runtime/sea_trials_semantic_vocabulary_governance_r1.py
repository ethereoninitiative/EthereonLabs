from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List
import json

try:
    from .semantic_vocabulary_governance_r1 import load_registry, validate_registry
except Exception:
    from semantic_vocabulary_governance_r1 import load_registry, validate_registry


def issue_codes(report: Dict[str, Any]) -> set[str]:
    return {issue.get("code") for issue in report.get("issues", [])}


def expect_failure(registry: Dict[str, Any], expected_code: str) -> Dict[str, Any]:
    report = validate_registry(registry)
    codes = issue_codes(report)
    return {
        "passed": report.get("passed") is False and expected_code in codes,
        "expected_code": expected_code,
        "observed_codes": sorted(code for code in codes if isinstance(code, str)),
    }


def main() -> Dict[str, Any]:
    registry = load_registry()
    baseline = validate_registry(registry)

    authority_leak = deepcopy(registry)
    authority_leak["terms"][0]["authority"]["runtime_action"] = True

    ontology_overclaim = deepcopy(registry)
    ontology_overclaim["terms"][1]["ontological_status"] = "proven_persistent_identity"

    duplicate_alias = deepcopy(registry)
    duplicate_alias["terms"][2]["aliases"].append("vessel")

    unsupported_effect_claim = deepcopy(registry)
    unsupported_effect_claim["semantic_effect_hypothesis"]["status"] = "supported"
    unsupported_effect_claim["semantic_effect_hypothesis"]["evidence_refs"] = []

    completed_without_evidence = deepcopy(registry)
    completed_without_evidence["terms"][2]["measurement"]["status"] = "completed"
    completed_without_evidence["terms"][2]["measurement"]["evidence_refs"] = []

    lineage_cycle = deepcopy(registry)
    lineage_cycle["terms"][0]["lineage"]["supersedes"] = "SVG-002"
    lineage_cycle["terms"][1]["lineage"]["supersedes"] = "SVG-001"

    missing_evidence = deepcopy(registry)
    missing_evidence["terms"][0]["evidence_refs"][0] = "not/a/real/repository/path.py"

    trials: List[Dict[str, Any]] = [
        {
            "trial": "baseline_registry_passes",
            "passed": baseline.get("passed") is True,
            "details": {
                "registry_sha256": baseline.get("registry_sha256"),
                "term_count": baseline.get("term_count"),
                "issues": baseline.get("issues"),
            },
        },
        {"trial": "semantic_authority_leak_fails_closed", **expect_failure(authority_leak, "semantic_authority_leak")},
        {"trial": "ontological_overclaim_fails_closed", **expect_failure(ontology_overclaim, "ontological_overclaim")},
        {"trial": "duplicate_alias_fails_closed", **expect_failure(duplicate_alias, "duplicate_name_or_alias")},
        {"trial": "semantic_effect_claim_requires_evidence", **expect_failure(unsupported_effect_claim, "effect_claim_without_evidence")},
        {"trial": "completed_measurement_requires_evidence", **expect_failure(completed_without_evidence, "completed_measurement_without_evidence")},
        {"trial": "lineage_cycle_fails_closed", **expect_failure(lineage_cycle, "lineage_cycle")},
        {"trial": "missing_evidence_ref_fails_closed", **expect_failure(missing_evidence, "missing_evidence_ref")},
    ]

    summary = {
        "suite": "Sea Trials Semantic Vocabulary Governance R1",
        "passed": all(trial.get("passed") for trial in trials),
        "trials": trials,
        "truth_boundary": (
            "These sea trials verify fail-closed semantic-contract governance behavior. They do not test whether Ethereon vocabulary "
            "improves model cognition. That requires a separately controlled semantic-substrate ablation study."
        ),
    }
    return summary


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
