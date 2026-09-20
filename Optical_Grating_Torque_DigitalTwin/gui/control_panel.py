"""Compact Chinese Stage-16 control panel."""
from __future__ import annotations

from PyQt5 import QtCore, QtWidgets


class ControlPanel(QtWidgets.QWidget):
    values_changed = QtCore.pyqtSignal(dict)
    housing_visible = QtCore.pyqtSignal(bool)
    component_visibility_changed = QtCore.pyqtSignal(str, bool)
    housing_opacity_changed = QtCore.pyqtSignal(float)
    reset_camera_requested = QtCore.pyqtSignal()
    start_requested = QtCore.pyqtSignal()
    pause_requested = QtCore.pyqtSignal()
    reset_zero_requested = QtCore.pyqtSignal()
    serial_toggled = QtCore.pyqtSignal(bool)

    COMPONENT_LABELS = {
        "housing": "测量腔体", "shaft": "扭轴", "elastic_element": "弹性元件",
        "front_fixed_cover": "前固定端盖", "rear_fixed_cover": "后固定端盖",
        "main_grating_fixing_chamber": "主光栅固定腔",
        "indicator_grating_fixing_chamber": "指示光栅固定腔",
        "main_grating": "主光栅", "indicator_grating": "指示光栅",
        "light_source": "光源", "condenser_lens": "聚光镜",
        "grating_sensors": "五路光栅传感器", "connection_structure": "连接结构",
    }

    def __init__(self, parameters, parent=None):
        super().__init__(parent)
        self._checks = {}
        root = QtWidgets.QVBoxLayout(self); root.setContentsMargins(4, 4, 4, 4); root.setSpacing(5)
        title = QtWidgets.QLabel("光栅扭矩数字孪生平台")
        title.setStyleSheet("font-weight:600;font-size:17px;padding:2px 0;")
        root.addWidget(title)
        self.tabs = QtWidgets.QTabWidget(); root.addWidget(self.tabs, 1)
        self._build_control_tab(parameters)
        self._build_component_tab()

    def _build_control_tab(self, parameters):
        page = QtWidgets.QWidget(); layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(7, 7, 7, 7); layout.setSpacing(6)
        group = QtWidgets.QGroupBox("物理输入"); form = QtWidgets.QFormLayout(group)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.torque = self._slider(-8000, 8000, int(parameters.torque*1000), lambda v:self.values_changed.emit({'torque':v/1000}))
        self.temperature = self._slider(-400, 1400, int(parameters.temperature*10), lambda v:self.values_changed.emit({'temperature':v/10}))
        self.shift = self._slider(-100, 100, int(parameters.grating_displacement*1e6), lambda v:self.values_changed.emit({'grating_displacement':v*1e-6}))
        self.calibration = self._slider(-100, 100, 0, lambda v:self.values_changed.emit({'optical_phase_zero':v/1000}))
        form.addRow("扭矩", self._value_row(self.torque, lambda v:f"{v/1000:.3f} N·m"))
        form.addRow("温度", self._value_row(self.temperature, lambda v:f"{v/10:.1f} °C"))
        form.addRow("相对位移", self._value_row(self.shift, lambda v:f"{v:.0f} μm"))
        form.addRow("零位校准", self._value_row(self.calibration, lambda v:f"{v:g} mrad"))
        layout.addWidget(group)

        serial_group = QtWidgets.QGroupBox("物理串口输出"); grid = QtWidgets.QGridLayout(serial_group)
        self.serial_port = QtWidgets.QComboBox(); self.serial_port.setEditable(True)
        try:
            from serial.tools import list_ports
            ports = list(dict.fromkeys(item.device for item in list_ports.comports()))
        except Exception:
            ports = []
        if parameters.serial_port not in ports: ports.insert(0, parameters.serial_port)
        self.serial_port.addItems(ports); self.serial_port.setCurrentText(parameters.serial_port)
        self.serial_baud = QtWidgets.QComboBox(); self.serial_baud.setEditable(True)
        self.serial_baud.addItems(["9600", "57600", "115200", "230400", "460800"]); self.serial_baud.setCurrentText(str(parameters.serial_baud_rate))
        self.serial_rate = QtWidgets.QSpinBox(); self.serial_rate.setRange(1, 4000); self.serial_rate.setValue(int(parameters.serial_send_rate)); self.serial_rate.setSuffix(" frame/s")
        self.serial_statistics = QtWidgets.QLabel("未发送")
        grid.addWidget(QtWidgets.QLabel("端口"),0,0); grid.addWidget(self.serial_port,0,1)
        grid.addWidget(QtWidgets.QLabel("波特率"),0,2); grid.addWidget(self.serial_baud,0,3)
        grid.addWidget(QtWidgets.QLabel("帧率"),1,0); grid.addWidget(self.serial_rate,1,1)
        grid.addWidget(QtWidgets.QLabel("统计"),1,2); grid.addWidget(self.serial_statistics,1,3)
        grid.setColumnStretch(1,1); grid.setColumnStretch(3,1); layout.addWidget(serial_group)

        buttons = QtWidgets.QHBoxLayout()
        for text, signal in (("启动动画",self.start_requested),("暂停",self.pause_requested),("零位复位",self.reset_zero_requested)):
            button=QtWidgets.QPushButton(text); button.clicked.connect(signal.emit); buttons.addWidget(button)
        self.serial=QtWidgets.QPushButton("串口 OFF"); self.serial.setCheckable(True); self.serial.setMinimumWidth(90); self.serial.toggled.connect(self._emit_serial); buttons.addWidget(self.serial)
        layout.addLayout(buttons)
        self.status=QtWidgets.QLabel("系统就绪"); self.status.setWordWrap(True)
        self.status.setStyleSheet("padding:6px;background:#eef3f8;border:1px solid #ccd6e0;border-radius:3px;")
        layout.addWidget(self.status); layout.addStretch(1)
        self.tabs.addTab(page,"参数与串口")

    def _build_component_tab(self):
        page=QtWidgets.QWidget(); layout=QtWidgets.QVBoxLayout(page); layout.setContentsMargins(7,7,7,7)
        view=QtWidgets.QGroupBox("三维视图"); form=QtWidgets.QFormLayout(view)
        self.housing=QtWidgets.QCheckBox("显示透明测量腔体"); self.housing.setChecked(True); self.housing.toggled.connect(self.housing_visible.emit)
        self.opacity=QtWidgets.QSlider(QtCore.Qt.Horizontal); self.opacity.setRange(0,100); self.opacity.setValue(25); self.opacity.valueChanged.connect(lambda v:self.housing_opacity_changed.emit(v/100))
        reset=QtWidgets.QPushButton("复位三维视角"); reset.clicked.connect(self.reset_camera_requested.emit)
        form.addRow(self.housing); form.addRow("腔体透明度",self.opacity); form.addRow(reset); layout.addWidget(view)
        self.selected=QtWidgets.QLabel("当前部件：未选择"); self.selected.setWordWrap(True); self.selected.setStyleSheet("padding:5px;background:#f6f6f6;border:1px solid #dddddd;"); layout.addWidget(self.selected)
        group=QtWidgets.QGroupBox("部件显示/隐藏"); box=QtWidgets.QVBoxLayout(group); scroll=QtWidgets.QScrollArea(); scroll.setWidgetResizable(True)
        container=QtWidgets.QWidget(); self.component_layout=QtWidgets.QVBoxLayout(container); self.component_layout.setContentsMargins(5,5,5,5); self.component_layout.addStretch(1)
        scroll.setWidget(container); box.addWidget(scroll); layout.addWidget(group,1); self.tabs.addTab(page,"部件与视图")

    @staticmethod
    def _slider(low,high,value,callback):
        slider=QtWidgets.QSlider(QtCore.Qt.Horizontal); slider.setRange(low,high); slider.setValue(max(low,min(high,value))); slider.valueChanged.connect(callback); return slider

    @staticmethod
    def _value_row(slider,formatter):
        row=QtWidgets.QWidget(); layout=QtWidgets.QHBoxLayout(row); layout.setContentsMargins(0,0,0,0)
        label=QtWidgets.QLabel(formatter(slider.value())); label.setMinimumWidth(82); label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        slider.valueChanged.connect(lambda value:label.setText(formatter(value))); layout.addWidget(slider,1); layout.addWidget(label); return row

    def _emit_serial(self,enabled):
        self.serial.setText("串口 ON" if enabled else "串口 OFF"); self.serial_toggled.emit(enabled)

    def set_components(self,names):
        for check in self._checks.values(): check.deleteLater()
        self._checks={}; groups=[]
        for name in names:
            parts=name.split('/'); token=parts[1] if len(parts)>1 else name
            if token not in groups: groups.append(token)
        insert_at=max(0,self.component_layout.count()-1)
        for token in groups:
            check=QtWidgets.QCheckBox(self.COMPONENT_LABELS.get(token,token.replace('_',' '))); check.setChecked(True)
            check.toggled.connect(lambda state,key=token:self.component_visibility_changed.emit(key,state)); self.component_layout.insertWidget(insert_at,check); insert_at+=1; self._checks[token]=check

    def set_selected(self,name):
        token=name.split('/')[1] if '/' in name else name; self.selected.setText('当前部件：'+self.COMPONENT_LABELS.get(token,name))
    def set_status(self,text): self.status.setText(text)
    def serial_settings(self): return {'port':self.serial_port.currentText().strip(),'baud_rate':int(self.serial_baud.currentText()),'send_rate':float(self.serial_rate.value())}
    def set_serial_statistics(self,frames,byte_count): self.serial_statistics.setText(f'{frames} 帧 / {byte_count} 字节')
