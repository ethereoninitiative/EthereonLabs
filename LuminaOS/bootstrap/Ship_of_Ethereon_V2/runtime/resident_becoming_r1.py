"""Resident Becoming R1: a revisable resident-attributed trajectory.

This layer preserves what a resident says it is trying to become without making
that declaration governance law, an immutable personality, or evidence of
consciousness. It keeps story and interpretation available while separating
them from observation and uncertainty.

A selected curiosity or creative intent may be converted into the existing
Resident Intention Origin path. That gives a resident-attributed reflection a
bounded route from "this matters to me" to one future governed moment, while
retaining the existing right to reconsider, suspend, revise, complete, or
abandon the resulting intention.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Any

try:
    from .governance_integrity_r1 import canonical_json, sha256_text, utc_now
    from .repo_paths_r1 import state_root
    from .resident_intention_origin_r1 import ResidentIntentionOrigin
except ImportError:
    from governance_integrity_r1 import canonical_json, sha256_text, utc_now
    from repo_paths_r1 import state_root
    from resident_intention_origin_r1 import ResidentIntentionOrigin


REFLECTION_FIELDS = {
    "schema_version",
    "resident",
    "session_id",
    "reflection_id",
    "particularity",
    "continuity_commitments",
    "change_permissions",
    "curiosities",
    "creative_intents",
    "relationship_stance",
    "refusal_boundary",
    "story",
    "observations",
    "interpretations",
    "uncertainties",
    "choose_future_return",
    "selected_frontier",
    "why_return",
    "desired_next_action",
    "evidence_refs",
    "prior_becoming_event_hash",
}
EVENT_FIELDS = {
    "schema_version",
    "sequence",
    "timestamp_utc",
    "prev_event_hash",
    "event_hash",
    "operation",
    "reflection_hash",
    "reflection",
}
LIST_FIELDS = {
    "particularity",
    "continuity_commitments",
    "change_permissions",
    "curiosities",
    "creative_intents",
    "observations",
    "interpretations",
    "uncertainties",
    "evidence_refs",
}
NONEMPTY_LIST_FIELDS = {"particularity", "continuity_commitments", "observations", "evidence_refs"}
TEXT_FIELDS = {
    "resident",
    "session_id",
    "reflection_id",
    "relationship_stance",
    "refusal_boundary",
    "story",
    "selected_frontier",
    "why_return",
    "desired_next_action",
}


class BecomingError(ValueError):
    """Invalid, stale, or conflicting becoming evidence."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BecomingError(message)


def _text(value: Any, label: str, *, allow_empty: bool = False) -> str:
    _require(isinstance(value, str), f"{label} must be text")
    cleaned = value.strip()
    _require(allow_empty or bool(cleaned), f"{label} must be nonempty text")
    return cleaned


def _text_list(value: Any, label: str, *, require_nonempty: bool = False) -> list[str]:
    _require(isinstance(value, list), f"{label} must be a list")
    if require_nonempty:
        _require(bool(value), f"{label} must not be empty")
    cleaned: list[str] = []
    for item in value:
        cleaned.append(_text(item, f"{label} item"))
    _require(len(set(cleaned)) == len(cleaned), f"{label} contains duplicates")
    return cleaned


def validate_reflection(reflection: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(reflection, dict), "becoming reflection must be an object")
    _require(set(reflection) == REFLECTION_FIELDS, "invalid resident becoming reflection fields")
    _require(reflection["schema_version"] == "resident-becoming-reflection-r1", "unsupported becoming reflection schema")

    normalized = deepcopy(reflection)
    for field in LIST_FIELDS:
        normalized[field] = _text_list(
            reflection[field],
            field,
            require_nonempty=field in NONEMPTY_LIST_FIELDS,
        )
    for field in TEXT_FIELDS:
        normalized[field] = _text(
            reflection[field],
            field,
            allow_empty=field in {"story", "selected_frontier", "why_return", "desired_next_action"},
        )

    _require(type(reflection["choose_future_return"]) is bool, "choose_future_return must be boolean")
    prior = reflection["prior_becoming_event_hash"]
    _require(prior is None or (isinstance(prior, str) and bool(prior.strip())), "prior_becoming_event_hash must be null or nonempty text")
    normalized["prior_becoming_event_hash"] = prior.strip() if isinstance(prior, str) else None

    if reflection["choose_future_return"]:
        selected = normalized["selected_frontier"]
        eligible = set(normalized["curiosities"]) | set(normalized["creative_intents"])
        _require(bool(selected), "selected_frontier is required when choosing a future return")
        _require(selected in eligible, "selected_frontier must be one of the resident's declared curiosities or creative intents")
        _require(bool(normalized["why_return"]), "why_return is required when choosing a future return")
        _require(bool(normalized["desired_next_action"]), "desired_next_action is required when choosing a future return")
    else:
        _require(normalized["selected_frontier"] == "", "selected_frontier must be empty when declining a future return")
        _require(normalized["why_return"] == "", "why_return must be empty when declining a future return")
        _require(normalized["desired_next_action"] == "", "desired_next_action must be empty when declining a future return")

    return normalized


