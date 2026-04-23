# Lumina OS Orchestrator v0.4
# Hardens the decision-engine lane against real repo/runtime paths

import json
import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).parent / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.append(str(RUNTIME_DIR))

from runtime_runner_r1_merged import RuntimeRunner
from lumina_context_loader_v0_1 import LuminaContextLoader
from lumina_decision_engine_v0_1 import LuminaDecisionEngine

STATE_FILE = Path(__file__).parent / "_lumina_state.json"


class LuminaOrchestrator:
    """
    Bounded orchestration layer.
    - Restores minimal context from runtime checkpoints
    - Routes next-step selection through LuminaDecisionEngine
    - Persists coarse continuity state across cycles
    - Remains subordinate to RuntimeRunner governance at execution time
    """

    def __init__(self, base_dir=None, orientation_vector=None):
        self.runner = RuntimeRunner(base_dir=base_dir) if base_dir else RuntimeRunner()
        self.loader = LuminaContextLoader(runtime_state_dir=self.runner.base_dir)
        self.decision_engine = LuminaDecisionEngine(orientation_vector=orientation_vector)
        self.state = self._load_state()

    def _load_state(self):
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text())
            except Exception:
                pass
        return {"last_action": None, "last_mode": "Continuity"}

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

    def _restore_context(self) -> dict:
        context_bundle = self.loader.load_context()
        if not context_bundle.get("last_action") and self.state.get("last_action"):
            context_bundle["last_action"] = self.state["last_action"]
        if not context_bundle.get("current_mode") and self.state.get("last_mode"):
            context_bundle["current_mode"] = self.state["last_mode"]
        return context_bundle

    def run_cycle(self):
        context_bundle = self._restore_context()
        current_mode = context_bundle.get("current_mode", "Continuity")

        next_action = self.decision_engine.select_next_action(context_bundle)

        result = self.runner.run_cycle(
            current_mode=current_mode,
            target_mode=next_action["target_mode"],
            requested_action=next_action["action"],
            action_type=next_action["action_type"],
        )

        self.state["last_action"] = next_action["action"]
        self.state["last_mode"] = next_action["target_mode"]
        self._save_state()

        return {
            "restored_context": context_bundle,
            "next_action": next_action,
            "runner_result": result.to_dict(),
        }

    def run(self, cycles=3):
        outputs = []
        for _ in range(cycles):
            outputs.append(self.run_cycle())
        return outputs


if __name__ == "__main__":
    orchestrator = LuminaOrchestrator()
    print(json.dumps(orchestrator.run(), indent=2))
