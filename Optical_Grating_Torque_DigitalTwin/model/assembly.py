"""Assemble the Stage-11 patent mechanical structure."""
from __future__ import annotations

from typing import Any

from .elastic_element import build_elastic_element
from .flange import build_flange
from .housing import build_housing
from .patent_structure import (
    build_connection_collars,
    build_five_sensor_positions,
    build_fixing_chamber,
    build_grating,
    build_light_path,
)
from .shaft import build_shaft
import vtk


def _translate(poly, dz):
    if not isinstance(poly, vtk.vtkPolyData) or dz == 0: return poly
    transform = vtk.vtkTransform(); transform.Translate(0, 0, dz)
    filt = vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(poly); filt.Update(); return filt.GetOutput()


def _explode(value, dz):
    if isinstance(value, vtk.vtkPolyData): return _translate(value, dz)
    if isinstance(value, dict): return {k: _explode(v, dz) if isinstance(v, (vtk.vtkPolyData, dict)) else v for k, v in value.items()}
    return value


def build_assembly(p, exploded: float = 0.0, angle: float | None = None) -> dict[str, Any]:
    """Return independently addressable patent components.

    The assembly axis is global z.  Gratings remain separate dictionaries so
    the VTK layer can rotate or translate either actor group independently.
    """
    angle = p.effective_angle if angle is None else float(angle)
    zoff = float(exploded)
    front_cover = build_flange(p, "left")
    rear_cover = build_flange(p, "right")
    light_path = build_light_path(p)
    assembly = {
        "housing": build_housing(p),
        "shaft": build_shaft(p, angle),
        "elastic_element": build_elastic_element(p, angle),
        "front_fixed_cover": front_cover,
        "rear_fixed_cover": rear_cover,
        "main_grating_fixing_chamber": build_fixing_chamber(p, "main"),
        "indicator_grating_fixing_chamber": build_fixing_chamber(p, "indicator"),
        "main_grating": build_grating(p, "main", rotation_offset=angle),
        "indicator_grating": build_grating(p, "indicator"),
        "light_source": light_path["light_source"],
        "condenser_lens": light_path["condenser_lens"],
        "grating_sensors": build_five_sensor_positions(p),
        "connection_structure": build_connection_collars(p),
        "angle": angle,
        "exploded": zoff,
    }
    if zoff:
        assembly["front_fixed_cover"] = _explode(assembly["front_fixed_cover"], -zoff)
        assembly["rear_fixed_cover"] = _explode(assembly["rear_fixed_cover"], zoff)
    return assembly
