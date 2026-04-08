from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import subprocess
import uuid

try:
    from ethereonic_layer_r1 import EthereonicLayerRegistry
except Exception:
    EthereonicLayerRegistry = None

try:
    from canon_lineage_store_r1 import CanonLineageStore
except Exception:
    CanonLineageStore = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_git(args: List[str], cwd: Path) -> Optional[str]:
    try:
        proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except Exception:
        return None


@dataclass
class ContextBundle:
    bundle_id: str
    created_at: str
    active_mode: str
    structural_context: Dict[str, Any] = field(default_factory=dict)
    artifact_context: Dict[str, Any] = field(default_factory=dict)
    memory_context: Dict[str, Any] = field(default_factory=dict)
    environment_context: Dict[str, Any] = field(default_factory=dict)
    supplemental_ethereonic_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ContextBundleBuilder:
    """Builds bounded, replayable context while separating core execution context from Ethereonic overlays."""

    def __init__(
        self,
        output_dir: str | Path,
        ethereonic_layer_registry: Optional[Any] = None,
        canon_lineage_store: Optional[Any] = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ethereonic_layer_registry = ethereonic_layer_registry
        self.canon_lineage_store = canon_lineage_store

    def _resolve_canon_lineage_head(self, fallback: Optional[str] = None) -> Optional[str]:
        if self.canon_lineage_store is not None:
            head = self.canon_lineage_store.current_head()
            if head:
                return head.get("canon_version")
        return fallback

    def build(
        self,
        *,
        repo_path: Optional[str | Path] = None,
        active_mode: str = "Continuity",
        artifacts: Optional[List[str]] = None,
        canon_lineage_head: Optional[str] = None,
        continuation_notes: Optional[List[str]] = None,
        available_tools: Optional[List[str]] = None,
        ethereonic_context: Optional[Dict[str, Any]] = None,
    ) -> ContextBundle:
        repo = Path(repo_path) if repo_path else None
        structural_context = self._collect_structural_context(repo)
        resolved_head = self._resolve_canon_lineage_head(canon_lineage_head)
        bundle = ContextBundle(
            bundle_id=str(uuid.uuid4()),
            created_at=utc_now(),
            active_mode=active_mode,
            structural_context=structural_context,
            artifact_context={
                "active_design_docs": list(artifacts or []),
                "canon_lineage_head": resolved_head,
                "canon_lineage_source": "store" if self.canon_lineage_store is not None else "provided_or_none",
            },
            memory_context={"session_continuation_notes": list(continuation_notes or [])},
            environment_context={"current_utc": utc_now(), "available_tools": list(available_tools or [])},
            supplemental_ethereonic_context={},
        )
        if ethereonic_context:
            if self.ethereonic_layer_registry is None:
                raise ValueError("Ethereonic attachment requires EthereonicLayerRegistry; direct injection is not allowed")
            bundle = self.attach_ethereonic_context(bundle, ethereonic_context)
        self.save(bundle)
        return bundle

    def attach_ethereonic_context(
        self,
        bundle: ContextBundle,
        ethereonic_context: Optional[Dict[str, Any]] = None,
        *,
        include_artifact_ids: Optional[List[str]] = None,
    ) -> ContextBundle:
        if self.ethereonic_layer_registry is None:
            raise ValueError("Ethereonic attachment requires EthereonicLayerRegistry")
        payload = self.ethereonic_layer_registry.attach_to_context_bundle(
            bundle.to_dict(),
            include_artifact_ids=include_artifact_ids,
            extra_context=ethereonic_context or {},
        )
        return ContextBundle(**payload)

    def save(self, bundle: ContextBundle) -> Path:
        path = self.output_dir / f"{bundle.bundle_id}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(bundle.to_dict(), f, indent=2)
        return path

    def _collect_structural_context(self, repo_path: Optional[Path]) -> Dict[str, Any]:
        if not repo_path or not repo_path.exists():
            return {"repo_available": False}
        branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
        status = _run_git(["status", "--short"], repo_path)
        commits = _run_git(["log", "--oneline", "-5"], repo_path)
        return {
            "repo_available": True,
            "repo_path": str(repo_path),
            "current_branch": branch,
            "changed_files": status.splitlines() if status else [],
            "recent_commits": commits.splitlines() if commits else [],
        }
