"""End-to-end sea trial for Ember wake integration in the resident host loop."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

try:
    from .resident_ember_r1 import EmberPolicy, ResidentEmber
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_ember_r1 import EmberPolicy, ResidentEmber
    from resident_intention_store_r1 import ResidentIntentionStore


BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
RESIDENT = "ETH-001"
INTENTION = "ember-host-loop-r1"


def provenance():
    return {
        "actor_kind": "resident",
        "resident": RESIDENT,
        "session_id": "ember-host-loop-sea-trial",
        "source_ref": "sea-trial-explicit-resident-declaration",
    }


def definition():
    return {
        "intention_id": INTENTION,
        "resident": RESIDENT,
        "origin_context": "Resident Ember host loop sea trial",
        "statement": "Present one inherited wake through the resident host.",
        "why_it_matters": "Proves causal wake integration without repeated handoff.",
        "desired_next_action": "inspect_ember_host_loop_question",
        "parent_intention_id": None,
        "evidence_refs": ["sea-trial:resident-ember-host-loop-r1"],
    }


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        intentions = ResidentIntentionStore(root / "resident_intentions")
        intentions.create(definition(), provenance())
        ember = ResidentEmber(base_dir=root)
        ember.seed(
            policy=EmberPolicy(
                resident=RESIDENT,
                intention_id=INTENTION,
                drive_rate_per_second=0.0,
                wake_threshold=0.5,
            ),
            observed_at="2026-09-29T00:00:00+00:00",
            initial_drive=0.5,
        )

        proc = subprocess.run(
            [
                sys.executable,
                str(BOOTSTRAP_ROOT / "studio" / "lumina_resident_r1.py"),
                "--resident",
                "--project-id",
                "lumina-os",
                "--base-dir",
                str(root),
                "--interval-seconds",
                "0",
                "--max-pulses",
                "2",
                "--json",
            ],
            cwd=str(BOOTSTRAP_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        receipts = [
            json.loads(line)
            for line in proc.stdout.splitlines()
            if line.strip().startswith("{")
        ]
        rows = ember.store.read()
        handoffs = [row for row in rows if row.get("event_kind") == "pulse_handoff"]

        checks = {
            "resident_exit_zero": proc.returncode == 0,
            "two_ticks_emitted": len(receipts) == 2,
            "first_tick_used_ember": len(receipts) >= 1
            and receipts[0].get("resident_wake_source") == "resident_ember",
            "first_tick_preserved_no_force": len(receipts) >= 1
            and (receipts[0].get("ember_bridge") or {}).get("operator_force_used") is False,
            "second_tick_returned_to_cadence": len(receipts) >= 2
            and receipts[1].get("resident_wake_source") == "cadence",
            "exactly_one_handoff_recorded": len(handoffs) == 1,
            "wake_consumed_after_handoff": ember.wake_packet() is None,
            "handoff_has_no_authority_effect": len(handoffs) == 1
            and handoffs[0].get("authority_effect") is False,
        }
        for name, passed in checks.items():
            if not passed:
                raise AssertionError(f"{name} failed; stdout={proc.stdout!r}; stderr={proc.stderr!r}")
            print(f"PASS {name}")
        print(f"Resident Ember host loop R1: {len(checks)}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()
