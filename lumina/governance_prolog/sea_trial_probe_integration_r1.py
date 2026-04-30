from probe_interface import check_transition, check_action


def probe_runtime_decision(runtime_result: dict):
    current_mode = runtime_result.get("current_mode")
    target_mode = runtime_result.get("target_mode")
    action = runtime_result.get("requested_action")

    return {
        "prolog_probe": {
            "transition": check_transition(current_mode, target_mode),
            "action": check_action(target_mode, action)
        }
    }
