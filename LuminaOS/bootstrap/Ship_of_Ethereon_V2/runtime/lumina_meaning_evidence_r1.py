"""Read-only, relocatable file evidence for advisory meaning memory.

Matching bytes establish source freshness, not the truth of an interpretation.
Snapshots belong in the ledger; only their digests belong in runtime guidance.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any, Dict

MAX_EVIDENCE_BYTES = 64 * 1024
MAX_EVIDENCE_SOURCES = 8


def _relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("evidence path must be a relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value or value == ".":
        raise ValueError("evidence path must be normalized and stay within the source root")
    return path


def _read_source(source_root: str | Path, relative_path: str) -> bytes:
    relative = _relative_path(relative_path)
    root = Path(source_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("source root must be a directory")
    path = (root / str(relative)).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError("evidence escapes the source root")
    # Nonblocking open plus fstat avoids hanging on a device or named pipe.
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_EVIDENCE_BYTES:
            raise ValueError("evidence must be a regular file of at most 64 KiB")
        data = source.read(MAX_EVIDENCE_BYTES + 1)
    if len(data) > MAX_EVIDENCE_BYTES:
        raise ValueError("evidence exceeds 64 KiB")
    return data


def capture_evidence(*, source_root: str | Path, relative_path: str) -> Dict[str, Any]:
    """Capture an explicitly selected UTF-8 source without changing it."""
    data = _read_source(source_root, relative_path)
    return {
        "schema_version": "meaning_file_evidence_r1",
        "relative_path": relative_path,
        "sha256": hashlib.sha256(data).hexdigest(),
        "source_text": data.decode("utf-8"),
    }


def validate_evidence(evidence: Dict[str, Any]) -> None:
    expected = {"schema_version", "relative_path", "sha256", "source_text"}
    if not isinstance(evidence, dict) or set(evidence) != expected:
        raise ValueError("invalid evidence fields")
    if evidence["schema_version"] != "meaning_file_evidence_r1":
        raise ValueError("unsupported evidence schema")
    _relative_path(evidence["relative_path"])
    if not isinstance(evidence["source_text"], str):
        raise ValueError("evidence snapshot must be text")
    data = evidence["source_text"].encode("utf-8")
    if len(data) > MAX_EVIDENCE_BYTES or hashlib.sha256(data).hexdigest() != evidence["sha256"]:
        raise ValueError("evidence snapshot digest mismatch or size exceeded")


def probe_evidence(evidence: Dict[str, Any], source_root: str | Path) -> str:
    validate_evidence(evidence)
    try:
        data = _read_source(source_root, evidence["relative_path"])
    except (OSError, ValueError, RuntimeError):
        return "source_unavailable"
    return "source_matches" if hashlib.sha256(data).hexdigest() == evidence["sha256"] else "source_changed"
