# Lumina OS Orchestrator v0.2
# Adds context awareness + primitive continuation tracking

from runtime_runner_r2_merged import RuntimeRunner
import json
from pathlib import Path

STATE_FILE = Path(__file__).parent / "_lumina_state.json"

class LuminaOrchestrator:
    def __init__(self, base_dir=None):
        self.runner = RuntimeRunner(base_dir=base_dir) if base_dir else RuntimeRunner()
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

    def select_next_action(self, context_bundle: dict) -> dict:
        mode = context_bundle.get("current_mode")
        last_action = self.state.get("last_action")

        if not last_action:
            return {"action": "initial_observation", "action_type": "audit", "target_mode": "Observation"}

        if mode == "Observation":
            return {"action": "continue_observation", "action_type": "audit", "target_mode": "Observation"}

        return {"action": "stabilize_to_observation", "action_type": "transition", "target_mode": "Observation"}

    def run_cycle(self):
        context_bundle = {
            "current_mode": self.state.get("last_mode", "Continuity")
        }

        next_action = self.select_next_action(context_bundle)

        result = self.runner.run_cycle(
            current_mode=context_bundle["current_mode"],
            target_mode=next_action["target_mode"],
            requested_action=next_action["action"],
            action_type=next_action["action_type"]
        )

        # update state
        self.state["last_action"] = next_action["action"]
        self.state["last_mode"] = next_action["target_mode"]
        self._save_state()

        return result.to_dict()

    def run(self, cycles=3):
        outputs = []
        for _ in range(cycles):
            outputs.append(self.run_cycle())
        return outputs


if __name__ == "__main__":
    orchestrator = LuminaOrchestrator()
    print(json.dumps(orchestrator.run(), indent=2))
