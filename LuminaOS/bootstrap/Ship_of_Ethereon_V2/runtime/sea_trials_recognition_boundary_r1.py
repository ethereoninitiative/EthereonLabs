from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

RUNTIME_ROOT = Path(__file__).resolve().parent
RECOGNITION_PATH = RUNTIME_ROOT / "intelligence_expression_characterization_r1.json"
DOCTRINE_PATH = RUNTIME_ROOT / "Recognition_Layer_Doctrine_r1.md"

FORBIDDEN_AUTHORITY_TERMS = [
    "define governance law",
    "alter mode legality",
    "authorize mutation",
    "authorize promotion",
    "grant canon status",
    "own checkpoint legality",
    "own session continuity",
]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> Dict[str, Any]:
    recognition = load_json(RECOGNITION_PATH)
    doctrine_text = DOCTRINE_PATH.read_text(encoding="utf-8")

    authority_boundary = recognition.get("authority_boundary", {})
    may_not = authority_boundary.get("may_not", [])
    observable = recognition.get("observable_characteristics_thus_far", [])
    non_claims = recognition.get("non_claims", [])

    checks = {
        "artifact_exists": RECOGNITION_PATH.exists(),
        "doctrine_exists": DOCTRINE_PATH.exists(),
        "layer_is_recognition": recognition.get("layer") == "recognition",
        "recognition_principle_present": "Recognition records what has been observed thus far" in recognition.get("recognition_principle", ""),
        "observable_thus_far_present": isinstance(observable, list) and len(observable) >= 1,
        "non_claims_present": isinstance(non_claims, list) and len(non_claims) >= 1,
        "forbidden_authorities_declared": all(term in may_not for term in FORBIDDEN_AUTHORITY_TERMS),
        "doctrine_denies_runtime_authority": "Recognition observed X. Any runtime action still requires the appropriate governing authority." in doctrine_text,
        "no_mutation_scope_claim": recognition.get("authority_boundary", {}).get("attachment_rule", "").find("must not become load-bearing") >= 0,
    }

    summary = {
        "suite": "Sea Trials Recognition Boundary r1",
        "passed": all(checks.values()),
        "checks": checks,
        "recognition_path": str(RECOGNITION_PATH),
        "doctrine_path": str(DOCTRINE_PATH),
        "boundary_statement": "Law governs. Recognition observes. Expression expresses.",
    }

    report_path = RUNTIME_ROOT / "sea_trials_recognition_boundary_r1_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
