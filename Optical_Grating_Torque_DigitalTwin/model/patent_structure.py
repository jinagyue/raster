"""Patent-inspired parametric mechanical and optical component builders.

The dimensions are simulation defaults.  The topology follows the axial
assembly relationship in the patent, but is intentionally not machining CAD.
"""
from __future__ import annotations

import math
import vtk


def _transform(poly: vtk.vtkPolyData, *, z: float = 0.0, angle: float = 0.0) -> vtk.vtkPolyData:
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.RotateZ(math.degrees(float(angle)))
    transform.Translate(0.0, 0.0, float(z))
    filt = vtk.vtkTransformPolyDataFilter()
    filt.SetTransform(transform)
    filt.SetInputData(poly)
    filt.Update()
    return filt.GetOutput()


def _solid_cylinder(radius: float, height: float, z: float, resolution: int = 96) -> vtk.vtkPolyData:
    src = vtk.vtkCylinderSource()
    src.SetRadius(float(radius))
    src.SetHeight(float(height))
    src.SetResolution(int(resolution))
    src.CappingOn()
    src.Update()
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.RotateX(90.0)
    transform.Translate(0.0, 0.0, float(z))
    filt = vtk.vtkTransformPolyDataFilter()
    filt.SetTransform(transform)
    filt.SetInputData(src.GetOutput())
    filt.Update()
    return filt.GetOutput()


def _annular_solid(inner_radius: float, outer_radius: float, height: float, z: float, resolution: int = 128) -> vtk.vtkPolyData:
    """Create a closed annular solid without fragile boolean operations."""
    n = int(resolution)
    z0, z1 = z - height / 2.0, z + height / 2.0
    points = vtk.vtkPoints()
    for radius, zz in ((outer_radius, z0), (outer_radius, z1), (inner_radius, z0), (inner_radius, z1)):
        for k in range(n):
            a = 2.0 * math.pi * k / n
            points.InsertNextPoint(radius * math.cos(a), radius * math.sin(a), zz)
    polys = vtk.vtkCellArray()

    def quad(a: int, b: int, c: int, d: int) -> None:
        cell = vtk.vtkQuad()
        for index, point_id in enumerate((a, b, c, d)):
            cell.GetPointIds().SetId(index, point_id)
        polys.InsertNextCell(cell)

    for k in range(n):
        j = (k + 1) % n
        quad(k, j, n + j, n + k)                              # outer wall
        quad(2 * n + k, 3 * n + k, 3 * n + j, 2 * n + j)    # inner wall
        quad(n + k, n + j, 3 * n + j, 3 * n + k)            # top face
        quad(k, 2 * n + k, 2 * n + j, j)                    # bottom face
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(polys)
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(poly)
    clean.Update()
    return clean.GetOutput()


def _grating_grooves(p, z: float, angle: float, phase_fraction: float) -> vtk.vtkPolyData:
    append = vtk.vtkAppendPolyData()
    maximum = min(int(p.line_number), int(p.disk_radius / p.grating_period))
    visible = max(1, min(maximum, 420))
    groove_radius = max(min(p.grating_period * 0.13, p.disk_thickness * 0.035), 0.5e-6)
    phase_shift = phase_fraction * p.grating_period
    for k in range(1, visible + 1):
        ring_radius = k * p.grating_period + phase_shift
        if ring_radius >= p.disk_radius * 0.98:
            break
        torus = vtk.vtkParametricTorus()
        torus.SetRingRadius(ring_radius)
        torus.SetCrossSectionRadius(groove_radius)
        src = vtk.vtkParametricFunctionSource()
        src.SetParametricFunction(torus)
        src.SetUResolution(30)
        src.SetVResolution(6)
        src.Update()
        append.AddInputData(_transform(src.GetOutput(), z=z + p.disk_thickness / 2.0, angle=angle))
    append.Update()
    return append.GetOutput()


