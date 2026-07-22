from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SHIP_ROOT = Path(__file__).resolve().parent
STUDIO_ROOT = SHIP_ROOT / "studio"
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

import lumina_studio_server as studio


def _invoke_handler(
    *,
    raised: Optional[Exception] = None,
    body: bytes = b"{}",
    content_type: str = "application/json",
) -> Dict[str, Any]:
    captured: Dict[str, Any] = {}
    handler = studio.LuminaStudioHandler.__new__(studio.LuminaStudioHandler)
    handler.path = "/run"
    handler.headers = {
        "Content-Length": str(len(body)),
        "Content-Type": content_type,
    }
    handler.rfile = io.BytesIO(body)
    handler._send = lambda status, response_body, response_type: captured.update(
        {
            "status": status,
            "body": response_body,
            "content_type": response_type,
        }
    )

    original_run = studio.run_lumina_cycle
    if raised is not None:
        def raise_error(_args: Any) -> Any:
            raise raised
        studio.run_lumina_cycle = raise_error
    try:
        handler.do_POST()
    finally:
        studio.run_lumina_cycle = original_run

    captured["payload"] = json.loads(captured["body"].decode("utf-8"))
    return captured


def main() -> Dict[str, Any]:
    long_path = "C:\\Lumina\\" + ("segment\\" * 40) + "receipt.json"
    path_error = OSError(206, "The filename or extension is too long", long_path)
    path_result = _invoke_handler(raised=path_error)
    os_result = _invoke_handler(raised=OSError(5, "simulated artifact write failure"))
    runtime_result = _invoke_handler(raised=RuntimeError("simulated runtime failure"))
    invalid_json_result = _invoke_handler(body=b"{not-json")

    required_keys = {"ok", "error_code", "error", "recoverable", "error_class"}
    checks = {
        "path_budget_error_classified": (
            path_result["status"] == 422
            and path_result["payload"].get("error_code") == "path_budget_exceeded"
            and path_result["payload"].get("recoverable") is True
            and path_result["payload"].get("path_budget") == studio.PORTABLE_PATH_BUDGET
            and path_result["payload"].get("path_length", 0) > studio.PORTABLE_PATH_BUDGET
        ),
        "generic_os_error_classified": (
            os_result["status"] == 500
            and os_result["payload"].get("error_code") == "artifact_write_failed"
            and os_result["payload"].get("recoverable") is True
        ),
        "runtime_error_has_bounded_fallback": (
            runtime_result["status"] == 500
            and runtime_result["payload"].get("error_code") == "runtime_cycle_failed"
            and runtime_result["payload"].get("recoverable") is False
        ),
        "invalid_json_is_operator_correctable": (
            invalid_json_result["status"] == 400
            and invalid_json_result["payload"].get("error_code") == "invalid_request_payload"
            and invalid_json_result["payload"].get("recoverable") is True
        ),
        "responses_share_bounded_shape": all(
            required_keys.issubset(result["payload"])
            and result["payload"].get("ok") is False
            and len(result["payload"].get("error", "")) <= studio.MAX_OPERATOR_ERROR_LENGTH
            and result["content_type"] == "application/json"
            for result in (path_result, os_result, runtime_result, invalid_json_result)
        ),
    }
    report = {
        "passed": all(checks.values()),
        "checks": checks,
        "samples": {
            "path_budget": path_result["payload"],
            "artifact_write": os_result["payload"],
            "runtime": runtime_result["payload"],
            "invalid_json": invalid_json_result["payload"],
        },
    }
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    main()
