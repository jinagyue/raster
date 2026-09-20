"""One-click entry point for the Python-MATLAB circular-grating twin."""
from __future__ import annotations

import argparse
import json

try:
    from .control.controller import TwinController
    from .matlab.matlab_bridge import MatlabBridge
    from .visualization.viewer import TwinViewer
except ImportError:  # pragma: no cover - direct script invocation
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from Circular_Grating_Digital_Twin.control.controller import TwinController
    from Circular_Grating_Digital_Twin.matlab.matlab_bridge import MatlabBridge
    from Circular_Grating_Digital_Twin.visualization.viewer import TwinViewer


def main(show_gui: bool = True) -> dict[str, object]:
    bridge = MatlabBridge()
    controller = TwinController(bridge=bridge)
    try:
        controller.refresh()
        result: dict[str, object] = {
            "parameter": controller.payload(),
            "mesh_watertight": {name: mesh.is_watertight for name, mesh in controller.last_assembly.items()},
            "adc_samples": len(controller.last_result["adc_code"]) if controller.last_result else 0,
            "serial_frame_hex": controller.serial_preview().hex(" "),
        }
        if show_gui:
            TwinViewer(controller).show()
        return result
    finally:
        bridge.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Circular grating MATLAB digital twin")
    parser.add_argument("--no-gui", action="store_true", help="run one coupled update without opening a window")
    args = parser.parse_args()
    print(json.dumps(main(show_gui=not args.no_gui), ensure_ascii=False, indent=2, default=str))
