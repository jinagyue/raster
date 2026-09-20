"""Interactive PyVista view for structure and MATLAB response data."""
from __future__ import annotations

from typing import Any

import numpy as np

from ..control.controller import TwinController


class TwinViewer:
    """Two-panel viewer: 3-D main/reference meshes and four-channel traces."""

    def __init__(self, controller: TwinController, off_screen: bool = False) -> None:
        self.controller = controller
        self.off_screen = off_screen
        self.plotter: Any = None
        self._mesh_actors: list[Any] = []
        self._signal_actors: list[Any] = []

    @staticmethod
    def _faces_for_pyvista(faces: np.ndarray) -> np.ndarray:
        count = faces.shape[0]
        return np.hstack((np.full((count, 1), 3, dtype=np.int64), faces)).ravel()

    def _add_mesh(self, mesh: Any, color: str, name: str) -> Any:
        import pyvista as pv
        poly = pv.PolyData(mesh.vertices, self._faces_for_pyvista(mesh.faces))
        actor = self.plotter.add_mesh(poly, name=name, color=color, smooth_shading=True, opacity=0.82)
        self._mesh_actors.append(actor)
        return actor

    def _add_signal_lines(self, result: dict[str, Any]) -> None:
        import pyvista as pv
        signal = np.asarray(result.get("signal", []), dtype=float)
        time = np.asarray(result.get("time", []), dtype=float).reshape(-1)
        if signal.ndim != 2 or signal.shape[1] != 4 or time.size != signal.shape[0]:
            return
        self.plotter.subplot(0, 1)
        colors = ("#1f77b4", "#d62728", "#2ca02c", "#9467bd")
        for k, color in enumerate(colors):
            points = np.column_stack((time, np.full(time.shape, float(k)), signal[:, k]))
            poly = pv.PolyData(points)
            poly.lines = np.hstack(([time.size], np.arange(time.size, dtype=np.int64)))
            self._signal_actors.append(self.plotter.add_mesh(poly, name=f"signal_{k+1}", color=color, line_width=2))
        self.plotter.add_text("MATLAB four-phase response", font_size=10)
        self.plotter.show_grid(xtitle="Time [s]", ytitle="Channel", ztitle="Signal [a.u.]")

    def build_scene(self, add_sliders: bool = False) -> Any:
        import pyvista as pv
        if self.plotter is None:
            self.plotter = pv.Plotter(shape=(1, 2), off_screen=self.off_screen, window_size=(1400, 760))
        if self.controller.last_assembly is None:
            self.controller.refresh(start_engine=self.controller.bridge is not None)
        self.plotter.subplot(0, 0)
        self.plotter.add_text("Circular Grating | Structure Layer", font_size=11)
        p = self.controller.parameters
        self.plotter.add_text(
            f"R={p.radius*1e3:.3f} mm | P={p.period*1e6:.2f} um | "
            f"N={p.ring_number} | shift={p.reference_shift[0]*1e6:.2f} um",
            position="upper_right", font_size=9)
        self._add_mesh(self.controller.last_assembly["main_grating"], "#2f80ed", "main_grating")
        self._add_mesh(self.controller.last_assembly["reference_grating"], "#f2994a", "reference_grating")
        self.plotter.show_grid(xtitle="x [m]", ytitle="y [m]", ztitle="z [m]")
        self.plotter.add_axes()
        if self.controller.last_result is not None:
            self._add_signal_lines(self.controller.last_result)
        if add_sliders:
            self.plotter.subplot(0, 0)
            self.plotter.add_slider_widget(lambda v: self._slider_update("period", v), (0.5*p.period, 1.5*p.period), value=p.period, title="Period P [m]", pointa=(0.05, 0.10), pointb=(0.42, 0.10))
            self.plotter.add_slider_widget(lambda v: self._slider_update("shift", v), (0.0, 50e-6), value=p.reference_shift[0], title="Reference shift [m]", pointa=(0.05, 0.04), pointb=(0.42, 0.04))
            self.plotter.add_slider_widget(lambda v: self._slider_update("radius", v), (0.5*p.radius, 1.5*p.radius), value=p.radius, title="Radius R [m]", pointa=(0.55, 0.10), pointb=(0.92, 0.10))
            self.plotter.add_slider_widget(lambda v: self._slider_update("ring_number", v), (max(1, 0.5*p.ring_number), 1.5*p.ring_number), value=p.ring_number, title="Ring number N", pointa=(0.55, 0.04), pointb=(0.92, 0.04))
        return self.plotter

    def _slider_update(self, field: str, value: float) -> None:
        self.controller.update(**{field: float(value)})
        self.close_scene_actors()
        self.build_scene(add_sliders=False)
        if self.plotter is not None:
            self.plotter.render()

    def close_scene_actors(self) -> None:
        if self.plotter is None:
            return
        for actor in self._mesh_actors + self._signal_actors:
            try:
                self.plotter.remove_actor(actor)
            except Exception:
                pass
        self._mesh_actors.clear()
        self._signal_actors.clear()

    def show(self) -> None:
        self.build_scene(add_sliders=True)
        self.plotter.show()

    def close(self) -> None:
        if self.plotter is not None:
            self.plotter.close()
            self.plotter = None
