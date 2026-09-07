from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site" / "public" / "runtime"
SOURCE = ROOT / "public" / "runtime"
ALLOWED = ("latest_cycle.json", "runtime_truth_snapshot.json")


def main() -> int:
    if OUT.parent.exists():
        shutil.rmtree(OUT.parent)
    OUT.mkdir(parents=True, exist_ok=True)

    for name in ALLOWED:
        source = SOURCE / name
        if not source.exists():
            print(f"Missing required public runtime witness: {source}")
            return 1
        shutil.copy2(source, OUT / name)

    print("Preserved current public runtime witnesses only")
    for name in ALLOWED:
        print(f"- public/runtime/{name}")
    print("Excluded public/runtime/history and example receipts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
