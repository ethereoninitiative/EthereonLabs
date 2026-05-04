from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

LAYER_DIR = Path(__file__).resolve().parent
PASSPORT_PATH = LAYER_DIR / "ethereon_passport_r1.json"
DIALECT_REGISTRY_PATH = LAYER_DIR / "dialect_registry_r1.json"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


PASSPORT = _load_json(PASSPORT_PATH)
CORE = PASSPORT["core_terms"]


def _load_dialect_map(dialect: Optional[str]) -> Dict[str, str]:
    if not dialect:
        return {}
    registry = _load_json(DIALECT_REGISTRY_PATH)
    dialect_config = registry.get("registered_dialects", {}).get(dialect)
    if not dialect_config or not dialect_config.get("allowed", False):
        return {}
    mapping_file = dialect_config.get("mapping_file")
    if not mapping_file:
        return {}
    mapping_payload = _load_json(LAYER_DIR / mapping_file)
    return mapping_payload.get("mappings", {})


def normalize_dialect_text(text: str, dialect: Optional[str] = None) -> Dict[str, Any]:
    normalized = text.lower()
    replacements: Dict[str, str] = {}
    for dialect_term, core_term in _load_dialect_map(dialect).items():
        if dialect_term in normalized:
            normalized = normalized.replace(dialect_term, core_term)
            replacements[dialect_term] = core_term
    return {
        "original_text": text,
        "normalized_text": normalized,
        "dialect": dialect,
        "replacements": replacements,
    }


def parse_ethereonic(text: str, dialect: Optional[str] = None) -> Dict[str, str]:
    normalized = normalize_dialect_text(text, dialect=dialect)["normalized_text"]
    mapping: Dict[str, str] = {}
    for core_term, runtime_meaning in CORE.items():
        if core_term in normalized:
            mapping[core_term] = runtime_meaning
    return mapping
