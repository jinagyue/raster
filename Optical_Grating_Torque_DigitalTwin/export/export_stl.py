"""Export VTK component solids to STL files."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import vtk


def _write(poly: vtk.vtkPolyData, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkSTLWriter(); writer.SetFileName(str(path)); writer.SetInputData(poly); writer.Write(); return path


def export_assembly_stl(assembly: dict[str, Any], output_dir: str | Path) -> list[Path]:
    out = Path(output_dir); written: list[Path] = []; append = vtk.vtkAppendPolyData()
    for name, value in assembly.items():
        if isinstance(value, vtk.vtkPolyData):
            written.append(_write(value, out / f"{name}.stl")); append.AddInputData(value)
        elif isinstance(value, dict):
            for sub, poly in value.items():
                if isinstance(poly, vtk.vtkPolyData):
                    written.append(_write(poly, out / f"{name}_{sub}.stl")); append.AddInputData(poly)
    append.Update()
    if append.GetOutput().GetNumberOfPoints() > 0:
        written.append(_write(append.GetOutput(), out / "assembly.stl"))
    return written
