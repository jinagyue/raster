"""Independent acceptance for the Stage-11 patent mechanical model.

This test intentionally does not start MATLAB and does not exercise torque or
signal algorithms.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

import vtk
from PyQt5 import QtWidgets

from Optical_Grating_Torque_DigitalTwin.config.parameter import TorqueSensorParameters, parameter
from Optical_Grating_Torque_DigitalTwin.control.torque_controller import TorqueController
from Optical_Grating_Torque_DigitalTwin.gui.main_window import MainWindow
from Optical_Grating_Torque_DigitalTwin.gui.vtk_widget import VTKWidget
from Optical_Grating_Torque_DigitalTwin.model.assembly import build_assembly


REQUIRED_COMPONENTS = (
    "shaft",
    "housing",
    "front_fixed_cover",
    "rear_fixed_cover",
    "main_grating_fixing_chamber",
    "indicator_grating_fixing_chamber",
    "main_grating",
    "indicator_grating",
    "light_source",
    "condenser_lens",
    "grating_sensors",
    "connection_structure",
)
REQUIRED_SENSORS = ("zero", "main", "direction_1", "direction_2", "direction_3")
EXPECTED_ACTOR_COUNT = 24


def _has_geometry(value) -> bool:
    if isinstance(value, vtk.vtkPolyData):
        return value.GetNumberOfPoints() > 0
    if isinstance(value, dict):
        geometry = [item for item in value.values() if isinstance(item, (vtk.vtkPolyData, dict))]
        return bool(geometry) and all(_has_geometry(item) for item in geometry)
    return True


def run_acceptance() -> dict[str, object]:
    report: dict[str, object] = {
        "pass_components": False,
        "pass_actor_count": False,
        "pass_assembly_relationship": False,
        "pass_parameters": False,
        "pass_independent_transform": False,
        "pass_gui": False,
        "pass": False,
    }
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    widget = None
    window = None
    try:
        p = parameter()
        assembly = build_assembly(p)
        components_present = all(name in assembly for name in REQUIRED_COMPONENTS)
        sensors_present = tuple(assembly["grating_sensors"].keys()) == REQUIRED_SENSORS
        geometry_valid = all(_has_geometry(assembly[name]) for name in REQUIRED_COMPONENTS)
        report["pass_components"] = bool(components_present and sensors_present and geometry_valid)
        report["component_count"] = len(REQUIRED_COMPONENTS)
        report["sensor_names"] = list(assembly["grating_sensors"].keys())

        housing_bounds = assembly["housing"].GetBounds()
        shaft_bounds = assembly["shaft"].GetBounds()
        front_bounds = assembly["front_fixed_cover"]["body"].GetBounds()
        rear_bounds = assembly["rear_fixed_cover"]["body"].GetBounds()
        source_z = p.light_source_z
        lens_z = p.condenser_z
        main_z = float(assembly["main_grating"]["center_z"])
        indicator_z0 = float(assembly["indicator_grating"]["center_z"])
        sensor_z = p.sensor_plane_z
        actual_gap = indicator_z0 - main_z - p.disk_thickness
        report["pass_assembly_relationship"] = bool(
            shaft_bounds[4] < housing_bounds[4]
            and shaft_bounds[5] > housing_bounds[5]
            and front_bounds[5] <= housing_bounds[4] + 1e-12
            and rear_bounds[4] >= housing_bounds[5] - 1e-12
            and source_z < lens_z < main_z < indicator_z0 < sensor_z
            and abs(actual_gap - p.grating_gap) < 1e-12
        )

        modified = TorqueSensorParameters.from_mapping({
            **p.to_dict(),
            "housing_radius": p.housing_radius + 0.001,
            "indicator_grating_z": p.indicator_grating_z + 0.0004,
            "sensor_ring_radius": p.sensor_ring_radius - 0.0003,
        })
        modified_assembly = build_assembly(modified)
        original_bounds = assembly["housing"].GetBounds()
        modified_bounds = modified_assembly["housing"].GetBounds()
        indicator_z = float(modified_assembly["indicator_grating"]["center_z"])
        report["pass_parameters"] = bool(
            modified_bounds[1] > original_bounds[1]
            and abs(indicator_z - modified.indicator_grating_z) < 1e-12
            and modified.sensor_ring_radius != p.sensor_ring_radius
        )

        widget = VTKWidget()
        widget.set_assembly(assembly)
        actor_names = widget.actor_names()
        report["actor_count"] = len(actor_names)
        report["pass_actor_count"] = bool(
            len(actor_names) == EXPECTED_ACTOR_COUNT
            and any(name.startswith("assembly/main_grating/") for name in actor_names)
            and any(name.startswith("assembly/indicator_grating/") for name in actor_names)
        )

        main_actors = [actor for name, actor in widget.actors.items() if name.startswith("assembly/main_grating/")]
        indicator_actors = [actor for name, actor in widget.actors.items() if name.startswith("assembly/indicator_grating/")]
        indicator_before = [(actor.GetOrientation(), actor.GetPosition()) for actor in indicator_actors]
        widget.transform_grating("main", 17.5, 0.0007)
        main_changed = all(abs(actor.GetOrientation()[2] - 17.5) < 1e-9 and abs(actor.GetPosition()[2] - 0.0007) < 1e-12 for actor in main_actors)
        indicator_unchanged = indicator_before == [(actor.GetOrientation(), actor.GetPosition()) for actor in indicator_actors]
        main_after = [(actor.GetOrientation(), actor.GetPosition()) for actor in main_actors]
        widget.transform_grating("indicator", -8.0, -0.0003)
        indicator_changed = all(abs(actor.GetOrientation()[2] + 8.0) < 1e-9 and abs(actor.GetPosition()[2] + 0.0003) < 1e-12 for actor in indicator_actors)
        main_unchanged = main_after == [(actor.GetOrientation(), actor.GetPosition()) for actor in main_actors]
        report["pass_independent_transform"] = bool(main_changed and indicator_unchanged and indicator_changed and main_unchanged)

        window = MainWindow(TorqueController(p, None), mechanical_only=True)
        window.show()
        app.processEvents()
        report["pass_gui"] = bool(
            window.isVisible()
            and len(window.vtk.actors) == EXPECTED_ACTOR_COUNT
            and "Stage 11" in window.windowTitle()
        )
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if window is not None:
            window.close()
        if widget is not None:
            widget.close()
        app.processEvents()

    report["pass"] = all(bool(report[key]) for key in (
        "pass_components",
        "pass_actor_count",
        "pass_assembly_relationship",
        "pass_parameters",
        "pass_independent_transform",
        "pass_gui",
    ))
    return report


if __name__ == "__main__":
    result = run_acceptance()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["pass"] else 1)
