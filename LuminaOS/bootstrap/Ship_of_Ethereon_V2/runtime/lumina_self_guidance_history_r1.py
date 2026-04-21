from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

try:
    from .repo_paths_r1 import state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import state_root as _state_root_helper
    except Exception:
        _state_root_helper = None

MODULE_SLUG = "lumina_self_guidance_history_r1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            return Path(_state_root_helper()).resolve()
        except Exception:
            pass
    return Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"


BASE_DIR = infer_state_root() / MODULE_SLUG


class ProjectGuidanceHistoryStore:
    """Append-only project-scoped memory rail for bounded self-guidance advisories."""

    def __init__(self, base_dir: str | Path = BASE_DIR):
        self.base_dir = Path(base_dir)
        self.history_dir = self.base_dir / "projects"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
        return slug or "lumina-core"

    def _history_path(self, project_id: str) -> Path:
        return self.history_dir / f"{self._safe_slug(project_id)}.jsonl"

    def read_history(self, project_id: str) -> List[Dict[str, Any]]:
        path = self._history_path(project_id)
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def append_entry(
        self,
        *,
        project_id: str,
        advisory_summary: Dict[str, Any],
        checkpoint_path: Optional[str],
        requested_action: str,
        current_mode: str,
        target_mode: str,
        working_stance: Optional[Dict[str, Any]] = None,
        source: str = "checkpoint_refresh",
    ) -> Dict[str, Any]:
        path = self._history_path(project_id)
        working_stance = dict(working_stance or {})
        entry = {
            "timestamp_utc": utc_now(),
            "project_id": project_id,
            "source": source,
            "requested_action": requested_action,
            "current_mode": current_mode,
            "target_mode": target_mode,
            "checkpoint_path": checkpoint_path,
            "recommended_next_action": advisory_summary.get("recommended_next_action"),
            "guidance_strategy": advisory_summary.get("guidance_strategy"),
            "confidence_label": advisory_summary.get("confidence_label"),
            "confidence_score": advisory_summary.get("confidence_score"),
            "working_stance_focus": working_stance.get("focus_target"),
            "active_layout_id": working_stance.get("active_layout_id"),
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    @staticmethod
    def history_summary(history: List[Dict[str, Any]]) -> Dict[str, Any]:
        rows = list(history or [])
        recent = rows[-3:]
        recent_recommendations = [
            row.get("recommended_next_action")
            for row in recent
            if row.get("recommended_next_action")
        ]
        return {
            "entry_count": len(rows),
            "recent_recommendations": recent_recommendations,
            "latest_recommendation": recent_recommendations[-1] if recent_recommendations else None,
            "latest_checkpoint_path": recent[-1].get("checkpoint_path") if recent else None,
        }
