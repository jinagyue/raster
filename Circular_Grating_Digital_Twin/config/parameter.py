"""Parameter registry for the Python-MATLAB circular-grating twin."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
import json


@dataclass(frozen=True)
class CircularGratingParameters:
    radius: float = 1e-3
    period: float = 20e-6
    ring_number: int = 50
    groove_height: float = 1e-6
    base_thickness: float = 0.2e-3
    radial_points: int = 100
    angular_points: int = 144
    main_shift: tuple[float, float, float] = (0.0, 0.0, 0.0)
    reference_shift: tuple[float, float, float] = (5e-6, 0.0, 0.0)
    reference_rotation: float = 0.0

    def validate(self) -> "CircularGratingParameters":
        if self.radius <= 0 or self.period <= 0:
            raise ValueError("radius and period must be positive")
        if self.ring_number < 1 or self.radial_points < 2 or self.angular_points < 8:
            raise ValueError("ring_number/radial_points/angular_points are too small")
        if self.groove_height < 0 or self.base_thickness <= 0:
            raise ValueError("groove_height must be non-negative and base_thickness positive")
        if len(self.main_shift) != 3 or len(self.reference_shift) != 3:
            raise ValueError("main_shift and reference_shift must be 3-vectors")
        return self

    @property
    def relative_shift(self) -> tuple[float, float, float]:
        return tuple(b - a for a, b in zip(self.main_shift, self.reference_shift))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save_json(self, path: str | Path) -> Path:
        self.validate()
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return output

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "CircularGratingParameters":
        data = cls().to_dict()
        data.update(dict(values))
        for key in ("main_shift", "reference_shift"):
            data[key] = tuple(data[key])
        return cls(**data).validate()


def parameter() -> CircularGratingParameters:
    return CircularGratingParameters().validate()
