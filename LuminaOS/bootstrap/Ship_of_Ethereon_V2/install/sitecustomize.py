from __future__ import annotations

from pathlib import Path
import sys

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
for candidate in (
    BOOTSTRAP_ROOT / "install",
    BOOTSTRAP_ROOT / "runtime",
    BOOTSTRAP_ROOT / "studio",
    BOOTSTRAP_ROOT,
):
    text = str(candidate)
    if text not in sys.path:
        sys.path.insert(0, text)
