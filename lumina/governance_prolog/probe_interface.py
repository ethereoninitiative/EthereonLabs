from probe_runner import query_prolog


def check_transition(current_mode: str, target_mode: str):
    query = f"legal_transition({current_mode},{target_mode})"
    return query_prolog(query)


def check_action(mode: str, action: str):
    query = f"illegal_action({mode},{action})"
    result = query_prolog(query)
    if result["available"]:
        result["result"] = not result["result"]
    return result
