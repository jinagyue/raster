"""Optical source, condenser and five-sensor readout assembly."""
from __future__ import annotations

import math
import vtk


def _source(kind: str, radius: float, height: float, center: tuple[float, float, float], resolution: int = 32) -> vtk.vtkPolyData:
    if kind == "sphere":
        src = vtk.vtkSphereSource(); src.SetRadius(radius); src.SetThetaResolution(resolution); src.SetPhiResolution(resolution)
    else:
        src = vtk.vtkCylinderSource(); src.SetRadius(radius); src.SetHeight(height); src.SetResolution(resolution); src.CappingOn()
    if kind == "sphere":
        src.SetCenter(*center); src.Update(); return src.GetOutput()
    src.Update()
    transform=vtk.vtkTransform(); transform.PostMultiply(); transform.RotateX(90); transform.Translate(*center)
    filt=vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(src.GetOutput()); filt.Update(); return filt.GetOutput()


def _translated(poly: vtk.vtkPolyData, translation: tuple[float, float, float]) -> vtk.vtkPolyData:
    transform = vtk.vtkTransform(); transform.Translate(*translation)
    filt = vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(poly); filt.Update(); return filt.GetOutput()


def build_optical_readout(p, angle: float = 0.0) -> dict[str, object]:
    """Return the patent-referenced source/lens/grating/sensor components."""
    z = p.elastic_thickness / 2 + p.disk_thickness + 0.0005
    fixed = _source("cylinder", p.disk_radius * 1.18, 0.0025, (0, 0, z + 0.0015))
    indicator = _source("cylinder", p.disk_radius * 1.10, 0.0020, (0, 0, z + 0.0045))
    light = _source("sphere", 0.0012, 0.0, (0, 0, z + 0.006))
    lens = _source("cylinder", 0.0020, 0.0008, (0, 0, z + 0.0075))
    sensors = vtk.vtkAppendPolyData()
    sensor_radius = 0.00035
    for k, phi in enumerate((0, math.pi / 2, math.pi, 3 * math.pi / 2, 0)):
        # Four quadrature sensors plus a zero-position sensor around the disk.
        a = phi if k < 4 else 0.0
        sensor = _source("cylinder", sensor_radius, 0.0006, (p.disk_radius * 1.25 * math.cos(a), p.disk_radius * 1.25 * math.sin(a), z + 0.0085), 20)
        sensors.AddInputData(sensor)
    sensors.Update()
    temperature = _source("cylinder", 0.00045, 0.001, (p.housing_radius * 0.7, 0, 0), 20)
    return {"main_grating_housing": fixed, "indicator_grating_housing": indicator,
            "light_source": light, "condenser_lens": lens,
            "sensor_array": sensors.GetOutput(), "temperature_sensor": temperature,
            "reference": "patent-inspired optical readout; dimensions are configurable defaults"}
