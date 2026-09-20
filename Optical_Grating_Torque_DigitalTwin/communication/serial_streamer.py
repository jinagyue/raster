"""Background serial sender for MATLAB-generated four-channel ADC data."""
from __future__ import annotations

import threading
import time
from typing import Any

import numpy as np
import serial
from PyQt5 import QtCore

from ..control.torque_controller import encode_adc_frame


class SerialStreamer(QtCore.QThread):
    status_changed = QtCore.pyqtSignal(str, bool)
    statistics_changed = QtCore.pyqtSignal(int, int)

    def __init__(self, port: str, baud_rate: int, send_rate: float, codes: Any, parent=None):
        super().__init__(parent)
        self.port_name = str(port).strip()
        self.baud_rate = int(baud_rate)
        self.send_rate = float(send_rate)
        if not self.port_name:
            raise ValueError("串口名称不能为空")
        if self.baud_rate <= 0 or self.send_rate <= 0:
            raise ValueError("波特率和发送帧率必须为正数")
        if self.send_rate > self.baud_rate / 110.0:
            raise ValueError("发送帧率超过11字节8N1协议的波特率上限")
        self._lock = threading.Lock()
        self._codes = self._validate_codes(codes)
        self.frames_sent = 0
        self.bytes_sent = 0

    @staticmethod
    def _validate_codes(codes: Any) -> np.ndarray:
        values = np.asarray(codes, dtype=np.uint16)
        if values.ndim != 2 or values.shape[1] != 4 or values.shape[0] == 0:
            raise ValueError("串口发送数据必须是非空N×4 ADC矩阵")
        return values.copy()

    def update_codes(self, codes: Any) -> None:
        values = self._validate_codes(codes)
        with self._lock:
            self._codes = values

    def stop(self) -> None:
        self.requestInterruption()
        self.wait(2500)

    def run(self) -> None:
        frame_count = 0
        byte_count = 0
        index = 0
        try:
            with serial.serial_for_url(
                self.port_name,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0,
                write_timeout=1,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            ) as device:
                self.status_changed.emit(
                    f"串口已打开：{self.port_name}，{self.baud_rate} baud，{self.send_rate:g} frame/s",
                    True,
                )
                period = 1.0 / self.send_rate
                deadline = time.perf_counter()
                while not self.isInterruptionRequested():
                    with self._lock:
                        codes = self._codes[index % self._codes.shape[0], :].copy()
                        length = self._codes.shape[0]
                    frame = encode_adc_frame(codes)
                    device.write(frame)
                    frame_count += 1
                    byte_count += len(frame)
                    self.frames_sent = frame_count
                    self.bytes_sent = byte_count
                    index = (index + 1) % length
                    if frame_count % 50 == 0:
                        self.statistics_changed.emit(frame_count, byte_count)
                    deadline += period
                    delay = deadline - time.perf_counter()
                    if delay > 0:
                        time.sleep(delay)
                    else:
                        deadline = time.perf_counter()
        except Exception as exc:
            self.status_changed.emit(f"串口打开/发送失败：{exc}", False)
        finally:
            self.statistics_changed.emit(frame_count, byte_count)
