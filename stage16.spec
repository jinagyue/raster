# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).resolve()
matlab_datas, matlab_binaries, matlab_hiddenimports = collect_all("matlab")

a = Analysis(
    [str(ROOT / "stage16_launcher.py")],
    pathex=[str(ROOT)],
    binaries=matlab_binaries,
    datas=matlab_datas + [
        (str(ROOT / "Grating_Digital_Twin"), "Grating_Digital_Twin"),
    ],
    hiddenimports=matlab_hiddenimports + [
        "vtkmodules.qt.QVTKRenderWindowInteractor",
        "matplotlib.backends.backend_qt5agg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PySide6", "PySide2", "PyQt6"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GratingTorqueDigitalTwin",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="GratingTorqueDigitalTwin",
)
