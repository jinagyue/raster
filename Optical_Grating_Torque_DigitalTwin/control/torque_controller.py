"""Mechanical torque -> angle -> optical displacement controller."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np

from ..config.parameter import TorqueSensorParameters, parameter
from ..model.assembly import build_assembly
from ..matlab.matlab_bridge import MatlabBridge
from ..mechanics.torque_model import calculate_torque_state


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8): crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode_adc_frame(codes: Any) -> bytes:
    values = np.asarray(codes, dtype=np.uint16).reshape(-1)
    if values.size != 4: raise ValueError("four ADC channels are required")
    body = bytearray([0xAA])
    for value in values: body.extend((int(value) >> 8, int(value) & 255))
    crc = crc16_ccitt(bytes(body)); return bytes(body) + bytes((crc >> 8, crc & 255))


@dataclass
class TorqueController:
    parameters: TorqueSensorParameters = field(default_factory=parameter)
    bridge: MatlabBridge | None = None
    assembly: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    mechanical_state: dict[str, Any] | None = None
    running: bool = False
    serial_enabled: bool = False

    def refresh(self):
        self.parameters = TorqueSensorParameters.from_mapping(self.parameters.to_dict())
        p = self.parameters
        dt = p.temperature - p.temperature_reference
        g_temp = p.shear_modulus * (1.0 + p.shear_modulus_temperature_coeff * dt)
        period_temp = p.grating_period * (1.0 + p.grating_period_temperature_coeff * dt)
        phase_zero = p.optical_phase_zero + 2.0 * np.pi * p.grating_displacement / period_temp
        self.mechanical_state = calculate_torque_state(
            torque=p.torque,
            torsion_length=p.torsion_length,
            shear_modulus=g_temp,
            shaft_diameter=p.torsion_diameter,
            grating_radius=p.effective_detection_radius,
            grating_period=period_temp,
            phase_zero=phase_zero,
            parameter_source=p.mechanical_parameter_source,
        )
        true_angle = float(self.mechanical_state["torsion_angle"])
        display_angle = true_angle * p.visual_torsion_scale
        self.assembly = build_assembly(p, angle=display_angle)
        if self.bridge is not None:
            self.bridge.start()
            self.result = self.bridge.run_torque({
                "torque": p.torque,
                "torsion_length": p.torsion_length,
                "shear_modulus": g_temp,
                "shaft_diameter": p.torsion_diameter,
                "grating_radius": p.effective_detection_radius,
                "grating_period": period_temp,
                "phase_zero": phase_zero,
                "parameter_source": p.mechanical_parameter_source,
                "excitation_frequency": 250.0,
                "excitation_amplitude": max(0.20, 0.15 * abs(p.torque)),
            })
        else:
            self.result = None
        if self.result is not None:
            phase = float(self.mechanical_state["optical_phase"])
            self.result.update({"angle": self.mechanical_state["torsion_angle"],
                                "torsion_angle": self.mechanical_state["torsion_angle"],
                                "grating_relative_displacement": self.mechanical_state["relative_displacement"],
                                "grating_displacement": self.mechanical_state["relative_displacement"], "optical_phase": phase,
                                "temperature": p.temperature, "direction": "顺时针" if p.torque > 0 else ("逆时针" if p.torque < 0 else "静止"),
                                "zero_status": abs((phase + np.pi) % (2*np.pi) - np.pi) < 0.08, "period": period_temp,
                                "display_torsion_angle": display_angle,
                                "visual_torsion_scale": p.visual_torsion_scale})
        return {"assembly": self.assembly, "simulation": self.result, "mechanics": self.mechanical_state}

    def update(self, **changes: float):
        if "angle" in changes:
            changes["rotation_angle"] = changes.pop("angle")
        values = self.parameters.to_dict(); values.update(changes)
        self.parameters = TorqueSensorParameters.from_mapping(values)
        return self.refresh()

    def serial_preview(self) -> bytes:
        if not self.result: raise RuntimeError("refresh first")
        return encode_adc_frame(np.asarray(self.result["adc_code"])[0, :])

    def set_running(self, running: bool) -> None:
        self.running = bool(running)

    def set_serial_enabled(self, enabled: bool) -> None:
        self.serial_enabled = bool(enabled)
