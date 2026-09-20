"""Solid optical disk with concentric three-dimensional grating ridges."""
from __future__ import annotations

import math
import vtk


def _disk(radius: float, thickness: float, z: float) -> vtk.vtkPolyData:
    src = vtk.vtkCylinderSource(); src.SetRadius(radius); src.SetHeight(thickness); src.SetResolution(128); src.CappingOn(); src.Update()
    transform = vtk.vtkTransform(); transform.PostMultiply(); transform.RotateX(90); transform.Translate(0, 0, z)
    filt = vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(src.GetOutput()); filt.Update(); return filt.GetOutput()


def build_grating_disk(p, angle: float = 0.0) -> dict[str, object]:
    disk_z = p.elastic_thickness / 2 + p.disk_thickness / 2 + 0.0005
    disk = _disk(p.disk_radius, p.disk_thickness, disk_z)
    rings = vtk.vtkAppendPolyData()
    physical_count = min(int(p.line_number), int(p.disk_radius / p.grating_period))
    visible_count = max(1, min(physical_count, 600))
    ridge_radius = max(min(p.grating_period * 0.12, p.disk_thickness * 0.04), 0.5e-6)
    for k in range(1, visible_count + 1):
        torus = vtk.vtkParametricTorus(); torus.SetRingRadius(k * p.grating_period); torus.SetCrossSectionRadius(ridge_radius)
        src = vtk.vtkParametricFunctionSource(); src.SetParametricFunction(torus); src.SetUResolution(36); src.SetVResolution(6); src.Update()
        transform = vtk.vtkTransform(); transform.PostMultiply(); transform.RotateZ(float(angle) * 180.0 / math.pi); transform.Translate(0, 0, disk_z + p.disk_thickness / 2)
        filt = vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(src.GetOutput()); filt.Update(); rings.AddInputData(filt.GetOutput())
    rings.Update()
    return {"disk": disk, "grooves": rings.GetOutput(), "center_z": disk_z,
            "physical_period": p.grating_period, "displayed_ring_count": visible_count}
