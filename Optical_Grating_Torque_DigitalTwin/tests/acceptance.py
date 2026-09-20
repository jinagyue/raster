"""End-to-end acceptance for the mechanical torque digital-twin platform."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]; WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path: sys.path.insert(0, str(WORKSPACE))

from Optical_Grating_Torque_DigitalTwin.config.parameter import parameter
from Optical_Grating_Torque_DigitalTwin.control.torque_controller import TorqueController
from Optical_Grating_Torque_DigitalTwin.matlab.matlab_bridge import MatlabBridge


def run_acceptance() -> dict[str, object]:
    p = parameter(); bridge = MatlabBridge(); controller = TorqueController(p, bridge)
    result = {"pass_gui": False, "pass_model": False, "pass_motion": False, "pass_matlab": False, "pass_signal": False, "pass_adc": False, "pass_serial": False, "pass": False}
    try:
        out0 = controller.refresh(); result["pass_matlab"] = bool(out0["simulation"] and out0["simulation"].get("status") == "ok")
        asm = out0["assembly"]
        result["pass_model"] = bool(
            asm["housing"].GetNumberOfPoints() > 0
            and asm["shaft"].GetNumberOfPoints() > 0
            and asm["left_flange"]["body"].GetNumberOfPoints() > 0
            and asm["right_flange"]["body"].GetNumberOfPoints() > 0
            and asm["grating_disk"]["disk"].GetNumberOfPoints() > 0
            and asm["grating_disk"]["grooves"].GetNumberOfPoints() > 0
            and asm["optical_readout"]["sensor_array"].GetNumberOfPoints() > 0
        )
        result["pass_motion"] = abs(controller.parameters.effective_angle - controller.parameters.torque_angle) < 1e-12
        adc0 = np.asarray(out0["simulation"]["adc_code"], dtype=float); sig0 = np.asarray(out0["simulation"]["four_phase_signal"], dtype=float)
        frame0 = controller.serial_preview()
        serial_frames = int(out0["simulation"]["serial_status"]["frames"])
        out1 = controller.update(torque=0.5)
        adc1 = np.asarray(out1["simulation"]["adc_code"], dtype=float); sig1 = np.asarray(out1["simulation"]["four_phase_signal"], dtype=float)
        result.update({"pass_signal": bool(np.max(np.abs(sig1-sig0)) > 1e-9), "pass_adc": bool(np.max(np.abs(adc1-adc0)) >= 1), "pass_serial": bool(serial_frames > 0 and controller.serial_preview() != frame0), "serial_frames": serial_frames, "adc_delta": float(np.max(np.abs(adc1-adc0))), "signal_delta": float(np.max(np.abs(sig1-sig0)))})
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt5 import QtWidgets
        from Optical_Grating_Torque_DigitalTwin.gui.main_window import MainWindow
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        win = MainWindow(TorqueController(parameter(), None)); result["pass_gui"] = bool(win.vtk.renderer.GetActors().GetNumberOfItems() > 0); win.close(); app.processEvents()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally: bridge.close()
    result["pass"] = all(bool(result[k]) for k in ("pass_gui", "pass_model", "pass_motion", "pass_matlab", "pass_signal", "pass_adc", "pass_serial"))
    return result


if __name__ == "__main__":
    report = run_acceptance(); print(json.dumps(report, ensure_ascii=False, indent=2, default=str)); raise SystemExit(0 if report["pass"] else 1)
