"""Entry point for the mechanical optical-grating torque twin."""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

if __package__:
    from .config.parameter import parameter
    from .control.torque_controller import TorqueController
    from .gui.main_window import MainWindow
    from .matlab.matlab_bridge import MatlabBridge
else:
    # Support IDE Run / direct ``python path\main.py`` without weakening the
    # normal package imports used by ``python -m`` and PyInstaller.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    parameter = importlib.import_module(
        "Optical_Grating_Torque_DigitalTwin.config.parameter"
    ).parameter
    TorqueController = importlib.import_module(
        "Optical_Grating_Torque_DigitalTwin.control.torque_controller"
    ).TorqueController
    MainWindow = importlib.import_module(
        "Optical_Grating_Torque_DigitalTwin.gui.main_window"
    ).MainWindow
    MatlabBridge = importlib.import_module(
        "Optical_Grating_Torque_DigitalTwin.matlab.matlab_bridge"
    ).MatlabBridge


def run_gui(with_matlab: bool = False) -> int:
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    bridge = MatlabBridge() if with_matlab else None
    controller = TorqueController(parameter(), bridge)
    window = MainWindow(controller); window.show()
    try: return app.exec_()
    finally:
        if bridge is not None:
            bridge.close()


def run_once() -> dict:
    bridge = MatlabBridge(); controller = TorqueController(parameter(), bridge)
    try:
        out = controller.refresh()
        return {"components": sorted(out["assembly"].keys()), "matlab_status": out["simulation"].get("status"), "serial_frame": controller.serial_preview().hex(" ")}
    finally: bridge.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--with-matlab", action="store_true", help="enable the existing MATLAB-coupled view")
    args = parser.parse_args()
    if args.no_gui: print(json.dumps(run_once(), ensure_ascii=False, indent=2, default=str))
    else: raise SystemExit(run_gui(with_matlab=True))
