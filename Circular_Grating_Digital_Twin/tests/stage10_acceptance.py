"""Stage-10 acceptance: round-trip Python parameters through MATLAB."""
from __future__ import annotations

import json
from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from Circular_Grating_Digital_Twin.matlab.matlab_bridge import MatlabBridge


def run_acceptance() -> dict[str, object]:
    requested = {"period": 20e-6, "radius": 1e-3, "ring_number": 50,
                 "height": 1e-6, "shift": 5e-6}
    result: dict[str, object] = {"pass_engine": False, "pass_parameter": False, "pass": False}
    bridge = MatlabBridge()
    try:
        bridge.start()
        result["pass_engine"] = bridge.ping().get("status") == "ok"
        sent = bridge.set_parameter(requested)
        received = sent.get("parameter", {})
        result["parameter"] = received
        result["max_abs_error"] = max(abs(float(received[name]) - value) for name, value in requested.items())
        result["pass_parameter"] = bool(result["max_abs_error"] < 1e-12)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        bridge.close()
    result["pass"] = bool(result["pass_engine"] and result["pass_parameter"])
    return result


if __name__ == "__main__":
    report = run_acceptance()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    raise SystemExit(0 if report["pass"] else 1)
