from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import tempfile

try:
    from .generate_lumina_weather_snapshot_r1 import write_snapshot
except Exception:
    from generate_lumina_weather_snapshot_r1 import write_snapshot


def _read(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="lumina-weather-idempotence-") as temp_dir:
        root = Path(temp_dir)
        snapshot_path = root / "lumina-weather-snapshot.json"
        history_path = root / "lumina-weather-history.json"

        write_snapshot(snapshot_path, history_output=history_path)
        first_snapshot_bytes = snapshot_path.read_bytes()
        first_history_bytes = history_path.read_bytes()
        first_snapshot = _read(snapshot_path)
        first_history = _read(history_path)

        write_snapshot(snapshot_path, history_output=history_path)
        second_snapshot_bytes = snapshot_path.read_bytes()
        second_history_bytes = history_path.read_bytes()
        second_history = _read(history_path)

        history_path.write_text("{invalid-history", encoding="utf-8")
        write_snapshot(snapshot_path, history_output=history_path)
        repaired_history = _read(history_path)

        metrics_path = root / "runtime-metrics.json"
        metrics_path.write_text(
            json.dumps(
                {
                    "states": {
                        "repair": {
                            "metrics": {
                                "lock": 0.31,
                                "presence": 0.22,
                                "coherence": 0.27,
                                "CRS": 0.24,
                                "AGR": 0.12,
                                "RF": 0.71,
                                "drift_index": 0.77,
                            }
                        }
                    }
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        write_snapshot(snapshot_path, metrics_input=metrics_path, history_output=history_path)
        changed_snapshot_bytes = snapshot_path.read_bytes()
        changed_history_bytes = history_path.read_bytes()
        changed_snapshot = _read(snapshot_path)
        changed_history = _read(history_path)

        write_snapshot(snapshot_path, metrics_input=metrics_path, history_output=history_path)
        repeated_changed_snapshot_bytes = snapshot_path.read_bytes()
        repeated_changed_history_bytes = history_path.read_bytes()
        repeated_changed_history = _read(history_path)

        checks = {
            "first_observation_writes_snapshot": snapshot_path.exists(),
            "first_observation_writes_history": history_path.exists(),
            "first_history_has_one_entry": first_history.get("entry_count") == 1,
            "history_entry_has_fingerprint": bool(
                first_history.get("entries", [{}])[-1].get("observation_fingerprint")
            ),
            "identical_sample_observation_preserves_snapshot_bytes": (
                second_snapshot_bytes == first_snapshot_bytes
            ),
            "identical_sample_observation_preserves_history_bytes": (
                second_history_bytes == first_history_bytes
            ),
            "identical_sample_observation_does_not_append_history": (
                second_history.get("entry_count") == 1
            ),
            "identical_snapshot_repairs_invalid_history": (
                repaired_history.get("entry_count") == 1
                and bool(
                    repaired_history.get("entries", [{}])[-1].get(
                        "observation_fingerprint"
                    )
                )
            ),
            "changed_metrics_replace_snapshot": changed_snapshot_bytes != second_snapshot_bytes,
            "changed_metrics_record_runtime_source": (
                str(metrics_path) in str(changed_snapshot.get("source"))
            ),
            "changed_metrics_append_history_once": changed_history.get("entry_count") == 2,
            "changed_metrics_create_distinct_fingerprint": (
                changed_history["entries"][0].get("observation_fingerprint")
                != changed_history["entries"][1].get("observation_fingerprint")
            ),
            "repeated_changed_metrics_preserve_snapshot_bytes": (
                repeated_changed_snapshot_bytes == changed_snapshot_bytes
            ),
            "repeated_changed_metrics_preserve_history_bytes": (
                repeated_changed_history_bytes == changed_history_bytes
            ),
            "repeated_changed_metrics_do_not_append_history": (
                repeated_changed_history.get("entry_count") == 2
            ),
            "generated_timestamp_changes_only_with_observation": (
                first_snapshot.get("generated_at_utc") != changed_snapshot.get("generated_at_utc")
            ),
        }
        report = {
            "suite": "Lumina Weather Snapshot Idempotence Sea Trial R1",
            "passed": all(checks.values()),
            "checks": checks,
        }
        print(json.dumps(report, indent=2))
        if not report["passed"]:
            raise SystemExit(1)
        return report


if __name__ == "__main__":
    main()
