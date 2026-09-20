"""VTK rendering widget used by the PyQt5 main window."""
from __future__ import annotations

from typing import Any

from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import os

# On Windows, VTK creates a separate ``vtkOutputWindow`` whenever a warning
# is emitted.  In a PyQt application that native window is often blank and
# looks like a second application.  Capture diagnostics in memory instead;
# application exceptions are still reported by the normal Python/Qt path.
_VTK_OUTPUT = vtk.vtkStringOutputWindow()
vtk.vtkOutputWindow.SetInstance(_VTK_OUTPUT)


class VTKWidget(QtWidgets.QWidget):
    component_picked = QtCore.pyqtSignal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout = QtWidgets.QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.addWidget(self.vtk_widget)
        self.renderer = vtk.vtkRenderer(); self.renderer.SetBackground(0.08, 0.10, 0.14)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self._headless = os.environ.get("QT_QPA_PLATFORM", "").lower() == "offscreen"
        if not self._headless:
            self.interactor.Initialize()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.AddObserver("LeftButtonPressEvent", self._on_left_button_press, 1.0)
        self.actors: dict[str, vtk.vtkActor] = {}
        self._selected_actor: vtk.vtkActor | None = None

    def _add_polydata(self, name: str, poly: vtk.vtkPolyData, color: tuple[float, float, float], opacity: float = 1.0) -> None:
        mapper = vtk.vtkPolyDataMapper(); mapper.SetInputData(poly)
        actor = vtk.vtkActor(); actor.SetMapper(mapper); actor.GetProperty().SetColor(*color); actor.GetProperty().SetOpacity(opacity)
        self.renderer.AddActor(actor); self.actors[name] = actor

    def _walk(self, prefix: str, obj: Any) -> None:
        if isinstance(obj, vtk.vtkPolyData):
            color, opacity = self._appearance(prefix)
            self._add_polydata(prefix, obj, color, opacity)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (vtk.vtkPolyData, dict)):
                    self._walk(f"{prefix}/{key}", value)

    @staticmethod
    def _appearance(name: str) -> tuple[tuple[float, float, float], float]:
        if "bolt_holes" in name:
            return (0.12, 0.12, 0.14), 1.0
        if name.endswith("/housing"):
            return (0.72, 0.78, 0.88), 0.25
        if "fixed_cover" in name:
            return (0.72, 0.42, 0.10), 0.78
        if "fixing_chamber" in name:
            return (0.62, 0.66, 0.72), 0.48
        if "/shaft" in name:
            return (0.12, 0.48, 0.82), 1.0
        if "elastic_element" in name:
            return (0.32, 0.72, 0.82), 0.95
        if "/main_grating/" in name:
            return ((0.10, 0.76, 0.82), 1.0) if name.endswith("/grooves") else ((0.16, 0.45, 0.52), 0.92)
        if "/indicator_grating/" in name:
            return ((0.98, 0.72, 0.12), 1.0) if name.endswith("/grooves") else ((0.64, 0.42, 0.08), 0.88)
        if "light_source" in name:
            return (1.0, 0.32, 0.12), 1.0
        if "condenser_lens" in name:
            return (0.42, 0.86, 1.0), 0.55
        if "/grating_sensors/zero" in name:
            return (1.0, 0.18, 0.18), 1.0
        if "/grating_sensors/" in name:
            return (0.20, 0.95, 0.48), 1.0
        if "connection_structure" in name:
            return (0.48, 0.50, 0.55), 0.95
        return (0.68, 0.72, 0.78), 0.92

    def set_assembly(self, assembly: dict[str, Any]) -> None:
        had_assembly = bool(self.actors)
        camera = self.renderer.GetActiveCamera()
        camera_state = None
        if had_assembly:
            camera_state = {
                "position": camera.GetPosition(),
                "focal_point": camera.GetFocalPoint(),
                "view_up": camera.GetViewUp(),
                "parallel_scale": camera.GetParallelScale(),
                "parallel_projection": camera.GetParallelProjection(),
                "view_angle": camera.GetViewAngle(),
            }
        actor_state = {
            name: (actor.GetVisibility(), actor.GetProperty().GetOpacity())
            for name, actor in self.actors.items()
        }
        self.clear()
        self._walk("assembly", assembly)
        for name, actor in self.actors.items():
            if name in actor_state:
                visible, opacity = actor_state[name]
                actor.SetVisibility(visible)
                actor.GetProperty().SetOpacity(opacity)
        if camera_state is None:
            self.reset_camera()
        else:
            camera.SetPosition(*camera_state["position"])
            camera.SetFocalPoint(*camera_state["focal_point"])
            camera.SetViewUp(*camera_state["view_up"])
            camera.SetParallelScale(camera_state["parallel_scale"])
            camera.SetParallelProjection(camera_state["parallel_projection"])
            camera.SetViewAngle(camera_state["view_angle"])
            self.renderer.ResetCameraClippingRange()
        if not self._headless:
            self.vtk_widget.GetRenderWindow().Render()

    def clear(self) -> None:
        for actor in self.actors.values(): self.renderer.RemoveActor(actor)
        self.actors.clear()
        self._selected_actor = None

    def set_component_visible(self, token: str, visible: bool) -> None:
        for name, actor in self.actors.items():
            if token in name: actor.SetVisibility(bool(visible))
        self._render()

    def set_housing_opacity(self, opacity: float) -> None:
        value = max(0.0, min(1.0, float(opacity)))
        for name, actor in self.actors.items():
            if name.endswith("/housing"):
                actor.GetProperty().SetOpacity(value)
        self._render()

    def transform_grating(self, kind: str, rotation_deg: float = 0.0, axial_shift: float = 0.0) -> None:
        if kind not in ("main", "indicator"):
            raise ValueError("kind must be 'main' or 'indicator'")
        prefix = f"assembly/{kind}_grating/"
        matched = [actor for name, actor in self.actors.items() if name.startswith(prefix)]
        if not matched:
            raise KeyError(f"No actor group found for {kind}_grating")
        for actor in matched:
            actor.SetOrientation(0.0, 0.0, float(rotation_deg))
            actor.SetPosition(0.0, 0.0, float(axial_shift))
        self._render()

    def reset_camera(self) -> None:
        self.renderer.ResetCamera()
        camera = self.renderer.GetActiveCamera()
        bounds = self.renderer.ComputeVisiblePropBounds()
        if bounds and len(bounds) == 6:
            center = (
                0.5 * (bounds[0] + bounds[1]),
                0.5 * (bounds[2] + bounds[3]),
                0.5 * (bounds[4] + bounds[5]),
            )
            span = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4], 1e-3)
            camera.SetFocalPoint(*center)
            camera.SetPosition(center[0] + 2.4 * span, center[1] - 2.8 * span, center[2] + 1.8 * span)
            camera.SetViewUp(0.0, 0.0, 1.0)
            camera.OrthogonalizeViewUp()
        self.renderer.ResetCameraClippingRange()
        self._render()

    def actor_names(self) -> tuple[str, ...]:
        return tuple(self.actors.keys())

    def _on_left_button_press(self, caller, event) -> None:
        position = self.interactor.GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(position[0], position[1], 0.0, self.renderer)
        picked = picker.GetActor()
        if self._selected_actor is not None:
            self._selected_actor.GetProperty().EdgeVisibilityOff()
        self._selected_actor = picked
        if picked is not None:
            picked.GetProperty().EdgeVisibilityOn()
            picked.GetProperty().SetEdgeColor(1.0, 1.0, 1.0)
            picked.GetProperty().SetLineWidth(2.0)
            name = next((key for key, actor in self.actors.items() if actor is picked), "unknown")
            self.component_picked.emit(name)
        else:
            self.component_picked.emit("none")
        self._render()

    def _render(self) -> None:
        if not self._headless:
            self.vtk_widget.GetRenderWindow().Render()
