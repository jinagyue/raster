"""Embedded Stage-16 time-domain waveform viewer."""
from __future__ import annotations

import numpy as np
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams

rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False


class _PlotPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5.2, 3.0), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.canvas)


class WaveformWidget(QtWidgets.QTabWidget):
    """Show five-channel, ADC and phase/displacement waveforms."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analog_page = _PlotPage()
        self.adc_page = _PlotPage()
        self.motion_page = _PlotPage()
        self.serial_text = QtWidgets.QPlainTextEdit()
        self.serial_text.setReadOnly(True)
        self.addTab(self.analog_page, "五路光栅信号")
        self.addTab(self.adc_page, "四通道ADC")
        self.addTab(self.motion_page, "相位/位移")
        self.addTab(self.serial_text, "串口帧")
        self.setMinimumHeight(330)
        self._cursor_lines = {}
        self._time_ranges = {}

    @staticmethod
    def _time_ms(simulation: dict, length: int) -> np.ndarray:
        t = np.asarray(simulation.get("time", []), dtype=float).reshape(-1)
        if t.size != length:
            t = np.arange(length, dtype=float)
        return t * 1e3

    def update_data(self, simulation: dict, serial_frame: bytes | None = None) -> None:
        five = np.asarray(simulation.get("five_channel_signal", []), dtype=float)
        adc = np.asarray(simulation.get("adc_code", []), dtype=float)
        phase = np.asarray(simulation.get("phase", []), dtype=float).reshape(-1)
        displacement = np.asarray(simulation.get("displacement_waveform", []), dtype=float).reshape(-1)

        self.analog_page.figure.clear()
        ax = self.analog_page.figure.add_subplot(111)
        if five.ndim == 2 and five.shape[1] == 5:
            t = self._time_ms(simulation, five.shape[0])
            labels = ("ZERO", "MAIN", "PHASE_90", "PHASE_180", "PHASE_270")
            for index, label in enumerate(labels):
                ax.plot(t, five[:, index], linewidth=1.25, label=label)
            ax.legend(loc="upper right", fontsize=7, ncol=2)
        ax.set_xlabel("时间 [ms]")
        ax.set_ylabel("幅值 [a.u.]")
        ax.set_title("五路光栅传感器动态信号")
        ax.grid(True, alpha=0.25)
        if five.ndim == 2 and five.shape[0]:
            self._cursor_lines[0] = ax.axvline(t[0], color="#222222", linewidth=0.8, alpha=0.65)
            self._time_ranges[0] = (float(t[0]), float(t[-1]))
        self.analog_page.canvas.draw_idle()

        self.adc_page.figure.clear()
        ax = self.adc_page.figure.add_subplot(111)
        if adc.ndim == 2 and adc.shape[1] == 4:
            t = self._time_ms(simulation, adc.shape[0])
            for index, label in enumerate(("A", "B", "C", "D")):
                ax.step(t, adc[:, index], where="mid", linewidth=1.0, label=label)
            ax.legend(loc="upper right", fontsize=8, ncol=4)
        ax.set_xlabel("时间 [ms]")
        ax.set_ylabel("ADC码值")
        ax.set_ylim(-100, 4195)
        ax.set_title("12位ADC输出")
        ax.grid(True, alpha=0.25)
        if adc.ndim == 2 and adc.shape[0]:
            self._cursor_lines[1] = ax.axvline(t[0], color="#222222", linewidth=0.8, alpha=0.65)
            self._time_ranges[1] = (float(t[0]), float(t[-1]))
        self.adc_page.canvas.draw_idle()

        self.motion_page.figure.clear()
        ax_phase = self.motion_page.figure.add_subplot(111)
        if phase.size:
            t = self._time_ms(simulation, phase.size)
            ax_phase.plot(t, phase, color="#3366cc", label="光学相位")
        ax_phase.set_xlabel("时间 [ms]")
        ax_phase.set_ylabel("相位 [rad]", color="#3366cc")
        ax_phase.tick_params(axis="y", labelcolor="#3366cc")
        ax_phase.grid(True, alpha=0.25)
        ax_disp = ax_phase.twinx()
        if displacement.size:
            t_disp = self._time_ms(simulation, displacement.size)
            ax_disp.plot(t_disp, displacement * 1e6, color="#d04a35", label="相对位移")
        ax_disp.set_ylabel("位移 [μm]", color="#d04a35")
        ax_disp.tick_params(axis="y", labelcolor="#d04a35")
        ax_phase.set_title("光学相位与光栅相对位移")
        if phase.size:
            self._cursor_lines[2] = ax_phase.axvline(t[0], color="#222222", linewidth=0.8, alpha=0.65)
            self._time_ranges[2] = (float(t[0]), float(t[-1]))
        self.motion_page.canvas.draw_idle()

        if serial_frame is not None:
            hex_text = " ".join(f"{byte:02X}" for byte in serial_frame)
            self.serial_text.setPlainText(
                "协议：帧头 + A/B/C/D（高字节在前）+ CRC16-CCITT\n\n"
                f"当前帧（{len(serial_frame)}字节）：\n{hex_text}\n\n"
                "说明：当前为协议预览；串口ON后才允许发送到配置的物理端口。"
            )

    def set_cursor_fraction(self, fraction: float) -> None:
        """Move only the visible page cursor; no MATLAB call or replot."""
        page = self.currentIndex()
        if page not in self._cursor_lines or page not in self._time_ranges:
            return
        start, stop = self._time_ranges[page]
        x = start + (stop - start) * (float(fraction) % 1.0)
        self._cursor_lines[page].set_xdata([x, x])
        (self.analog_page, self.adc_page, self.motion_page)[page].canvas.draw_idle()
