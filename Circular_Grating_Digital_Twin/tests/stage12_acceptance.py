"""Stage-12 acceptance for the coupled controller and off-screen GUI scene."""
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
from Circular_Grating_Digital_Twin.control.controller import TwinController
from Circular_Grating_Digital_Twin.matlab.matlab_bridge import MatlabBridge
from Circular_Grating_Digital_Twin.visualization.viewer import TwinViewer


def run_acceptance() -> dict[str, object]:
    params = CircularGratingParameters.from_mapping({"radial_points": 20, "angular_points": 48})
    bridge = MatlabBridge()
    controller = TwinController(parameters=params, bridge=bridge)
    result: dict[str, object] = {"pass_gui": False, "pass_matlab": False,
                                 "pass_model": False, "pass_signal": False,
                                 "pass_adc": False, "pass_serial": False, "pass": False}
    try:
        controller.refresh()
        result["pass_matlab"] = bool(controller.last_result and controller.last_result.get("status") == "ok")
        initial_assembly = controller.last_assembly
        initial_result = controller.last_result
        viewer = TwinViewer(controller, off_screen=True)
        viewer.build_scene(add_sliders=False)
        result["pass_gui"] = viewer.plotter is not None
        viewer.close()
        controller.update(period=30e-6)
        period_result = controller.last_result
        period_assembly = controller.last_assembly
        controller.update(shift=15e-6)
        shift_result = controller.last_result
        model_delta = float(np.max(np.abs(period_assembly["main_grating"].vertices - initial_assembly["main_grating"].vertices)))
        signal_delta = float(np.max(np.abs(np.asarray(period_result["signal"], dtype=float) - np.asarray(initial_result["signal"], dtype=float))))
        adc_delta = float(np.max(np.abs(np.asarray(period_result["adc_code"], dtype=float) - np.asarray(initial_result["adc_code"], dtype=float))))
        frame0 = TwinController(parameters=params, bridge=None)
        frame0.last_result = initial_result
        frame1 = TwinController(parameters=params, bridge=None)
        frame1.last_result = period_result
        result.update({"model_max_delta": model_delta, "signal_max_delta": signal_delta,
                       "adc_max_delta": adc_delta,
                       "pass_model": bool(model_delta > 0),
                       "pass_signal": bool(signal_delta > 1e-9),
                       "pass_adc": bool(adc_delta >= 1),
                       "pass_serial": bool(frame0.serial_preview() != frame1.serial_preview())})
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        bridge.close()
    result["pass"] = all(bool(result[key]) for key in ("pass_gui", "pass_matlab", "pass_model", "pass_signal", "pass_adc", "pass_serial"))
    return result


if __name__ == "__main__":
    report = run_acceptance()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    raise SystemExit(0 if report["pass"] else 1)
