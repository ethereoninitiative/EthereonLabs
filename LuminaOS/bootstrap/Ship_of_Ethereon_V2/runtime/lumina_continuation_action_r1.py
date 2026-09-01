from __future__ import annotations

import re
from typing import Any


CONTINUATION_PREFIX = "continue from "
DEFAULT_CONTINUATION_TARGET = "latest lawful checkpoint"
_LEADING_CONTINUATION_PATTERN = re.compile(
    r"^(?:(?:continue\s+from)(?:\s+|$))+",
    flags=re.IGNORECASE,
)


def continuation_target(value: Any) -> str:
    """Return the underlying target without repeated continuation wrappers.

    This function owns continuation-directive syntax only. It does not choose a
    target, authorize a cycle, or alter governance, checkpoint, or canon truth.
    """

    candidate = str(value or "").strip()
    target = _LEADING_CONTINUATION_PATTERN.sub("", candidate, count=1).strip()
    return target or DEFAULT_CONTINUATION_TARGET


def as_continuation_action(value: Any) -> str:
    """Represent a target as exactly one stable ``continue from`` directive."""

    return f"{CONTINUATION_PREFIX}{continuation_target(value)}"


def normalize_continuation_action(value: Any) -> str:
    """Repair an existing continuation directive while preserving plain actions."""

    candidate = str(value or "").strip()
    if not _LEADING_CONTINUATION_PATTERN.match(candidate):
        return candidate
    return as_continuation_action(candidate)
