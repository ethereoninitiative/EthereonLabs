from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid

try:
    from .repo_paths_r1 import state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import state_root as _state_root_helper
    except Exception:
        _state_root_helper = None


MODULE_SLUG = "continuity_restore_repo_native_r1"
WORKSPACE_HOST_MODULE_SLUG = "lumina_workspace_host_repo_native_r1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            candidate = Path(_state_root_helper()).resolve()
            if candidate.exists():
                return candidate
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent