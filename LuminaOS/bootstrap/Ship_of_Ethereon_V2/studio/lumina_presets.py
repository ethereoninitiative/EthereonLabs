#!/usr/bin/env python3
"""Lumina Studio Presets v0.3.

Small UI defaults for common Studio cycles. These only prefill forms.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

PRESETS: Dict[str, Dict[str, Any]] = {
    "observe_continuity": {
        "label": "Observe continuity",
        "description": "Inspect project state from Continuity into Observation.",
        "current_mode": "Continuity",
        "target_mode": "Observation",
        "action_type": "audit",
        "focus": "continuity",
        "depth": "structural",
        "intent": "verify",
        "action": "studio_observe_continuity",
        "project_id": "lumina-os",
        "prompt": "Review Lumina OS continuity and produce a Studio receipt.",
        "ethereonic_overlay": False,
    },
    "architecture_review": {
        "label": "Architecture review",
        "description": "Inspect runtime structure.",
        "current_mode": "Continuity",
        "target_mode": "Observation",
        "action_type": "audit",
        "focus": "architecture",
        "depth": "foundational",
        "intent": "verify",
        "action": "studio_architecture_review",
        "project_id": "lumina-os",
        "prompt": "Inspect the Lumina runtime architecture and summarize the receipt.",
        "ethereonic_overlay": False,
    },
    "sandbox_design": {
        "label": "Sandbox design",
        "description": "Explore a design move in Sandbox.",
        "current_mode": "Continuity",
        "target_mode": "Sandbox",
        "action_type": "audit",
        "focus": "integration",
        "depth": "structural",
        "intent": "build",
        "action": "studio_sandbox_design",
        "project_id": "lumina-os",
        "prompt": "Explore the next Lumina Studio design move as a Sandbox proposal.",
        "ethereonic_overlay": True,
    },
    "receipt_review": {
        "label": "Receipt review",
        "description": "Review recent Studio receipts.",
        "current_mode": "Continuity",
        "target_mode": "Observation",
        "action_type": "audit",
        "focus": "governance_review",
        "depth": "structural",
        "intent": "verify",
        "action": "studio_receipt_review",
        "project_id": "lumina-os",
        "prompt": "Review recent Studio receipts and identify boundary concerns.",
        "ethereonic_overlay": False,
    },
}


def list_presets() -> List[Dict[str, Any]]:
    return [{"id": preset_id, **payload} for preset_id, payload in PRESETS.items()]


def get_preset(preset_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not preset_id:
        return None
    payload = PRESETS.get(preset_id)
    if payload is None:
        return None
    return {"id": preset_id, **payload}


def presets_payload() -> Dict[str, Any]:
    return {
        "schema_version": "lumina-studio-presets-v0.3",
        "presets": list_presets(),
    }


if __name__ == "__main__":
    print(json.dumps(presets_payload(), indent=2))
