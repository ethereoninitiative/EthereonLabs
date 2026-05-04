from parser_r1 import parse_ethereonic

ACTIONS = ["stabilize", "observe", "amplify", "reduce"]

def interpret(text: str):
    mapping = parse_ethereonic(text)
    action = None

    for a in ACTIONS:
        if a in text.lower():
            action = a
            break

    return {
        "action": action,
        "targets": list(mapping.values()),
        "raw_mapping": mapping
    }
