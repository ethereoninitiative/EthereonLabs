import json
from probe_interface import check_transition, check_action


CASES = [
    {
        "name": "continuity_to_sea_trial_allowed",
        "kind": "transition",
        "current_mode": "continuity",
        "target_mode": "sea_trial",
        "expected_allowed": True,
    },
    {
        "name": "sea_trial_to_drydock_not_declared",
        "kind": "transition",
        "current_mode": "sea_trial",
        "target_mode": "drydock",
        "expected_allowed": False,
    },
    {
        "name": "sea_trial_canon_promotion_forbidden",
        "kind": "action",
        "mode": "sea_trial",
        "action": "canon_promotion",
        "expected_allowed": False,
    },
    {
        "name": "continuity_review_allowed_by_absence_of_forbid",
        "kind": "action",
        "mode": "continuity",
        "action": "review",
        "expected_allowed": True,
    },
]


def run_case(case: dict) -> dict:
    if case["kind"] == "transition":
        probe = check_transition(case["current_mode"], case["target_mode"])
    else:
        probe = check_action(case["mode"], case["action"])

    available = probe.get("available") is True
    observed = probe.get("result")
    passed = available and observed is case["expected_allowed"]

    return {
        **case,
        "probe_available": available,
        "observed_allowed": observed,
        "passed": passed,
    }


def main() -> dict:
    results = [run_case(case) for case in CASES]
    return {
        "suite": "Governance Prolog Probe Self Check r1",
        "passed": all(item["passed"] for item in results),
        "results": results,
        "authority": "non-authoritative probe only; does not govern runtime behavior",
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
