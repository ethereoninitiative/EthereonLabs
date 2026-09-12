"""IRP-R1: bounded externalized interchange, never identity or execution authority.

Standalone standard-library implementation. Content hashes bind declarations;
they do not authenticate a resident or make a claim true. Nothing is executed,
fetched, promoted, or installed by receiving an exchange.
"""
from __future__ import annotations

import argparse
from collections import deque
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys

VERSION = "IRP-R1"
SCHEMA_PATH = Path(__file__).with_name("interresident_resonance_packet_r1.schema.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
CLAIM_GROUPS = ("observations", "interpretations", "questions", "proposals", "intentions", "memories")
MAX_PACKET_BYTES = 262144
MAX_EXCHANGE_BYTES = 8 * 1024 * 1024
MAX_PACKETS = 128
MAX_SEMANTIC_ITEMS = 1024


class ResonanceError(ValueError):
    """Fail-closed protocol violation; no append may follow."""


def require(condition, message):
    if not condition:
        raise ResonanceError(message)


def _json_domain(value, depth=0, max_depth=64):
    require(depth <= max_depth, f"IRP JSON exceeds depth {max_depth}")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        require(abs(value) <= 2**53 - 1, "integer outside interoperable safe range")
    elif type(value) is str:
        require(len(value) <= 65536, "string exceeds IRP limit")
        require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), "unpaired Unicode surrogate")
    elif type(value) is list:
        require(len(value) <= 1024, "array exceeds IRP limit")
        for item in value:
            _json_domain(item, depth + 1, max_depth)
    elif type(value) is dict:
        require(len(value) <= 1024, "object exceeds IRP limit")
        for key, item in value.items():
            require(type(key) is str, "JSON object key must be text")
            _json_domain(key, depth + 1, max_depth)
            _json_domain(item, depth + 1, max_depth)
    else:
        raise ResonanceError("IRP JSON rejects floats and non-JSON values")


def canonical(value):
    """UTF-8, code-point-sorted keys, compact separators, no float or normalization."""
    _json_domain(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def strict_json(raw):
    require(type(raw) in (str, bytes, bytearray), "JSON input must be text or bytes")
    require(len(raw) <= MAX_EXCHANGE_BYTES, "JSON input exceeds bounded size")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise ResonanceError(f"non-integral JSON number: {value}")

    try:
        value = json.loads(raw, object_pairs_hook=unique, parse_float=invalid, parse_constant=invalid)
        _json_domain(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, ResonanceError):
            raise
        raise ResonanceError("malformed IRP JSON") from exc


def load(path, limit=MAX_EXCHANGE_BYTES):
    with Path(path).open("rb") as handle:
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, "input exceeds bounded size")
    return strict_json(raw)


