"""Windows/packaged launcher for the Stage-16 digital-twin platform."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path


def _show_fatal_error(message: str) -> None:
    log_path = Path.cwd() / "stage16_error.log"
    try:
        log_path.write_text(message, encoding="utf-8")
    except OSError:
        pass
    try:
        from PyQt5 import QtWidgets
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QMessageBox.critical(
            None,
            "光栅扭矩数字孪生平台 - 启动失败",
            "程序未能启动。详细信息已写入 stage16_error.log。\n\n" + message[-1800:],
        )
    except Exception:
        pass


def main() -> int:
    try:
        from Optical_Grating_Torque_DigitalTwin.main import run_gui
        return run_gui(with_matlab=True)
    except Exception:
        detail = traceback.format_exc()
        _show_fatal_error(detail)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
