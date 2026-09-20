"""Stage-9 acceptance: Python starts MATLAB and calls ``python_control``."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from Circular_Grating_Digital_Twin.matlab.matlab_bridge import MatlabBridge


def run_acceptance() -> dict[str, object]:
    result: dict[str, object] = {
        "pass_engine": False,
        "pass_interface": False,
        "pass": False,
    }
    bridge = MatlabBridge()
    try:
        bridge.start()
        result["pass_engine"] = True
        response = bridge.ping()
        result["response"] = response
        result["pass_interface"] = response.get("status") == "ok"
    except Exception as exc:  # Acceptance output must explain environment failures.
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        bridge.close()
    result["pass"] = bool(result["pass_engine"] and result["pass_interface"])
    return result


if __name__ == "__main__":
    report = run_acceptance()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    raise SystemExit(0 if report["pass"] else 1)
