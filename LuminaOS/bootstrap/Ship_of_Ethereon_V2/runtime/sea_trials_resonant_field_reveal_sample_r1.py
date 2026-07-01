from __future__ import annotations

"""Sea trial for the committed Resonant Field Reveal sample."""

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from resonant_field_reveal_sample_r1 import (
    INPUT_FILE,
    RECEIPT_FILE,
    SAMPLE_DIR,
    SAMPLE_FILES,
    SAMPLE_ID,
    generate_sample,
)


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def run_trial() -> dict:
    committed = {
        name: (SAMPLE_DIR / name).read_bytes()
        for name in SAMPLE_FILES
        if (SAMPLE_DIR / name).is_file()
    }
    with TemporaryDirectory() as temporary:
        generated_dir = Path(temporary)
        generate_sample(generated_dir)
        generated = {
            name: (generated_dir / name).read_bytes()
            for name in SAMPLE_FILES
            if (generated_dir / name).is_file()
        }

    receipt = json.loads(committed.get(RECEIPT_FILE, b"{}"))
    manifest = json.loads(committed.get(INPUT_FILE, b"{}"))
    expected = set(SAMPLE_FILES)
    output_hashes = receipt.get("artifacts", {})
    checks = {
        "sample_complete": set(committed) == expected,
        "byte_identical_regeneration": (
            set(generated) == expected
            and all(committed[name] == generated[name] for name in expected)
        ),
        "sample_receipt_present": (
            receipt.get("sample_id") == SAMPLE_ID
            and receipt.get("reproducible") is True
        ),
        "input_hash_matches": (
            receipt.get("input_artifact", {}).get(INPUT_FILE)
            == digest(committed.get(INPUT_FILE, b""))
        ),
        "output_hashes_match": all(
            value == digest(committed.get(name, b""))
            for name, value in output_hashes.items()
        ),
        "boundary_note_present": (
            manifest.get("sample_id") == SAMPLE_ID
            and "not runtime truth" in manifest.get("authority_note", "")
        ),
    }
    return {
        "trial_id": "sea-trials-resonant-field-reveal-sample-r1",
        "passed": all(checks.values()),
        "checks": checks,
    }


if __name__ == "__main__":
    result = run_trial()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
