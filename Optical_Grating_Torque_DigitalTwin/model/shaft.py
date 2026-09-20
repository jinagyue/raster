"""Parametric central shaft VTK solid."""
from __future__ import annotations

import vtk


def build_shaft(p, angle: float = 0.0) -> vtk.vtkPolyData:
    src = vtk.vtkCylinderSource()
    src.SetRadius(p.shaft_radius)
    src.SetHeight(p.shaft_length)
    src.SetResolution(64)
    src.CappingOn()
    src.Update()
    # The axis is z; a z-axis rotation carries the optical disk orientation.
    transform = vtk.vtkTransform()
    # CylinderSource is aligned with the y-axis. Rotate it once to the
    # housing z-axis; a rotation about z must not change the shaft axis.
    # The scalar ``angle`` is retained by the assembly/controller and is
    # applied to the asymmetric optical disk/elastic element instead.
    transform.RotateX(90.0)
    filt = vtk.vtkTransformPolyDataFilter()
    filt.SetTransform(transform)
    filt.SetInputConnection(src.GetOutputPort())
    filt.Update()
    return filt.GetOutput()
