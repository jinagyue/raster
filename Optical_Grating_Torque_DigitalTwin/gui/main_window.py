"""Stage-16 integrated Chinese digital-twin window."""
from PyQt5 import QtCore, QtWidgets
from .control_panel import ControlPanel
from .vtk_widget import VTKWidget
from .waveform_widget import WaveformWidget
from ..communication.serial_streamer import SerialStreamer
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent); self.controller=controller; self.setWindowTitle('光栅扭矩数字孪生平台'); self.resize(1700,1000)
        splitter=QtWidgets.QSplitter(QtCore.Qt.Horizontal); splitter.setChildrenCollapsible(False); self.setCentralWidget(splitter)
        self.vtk=VTKWidget(); splitter.addWidget(self.vtk)
        side_splitter=QtWidgets.QSplitter(QtCore.Qt.Vertical); side_splitter.setChildrenCollapsible(False); splitter.addWidget(side_splitter)
        upper=QtWidgets.QWidget(); upper_layout=QtWidgets.QVBoxLayout(upper); upper_layout.setContentsMargins(5,5,5,2); upper_layout.setSpacing(4)
        self.controls=ControlPanel(controller.parameters); upper_layout.addWidget(self.controls,1)
        status_group=QtWidgets.QGroupBox('实时测量状态'); status_layout=QtWidgets.QVBoxLayout(status_group); status_layout.setContentsMargins(5,5,5,5)
        self.readout=QtWidgets.QPlainTextEdit(); self.readout.setReadOnly(True); self.readout.setMaximumBlockCount(20); self.readout.setMinimumHeight(92); self.readout.setMaximumHeight(115); status_layout.addWidget(self.readout)
        upper_layout.addWidget(status_group); side_splitter.addWidget(upper)
        self.waveforms=WaveformWidget(); side_splitter.addWidget(self.waveforms)
        splitter.setStretchFactor(0,3); splitter.setStretchFactor(1,2); splitter.setSizes([1080,620])
        side_splitter.setStretchFactor(0,1); side_splitter.setStretchFactor(1,1); side_splitter.setSizes([480,500])
        self.controls.values_changed.connect(self._queue_update); self.controls.start_requested.connect(self._start); self.controls.pause_requested.connect(self._pause); self.controls.reset_zero_requested.connect(self._zero); self.controls.serial_toggled.connect(self._toggle_serial); self.controls.housing_visible.connect(lambda v:self.vtk.set_component_visible('housing',v)); self.controls.housing_opacity_changed.connect(self.vtk.set_housing_opacity); self.controls.component_visibility_changed.connect(self.vtk.set_component_visible); self.controls.reset_camera_requested.connect(self.vtk.reset_camera); self.vtk.component_picked.connect(self.controls.set_selected)
        self._pending_change={}; self._cursor_step=0; self.serial_streamer=None; self._serial_status='串口已关闭'
        self.update_timer=QtCore.QTimer(self); self.update_timer.setSingleShot(True); self.update_timer.setInterval(180); self.update_timer.timeout.connect(self._apply_update)
        self.timer=QtCore.QTimer(self); self.timer.setInterval(60); self.timer.timeout.connect(self._tick); self.refresh()
    def refresh(self):
        try:
            out=self.controller.refresh(); self.vtk.set_assembly(out['assembly']); self.controls.set_components(self.vtk.actor_names()); self._display(out.get('simulation')); self._status('MATLAB Engine 已连接，系统已更新' if self.controller.bridge else '离线仿真模式')
        except Exception as e: self._status('更新失败：'+str(e))
    def _queue_update(self,change):
        self._pending_change.update(change)
        self.update_timer.start()
        self._status('参数调整中…')
    def _apply_update(self):
        change=dict(self._pending_change); self._pending_change.clear()
        if not change:return
        try:
            out=self.controller.update(**change); self.vtk.set_assembly(out['assembly']); self._display(out.get('simulation')); self._status('参数已更新（MATLAB Engine 持续运行）')
        except Exception as e:self._status('更新失败：'+str(e))
    def _tick(self):
        if self.controller.running:
            self._cursor_step=(self._cursor_step+1)%100
            self.waveforms.set_cursor_fraction(self._cursor_step/99.0)
    def _start(self):
        self.controller.set_running(True); self.timer.start(); self._status('动态波形已开始')
    def _pause(self):
        self.controller.set_running(False); self.timer.stop(); self._status('动态波形已暂停')
    def _toggle_serial(self,enabled):
        if enabled:
            try:
                if not self.controller.result:
                    raise RuntimeError('MATLAB尚未生成ADC数据')
                settings=self.controls.serial_settings()
                if self.serial_streamer is not None and self.serial_streamer.isRunning():
                    self.serial_streamer.stop()
                self.serial_streamer=SerialStreamer(codes=np.asarray(self.controller.result['adc_code']),**settings)
                self.serial_streamer.status_changed.connect(self._on_serial_status)
                self.serial_streamer.statistics_changed.connect(self.controls.set_serial_statistics)
                self.controller.set_serial_enabled(True); self._serial_status='正在打开串口…'; self._status(self._serial_status)
                self.serial_streamer.start()
            except Exception as e:
                self.controller.set_serial_enabled(False); self._serial_status='串口打开失败：'+str(e); self._status(self._serial_status)
                blocker=QtCore.QSignalBlocker(self.controls.serial); self.controls.serial.setChecked(False); self.controls.serial.setText('串口 OFF'); del blocker
        else:
            if self.serial_streamer is not None and self.serial_streamer.isRunning(): self.serial_streamer.stop()
            self.controller.set_serial_enabled(False); self._serial_status='串口已关闭'; self._status(self._serial_status)
    def _on_serial_status(self,text,opened):
        self._serial_status=text; self._status(text); self.controller.set_serial_enabled(opened)
        if not opened:
            blocker=QtCore.QSignalBlocker(self.controls.serial); self.controls.serial.setChecked(False); self.controls.serial.setText('串口 OFF'); del blocker
    def _zero(self):
        blocker=QtCore.QSignalBlocker(self.controls.calibration); self.controls.calibration.setValue(0); del blocker
        self._pending_change.clear(); self.update_timer.stop()
        out=self.controller.update(optical_phase_zero=0.0,grating_displacement=0.0); self.vtk.set_assembly(out['assembly']); self._display(out.get('simulation')); self._status('零位已复位')
    def _status(self,t): self.controls.set_status(t)
    def _display(self,s):
        if not s:return
        adc=np.asarray(s.get('adc_code',[])); frame=self.controller.serial_preview()
        if self.serial_streamer is not None and self.serial_streamer.isRunning(): self.serial_streamer.update_codes(adc)
        self.waveforms.update_data(s,frame)
        scale=s.get('visual_torsion_scale',1.0); display_angle=s.get('display_torsion_angle',s.get('torsion_angle',0))
        self.readout.setPlainText(f"扭矩 Torque：{s.get('torque',0):.6g} N·m    真实扭角：{s.get('torsion_angle',0):.6g} rad\n三维显示角：{display_angle*180/np.pi:.4g}°（仅显示放大×{scale:g}）\n温度 Temperature：{s.get('temperature',20):.3g} °C    方向 Direction：{s.get('direction','静止')}    零位 Zero：{'是' if s.get('zero_status',False) else '否'}\n周期 Period：{s.get('period',0)*1e6:.6g} μm    相位：{s.get('optical_phase',0):.6g} rad\nADC：{adc.shape[0]}×{adc.shape[1] if adc.ndim>1 else 0}，0~4095    串口：{'ON' if self.controller.serial_enabled else 'OFF'}    MATLAB Engine：{'持久连接' if self.controller.bridge and self.controller.bridge._engine is not None else '未连接'}")
    def closeEvent(self,e):
        self.timer.stop(); self.update_timer.stop()
        if self.serial_streamer is not None and self.serial_streamer.isRunning(): self.serial_streamer.stop()
        super().closeEvent(e)
