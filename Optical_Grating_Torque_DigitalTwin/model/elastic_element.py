"""Thin-walled elastic torsion beam."""
from __future__ import annotations

import vtk


def build_elastic_element(p, angle: float = 0.0) -> vtk.vtkPolyData:
    src = vtk.vtkCubeSource()
    src.SetXLength(p.elastic_width); src.SetYLength(p.elastic_length); src.SetZLength(p.elastic_thickness)
    src.SetCenter(0, 0, 0); src.Update()
    transform = vtk.vtkTransform(); transform.RotateZ(float(angle) * 180.0 / 3.141592653589793)
    filt = vtk.vtkTransformPolyDataFilter(); filt.SetTransform(transform); filt.SetInputData(src.GetOutput()); filt.Update()
    return filt.GetOutput()
