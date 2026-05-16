from __future__ import annotations

from psi42_v17_observation_receipt_summary_r1 import summarize


def main() -> int:
    receipt = {
        "run_id": "run-example",
        "target_mode": "Observation",
        "action_type": "audit",
        "halted": False,
        "governance_chain_status": {"valid": True},
        "probe_artifacts": {
            "instrument_version": "v1.7",
            "metrics": {
                "hybrid_continuity_coherence": 0.8096,
                "RTC": 1.0,
                "RDS": 0.0,
                "RRS": 1.0,
                "HRC": 1.0,
            },
            "topology_receipt": {"receipt_type": "psi42_relational_restoration_r1"},
        },
    }
    summary = summarize(receipt)
    assert summary["overall_pass"] is True
    assert summary["checks"]["psi42_v17_selected"] is True
    assert summary["checks"]["topology_metrics_present"] is True
    assert summary["hybrid_continuity_coherence"] == 0.8096
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
