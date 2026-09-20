"""Stage-11 acceptance: geometry and MATLAB response are parameter-coupled."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from Circular_Grating_Digital_Twin.config.parameter import CircularGratingParameters
from Circular_Grating_Digital_Twin.matlab.matlab_bridge import MatlabBridge
from Circular_Grating_Digital_Twin.model.circular_grating import build_assembly


def run_acceptance() -> dict[str, object]:
    p = CircularGratingParameters.from_mapping({"radial_points": 24, "angular_points": 48})
    assembly = build_assembly(p)
    pass_geometry = all(mesh.is_watertight and mesh.volume > 0 for mesh in assembly.values())
    base = {"period": 20e-6, "radius": 1e-3, "ring_number": 50, "height": 1e-6, "shift": 5e-6}
    result: dict[str, object] = {"pass_geometry": pass_geometry, "pass_signal": False,
                                 "pass_adc": False, "pass": False}
    bridge = MatlabBridge()
    try:
        bridge.start()
        nominal = bridge.run_simulation(base)
        changed_period = bridge.run_simulation({**base, "period": 30e-6})
        changed_shift = bridge.run_simulation({**base, "shift": 15e-6})
        adc0 = np.asarray(nominal["adc_code"], dtype=float)
        adc1 = np.asarray(changed_period["adc_code"], dtype=float)
        phase0 = np.asarray(nominal["phase"], dtype=float)
        phase1 = np.asarray(changed_shift["phase"], dtype=float)
        adc_delta = float(np.max(np.abs(adc1 - adc0)))
        phase_delta = float(np.max(np.abs(phase1 - phase0)))
        result.update({"adc_max_delta": adc_delta, "phase_max_delta": phase_delta,
                       "pass_signal": bool(phase_delta > 1e-9),
                       "pass_adc": bool(adc_delta >= 1.0)})
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        bridge.close()
    result["pass"] = bool(result["pass_geometry"] and result["pass_signal"] and result["pass_adc"])
    return result


if __name__ == "__main__":
    report = run_acceptance()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    raise SystemExit(0 if report["pass"] else 1)
