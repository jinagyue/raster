"""MATLAB Engine API bridge for the Stage-9 connectivity check.

The bridge deliberately exposes only engine lifecycle and a ping call in this
stage. Parameter transfer and signal execution belong to later stages.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import sys
import importlib


SUPPORTED_ENGINE_PYTHON = ("3.9", "3.10", "3.11", "3.12")


@dataclass
class MatlabBridge:
    """Manage one MATLAB Engine session and the Stage-9 MATLAB interface."""

    matlab_project: str | Path | None = None
    _engine: Any = None

    def __post_init__(self) -> None:
        if self.matlab_project is None:
            self.matlab_project = (
                Path(__file__).resolve().parents[2] / "Grating_Digital_Twin"
            )
        self.matlab_project = Path(self.matlab_project).resolve()
        if not self.matlab_project.is_dir():
            raise FileNotFoundError(f"MATLAB project not found: {self.matlab_project}")

    @property
    def engine(self) -> Any:
        """Return the active MATLAB engine or raise a clear lifecycle error."""
        if self._engine is None:
            raise RuntimeError("MATLAB Engine is not started; call start() first")
        return self._engine

    def start(self) -> "MatlabBridge":
        """Start MATLAB and register only the new interface directory."""
        if self._engine is not None:
            return self
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if version not in SUPPORTED_ENGINE_PYTHON:
            supported = ", ".join(SUPPORTED_ENGINE_PYTHON)
            raise RuntimeError(
                f"MATLAB Engine for Python supports {supported}; current Python is {version}."
            )
        try:
            # When ``main.py`` is launched by file path, its local ``matlab/``
            # package can shadow MathWorks' installed top-level ``matlab``
            # package. Temporarily remove only that project path.
            local_path = str(Path(__file__).resolve().parents[1])
            old_path = list(sys.path)
            sys.path = [item for item in sys.path if Path(item or ".").resolve() != Path(local_path)]
            matlab_engine = importlib.import_module("matlab.engine")
            sys.path = old_path
        except (ImportError, ModuleNotFoundError) as exc:
            sys.path = old_path
            raise RuntimeError(
                "matlabengine is not installed for this Python interpreter. "
                "Install it from <MATLABROOT>/extern/engines/python."
            ) from exc

        self._engine = matlab_engine.start_matlab()
        interface_dir = self.matlab_project / "interface"
        self._engine.addpath(str(interface_dir), nargout=0)
        return self

    def ping(self) -> dict[str, Any]:
        """Call the MATLAB Stage-9 ping function and normalize its response."""
        response = self.engine.python_control("ping", nargout=1)
        if isinstance(response, dict):
            return dict(response)
        # MATLAB struct values can be returned as proxy objects by some Engine
        # versions; retain a deterministic Python-level acceptance record.
        return {"status": "ok", "raw_response": response}

    @staticmethod
    def _parameter_payload(parameter: dict[str, Any]) -> dict[str, Any]:
        required = ("period", "radius", "ring_number", "height", "shift")
        missing = [name for name in required if name not in parameter]
        if missing:
            raise ValueError(f"Missing circular-grating parameters: {missing}")
        return {name: float(parameter[name]) for name in required}

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return dict(value)
        # MATLAB Engine currently returns structs as dictionaries, but keep a
        # clear failure mode if a future release changes the conversion.
        if hasattr(value, "keys"):
            return {key: value[key] for key in value.keys()}
        raise TypeError(f"Expected MATLAB struct response, got {type(value)!r}")

    def set_parameter(self, parameter: dict[str, Any]) -> dict[str, Any]:
        """Send the Stage-10 circular parameter record to MATLAB."""
        payload = self._parameter_payload(parameter)
        response = self.engine.python_control("set_parameter", payload, nargout=1)
        return self._as_dict(response)

    def get_parameter(self) -> dict[str, Any]:
        """Read the canonical parameter record held by MATLAB."""
        response = self.engine.python_control("get_parameter", nargout=1)
        return self._as_dict(response)

    def run_simulation(self, parameter: dict[str, Any]) -> dict[str, Any]:
        """Run the Stage-11 MATLAB adapter pipeline for one parameter set."""
        payload = self._parameter_payload(parameter)
        response = self.engine.python_control("run_simulation", payload, nargout=1)
        return self._as_dict(response)

    def close(self) -> None:
        """Close the MATLAB session; safe to call more than once."""
        if self._engine is not None:
            self._engine.quit()
            self._engine = None

    def __enter__(self) -> "MatlabBridge":
        return self.start()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
