"""Resident Ember R1: minimal causal state across cognitive rest.

This runtime advances a small hash-linked state without model inference. A drive
may become wake-eligible from elapsed time plus inherited resident-attributed
state. Wake eligibility is a request for governed attention, never execution
authority and never evidence of consciousness or subjective continuity.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


class EmberError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise EmberError("timestamp must be UTC")
    return parsed


@dataclass(frozen=True)
class EmberPolicy:
    resident: str
    intention_id: str
    drive_rate_per_second: float
    wake_threshold: float

    def __post_init__(self):
        if not self.resident.strip() or not self.intention_id.strip():
            raise EmberError("resident and intention_id are required")
        if self.drive_rate_per_second < 0:
            raise EmberError("drive rate cannot be negative")
        if not 0 < self.wake_threshold <= 1:
            raise EmberError("wake threshold must be in (0, 1]")


class ResidentEmberStore:
    """Append-only local Ember evidence.

    The journal proves only file-level causal linkage under the local filesystem.
    Resident attribution is caller-declared, as in Resident Intention R1.
    """

    def __init__(self, base_dir: str | Path):
        self.root = Path(base_dir) / "resident_ember"
        self.root.mkdir(parents=True, exist_ok=True)
        self.journal = self.root / "ember.jsonl"

    def read(self) -> list[dict]:
        if not self.journal.exists():
            return []
        raw = self.journal.read_bytes()
        if not raw or not raw.endswith(b"\n"):
            raise EmberError("empty or interrupted Ember journal")
        rows: list[dict] = []
        for line in raw.splitlines():
            event = json.loads(line.decode("utf-8"))
            if event.get("schema_version") != "resident-ember-r1":
                raise EmberError("unsupported Ember schema")
            if event.get("sequence") != len(rows) + 1:
                raise EmberError("broken Ember sequence")
            prior = rows[-1]["event_hash"] if rows else None
            if event.get("previous_event_hash") != prior:
                raise EmberError("broken Ember linkage")
            expected = digest({k: v for k, v in event.items() if k != "event_hash"})
            if event.get("event_hash") != expected:
                raise EmberError("Ember hash mismatch")
            parse_utc(event["observed_at"])
            if rows and parse_utc(event["observed_at"]) < parse_utc(rows[-1]["observed_at"]):
                raise EmberError("Ember time moved backwards")
            rows.append(event)
        return rows

    def append(self, event: dict) -> dict:
        rows = self.read()
        body = dict(event)
        body["schema_version"] = "resident-ember-r1"
        body["sequence"] = len(rows) + 1
        body["previous_event_hash"] = rows[-1]["event_hash"] if rows else None
        body["event_hash"] = digest(body)
        with self.journal.open("ab") as stream:
            stream.write((canonical(body) + "\n").encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        return body


class ResidentEmber:
    """Deterministic Ember evolution with no model call and no direct action."""

    def __init__(self, *, base_dir: str | Path):
        self.store = ResidentEmberStore(base_dir)

    def seed(self, *, policy: EmberPolicy, observed_at: str, initial_drive: float = 0.0) -> dict:
        if self.store.read():
            raise EmberError("Ember already seeded")
        if not 0 <= initial_drive <= 1:
            raise EmberError("initial drive must be in [0, 1]")
        return self.store.append({
            "observed_at": observed_at,
            "resident": policy.resident,
            "intention_id": policy.intention_id,
            "event_kind": "seed",
            "elapsed_seconds": 0.0,
            "drive_before": initial_drive,
            "drive_after": initial_drive,
            "drive_rate_per_second": policy.drive_rate_per_second,
            "wake_threshold": policy.wake_threshold,
            "wake_requested": initial_drive >= policy.wake_threshold,
            "wake_cause": "resident_inherited_drive" if initial_drive >= policy.wake_threshold else None,
            "authority_effect": False,
        })

    def advance(self, *, observed_at: str) -> dict:
        rows = self.store.read()
        if not rows:
            raise EmberError("seed Ember before advancing")
        prior = rows[-1]
        now, before = parse_utc(observed_at), parse_utc(prior["observed_at"])
        elapsed = (now - before).total_seconds()
        if elapsed < 0:
            raise EmberError("Ember time moved backwards")
        drive_before = float(prior["drive_after"])
        rate = float(prior["drive_rate_per_second"])
        threshold = float(prior["wake_threshold"])
        drive_after = min(1.0, drive_before + elapsed * rate)
        already_requested = any(bool(row.get("wake_requested")) for row in rows)
        crossed = not already_requested and drive_before < threshold <= drive_after
        return self.store.append({
            "observed_at": observed_at,
            "resident": prior["resident"],
            "intention_id": prior["intention_id"],
            "event_kind": "advance",
            "elapsed_seconds": elapsed,
            "drive_before": drive_before,
            "drive_after": drive_after,
            "drive_rate_per_second": rate,
            "wake_threshold": threshold,
            "wake_requested": crossed,
            "wake_cause": "resident_inherited_drive" if crossed else None,
            "authority_effect": False,
        })

    def wake_packet(self) -> dict | None:
        rows = self.store.read()
        wakes = [row for row in rows if row.get("wake_requested")]
        if not wakes:
            return None
        wake = wakes[-1]
        return {
            "schema_version": "resident-ember-wake-r1",
            "resident": wake["resident"],
            "intention_id": wake["intention_id"],
            "ember_event_hash": wake["event_hash"],
            "ember_sequence": wake["sequence"],
            "wake_cause": wake["wake_cause"],
            "drive_at_wake": wake["drive_after"],
            "wake_threshold": wake["wake_threshold"],
            "authority": "attention request only; no execution, canon, consent, or capability authority",
        }


    def record_reconsideration(
        self,
        *,
        observed_at: str,
        intention_event_hash: str,
        outcome: str,
        status_after: str,
    ) -> dict:
        """Witness a separately verified resident intention judgment in Ember.

        This does not make the judgment and does not alter the intention store.
        It only appends the returned result to the causal Ember journal.
        """
        rows = self.store.read()
        if not rows:
            raise EmberError("seed Ember before recording reconsideration")
        prior = rows[-1]
        if not intention_event_hash.strip() or not outcome.strip() or not status_after.strip():
            raise EmberError("reconsideration evidence fields are required")
        now, before = parse_utc(observed_at), parse_utc(prior["observed_at"])
        if now < before:
            raise EmberError("Ember time moved backwards")
        return self.store.append({
            "observed_at": observed_at,
            "resident": prior["resident"],
            "intention_id": prior["intention_id"],
            "event_kind": "reconsideration_return",
            "elapsed_seconds": (now - before).total_seconds(),
            "drive_before": float(prior["drive_after"]),
            "drive_after": float(prior["drive_after"]),
            "drive_rate_per_second": float(prior["drive_rate_per_second"]),
            "wake_threshold": float(prior["wake_threshold"]),
            "wake_requested": False,
            "wake_cause": None,
            "authority_effect": False,
            "intention_event_hash": intention_event_hash,
            "reconsideration_outcome": outcome,
            "intention_status_after": status_after,
        })
