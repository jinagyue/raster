"""End flanges and visible bolt-hole inserts."""
from __future__ import annotations

import math
import vtk


def _disk(p, z: float) -> vtk.vtkPolyData:
    src = vtk.vtkCylinderSource()
    src.SetRadius(p.flange_radius); src.SetHeight(p.flange_thickness); src.SetResolution(96); src.CappingOn(); src.Update()
    transform=vtk.vtkTransform(); transform.PostMultiply(); transform.RotateX(90); transform.Translate(0,0,z)
    filt=vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(src.GetOutput()); filt.Update(); return filt.GetOutput()


def _hole_markers(p, z: float) -> vtk.vtkPolyData:
    append = vtk.vtkAppendPolyData()
    for k in range(p.bolt_number):
        a = 2 * math.pi * k / p.bolt_number
        src = vtk.vtkCylinderSource()
        src.SetRadius(0.0012); src.SetHeight(p.flange_thickness * 1.2); src.SetResolution(24)
        src.CappingOn(); src.Update()
        transform=vtk.vtkTransform(); transform.PostMultiply(); transform.RotateX(90); transform.Translate(p.bolt_circle_radius * math.cos(a), p.bolt_circle_radius * math.sin(a), z)
        filt=vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(src.GetOutput()); filt.Update(); append.AddInputData(filt.GetOutput())
    append.Update(); return append.GetOutput()


def build_flange(p, side: str) -> dict[str, vtk.vtkPolyData]:
    if side not in ("left", "right"):
        raise ValueError("side must be left or right")
    z = (-1 if side == "left" else 1) * (p.housing_length / 2 + p.flange_thickness / 2)
    return {"body": _disk(p, z), "bolt_holes": _hole_markers(p, z), "side": side}
