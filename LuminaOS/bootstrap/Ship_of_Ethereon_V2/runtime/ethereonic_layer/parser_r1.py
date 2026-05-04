import json

with open('ethereon_passport_r1.json') as f:
    PASSPORT = json.load(f)

CORE = PASSPORT['core_terms']

def parse_ethereonic(text: str):
    text = text.lower()
    mapping = {}
    for k, v in CORE.items():
        if k in text:
            mapping[k] = v
    return mapping
