# Lumina Context Loader v0.1
# Pulls latest checkpoint + extracts minimal usable context

import json
from pathlib import Path

class LuminaContextLoader:
    def __init__(self, runtime_state_dir=None):
        self.runtime_state_dir = Path(runtime_state_dir) if runtime_state_dir else None

    def find_latest_checkpoint(self):
        if not self.runtime_state_dir or not self.runtime_state_dir.exists():
            return None

        checkpoints = list(self.runtime_state_dir.rglob("*checkpoint*.json"))
        if not checkpoints:
            return None

        return max(checkpoints, key=lambda p: p.stat().st_mtime)

    def load_context(self):
        checkpoint = self.find_latest_checkpoint()
        if not checkpoint:
            return {"current_mode": "Continuity", "last_action": None}

        try:
            data = json.loads(checkpoint.read_text())
            session_state = data.get("session_state", {})
            return {
                "current_mode": session_state.get("current_mode", "Continuity"),
                "last_action": session_state.get("last_completed_action")
            }
        except Exception:
            return {"current_mode": "Continuity", "last_action": None}
