"""MATLAB Engine bridge for torque-sensor response calculation."""
from __future__ import annotations

import importlib
from pathlib import Path
import sys
from typing import Any


class MatlabBridge:
    def __init__(self, matlab_project: str | Path | None = None):
        self.matlab_project = Path(matlab_project or Path(__file__).resolve().parents[2] / "Grating_Digital_Twin").resolve()
        self._engine: Any = None

    def start(self):
        if self._engine is not None: return self
        if f"{sys.version_info.major}.{sys.version_info.minor}" not in ("3.9", "3.10", "3.11", "3.12"):
            raise RuntimeError("MATLAB R2024b Engine requires Python 3.9-3.12; use py -3.12")
        local = Path(__file__).resolve().parents[1]
        old = list(sys.path)
        sys.path = [x for x in sys.path if Path(x or ".").resolve() != local]
        try:
            eng_mod = importlib.import_module("matlab.engine")
        finally:
            sys.path = old
        self._engine = eng_mod.start_matlab()
        self._engine.addpath(str(self.matlab_project / "interface"), nargout=0)
        return self

    @property
    def engine(self):
        if self._engine is None: raise RuntimeError("MATLAB Engine is not started")
        return self._engine

    def run_torque(self, parameter: dict[str, Any]) -> dict[str, Any]:
        defaults = {
            "torque": 0.0,
            "torsion_length": 0.012,
            "shear_modulus": 79e9,
            "shaft_diameter": 0.008,
            "grating_radius": 0.007,
            "grating_period": 20e-6,
            "phase_zero": 0.0,
        }
        payload = {name: float(parameter.get(name, value)) for name, value in defaults.items()}
        for name, value in (("excitation_frequency", 250.0), ("excitation_amplitude", 0.20)):
            payload[name] = float(parameter.get(name, value))
        payload["parameter_source"] = str(parameter.get("parameter_source", "simulation/default"))
        if "serial_mode" in parameter:
            payload["serial_mode"] = str(parameter["serial_mode"])
        response = self.engine.python_control("run_torque", payload, nargout=1)
        return dict(response) if isinstance(response, dict) else {"status": "ok", "raw": response}

    def close(self):
        if self._engine is not None: self._engine.quit(); self._engine = None

    def __enter__(self): return self.start()
    def __exit__(self, *_): self.close()
