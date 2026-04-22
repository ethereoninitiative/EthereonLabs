# Lumina OS Orchestrator v0.1
from runtime_runner_r2_merged import RuntimeRunner

class LuminaOrchestrator:
    def __init__(self, base_dir=None):
        self.runner = RuntimeRunner(base_dir=base_dir) if base_dir else RuntimeRunner()

    def select_next_action(self, context_bundle: dict) -> dict:
        mode = context_bundle.get("current_mode")
        last_action = context_bundle.get("last_action")

        if not last_action:
            return {"action": "initial_observation", "action_type": "audit", "target_mode": "Observation"}

        if mode == "Observation":
            return {"action": "continue_observation", "action_type": "audit", "target_mode": "Observation"}

        return {"action": "stabilize_to_observation", "action_type": "transition", "target_mode": "Observation"}

    def run(self):
        context_bundle = {"current_mode": "Continuity", "last_action": None}
        next_action = self.select_next_action(context_bundle)

        result = self.runner.run_cycle(
            current_mode=context_bundle["current_mode"],
            target_mode=next_action["target_mode"],
            requested_action=next_action["action"],
            action_type=next_action["action_type"]
        )

        return result.to_dict()

if __name__ == "__main__":
    orchestrator = LuminaOrchestrator()
    import json
    print(json.dumps(orchestrator.run(), indent=2))
