from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from runtime_ui_snapshot_emitter_r1 import runtime_snapshot_semantic_fingerprint  # noqa: E402


LATEST_PATH = "public/runtime/latest_cycle.json"
PUBLIC_TRUTH_PATH = "public/runtime/runtime_truth_snapshot.json"
HISTORY_PREFIX = "public/runtime/history/"
OBSERVATION_PREFIX = "artifacts/runtime_truth/current/observation_"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tracked_paths() -> set[str]:
    return set(git("ls-files").splitlines())


def read_ref_json(ref: str, path: str) -> dict:
    return json.loads(git("show", f"{ref}:{path}"))


def restore_tracked(paths: Iterable[str], tracked: set[str], changed: set[str]) -> list[str]:
    restored: list[str] = []
    for path in sorted(set(paths) & tracked & changed):
        subprocess.run(["git", "restore", "--source=HEAD", "--", path], cwd=ROOT, check=True)
        restored.append(path)
    return restored


def remove_untracked_generated_files(
    *,
    tracked: set[str],
    prefix: str,
    directory: Path,
) -> list[str]:
    removed: list[str] = []
    if not directory.exists():
        return removed
    for path in directory.glob("*.json"):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(prefix) and relative not in tracked:
            path.unlink()
            removed.append(relative)
    return removed


def main() -> int:
    baseline = read_ref_json("HEAD", LATEST_PATH)
    current_path = ROOT / LATEST_PATH
    if not current_path.exists():
        raise SystemExit(f"missing generated observation: {LATEST_PATH}")
    current = json.loads(current_path.read_text(encoding="utf-8"))

    baseline_fingerprint = runtime_snapshot_semantic_fingerprint(baseline)
    current_fingerprint = runtime_snapshot_semantic_fingerprint(current)
    semantic_changed = baseline_fingerprint != current_fingerprint

    result = {
        "status": "semantic_change" if semantic_changed else "semantic_noop",
        "baseline_fingerprint": baseline_fingerprint,
        "current_fingerprint": current_fingerprint,
        "restored": [],
        "removed_untracked": [],
    }

    if not semantic_changed:
        tracked = tracked_paths()
        changed = set(git("diff", "--name-only", "HEAD").splitlines())
        restore_candidates = {
            LATEST_PATH,
            PUBLIC_TRUTH_PATH,
            "public/runtime/history/index.json",
            *[path for path in tracked if path.startswith(HISTORY_PREFIX)],
            *[path for path in tracked if path.startswith(OBSERVATION_PREFIX)],
        }
        result["restored"] = restore_tracked(restore_candidates, tracked, changed)
        result["removed_untracked"] = [
            *remove_untracked_generated_files(
                tracked=tracked,
                prefix=HISTORY_PREFIX,
                directory=ROOT / "public/runtime/history",
            ),
            *remove_untracked_generated_files(
                tracked=tracked,
                prefix=OBSERVATION_PREFIX,
                directory=ROOT / "artifacts/runtime_truth/current",
            ),
        ]

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
