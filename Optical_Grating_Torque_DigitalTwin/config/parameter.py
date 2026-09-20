"""Central mechanical and optical parameter registry (SI units)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class TorqueSensorParameters:
    housing_length: float = 0.040
    housing_radius: float = 0.015
    wall_thickness: float = 0.002
    flange_radius: float = 0.021
    flange_thickness: float = 0.004
    bolt_number: int = 6
    bolt_circle_radius: float = 0.017
    shaft_radius: float = 0.004
    shaft_length: float = 0.070
    elastic_length: float = 0.012
    elastic_width: float = 0.010
    elastic_thickness: float = 0.001
    torsion_length: float = 0.012
    shear_modulus: float = 79e9
    torsion_diameter: float = 0.008
    effective_detection_radius: float = 0.007
    optical_phase_zero: float = 0.0
    mechanical_parameter_source: str = "simulation/default"
    torsional_stiffness: float = 0.08
    disk_radius: float = 0.010
    disk_thickness: float = 0.0015
    grating_period: float = 20e-6
    line_number: int = 500
    main_grating_z: float = -0.0012
    indicator_grating_z: float = 0.0012
    grating_gap: float = 0.0009
    main_grating_rotation: float = 0.0
    indicator_grating_rotation: float = 0.0
    main_grating_axial_shift: float = 0.0
    indicator_grating_axial_shift: float = 0.0
    fixing_chamber_outer_radius: float = 0.0125
    fixing_chamber_inner_radius: float = 0.0105
    fixing_chamber_height: float = 0.0030
    connection_collar_radius: float = 0.0060
    connection_collar_height: float = 0.0030
    light_source_radius: float = 0.0012
    light_source_z: float = -0.0090
    condenser_radius: float = 0.0030
    condenser_thickness: float = 0.0010
    condenser_z: float = -0.0065
    sensor_radius: float = 0.00055
    sensor_height: float = 0.0010
    sensor_ring_radius: float = 0.0070
    sensor_plane_z: float = 0.0080
    torque: float = 0.0
    rotation_angle: float = 0.0
    grating_displacement: float = 0.0
    temperature: float = 20.0
    temperature_reference: float = 20.0
    shear_modulus_temperature_coeff: float = -3.0e-4
    grating_period_temperature_coeff: float = 1.2e-5
    # Visualization only. Physical calculations always use the true angle.
    visual_torsion_scale: float = 80.0
    serial_port: str = "COM5"
    serial_baud_rate: int = 115200
    serial_send_rate: float = 500.0

    def validate(self) -> "TorqueSensorParameters":
        positive = ("housing_length", "housing_radius", "wall_thickness", "flange_radius", "flange_thickness", "bolt_circle_radius", "shaft_radius", "shaft_length", "elastic_length", "elastic_width", "elastic_thickness", "torsion_length", "shear_modulus", "torsion_diameter", "effective_detection_radius", "torsional_stiffness", "disk_radius", "disk_thickness", "grating_period", "grating_gap", "fixing_chamber_outer_radius", "fixing_chamber_inner_radius", "fixing_chamber_height", "connection_collar_radius", "connection_collar_height", "light_source_radius", "condenser_radius", "condenser_thickness", "sensor_radius", "sensor_height", "sensor_ring_radius", "visual_torsion_scale")
        for name in positive:
            if float(getattr(self, name)) <= 0:
                raise ValueError(f"{name} must be positive")
        if self.wall_thickness >= self.housing_radius:
            raise ValueError("wall_thickness must be smaller than housing_radius")
        if self.bolt_number < 3 or int(self.bolt_number) != self.bolt_number:
            raise ValueError("bolt_number must be an integer >= 3")
        if self.line_number < 1 or int(self.line_number) != self.line_number:
            raise ValueError("line_number must be a positive integer")
        if self.fixing_chamber_inner_radius >= self.fixing_chamber_outer_radius:
            raise ValueError("fixing_chamber_inner_radius must be smaller than fixing_chamber_outer_radius")
        if self.disk_radius >= self.fixing_chamber_inner_radius:
            raise ValueError("disk_radius must be smaller than fixing_chamber_inner_radius")
        if self.sensor_ring_radius >= self.disk_radius:
            raise ValueError("sensor_ring_radius must lie inside the grating radius")
        if self.mechanical_parameter_source != "simulation/default":
            raise ValueError("unverified Stage-12 mechanics must remain marked simulation/default")
        if not self.serial_port:
            raise ValueError("serial_port must not be empty")
        if int(self.serial_baud_rate) <= 0:
            raise ValueError("serial_baud_rate must be positive")
        max_frame_rate = float(self.serial_baud_rate) / 110.0
        if not 0 < float(self.serial_send_rate) <= max_frame_rate:
            raise ValueError("serial_send_rate exceeds the 11-byte 8N1 baud-rate limit")
        return self

    @property
    def torque_angle(self) -> float:
        from ..mechanics.torque_model import calculate_torque_state
        return float(calculate_torque_state(
            torque=self.torque,
            torsion_length=self.torsion_length,
            shear_modulus=self.shear_modulus,
            shaft_diameter=self.torsion_diameter,
            grating_radius=self.effective_detection_radius,
            grating_period=self.grating_period,
            phase_zero=self.optical_phase_zero,
            parameter_source=self.mechanical_parameter_source,
        )["torsion_angle"])

    @property
    def effective_angle(self) -> float:
        return self.rotation_angle if self.rotation_angle != 0 else self.torque_angle

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "TorqueSensorParameters":
        data = cls().to_dict()
        data.update(dict(values))
        return cls(**data).validate()


def parameter() -> TorqueSensorParameters:
    return TorqueSensorParameters().validate()
