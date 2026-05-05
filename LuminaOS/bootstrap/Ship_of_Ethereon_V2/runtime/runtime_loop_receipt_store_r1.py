from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class RuntimeLoopReceiptStore:
    """Persistent storage for Lumina runtime loop receipts.

    Stores receipts in .lumina_state/runtime_loop/ for continuity tracking.
    Non-authoritative: storage and retrieval only.
    """

    def __init__(self, base_path: Optional[str] = None) -> None:
        self.base_path = Path(base_path or ".lumina_state/runtime_loop")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.history_path = self.base_path / "receipts.jsonl"
        self.latest_path = self.base_path / "latest.json"

    def append_receipt(self, receipt: Dict[str, Any]) -> None:
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(receipt) + "\n")

        with self.latest_path.open("w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)

    def load_latest(self) -> Optional[Dict[str, Any]]:
        if not self.latest_path.exists():
            return None
        with self.latest_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self.history_path.exists():
            return []

        with self.history_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        if limit:
            lines = lines[-limit:]

        return [json.loads(line) for line in lines]

    def load_previous_signal(self) -> Optional[Dict[str, Any]]:
        latest = self.load_latest()
        if not latest:
            return None

        return latest.get("signal_emit")
