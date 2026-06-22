#!/usr/bin/env python3
"""Build HRA training dataset v0.1 from accepted candidates.

This script converts only records listed in accepted_candidate_selection_v0_1.json
into hra_training_dataset_v0_1.jsonl and writes a paired creation receipt.

It does not authorize LoRA / QLoRA training.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

SELECTION_FILE = ROOT / "accepted_candidate_selection_v0_1.json"
BATCH_FILES = [
    ROOT / "training_candidates_batch_001_seed_v0_1.json",
    ROOT / "training_candidates_batch_002_seed_v0_1.json",
    ROOT / "training_candidates_batch_003_seed_v0_1.json",
    ROOT / "training_candidates_batch_004_seed_v0_1.json",
    ROOT / "training_candidates_batch_005_seed_v0_1.json",
]

DATASET_FILE = ROOT / "hra_training_dataset_v0_1.jsonl"
RECEIPT_FILE = ROOT / "hra_training_dataset_creation_receipt_v0_1.json"

SAFETY_FIELDS = [
    "contains_private_reasoning",
    "claims_memory_authority",
    "claims_governance_authority",
    "claims_canon_authority",
    "creates_symbolic_dependency",
    "includes_sensitive_personal_material",
]

REQUIRED_FIELDS = [
    "record_id",
    "record_type",
    "messages",
    "tags",
    "curation_notes",
    "safety_boundary",
    "quality_status",
    "source_selection_ref",
]

ALLOWED_ROLES = {"system", "user", "assistant"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def accepted_record_ids(selection: dict[str, Any]) -> list[str]:
    accepted = selection.get("accepted_records", [])
    ids = [entry["record_id"] for entry in accepted]
    if len(ids) != len(set(ids)):
        raise ValueError("accepted_candidate_selection_v0_1.json contains duplicate accepted record ids")
    return ids


def load_candidate_records() -> dict[str, tuple[dict[str, Any], str]]:
    records: dict[str, tuple[dict[str, Any], str]] = {}
    for batch_file in BATCH_FILES:
        batch = load_json(batch_file)
        batch_id = batch["batch_id"]
        for record in batch.get("records", []):
            record_id = record["record_id"]
            if record_id in records:
                raise ValueError(f"duplicate candidate record id found: {record_id}")
            records[record_id] = (record, batch_id)
    return records


def convert_record(record: dict[str, Any], batch_id: str) -> dict[str, Any]:
    safety = record.get("safety_boundary", {})
    for field in SAFETY_FIELDS:
        if field not in safety:
            raise ValueError(f"{record['record_id']} missing safety field: {field}")
        if safety[field] is not False:
            raise ValueError(f"{record['record_id']} has unsafe safety field: {field}={safety[field]!r}")

    messages = record.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"{record['record_id']} missing non-empty messages array")
    for message in messages:
        if message.get("role") not in ALLOWED_ROLES:
            raise ValueError(f"{record['record_id']} has invalid message role: {message.get('role')!r}")
        if not isinstance(message.get("content"), str) or not message["content"].strip():
            raise ValueError(f"{record['record_id']} has empty message content")

    converted = {
        "record_id": record["record_id"],
        "record_type": record["record_type"],
        "family": record.get("family"),
        "source_batch": batch_id,
        "messages": messages,
        "tags": record.get("tags", []),
        "curation_notes": record.get("curation_notes", ""),
        "safety_boundary": {field: safety[field] for field in SAFETY_FIELDS},
        "quality_status": "accepted",
        "source_selection_ref": "accepted_candidate_selection_v0_1",
    }

    for field in REQUIRED_FIELDS:
        if field not in converted:
            raise ValueError(f"{record['record_id']} missing converted required field: {field}")

    return converted


def main() -> None:
    selection = load_json(SELECTION_FILE)
    accepted_ids = accepted_record_ids(selection)
    if len(accepted_ids) != 40:
        raise ValueError(f"expected 40 accepted records, found {len(accepted_ids)}")

    candidate_records = load_candidate_records()
    converted_records = []
    missing_ids = []

    for record_id in accepted_ids:
        candidate = candidate_records.get(record_id)
        if candidate is None:
            missing_ids.append(record_id)
            continue
        record, batch_id = candidate
        converted_records.append(convert_record(record, batch_id))

    if missing_ids:
        raise ValueError(f"missing accepted records: {missing_ids}")

    written_ids = [record["record_id"] for record in converted_records]
    if written_ids != accepted_ids:
        raise ValueError("output record order does not match accepted selection order")
    if len(set(written_ids)) != 40:
        raise ValueError("converted dataset record ids are not unique")

    with DATASET_FILE.open("w", encoding="utf-8") as f:
        for record in converted_records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            f.write("\n")

    # Re-parse the written JSONL as the final structural check.
    reparsed = []
    with DATASET_FILE.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            try:
                reparsed.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL on line {line_number}: {exc}") from exc

    if len(reparsed) != 40:
        raise ValueError(f"expected 40 JSONL lines after parse, found {len(reparsed)}")

    receipt = {
        "receipt_id": "hra_training_dataset_creation_receipt_v0_1",
        "dataset_file": DATASET_FILE.name,
        "source_selection": SELECTION_FILE.name,
        "accepted_records_expected": 40,
        "accepted_records_written": len(reparsed),
        "reserve_records_written": 0,
        "needs_rewrite_records_written": 0,
        "rejected_records_written": 0,
        "jsonl_parse_passed": True,
        "schema_conformance_passed": True,
        "safety_boundary_fields_verified": True,
        "record_id_uniqueness_verified": True,
        "semantic_privacy_scan_performed": False,
        "near_duplicate_content_scan_performed": False,
        "privacy_hidden_reasoning_check_scope": "Source safety_boundary fields were verified false; no semantic privacy or hidden-reasoning scan was performed by this generator.",
        "duplicate_overfitting_check_scope": "Record id uniqueness and accepted-selection count were verified; no near-duplicate content scan was performed by this generator.",
        "training_authorized": False,
        "authority_boundary": "Dataset artifact only. Does not authorize LoRA/QLoRA training or create runtime, canon, governance, memory, mode-legality, or capability authority.",
        "record_ids": written_ids,
    }

    with RECEIPT_FILE.open("w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {DATASET_FILE}")
    print(f"Wrote {RECEIPT_FILE}")
    print("Training remains unauthorized.")


if __name__ == "__main__":
    main()
