"""Durable resident declarations and reconsiderations; no execution authority.

The JSONL journal is the source of truth. Materialized records are replayed,
never written back. Hashes witness content/lineage, not an authenticated mind.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import re
from typing import Any
import uuid

try:
    from .governance_integrity_r1 import canonical_json, sha256_text, utc_now
    from .repo_paths_r1 import state_root
except ImportError:
    from governance_integrity_r1 import canonical_json, sha256_text, utc_now
    from repo_paths_r1 import state_root

UNRESOLVED = frozenset({"proposed", "active", "suspended"})
TRANSITIONS = {
    "continue": {"proposed": "active", "active": "active", "suspended": "active"},
    "suspend": {"proposed": "suspended", "active": "suspended"},
    "complete": {"active": "completed"},
    "abandon": dict.fromkeys(UNRESOLVED, "abandoned"),
    "revise": dict.fromkeys(UNRESOLVED, "superseded"),
    "supersede": dict.fromkeys(UNRESOLVED, "superseded"),
}
CONTENT_FIELDS = {"statement", "why_it_matters", "desired_next_action"}
DEFINITION_FIELDS = CONTENT_FIELDS | {"intention_id", "resident", "origin_context", "parent_intention_id", "evidence_refs"}
EVENT_FIELDS = {"schema_version", "sequence", "timestamp_utc", "prev_event_hash", "record_hash", "operation", "provenance", "request"}


class IntentionError(ValueError):
    """Invalid or conflicting evidence. No append is allowed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IntentionError(message)


def _text(value: Any, label: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty text")


def _keys(value: Any, expected: set[str], label: str) -> None:
    _require(isinstance(value, dict) and set(value) == expected, f"invalid {label} fields")


def _refs(value: Any) -> None:
    _require(isinstance(value, list) and bool(value), "evidence_refs must be a nonempty list")
    for ref in value:
        _text(ref, "evidence reference")
    _require(len(set(value)) == len(value), "duplicate evidence reference")


def _timestamp(value: Any) -> datetime:
    _text(value, "timestamp_utc")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise IntentionError("invalid timestamp_utc") from exc
    _require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0, "timestamp must be UTC")
    return parsed


def strict_json(text: str) -> Any:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise IntentionError(f"invalid JSON constant: {value}")

    try:
        return json.loads(text, object_pairs_hook=unique, parse_constant=invalid_constant)
    except json.JSONDecodeError as exc:
        raise IntentionError("malformed JSON") from exc


