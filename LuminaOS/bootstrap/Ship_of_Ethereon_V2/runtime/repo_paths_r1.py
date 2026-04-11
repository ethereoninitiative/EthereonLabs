from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def runtime_root() -> Path:
    return repo_root() / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime"


def state_root() -> Path:
    return repo_root() / ".lumina_state" / "ship_of_ethereon_v2"
