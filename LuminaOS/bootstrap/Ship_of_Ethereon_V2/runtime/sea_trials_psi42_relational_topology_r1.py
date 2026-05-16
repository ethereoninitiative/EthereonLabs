import json
from psi42_relational_topology_r1 import (
    compare_topologies,
    extract_relational_topology,
    make_restoration_receipt,
    simulate_semantic_drift,
)


def main() -> int:
    intent = (
        "Lumina OS is a HABITAT for harmonic human-AI continuity, governance, "
        "Minerva OS inhabitation, and recoverable topology."
    )
    symbols = {"HABITAT": 1.0, "CONTINUITY": 0.9, "MINERVA": 0.7}
    original = extract_relational_topology(intent, symbols)
    drifted = extract_relational_topology(simulate_semantic_drift(intent), symbols)
    comparison = compare_topologies(original, drifted)
    receipt = make_restoration_receipt(original, drifted, comparison)

    metrics = comparison.metrics
    assert metrics["RTC"] >= 0.25
    assert metrics["RDS"] <= 0.75
    assert receipt["receipt_type"] == "psi42_relational_restoration_r1"

    print(json.dumps({"metrics": metrics, "recommendation": receipt["recommended_repair"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
