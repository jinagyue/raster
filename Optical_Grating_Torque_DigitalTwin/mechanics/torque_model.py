"""Python reference implementation of the Stage-12 circular-shaft model."""
from __future__ import annotations

import math


def calculate_torque_state(
    *,
    torque: float,
    torsion_length: float,
    shear_modulus: float,
    shaft_diameter: float,
    grating_radius: float,
    grating_period: float,
    phase_zero: float = 0.0,
    parameter_source: str = "simulation/default",
) -> dict[str, float | str]:
    values = {
        "torsion_length": float(torsion_length),
        "shear_modulus": float(shear_modulus),
        "shaft_diameter": float(shaft_diameter),
        "grating_radius": float(grating_radius),
        "grating_period": float(grating_period),
    }
    if any(value <= 0.0 or not math.isfinite(value) for value in values.values()):
        raise ValueError("mechanical dimensions, modulus and grating period must be finite and positive")
    torque = float(torque)
    phase_zero = float(phase_zero)
    if not math.isfinite(torque) or not math.isfinite(phase_zero):
        raise ValueError("torque and phase_zero must be finite")
    polar_moment = math.pi * values["shaft_diameter"] ** 4 / 32.0
    torsion_angle = torque * values["torsion_length"] / (values["shear_modulus"] * polar_moment)
    relative_displacement = values["grating_radius"] * torsion_angle
    optical_phase = 2.0 * math.pi * relative_displacement / values["grating_period"] + phase_zero
    return {
        "torque": torque,
        "polar_moment": polar_moment,
        "torsion_angle": torsion_angle,
        "relative_displacement": relative_displacement,
        "optical_phase": optical_phase,
        "parameter_source": str(parameter_source),
    }
