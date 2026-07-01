from __future__ import annotations

import os
from pathlib import Path


STATE_ENVIRONMENT_VARIABLE = "LUMINA_STATE_ROOT"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def bootstrap_root() -> Path:
    return repo_root() / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2"


def runtime_root() -> Path:
    return bootstrap_root() / "runtime"


def default_windows_state_root() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data).expanduser() if local_app_data else Path.home() / "AppData" / "Local"
    return base / "Lumina" / "state" / "ship_of_ethereon_v2"


def state_root_source() -> str:
    if os.environ.get(STATE_ENVIRONMENT_VARIABLE):
        return "environment"
    if os.name == "nt":
        return "windows_user_data"
    return "repository_local"


def state_root() -> Path:
    configured = os.environ.get(STATE_ENVIRONMENT_VARIABLE)
    if configured:
        return Path(configured).expanduser()
    if os.name == "nt":
        return default_windows_state_root()
    return repo_root() / ".lumina_state" / "ship_of_ethereon_v2"