def _definition(definition: Any, states: dict, provenance: dict) -> None:
    _keys(definition, DEFINITION_FIELDS, "intention definition")
    ident = definition["intention_id"]
    _require(isinstance(ident, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", ident) is not None, "invalid intention_id")
    _require(ident not in states, "intention_id already exists; history cannot be replaced")
    for field in CONTENT_FIELDS | {"resident", "origin_context"}:
        _text(definition[field], field)
    _require(definition["resident"] == provenance["resident"], "resident/provenance mismatch")
    _refs(definition["evidence_refs"])
    parent = definition["parent_intention_id"]
    if parent is not None:
        _require(isinstance(parent, str) and parent in states, "parent intention is missing")
        _require(states[parent]["resident"] == definition["resident"], "cross-resident parent lineage")


def _new_record(definition: dict, event: dict, supersedes: list[str]) -> dict:
    return {
        **deepcopy(definition), "created_at": event["timestamp_utc"],
        "status": "proposed", "supersedes": supersedes,
        "last_reconsidered_at": None, "reconsideration_statement": None,
        "last_event_hash": event["record_hash"], "transition_history": [deepcopy(event)],
    }


def _apply(event: dict, states: dict) -> None:
    provenance = event["provenance"]
    _keys(provenance, {"actor_kind", "resident", "session_id", "source_ref"}, "provenance")
    _require(provenance["actor_kind"] == "resident", "requires an explicit resident declaration")
    for field in ("resident", "session_id", "source_ref"):
        _text(provenance[field], field)
    request = event["request"]
    if event["operation"] == "create":
        _definition(request, states, provenance)
        states[request["intention_id"]] = _new_record(request, event, [])
        return
    _require(event["operation"] == "reconsider", "unknown operation")
    _keys(request, {"intention_id", "expected_event_hash", "outcome", "reconsideration_statement", "evidence_refs", "replacement"}, "reconsideration")
    ident = request["intention_id"]
    _require(isinstance(ident, str) and ident in states, "unknown intention")
    current = states[ident]
    _require(provenance["resident"] == current["resident"], "reconsidering resident does not match origin")
    _require(request["expected_event_hash"] == current["last_event_hash"], "stale reconsideration; inspect current history first")
    _text(request["reconsideration_statement"], "reconsideration_statement")
    _refs(request["evidence_refs"])
    outcome = request["outcome"]
    _require(isinstance(outcome, str) and outcome in TRANSITIONS, "unknown reconsideration outcome")
    target = TRANSITIONS[outcome].get(current["status"])
    _require(target is not None, f"illegal transition: {current['status']} -> {outcome}")
    replacement = request["replacement"]
    if outcome in {"revise", "supersede"}:
        _definition(replacement, states, provenance)
        _require(replacement["parent_intention_id"] == ident, "replacement must name its predecessor as parent")
        states[replacement["intention_id"]] = _new_record(replacement, event, [ident])
    else:
        _require(replacement is None, "only revise/supersede may supply replacement content")
    current["status"] = target
    current["last_reconsidered_at"] = event["timestamp_utc"]
    current["reconsideration_statement"] = request["reconsideration_statement"]
    current["last_event_hash"] = event["record_hash"]
    current["transition_history"].append(deepcopy(event))


class ResidentIntentionStore:
    """Serialized, fsynced appends with strict replay and optimistic concurrency.

    A partial last line fails closed. Recovery is explicit; no repair/truncate API.
    OS locks are released when the process exits, including unexpected exits.
    """

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else state_root() / "resident_intentions"
        self.journal_path = self.base_dir / "intentions.jsonl"

    @contextmanager
    def _locked(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        with (self.base_dir / "intentions.lock").open("a+b") as lock:
            if os.name == "nt":
                import msvcrt
                if lock.seek(0, os.SEEK_END) == 0:
                    lock.write(b"\0")
                    lock.flush()
                lock.seek(0)
                try:
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise IntentionError("intention store busy; retry after rereading") from exc
            else:
                import fcntl
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise IntentionError("intention store busy; retry after rereading") from exc
            try:
                yield
            finally:
                if os.name == "nt":
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock, fcntl.LOCK_UN)

    def _read(self) -> tuple[list[dict], dict]:
        rows, states = [], {}
        if not self.journal_path.exists():
            return rows, states
        raw = self.journal_path.read_bytes()
        _require(bool(raw) and raw.endswith(b"\n"), "empty or interrupted intention journal")
        previous_time = None
        for line in raw.splitlines():
            try:
                event = strict_json(line.decode("utf-8"))
            except UnicodeError as exc:
                raise IntentionError("journal is not UTF-8") from exc
            _keys(event, EVENT_FIELDS, "journal event")
            _require(type(event["schema_version"]) is int and event["schema_version"] == 1, "unsupported intention schema")
            _require(type(event["sequence"]) is int and event["sequence"] == len(rows) + 1, "broken event sequence")
            _require(event["prev_event_hash"] == (rows[-1]["record_hash"] if rows else None), "broken event linkage")
            expected_hash = sha256_text(canonical_json({k: v for k, v in event.items() if k != "record_hash"}))
            _require(event["record_hash"] == expected_hash, "journal record hash mismatch")
            timestamp = _timestamp(event["timestamp_utc"])
            _require(previous_time is None or timestamp >= previous_time, "event timestamp moved backwards")
            _apply(event, states)
            rows.append(event)
            previous_time = timestamp
        return rows, states

    @staticmethod
    def _receipt(rows: list[dict]) -> dict:
        return {"schema_version": 1, "event_count": len(rows), "head_hash": rows[-1]["record_hash"] if rows else None,
                "authority": "resident declarations only; no execution or canon authority",
                "authorship_verification": "caller-declared resident metadata; not identity authentication"}

    def inspect(self, *, resident: str | None = None, intention_id: str | None = None, unresolved_only: bool = True, required_head: str | None = None) -> dict:
        with self._locked():
            rows, states = self._read()
            if required_head is not None:
                _text(required_head, "required_head")
                _require(any(row["record_hash"] == required_head for row in rows), "saved receipt head is absent; history was replaced, truncated, or is the wrong store")
            if intention_id is not None:
                _require(intention_id in states, "unknown intention")
                records = [states[intention_id]]
            else:
                records = [r for r in states.values() if not unresolved_only or r["status"] in UNRESOLVED]
            if resident is not None:
                records = [r for r in records if r["resident"] == resident]
            return {**self._receipt(rows), "journal_exists": self.journal_path.exists(), "required_head": required_head, "intentions": records}

    def _append(self, operation: str, request: dict, provenance: dict) -> dict:
        with self._locked():
            rows, states = self._read()
            event = {"schema_version": 1, "sequence": len(rows) + 1, "timestamp_utc": utc_now(),
                     "prev_event_hash": rows[-1]["record_hash"] if rows else None,
                     "operation": operation, "request": deepcopy(request), "provenance": deepcopy(provenance)}
            event["record_hash"] = sha256_text(canonical_json(event))
            _require(not rows or _timestamp(event["timestamp_utc"]) >= _timestamp(rows[-1]["timestamp_utc"]), "clock moved backwards")
            _apply(event, states)  # Validate the entire operation before any bytes are appended.
            with self.journal_path.open("ab") as journal:
                journal.write((canonical_json(event) + "\n").encode("utf-8"))
                journal.flush()
                os.fsync(journal.fileno())
            if os.name != "nt":
                directory_fd = os.open(self.base_dir, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            rows.append(event)
            affected = [r for r in states.values() if r["last_event_hash"] == event["record_hash"]]
            return {**self._receipt(rows), "event": event, "intentions": affected}

    def create(self, definition: dict, provenance: dict) -> dict:
        _require(isinstance(definition, dict), "definition must be an object")
        definition = deepcopy(definition)
        definition.setdefault("intention_id", "intent-" + uuid.uuid4().hex)
        definition.setdefault("parent_intention_id", None)
        return self._append("create", definition, provenance)

    def reconsider(self, request: dict, provenance: dict) -> dict:
        _require(isinstance(request, dict), "reconsideration must be an object")
        request = deepcopy(request)
        request.setdefault("replacement", None)
        return self._append("reconsider", request, provenance)
