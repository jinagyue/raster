"""Main/reference circular-grating assembly adapter."""
from __future__ import annotations

from typing import Any, Mapping

from ..config.parameter import CircularGratingParameters
from .circular_grating import MeshData, build_assembly

__all__ = ["MeshData", "build_assembly", "build_pair"]


def build_pair(parameters: CircularGratingParameters | Mapping[str, Any]) -> dict[str, MeshData]:
    """Return named main and reference meshes for a parameter set."""
    return build_assembly(parameters)
