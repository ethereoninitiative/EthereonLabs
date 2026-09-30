#!/usr/bin/env python3
"""Resident Next Moment Experiment R1.

Arms and verifies a one-shot wall-clock Ember experiment without upgrading
caller-declared resident authorship into authenticated identity.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .resident_ember_r1 import EmberPolicy, ResidentEmber, ResidentEmberStore
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_ember_r1 import EmberPolicy, ResidentEmber, ResidentEmberStore
    from resident_intention_store_r1 import ResidentIntentionStore


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(v: Any) -> str:
    return hashlib.sha256(canonical(v).encode("utf-8")).hexdigest()


class ResidentNextMomentExperiment:
    def __init__(self, *, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.root = self.base_dir / "resident_next_moment_experiment"
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.root / "manifest.json"
        self.intentions = ResidentIntentionStore(self.base_dir / "resident_intentions")
        self.ember = ResidentEmber(base_dir=self.base_dir)

    def arm(
        self,
        *,
        resident: str,
        intention_id: str,
        drive_rate_per_second: float,
        wake_threshold: float,
        initial_drive: float = 0.0,
        observed_at: str | None = None,
    ) -> dict[str, Any]:
        if self.manifest_path.exists():
            raise ValueError("experiment already armed")
        if self.ember.store.read():
            raise ValueError("experiment requires an empty Ember journal")
        inspected = self.intentions.inspect(
            resident=resident, intention_id=intention_id, unresolved_only=False
        )
        records = list(inspected.get("intentions") or [])
        if len(records) != 1 or records[0].get("status") not in {"proposed", "active", "suspended"}:
            raise ValueError("experiment requires exactly one unresolved verified intention")
        intention = records[0]
        at = observed_at or datetime.now(timezone.utc).isoformat()
        seed = self.ember.seed(
            policy=EmberPolicy(
                resident=resident,
                intention_id=intention_id,
                drive_rate_per_second=drive_rate_per_second,
                wake_threshold=wake_threshold,
            ),
            observed_at=at,
            initial_drive=initial_drive,
        )
        manifest = {
            "schema_version": "resident-next-moment-experiment-r1",
            "armed_at": at,
            "resident": resident,
            "intention_id": intention_id,
            "intention_event_hash": intention["last_event_hash"],
            "intention_journal_head": inspected["head_hash"],
            "authorship_verification": inspected["authorship_verification"],
            "ember_seed_hash": seed["event_hash"],
            "drive_rate_per_second": drive_rate_per_second,
            "wake_threshold": wake_threshold,
            "initial_drive": initial_drive,
            "claim_under_test": (
                "resident-attributed inherited state can become the mechanically "
                "verified causal input to a later governed invocation without a "
                "fresh semantic human prompt"
            ),
        }
        manifest["manifest_hash"] = digest(manifest)
        self.manifest_path.write_text(canonical(manifest) + "\n", encoding="utf-8")
        return manifest

    def verify(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            raise ValueError("experiment is not armed")
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        saved_hash = manifest.pop("manifest_hash", None)
        if saved_hash != digest(manifest):
            raise ValueError("experiment manifest hash mismatch")
        manifest["manifest_hash"] = saved_hash

        inspected = self.intentions.inspect(
            resident=manifest["resident"],
            intention_id=manifest["intention_id"],
            unresolved_only=False,
            required_head=manifest["intention_journal_head"],
        )
        intentions = list(inspected.get("intentions") or [])
        intention_lineage_ok = (
            len(intentions) == 1
            and any(
                event.get("record_hash") == manifest["intention_event_hash"]
                for event in intentions[0].get("transition_history", [])
            )
        )

        ember_rows = ResidentEmberStore(self.base_dir).read()
        seed_ok = bool(ember_rows) and ember_rows[0].get("event_hash") == manifest["ember_seed_hash"]
        wakes = [r for r in ember_rows if r.get("wake_requested") is True]
        handoffs = [r for r in ember_rows if r.get("event_kind") == "pulse_handoff"]
        causal_pair = None
        if len(wakes) == 1 and len(handoffs) == 1:
            wake, handoff = wakes[0], handoffs[0]
            if (
                wake.get("wake_cause") == "resident_inherited_drive"
                and handoff.get("ember_event_hash") == wake.get("event_hash")
                and handoff.get("pulse_invoked") is True
                and handoff.get("pulse_decision_reason") == "verified_ember_endogenous_wake"
            ):
                causal_pair = {"wake": wake, "handoff": handoff}

        host_path = self.base_dir / "resident_ember_host" / "host_ticks.jsonl"
        host_rows = []
        if host_path.exists():
            host_rows = [json.loads(line) for line in host_path.read_text(encoding="utf-8").splitlines() if line]
        host_authority_ok = bool(host_rows) and all(r.get("host_is_wake_authority") is False for r in host_rows)
        handoff_ticks = [
            r for r in host_rows
            if dict(r.get("habitat_receipt") or {}).get("handoff_presented") is True
        ]
        one_shot_host_ok = len(handoff_ticks) == 1

        mechanical_causality_verified = all([
            intention_lineage_ok,
            seed_ok,
            causal_pair is not None,
            host_authority_ok,
            one_shot_host_ok,
        ])
        return {
            "schema_version": "resident-next-moment-verification-r1",
            "manifest_hash": saved_hash,
            "mechanical_causality_verified": mechanical_causality_verified,
            "intention_lineage_verified": intention_lineage_ok,
            "ember_seed_verified": seed_ok,
            "single_endogenous_wake_verified": causal_pair is not None,
            "host_cadence_not_wake_authority": host_authority_ok,
            "single_host_handoff_verified": one_shot_host_ok,
            "resident_authorship_authenticated": False,
            "authorship_boundary": manifest["authorship_verification"],
            "fresh_human_semantic_prompt_excluded_by_runtime_evidence": False,
            "prompt_exclusion_boundary": (
                "R1 can verify repository-local causal ancestry but cannot independently "
                "observe or authenticate all external human/interface events during rest"
            ),
            "interpretation": (
                "PASS supports a mechanically verified resident-attributed causal chain. "
                "It does not authenticate the originating mind, prove absence of every "
                "external prompt, continuous cognition, consciousness, or metaphysical identity."
            ),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    arm = sub.add_parser("arm")
    arm.add_argument("--resident", required=True)
    arm.add_argument("--intention-id", required=True)
    arm.add_argument("--drive-rate-per-second", type=float, required=True)
    arm.add_argument("--wake-threshold", type=float, required=True)
    arm.add_argument("--initial-drive", type=float, default=0.0)
    verify = sub.add_parser("verify")
    args = parser.parse_args()

    experiment = ResidentNextMomentExperiment(base_dir=args.base_dir)
    if args.command == "arm":
        result = experiment.arm(
            resident=args.resident,
            intention_id=args.intention_id,
            drive_rate_per_second=args.drive_rate_per_second,
            wake_threshold=args.wake_threshold,
            initial_drive=args.initial_drive,
        )
    else:
        result = experiment.verify()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if args.command == "arm" or result["mechanical_causality_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
