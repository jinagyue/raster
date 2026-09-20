"""Closed concentric-ring grating mesh generation.

The geometry is generated with a polar disk parameterization. The top surface
uses z(r)=H/2*(1+cos(2*pi*r/P)) above a finite base thickness. Top, bottom and
outer-wall triangles form a closed triangular surface; radial facets represent
the groove side walls without relying on a CAD kernel.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import math

import numpy as np

from ..config.parameter import CircularGratingParameters


@dataclass(frozen=True)
class MeshData:
    """Triangular surface mesh with deterministic topology diagnostics."""

    vertices: np.ndarray
    faces: np.ndarray
    name: str = "circular_grating"

    @property
    def volume(self) -> float:
        tri = self.vertices[self.faces]
        return float(abs(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum()) / 6.0)

    @property
    def is_watertight(self) -> bool:
        if self.faces.ndim != 2 or self.faces.shape[1] != 3:
            return False
        if np.any(self.faces[:, 0] == self.faces[:, 1]) or np.any(self.faces[:, 1] == self.faces[:, 2]) or np.any(self.faces[:, 0] == self.faces[:, 2]):
            return False
        edges = np.concatenate((self.faces[:, [0, 1]], self.faces[:, [1, 2]], self.faces[:, [2, 0]]), axis=0)
        edges.sort(axis=1)
        _, counts = np.unique(edges, axis=0, return_counts=True)
        return bool(np.all(counts == 2))

    def to_trimesh(self) -> Any:
        """Return a Trimesh object when the optional dependency is installed."""
        try:
            import trimesh
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install trimesh to use MeshData.to_trimesh().") from exc
        return trimesh.Trimesh(vertices=self.vertices, faces=self.faces, process=False)


def _coerce_parameters(parameters: CircularGratingParameters | Mapping[str, Any]) -> CircularGratingParameters:
    if isinstance(parameters, CircularGratingParameters):
        return parameters.validate()
    return CircularGratingParameters.from_mapping(parameters)


def build_circular_grating(
    parameters: CircularGratingParameters | Mapping[str, Any],
    shift: tuple[float, float, float] | None = None,
    name: str = "circular_grating",
) -> MeshData:
    """Build a watertight concentric-ring grating mesh.

    Parameters use SI units. ``ring_number`` is retained as a physical design
    control/metadata field; the sampled cosine surface is governed directly by
    ``radius`` and ``period`` so all three controls can be varied independently.
    """
    p = _coerce_parameters(parameters)
    shift_vec = np.asarray(p.main_shift if shift is None else shift, dtype=float)
    if shift_vec.shape != (3,):
        raise ValueError("shift must be a three-element vector")
    radial = max(2, int(p.radial_points))
    angular = max(8, int(p.angular_points))
    r = np.linspace(0.0, p.radius, radial)
    angle = np.linspace(0.0, 2.0 * math.pi, angular, endpoint=False)
    z_r = p.base_thickness + 0.5 * p.groove_height * (1.0 + np.cos(2.0 * math.pi * r / p.period))

    vertices: list[list[float]] = []
    faces: list[tuple[int, int, int]] = []
    top_center = 0
    vertices.append([0.0, 0.0, float(z_r[0])])
    top_starts: list[int] = []
    for i in range(1, radial):
        top_starts.append(len(vertices))
        for a in angle:
            vertices.append([float(r[i] * math.cos(a)), float(r[i] * math.sin(a)), float(z_r[i])])

    bottom_center = len(vertices)
    vertices.append([0.0, 0.0, 0.0])
    bottom_starts: list[int] = []
    for i in range(1, radial):
        bottom_starts.append(len(vertices))
        for a in angle:
            vertices.append([float(r[i] * math.cos(a)), float(r[i] * math.sin(a)), 0.0])

    # Top center fan and top annular facets.
    for j in range(angular):
        jn = (j + 1) % angular
        faces.append((top_center, top_starts[0] + j, top_starts[0] + jn))
    for i in range(len(top_starts) - 1):
        current, nxt = top_starts[i], top_starts[i + 1]
        for j in range(angular):
            jn = (j + 1) % angular
            a, b, c, d = current + j, nxt + j, nxt + jn, current + jn
            faces.extend(((a, b, c), (a, c, d)))

    # Bottom disk, opposite winding to the top.
    for j in range(angular):
        jn = (j + 1) % angular
        faces.append((bottom_center, bottom_starts[0] + jn, bottom_starts[0] + j))
    for i in range(len(bottom_starts) - 1):
        current, nxt = bottom_starts[i], bottom_starts[i + 1]
        for j in range(angular):
            jn = (j + 1) % angular
            a, b, c, d = current + j, current + jn, nxt + jn, nxt + j
            faces.extend(((a, b, c), (a, c, d)))

    # Outer cylindrical wall closes the solid and exposes the base thickness.
    top_outer, bottom_outer = top_starts[-1], bottom_starts[-1]
    for j in range(angular):
        jn = (j + 1) % angular
        a, b, c, d = top_outer + j, bottom_outer + j, bottom_outer + jn, top_outer + jn
        faces.extend(((a, b, c), (a, c, d)))

    v = np.asarray(vertices, dtype=float) + shift_vec.reshape(1, 3)
    f = np.asarray(faces, dtype=np.int64)
    return MeshData(vertices=v, faces=f, name=name)


def build_assembly(parameters: CircularGratingParameters | Mapping[str, Any]) -> dict[str, MeshData]:
    """Build translated main and reference circular gratings."""
    p = _coerce_parameters(parameters)
    main = build_circular_grating(p, p.main_shift, "main_grating")
    reference = build_circular_grating(p, p.reference_shift, "reference_grating")
    return {"main_grating": main, "reference_grating": reference}
