# Lumina Decision Engine v0.1
# Orientation-aware next-action selection

class LuminaDecisionEngine:
    """
    Non-authoritative decision layer.
    - Reads context + optional orientation
    - Proposes next action
    - Must always defer to ModeGuard at execution time
    """

    def __init__(self, orientation_vector=None):
        self.orientation = orientation_vector or {}

    def select_next_action(self, context_bundle: dict) -> dict:
        mode = context_bundle.get("current_mode")
        last_action = context_bundle.get("last_action")

        # --- Base heuristic ---
        if not last_action:
            return self._observation_start()

        # --- Orientation-aware adjustments ---
        priority = self.orientation.get("priority")

        if priority == "stability":
            return self._stabilize(mode)

        if priority == "progression":
            return self._progress(mode)

        # --- Default behavior ---
        if mode == "Observation":
            return self._continue_observation()

        return self._stabilize(mode)

    # --- Action templates ---

    def _observation_start(self):
        return {
            "action": "initial_observation",
            "action_type": "audit",
            "target_mode": "Observation"
        }

    def _continue_observation(self):
        return {
            "action": "continue_observation",
            "action_type": "audit",
            "target_mode": "Observation"
        }

    def _stabilize(self, mode):
        if mode != "Observation":
            return {
                "action": "stabilize_to_observation",
                "action_type": "transition",
                "target_mode": "Observation"
            }
        return self._continue_observation()

    def _progress(self, mode):
        if mode == "Observation":
            return {
                "action": "enter_drydock",
                "action_type": "transition",
                "target_mode": "DryDock"
            }
        if mode == "DryDock":
            return {
                "action": "prepare_promotion",
                "action_type": "validation",
                "target_mode": "DryDock"
            }
        return self._stabilize(mode)