def _schema(value, rule, label="packet"):
    """Evaluate the local schema's deliberately small JSON-Schema vocabulary.

    No remote schema resolution and no external dependencies. Unknown keywords
    fail closed so additions to the schema cannot silently weaken validation.
    """
    supported = {"$schema", "$id", "$defs", "title", "description", "$ref", "anyOf", "type", "const", "enum", "properties", "required", "additionalProperties", "items", "minItems", "maxItems", "uniqueItems", "minLength", "maxLength", "pattern", "minimum", "maximum"}
    require(set(rule) <= supported, "unsupported local schema keyword")
    if "$ref" in rule:
        require(rule["$ref"].startswith("#/$defs/"), "unsupported schema reference")
        return _schema(value, SCHEMA["$defs"][rule["$ref"].split("/")[-1]], label)
    if "anyOf" in rule:
        for choice in rule["anyOf"]:
            try:
                _schema(value, choice, label)
                return
            except ResonanceError:
                pass
        raise ResonanceError(f"{label}: no allowed value type")
    if "const" in rule:
        require(canonical(value) == canonical(rule["const"]), f"{label}: invalid fixed boundary/value")
    if "enum" in rule:
        require(any(canonical(value) == canonical(v) for v in rule["enum"]), f"{label}: unknown enum value")
    if "type" in rule:
        expected = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "null": type(None)}[rule["type"]]
        require(type(value) is expected, f"{label}: expected {rule['type']}")
    if type(value) is dict:
        properties = rule.get("properties", {})
        require(set(rule.get("required", [])) <= set(value), f"{label}: missing required field")
        for key, item in value.items():
            sub = properties.get(key, rule.get("additionalProperties", True))
            require(sub is not False, f"{label}: unknown field {key}")
            if type(sub) is dict:
                _schema(item, sub, f"{label}.{key}")
    elif type(value) is list:
        require(rule.get("minItems", 0) <= len(value) <= rule.get("maxItems", 1024), f"{label}: invalid array length")
        if rule.get("uniqueItems"):
            require(len({canonical(v) for v in value}) == len(value), f"{label}: duplicate entry")
        if "items" in rule:
            for i, item in enumerate(value):
                _schema(item, rule["items"], f"{label}[{i}]")
    elif type(value) is str:
        require(rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", 65536), f"{label}: invalid string length")
        if rule.get("minLength", 0):
            require(bool(value.strip()), f"{label}: blank text")
        if "pattern" in rule:
            require(re.fullmatch(rule["pattern"], value) is not None, f"{label}: invalid format")
    elif type(value) is int:
        require(rule.get("minimum", -(2**53 - 1)) <= value <= rule.get("maximum", 2**53 - 1), f"{label}: integer out of range")


def _unique(items, key, label):
    indexed = {item[key]: item for item in items}
    require(len(indexed) == len(items), f"duplicate {label}")
    return indexed


def claims(packet):
    return {claim["claim_id"]: (group, claim) for group in CLAIM_GROUPS for claim in packet[group]}


def _semantic_body(packet):
    return {k: v for k, v in packet.items() if k not in {"human_gloss", "semantic_sha256", "packet_sha256"}}


def _timestamp(packet):
    try:
        return datetime.fromisoformat(packet["created_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ResonanceError("invalid UTC timestamp") from exc


def _local(packet):
    _json_domain(packet, max_depth=24)
    require(len(canonical(packet).encode("utf-8")) <= MAX_PACKET_BYTES, "packet exceeds bounded size")
    _schema(packet, SCHEMA)
    _timestamp(packet)
    source_map = _unique(packet["source_manifest"], "source_id", "source identifier")
    for source in source_map.values():
        require(digest(source["content"]) == source["content_sha256"], "source content hash mismatch")
    items = [c for group in CLAIM_GROUPS for c in packet[group]]
    claim_map = _unique(items, "claim_id", "claim identifier")
    uncertainty_map = _unique(packet["uncertainties"], "uncertainty_id", "uncertainty identifier")
    _unique(packet["relations"], "relation_id", "relation identifier")
    require(bool(items or uncertainty_map), "canonical semantic payload is empty")
    for item in items + packet["uncertainties"] + packet["relations"]:
        require(set(item["source_refs"]) <= set(source_map), "missing source evidence")
    for item in items:
        require(set(item["uncertainty_refs"]) <= set(uncertainty_map), "missing uncertainty reference")
    parents = _unique(packet["parents"], "packet_id", "parent identifier")
    require(packet["packet_id"] not in parents, "cycle in lineage")
    require(set(packet["responds_to"] + packet["supersedes"]) <= set(parents), "response/supersession lacks bound parent")
    for relation in packet["relations"]:
        require(relation["from_claim_id"] in claim_map, "relation lacks local claim")
        target = relation["to"]
        require(target["packet_id"] in parents, "relation target lacks bound parent")
        require(target["packet_sha256"] == parents[target["packet_id"]]["packet_sha256"], "relation target digest differs from parent")
    if "native_externalization" in packet:
        native = packet["native_externalization"]
        require(digest(native["content"]) == native["content_sha256"], "opaque content hash mismatch")
    require(digest(_semantic_body(packet)) == packet["semantic_sha256"], "semantic content hash mismatch")
    if "human_gloss" in packet:
        require(packet["human_gloss"]["derived_from_sha256"] == packet["semantic_sha256"], "gloss derived from different payload")
    require(digest({k: v for k, v in packet.items() if k != "packet_sha256"}) == packet["packet_sha256"], "packet content hash mismatch")


def seal_packet(draft):
    """Bind a declaration, not certify it. Full intake must validate its exchange."""
    packet = deepcopy(draft)
    require(type(packet) is dict, "draft must be an object")
    packet["semantic_sha256"] = digest(_semantic_body(packet))
    if "human_gloss" in packet:
        require(type(packet["human_gloss"]) is dict, "gloss must be an object")
        packet["human_gloss"]["derived_from_sha256"] = packet["semantic_sha256"]
    packet["packet_sha256"] = digest({k: v for k, v in packet.items() if k != "packet_sha256"})
    _local(packet)
    return packet


def validate_exchange(packets, *, project_id, encounter_scope):
    """Validate a complete bounded DAG, including all evidence and ancestors."""
    for value in (project_id, encounter_scope):
        _schema(value, SCHEMA["properties"]["project_id"], "exchange scope")
    require(type(packets) is list and len(packets) <= MAX_PACKETS, "exchange must be a bounded packet list")
    require(len(canonical(packets).encode("utf-8")) <= MAX_EXCHANGE_BYTES, "exchange exceeds bounded size")
    for packet in packets:
        _local(packet)
        require(packet["project_id"] == project_id, "cross-project packet contamination")
        require(packet["encounter_scope"] == encounter_scope, "cross-encounter packet contamination")
    require(sum(len(p[group]) for p in packets for group in CLAIM_GROUPS + ("uncertainties", "relations")) <= MAX_SEMANTIC_ITEMS, "exchange semantic item limit reached")
    index = _unique(packets, "packet_id", "packet identifier (history cannot be replaced)")
    residents, sources = {}, {}
    children = {ident: [] for ident in index}
    degree = {ident: len(p["parents"]) for ident, p in index.items()}
    for packet in packets:
        resident = packet["resident"]
        ident = resident["declared_id"]
        require(ident not in residents or residents[ident] == resident, "resident identity collapse or conflicting origin declaration")
        residents[ident] = resident
        for source in packet["source_manifest"]:
            sid = source["source_id"]
            require(sid not in sources or sources[sid] == source, "conflicting source binding in encounter")
            sources[sid] = source
        for parent in packet["parents"]:
            require(parent["packet_id"] in index, "broken parent lineage: missing predecessor")
            children[parent["packet_id"]].append(packet["packet_id"])
    queue = deque(ident for ident, count in degree.items() if count == 0)
    visited = 0
    while queue:
        ident = queue.popleft()
        visited += 1
        for child in children[ident]:
            degree[child] -= 1
            if degree[child] == 0:
                queue.append(child)
    require(visited == len(index), "cycle in lineage")
    for packet in packets:
        for parent_ref in packet["parents"]:
            parent = index[parent_ref["packet_id"]]
            require(parent_ref["packet_sha256"] == parent["packet_sha256"], "broken parent content binding")
            require(_timestamp(parent) <= _timestamp(packet), "child predates parent")
            if parent["packet_id"] in packet["supersedes"]:
                require(parent["resident"] == packet["resident"], "cross-resident supersession forbidden")
        for relation in packet["relations"]:
            target = relation["to"]
            require(target["claim_id"] in claims(index[target["packet_id"]]), "relation target claim missing")
    return {"protocol_version": VERSION, "valid": True, "project_id": project_id,
            "encounter_scope": encounter_scope, "packet_count": len(index),
            "declared_resident_count": len(residents), "exchange_sha256": digest(packets),
            "authority_granted": False, "identity_authenticated": False}


def compare(packets, *, project_id, encounter_scope):
    receipt = validate_exchange(packets, project_id=project_id, encounter_scope=encounter_scope)
    groups = {}
    for packet in packets:
        for category in CLAIM_GROUPS:
            for claim in packet[category]:
                # Exact source bindings prevent silent alignment across different evidence.
                source_map = {s["source_id"]: digest(s) for s in packet["source_manifest"]}
                grounding = sorted(source_map[sid] for sid in claim["source_refs"])
                key = canonical([packet["focus"], category, claim["subject"], claim["predicate"], grounding])
                entry = {"packet_id": packet["packet_id"], "packet_sha256": packet["packet_sha256"],
                         "claim_id": claim["claim_id"], "resident": deepcopy(packet["resident"]),
                         "provenance": deepcopy(packet["provenance"]), "supersedes": deepcopy(packet["supersedes"]),
                         "value": deepcopy(claim["value"]), "confidence_bps": claim["confidence_bps"],
                         "source_refs": deepcopy(claim["source_refs"]),
                         "uncertainties": [deepcopy(u) for u in packet["uncertainties"] if u["uncertainty_id"] in claim["uncertainty_refs"]]}
                groups.setdefault(key, []).append(entry)
    alignments = []
    for key, entries in sorted(groups.items()):
        focus, category, subject, predicate, grounding = strict_json(key)
        entries.sort(key=lambda e: (e["packet_id"], e["claim_id"]))
        values = {}
        for entry in entries:
            values.setdefault(canonical(entry["value"]), []).append(entry)
        distinct_residents = {e["resident"]["declared_id"] for e in entries}
        status = "unpaired"
        if len(distinct_residents) > 1:
            status = "agreement" if len(values) == 1 else "disagreement"
        alignments.append({"focus": focus, "category": category, "subject": subject,
                           "predicate": predicate, "source_bindings": grounding, "status": status,
                           "positions": [{"value": strict_json(value), "declarations": entries}
                                         for value, entries in sorted(values.items())]})
    report = {**receipt, "derivative": True, "comparison_basis": "exact declared slot, category, and source bindings; no semantic inference",
              "consensus_established": False, "canon_effect": False, "alignments": alignments}
    require(len(canonical(report).encode("utf-8")) <= MAX_EXCHANGE_BYTES, "comparison exceeds bounded size")
    return report


def orientation_projection(packets, packet_id, *, project_id, encounter_scope):
    """Lossless packet carried alongside orientation's existing four-way split.

    Content digests describe canonical inline JSON, not independently read files.
    An orientation profile's own exposure checks still apply.
    """
    validate_exchange(packets, project_id=project_id, encounter_scope=encounter_scope)
    packet = next((p for p in packets if p["packet_id"] == packet_id), None)
    require(packet is not None, "unknown orientation packet")
    return {"source_manifest": [{"path": s["locator"], "sha256": s["content_sha256"], "encoding": "irp-canonical-json"} for s in packet["source_manifest"]],
            "response": {"observations": deepcopy(packet["observations"]), "interpretations": deepcopy(packet["interpretations"]),
                         "uncertainties": deepcopy(packet["uncertainties"]), "authority_boundaries": deepcopy(packet["authority"]),
                         "irp_packet": deepcopy(packet), "derivative_projection": True}}


def render(packets, *, project_id, encounter_scope):
    report = compare(packets, project_id=project_id, encounter_scope=encounter_scope)
    lines = ["DERIVATIVE / LOSSY HUMAN RENDERING — JSON packets remain canonical.",
             "Declared identities only; no consensus, canon, or execution authority."]
    for alignment in report["alignments"]:
        lines.append(f"{alignment['category']} {alignment['subject']} / {alignment['predicate']}: {alignment['status']}")
        for position in alignment["positions"]:
            for declaration in position["declarations"]:
                lines.append(f"  {declaration['resident']['declared_id']} [{declaration['packet_id']}/{declaration['claim_id']}] "
                             f"{canonical(position['value'])}; confidence_bps={declaration['confidence_bps']}")
    return "\n".join(lines) + "\n"


class ExchangeLedger:
    """Explicit local JSONL store. Locked, fsynced appends, no rewrite/delete API.

    Retain a receipt head outside this store to detect truncation/replacement.
    This is a bounded artifact journal, not a network or a trusted identity store.
    """
    def __init__(self, directory, *, project_id, encounter_scope):
        self.directory = Path(directory)
        self.path = self.directory / "exchange.jsonl"
        self.scope = {"project_id": project_id, "encounter_scope": encounter_scope}
        for value in self.scope.values():
            _schema(value, SCHEMA["properties"]["project_id"], "ledger scope")

    @contextmanager
    def _locked(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / "exchange.lock").open("a+b") as lock:
            try:
                if os.name == "nt":
                    import msvcrt
                    if lock.seek(0, os.SEEK_END) == 0:
                        lock.write(b"\0")
                        lock.flush()
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ResonanceError("exchange busy; reread and retry") from exc
            try:
                yield
            finally:
                if os.name == "nt":
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock, fcntl.LOCK_UN)

    def _read(self, required_head=None):
        events, packets, seen = [], [], set()
        if self.path.exists():
            with self.path.open("rb") as handle:
                raw = handle.read(MAX_EXCHANGE_BYTES + 1)
            require(0 < len(raw) <= MAX_EXCHANGE_BYTES and raw.endswith(b"\n"), "empty, oversized, or interrupted exchange ledger")
            for line in raw.splitlines():
                event = strict_json(line)
                require(type(event) is dict and set(event) == {"schema", "sequence", "previous_event_sha256", "packet", "event_sha256"}, "invalid ledger event fields")
                require(event["schema"] == "IRP-R1-ledger", "unknown ledger schema")
                require(type(event["sequence"]) is int and event["sequence"] == len(events) + 1, "broken ledger sequence")
                require(event["previous_event_sha256"] == (events[-1]["event_sha256"] if events else None), "broken ledger linkage")
                require(event["event_sha256"] == digest({k: v for k, v in event.items() if k != "event_sha256"}), "ledger content hash mismatch")
                packet = event["packet"]
                _local(packet)
                require(all(p["packet_id"] in seen for p in packet["parents"]), "ledger predecessor missing or out of order")
                packets.append(packet)
                seen.add(packet["packet_id"])
                events.append(event)
                require(len(events) <= MAX_PACKETS, "ledger packet limit reached")
        receipt = validate_exchange(packets, **self.scope)
        if required_head is not None:
            _schema(required_head, SCHEMA["properties"]["packet_sha256"], "required head")
            require(required_head in {e["event_sha256"] for e in events}, "saved receipt head absent: truncated/replaced/wrong ledger")
        return events, packets, {**receipt, "head_sha256": events[-1]["event_sha256"] if events else None}

    def inspect(self, *, required_head=None):
        with self._locked():
            _, packets, receipt = self._read(required_head)
            return {**receipt, "packets": packets}

    def append(self, packet, *, expected_head):
        packet = deepcopy(packet)
        if expected_head is not None:
            _schema(expected_head, SCHEMA["properties"]["packet_sha256"], "expected head")
        with self._locked():
            events, packets, receipt = self._read()
            require(receipt["head_sha256"] == expected_head, "stale ledger head; inspect before append")
            _local(packet)
            for previous in packets:
                if packet["packet_id"] == previous["packet_id"]:
                    require(packet == previous, "duplicate packet identifier with conflicting content")
                    return {**receipt, "appended": False}
            validation = validate_exchange(packets + [packet], **self.scope)
            event = {"schema": "IRP-R1-ledger", "sequence": len(events) + 1,
                     "previous_event_sha256": expected_head, "packet": packet}
            event["event_sha256"] = digest(event)
            encoded = (canonical(event) + "\n").encode("utf-8")
            require((self.path.stat().st_size if self.path.exists() else 0) + len(encoded) <= MAX_EXCHANGE_BYTES, "ledger size limit reached")
            with self.path.open("ab") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            if os.name != "nt":
                fd = os.open(self.directory, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            return {**validation, "head_sha256": event["event_sha256"], "appended": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "compare", "render", "seal", "append", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--project", required=True)
        command.add_argument("--encounter", required=True)
        if name != "verify":
            command.add_argument("file")
        if name in {"append", "verify"}:
            command.add_argument("--ledger", required=True)
        if name == "seal":
            command.add_argument("--parents-file", help="Complete existing exchange, if this draft has parents")
        if name == "append":
            command.add_argument("--expected-head", required=True, help="Saved head SHA-256 or 'empty'")
        if name == "verify":
            command.add_argument("--required-head")
    args = parser.parse_args(argv)
    scope = {"project_id": args.project, "encounter_scope": args.encounter}
    try:
        if args.command in {"verify", "append"}:
            ledger = ExchangeLedger(args.ledger, **scope)
            if args.command == "verify":
                output = ledger.inspect(required_head=args.required_head)
            else:
                output = ledger.append(load(args.file, MAX_PACKET_BYTES), expected_head=None if args.expected_head == "empty" else args.expected_head)
        elif args.command == "seal":
            output = seal_packet(load(args.file, MAX_PACKET_BYTES))
            parents = load(args.parents_file) if args.parents_file else []
            require(type(parents) is list, "parents file must contain a packet list")
            validate_exchange(parents + [output], **scope)
        else:
            packets = load(args.file)
            if type(packets) is dict:
                packets = [packets]
            if args.command == "render":
                print(render(packets, **scope), end="")
                return 0
            output = (compare if args.command == "compare" else validate_exchange)(packets, **scope)
        print(canonical(output))
        return 0
    except (ResonanceError, OSError) as exc:
        print(canonical({"valid": False, "authority_granted": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
