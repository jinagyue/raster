"""Coordinate Python geometry updates and MATLAB physical-response calls."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..config.parameter import CircularGratingParameters, parameter
from ..matlab.matlab_bridge import MatlabBridge
from ..model.circular_grating import MeshData, build_assembly


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode_adc_frame(codes: Any) -> bytes:
    """Encode one four-channel ADC sample using the existing AA/CRC protocol."""
    values = np.asarray(codes, dtype=np.uint16).reshape(-1)
    if values.size != 4 or np.any(values > 4095):
        raise ValueError("codes must contain four 12-bit ADC values")
    body = bytearray([0xAA])
    for value in values:
        body.extend((int(value) >> 8, int(value) & 0xFF))
    crc = crc16_ccitt(bytes(body))
    return bytes(body) + bytes((crc >> 8, crc & 0xFF))


@dataclass
class TwinController:
    """Single source of truth for stage-12 UI parameters and results."""

    parameters: CircularGratingParameters = field(default_factory=parameter)
    bridge: MatlabBridge | None = None
    last_result: dict[str, Any] | None = None
    last_assembly: dict[str, MeshData] | None = None

    def payload(self) -> dict[str, float]:
        p = self.parameters
        return {"period": p.period, "radius": p.radius, "ring_number": p.ring_number,
                "height": p.groove_height, "shift": p.reference_shift[0]}

    def refresh(self, start_engine: bool = True) -> dict[str, Any]:
        self.last_assembly = build_assembly(self.parameters)
        if self.bridge is None:
            self.last_result = None
            return {"assembly": self.last_assembly}
        if start_engine:
            self.bridge.start()
        self.last_result = self.bridge.run_simulation(self.payload())
        return {"assembly": self.last_assembly, "simulation": self.last_result}

    def update(self, **changes: Any) -> dict[str, Any]:
        values = self.parameters.to_dict()
        if "ring_number" in changes:
            changes["ring_number"] = int(round(float(changes["ring_number"])))
        if "height" in changes:
            changes["groove_height"] = changes.pop("height")
        if "shift" in changes:
            values["reference_shift"] = (float(changes.pop("shift")), 0.0, 0.0)
        values.update(changes)
        self.parameters = CircularGratingParameters.from_mapping(values)
        return self.refresh()

    def serial_preview(self) -> bytes:
        if self.last_result is None:
            raise RuntimeError("refresh() must be called before serial_preview()")
        codes = np.asarray(self.last_result["adc_code"], dtype=np.uint16)
        return encode_adc_frame(codes[0, :])
