"""Cross-language acceptance for the Stage-12 torque physical chain."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

import numpy as np

from Optical_Grating_Torque_DigitalTwin.config.parameter import TorqueSensorParameters, parameter
from Optical_Grating_Torque_DigitalTwin.matlab.matlab_bridge import MatlabBridge
from Optical_Grating_Torque_DigitalTwin.mechanics.torque_model import calculate_torque_state
from Optical_Grating_Torque_DigitalTwin.model.assembly import build_assembly


def _payload(p: TorqueSensorParameters, torque: float) -> dict[str, float | str]:
    return {
        "torque": torque,
        "torsion_length": p.torsion_length,
        "shear_modulus": p.shear_modulus,
        "shaft_diameter": p.torsion_diameter,
        "grating_radius": p.effective_detection_radius,
        "grating_period": p.grating_period,
        "phase_zero": p.optical_phase_zero,
        "parameter_source": p.mechanical_parameter_source,
        "serial_mode": "none",
    }


def _python_state(p: TorqueSensorParameters, torque: float) -> dict[str, float | str]:
    return calculate_torque_state(
        torque=torque,
        torsion_length=p.torsion_length,
        shear_modulus=p.shear_modulus,
        shaft_diameter=p.torsion_diameter,
        grating_radius=p.effective_detection_radius,
        grating_period=p.grating_period,
        phase_zero=p.optical_phase_zero,
        parameter_source=p.mechanical_parameter_source,
    )


def run_acceptance() -> dict[str, object]:
    report: dict[str, object] = {
        "pass_zero": False,
        "pass_double": False,
        "pass_theta_formula": False,
        "pass_dx": False,
        "pass_phase": False,
        "pass_vtk_drive": False,
        "pass_existing_signal_chain": False,
        "pass_python_matlab_consistency": False,
        "pass_matlab_acceptance": False,
        "pass": False,
    }
    bridge = MatlabBridge()
    try:
        p = parameter()
        torque1, torque2 = 0.25, 0.50
        py0, py1, py2 = (_python_state(p, value) for value in (0.0, torque1, torque2))
        moment = math.pi * p.torsion_diameter**4 / 32.0
        expected_theta = torque1 * p.torsion_length / (p.shear_modulus * moment)
        expected_dx = p.effective_detection_radius * expected_theta
        expected_phase = 2.0 * math.pi * expected_dx / p.grating_period + p.optical_phase_zero
        tolerance = 1e-12
        report["pass_zero"] = bool(abs(float(py0["torsion_angle"])) < tolerance)
        report["pass_double"] = bool(abs(float(py2["torsion_angle"]) - 2.0 * float(py1["torsion_angle"])) < tolerance)
        report["pass_theta_formula"] = bool(abs(float(py1["torsion_angle"]) - expected_theta) < tolerance)
        report["pass_dx"] = bool(abs(float(py1["relative_displacement"]) - expected_dx) < tolerance)
        report["pass_phase"] = bool(abs(float(py1["optical_phase"]) - expected_phase) < tolerance)

        p0 = TorqueSensorParameters.from_mapping({**p.to_dict(), "torque": 0.0})
        p1 = TorqueSensorParameters.from_mapping({**p.to_dict(), "torque": torque1})
        assembly0 = build_assembly(p0, angle=float(py0["torsion_angle"]))
        assembly1 = build_assembly(p1, angle=float(py1["torsion_angle"]))
        mark0 = np.asarray(assembly0["main_grating"]["orientation_mark"].GetBounds())
        mark1 = np.asarray(assembly1["main_grating"]["orientation_mark"].GetBounds())
        report["pass_vtk_drive"] = bool(
            abs(float(assembly1["main_grating"]["rotation"]) - expected_theta) < tolerance
            and np.max(np.abs(mark1 - mark0)) > 0.0
        )

        bridge.start()
        mat0 = bridge.run_torque(_payload(p, 0.0))
        mat1 = bridge.run_torque(_payload(p, torque1))
        mat2 = bridge.run_torque(_payload(p, torque2))
        matlab_values = np.asarray([
            float(mat1["torsion_angle"]),
            float(mat1["grating_relative_displacement"]),
            float(mat1["optical_phase"]),
            float(mat1["polar_moment"]),
        ])
        python_values = np.asarray([
            float(py1["torsion_angle"]),
            float(py1["relative_displacement"]),
            float(py1["optical_phase"]),
            float(py1["polar_moment"]),
        ])
        consistency_error = float(np.max(np.abs(matlab_values - python_values)))
        report["pass_python_matlab_consistency"] = bool(
            consistency_error < tolerance
            and abs(float(mat0["torsion_angle"])) < tolerance
            and abs(float(mat2["torsion_angle"]) - 2.0 * float(mat1["torsion_angle"])) < tolerance
        )
        signal = np.asarray(mat1["four_phase_signal"], dtype=float)
        report["pass_existing_signal_chain"] = bool(mat1.get("status") == "ok" and signal.ndim == 2 and signal.shape[1] == 4)

        bridge.engine.addpath(str(WORKSPACE / "Grating_Digital_Twin" / "tests"), nargout=0)
        matlab_report = bridge.engine.stage12_acceptance(nargout=1)
        report["pass_matlab_acceptance"] = bool(matlab_report["pass"])
        report.update({
            "parameter_source": p.mechanical_parameter_source,
            "polar_moment_m4": moment,
            "torsion_angle_rad": expected_theta,
            "relative_displacement_m": expected_dx,
            "optical_phase_rad": expected_phase,
            "python_matlab_max_abs_error": consistency_error,
        })
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        bridge.close()
    keys = (
        "pass_zero", "pass_double", "pass_theta_formula", "pass_dx", "pass_phase",
        "pass_vtk_drive", "pass_existing_signal_chain", "pass_python_matlab_consistency",
        "pass_matlab_acceptance",
    )
    report["pass"] = all(bool(report[key]) for key in keys) and report.get("parameter_source") == "simulation/default"
    return report


if __name__ == "__main__":
    result = run_acceptance()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["pass"] else 1)