def _orientation_mark(p, z: float, angle: float) -> vtk.vtkPolyData:
    src = vtk.vtkCubeSource()
    src.SetXLength(p.disk_radius * 0.58)
    src.SetYLength(max(p.grating_period * 8.0, 0.00025))
    src.SetZLength(p.disk_thickness * 0.12)
    src.SetCenter(p.disk_radius * 0.33, 0.0, 0.0)
    src.Update()
    return _transform(src.GetOutput(), z=z + p.disk_thickness * 0.56, angle=angle)


def build_grating(p, kind: str, rotation_offset: float = 0.0) -> dict[str, object]:
    if kind not in ("main", "indicator"):
        raise ValueError("kind must be 'main' or 'indicator'")
    if kind == "main":
        z = p.main_grating_z + p.main_grating_axial_shift
        angle = p.main_grating_rotation + float(rotation_offset)
        phase_fraction = 0.0
    else:
        z = p.indicator_grating_z + p.indicator_grating_axial_shift
        angle = p.indicator_grating_rotation
        phase_fraction = 0.5
    return {
        "body": _solid_cylinder(p.disk_radius, p.disk_thickness, z, 128),
        "grooves": _grating_grooves(p, z, angle, phase_fraction),
        "orientation_mark": _orientation_mark(p, z, angle),
        "center_z": z,
        "rotation": angle,
        "kind": kind,
    }


def build_fixing_chamber(p, kind: str) -> vtk.vtkPolyData:
    if kind == "main":
        z = p.main_grating_z - (p.disk_thickness + p.fixing_chamber_height) / 2.0
    elif kind == "indicator":
        z = p.indicator_grating_z + (p.disk_thickness + p.fixing_chamber_height) / 2.0
    else:
        raise ValueError("kind must be 'main' or 'indicator'")
    return _annular_solid(
        p.fixing_chamber_inner_radius,
        p.fixing_chamber_outer_radius,
        p.fixing_chamber_height,
        z,
    )


def build_connection_collars(p) -> dict[str, vtk.vtkPolyData]:
    offset = p.fixing_chamber_height + p.disk_thickness
    return {
        "front_shaft_collar": _annular_solid(
            p.shaft_radius * 1.03,
            p.connection_collar_radius,
            p.connection_collar_height,
            p.main_grating_z - offset,
            64,
        ),
        "rear_shaft_collar": _annular_solid(
            p.shaft_radius * 1.03,
            p.connection_collar_radius,
            p.connection_collar_height,
            p.indicator_grating_z + offset,
            64,
        ),
    }


def build_light_path(p) -> dict[str, vtk.vtkPolyData]:
    light = vtk.vtkSphereSource()
    light.SetRadius(p.light_source_radius)
    light.SetCenter(0.0, 0.0, p.light_source_z)
    light.SetThetaResolution(36)
    light.SetPhiResolution(24)
    light.Update()
    lens = _solid_cylinder(p.condenser_radius, p.condenser_thickness, p.condenser_z, 72)
    return {"light_source": light.GetOutput(), "condenser_lens": lens}


def build_five_sensor_positions(p) -> dict[str, vtk.vtkPolyData]:
    # Zero reference is offset from the four quadrature read heads so it is
    # separately visible and pickable in the mechanical review model.
    angles = {
        "zero": math.radians(35.0),
        "main": 0.0,
        "direction_1": math.pi / 2.0,
        "direction_2": math.pi,
        "direction_3": 3.0 * math.pi / 2.0,
    }
    sensors: dict[str, vtk.vtkPolyData] = {}
    for name, angle in angles.items():
        radius = p.sensor_ring_radius * (0.72 if name == "zero" else 1.0)
        center = (radius * math.cos(angle), radius * math.sin(angle), p.sensor_plane_z)
        src = vtk.vtkCylinderSource()
        src.SetRadius(p.sensor_radius)
        src.SetHeight(p.sensor_height)
        src.SetResolution(32)
        src.CappingOn()
        src.Update()
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        transform.RotateX(90.0)
        transform.Translate(*center)
        filt = vtk.vtkTransformPolyDataFilter()
        filt.SetTransform(transform)
        filt.SetInputData(src.GetOutput())
        filt.Update()
        sensors[name] = filt.GetOutput()
    return sensors