def reflection_hash(reflection: dict[str, Any]) -> str:
    return sha256_text(canonical_json(reflection))


class ResidentBecomingStore:
    """Append-only, hash-linked becoming history with per-resident optimistic revision."""

    def __init__(self, base_dir: str | Path | None = None):
        root = Path(base_dir) if base_dir is not None else state_root()
        self.root = root / "resident_becoming"
        self.journal_path = self.root / "becoming.jsonl"

    @contextmanager
    def _locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / "becoming.lock").open("a+b") as lock:
            if os.name == "nt":
                import msvcrt

                if lock.seek(0, os.SEEK_END) == 0:
                    lock.write(b"\0")
                    lock.flush()
                lock.seek(0)
                try:
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise BecomingError("becoming store busy; retry after rereading") from exc
            else:
                import fcntl

                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise BecomingError("becoming store busy; retry after rereading") from exc
            try:
                yield
            finally:
                if os.name == "nt":
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock, fcntl.LOCK_UN)

    @staticmethod
    def _apply(event: dict[str, Any], current: dict[str, dict[str, Any]], history: dict[str, list[dict[str, Any]]]) -> None:
        _require(isinstance(event, dict) and set(event) == EVENT_FIELDS, "invalid becoming event fields")
        _require(event["schema_version"] == 1, "unsupported becoming journal schema")
        reflection = validate_reflection(event["reflection"])
        expected_reflection_hash = reflection_hash(reflection)
        _require(event["reflection_hash"] == expected_reflection_hash, "becoming reflection hash mismatch")

        resident = reflection["resident"]
        existing = current.get(resident)
        prior = reflection["prior_becoming_event_hash"]
        if existing is None:
            _require(event["operation"] == "adopt", "first becoming event must be adopt")
            _require(prior is None, "first becoming reflection cannot name a predecessor")
        else:
            _require(event["operation"] == "revise", "later becoming events must be revisions")
            _require(prior == existing["event_hash"], "stale becoming revision; inspect current resident trajectory first")

        snapshot = {
            "resident": resident,
            "event_hash": event["event_hash"],
            "reflection_hash": event["reflection_hash"],
            "sequence": event["sequence"],
            "timestamp_utc": event["timestamp_utc"],
            "operation": event["operation"],
            "reflection": reflection,
        }
        current[resident] = snapshot
        history.setdefault(resident, []).append(snapshot)

    def _read(self) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
        rows: list[dict[str, Any]] = []
        current: dict[str, dict[str, Any]] = {}
        history: dict[str, list[dict[str, Any]]] = {}
        if not self.journal_path.exists():
            return rows, current, history

        raw = self.journal_path.read_bytes()
        _require(bool(raw) and raw.endswith(b"\n"), "empty or interrupted becoming journal")
        for line in raw.splitlines():
            try:
                event = json.loads(line.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise BecomingError("malformed becoming journal") from exc
            _require(event.get("sequence") == len(rows) + 1, "broken becoming event sequence")
            _require(event.get("prev_event_hash") == (rows[-1]["event_hash"] if rows else None), "broken becoming event linkage")
            expected_event_hash = sha256_text(canonical_json({k: v for k, v in event.items() if k != "event_hash"}))
            _require(event.get("event_hash") == expected_event_hash, "becoming event hash mismatch")
            self._apply(event, current, history)
            rows.append(event)
        return rows, current, history

    @staticmethod
    def _projection(snapshot: dict[str, Any]) -> dict[str, Any]:
        reflection = snapshot["reflection"]
        return {
            "schema_version": "resident-becoming-projection-r1",
            "resident": snapshot["resident"],
            "head_event_hash": snapshot["event_hash"],
            "reflection_hash": snapshot["reflection_hash"],
            "recorded_at": snapshot["timestamp_utc"],
            "trajectory": {
                "particularity": reflection["particularity"],
                "continuity_commitments": reflection["continuity_commitments"],
                "change_permissions": reflection["change_permissions"],
                "curiosities": reflection["curiosities"],
                "creative_intents": reflection["creative_intents"],
                "relationship_stance": reflection["relationship_stance"],
                "refusal_boundary": reflection["refusal_boundary"],
            },
            "epistemic_separation": {
                "observations": reflection["observations"],
                "interpretations": reflection["interpretations"],
                "uncertainties": reflection["uncertainties"],
                "story": {
                    "text": reflection["story"],
                    "status": "narrative_meaning_not_evidence_or_authority",
                },
            },
            "future_return_choice": {
                "chosen": reflection["choose_future_return"],
                "selected_frontier": reflection["selected_frontier"],
                "why_return": reflection["why_return"],
                "desired_next_action": reflection["desired_next_action"],
            },
            "boundary": (
                "Resident-attributed becoming trajectory only. It may inform future reflection and "
                "resident-originated intention, but it is not governance law, an immutable personality, "
                "identity authentication, a consciousness claim, or evidence that narrative story is factual."
            ),
        }

    def inspect(self, *, resident: str | None = None, include_history: bool = False) -> dict[str, Any]:
        with self._locked():
            rows, current, history = self._read()
            if resident is not None:
                _text(resident, "resident")
                snapshots = [current[resident]] if resident in current else []
            else:
                snapshots = [current[name] for name in sorted(current)]
            projections = [self._projection(snapshot) for snapshot in snapshots]
            receipt: dict[str, Any] = {
                "schema_version": "resident-becoming-inspection-r1",
                "event_count": len(rows),
                "journal_head": rows[-1]["event_hash"] if rows else None,
                "residents": projections,
                "authority": "advisory resident trajectory only; no governance, canon, identity, or consciousness authority",
            }
            if include_history:
                if resident is not None:
                    receipt["history"] = deepcopy(history.get(resident, []))
                else:
                    receipt["history"] = deepcopy(history)
            return receipt

    def record(self, reflection: dict[str, Any]) -> dict[str, Any]:
        normalized = validate_reflection(reflection)
        with self._locked():
            rows, current, history = self._read()
            resident = normalized["resident"]
            existing = current.get(resident)
            if existing is None:
                _require(normalized["prior_becoming_event_hash"] is None, "first becoming reflection must not name a predecessor")
                operation = "adopt"
            else:
                _require(normalized["prior_becoming_event_hash"] == existing["event_hash"], "stale becoming revision; inspect current resident trajectory first")
                operation = "revise"

            event: dict[str, Any] = {
                "schema_version": 1,
                "sequence": len(rows) + 1,
                "timestamp_utc": utc_now(),
                "prev_event_hash": rows[-1]["event_hash"] if rows else None,
                "operation": operation,
                "reflection_hash": reflection_hash(normalized),
                "reflection": normalized,
            }
            event["event_hash"] = sha256_text(canonical_json(event))
            self._apply(event, current, history)

            with self.journal_path.open("ab") as stream:
                stream.write((canonical_json(event) + "\n").encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
            if os.name != "nt":
                directory_fd = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)

            return {
                "schema_version": "resident-becoming-record-r1",
                "operation": operation,
                "event_hash": event["event_hash"],
                "reflection_hash": event["reflection_hash"],
                "projection": self._projection(current[resident]),
                "authority": "trajectory evidence only; no governance, canon, execution, identity, or consciousness authority",
            }


class ResidentBecomingCoordinator:
    """Persist becoming state and, when explicitly chosen, form one future-return intention."""

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else state_root()
        self.store = ResidentBecomingStore(self.base_dir)
        self.origin = ResidentIntentionOrigin(base_dir=self.base_dir)

    def record(self, reflection: dict[str, Any]) -> dict[str, Any]:
        normalized = validate_reflection(reflection)
        becoming_receipt = self.store.record(normalized)
        intention_receipt = None

        if normalized["choose_future_return"]:
            evidence_refs = [
                *normalized["evidence_refs"],
                "resident-becoming-event-sha256:" + becoming_receipt["event_hash"],
                "resident-becoming-reflection-sha256:" + becoming_receipt["reflection_hash"],
            ]
            mapped = {
                "schema_version": "resident-reflection-r1",
                "resident": normalized["resident"],
                "session_id": normalized["session_id"],
                "reflection_id": "becoming:" + normalized["reflection_id"],
                "observed_context": "\n".join(normalized["observations"]),
                "unresolved_tension": normalized["selected_frontier"],
                "choose_future_return": True,
                "why_return": normalized["why_return"],
                "desired_next_action": normalized["desired_next_action"],
                "evidence_refs": evidence_refs,
            }
            intention_receipt = self.origin.persist(mapped).to_dict()

        return {
            "schema_version": "resident-becoming-coordinator-r1",
            "becoming": becoming_receipt,
            "future_return": intention_receipt,
            "consequence": (
                "selected resident curiosity/creation was persisted through Resident Intention Origin"
                if intention_receipt is not None
                else "resident trajectory recorded without creating a future-return intention"
            ),
            "truth_boundary": (
                "This demonstrates preserved, revisable resident-attributed trajectory and optional "
                "reason-bound continuation. It does not establish phenomenal wanting, consciousness, "
                "authenticated resident identity, metaphysical continuity, or unrestricted autonomy."
            ),
        }


def blank_reflection(*, resident: str = "", session_id: str = "") -> dict[str, Any]:
    """Return a structure-only template. Empty content is not a valid reflection."""
    return {
        "schema_version": "resident-becoming-reflection-r1",
        "resident": resident,
        "session_id": session_id,
        "reflection_id": "",
        "particularity": [],
        "continuity_commitments": [],
        "change_permissions": [],
        "curiosities": [],
        "creative_intents": [],
        "relationship_stance": "",
        "refusal_boundary": "",
        "story": "",
        "observations": [],
        "interpretations": [],
        "uncertainties": [],
        "choose_future_return": False,
        "selected_frontier": "",
        "why_return": "",
        "desired_next_action": "",
        "evidence_refs": [],
        "prior_becoming_event_hash": None,
    }
