import subprocess
from pathlib import Path

PROLOG_FILE = Path(__file__).parent / "rules_r1.pl"


def query_prolog(query: str) -> dict:
    try:
        cmd = [
            "swipl",
            "-q",
            "-s",
            str(PROLOG_FILE),
            "-g",
            f"({query} -> writeln(true); writeln(false)), halt."
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.strip()

        return {
            "available": True,
            "result": output == "true"
        }
    except Exception:
        return {
            "available": False,
            "result": None
        }
