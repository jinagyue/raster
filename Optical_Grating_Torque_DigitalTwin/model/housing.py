"""Explicit watertight cylindrical measurement-cavity shell."""
from __future__ import annotations

import math
import vtk


def build_housing(p) -> vtk.vtkPolyData:
    n = 96
    ro, ri = p.housing_radius, p.housing_radius - p.wall_thickness
    z0, z1 = -p.housing_length / 2, p.housing_length / 2
    points = vtk.vtkPoints()
    for radius, z in ((ro, z0), (ro, z1), (ri, z0), (ri, z1)):
        for k in range(n):
            a = 2 * math.pi * k / n
            points.InsertNextPoint(radius * math.cos(a), radius * math.sin(a), z)
    polys = vtk.vtkCellArray()

    def quad(a: int, b: int, c: int, d: int) -> None:
        cell = vtk.vtkQuad()
        for index, value in enumerate((a, b, c, d)):
            cell.GetPointIds().SetId(index, value)
        polys.InsertNextCell(cell)

    for k in range(n):
        j = (k + 1) % n
        quad(k, j, n + j, n + k)
        quad(2 * n + k, 3 * n + k, 3 * n + j, 2 * n + j)
        quad(k, 2 * n + k, 2 * n + j, j)
        quad(n + k, n + j, 3 * n + j, 3 * n + k)
    poly = vtk.vtkPolyData(); poly.SetPoints(points); poly.SetPolys(polys)
    clean = vtk.vtkCleanPolyData(); clean.SetInputData(poly); clean.Update()
    return clean.GetOutput()
