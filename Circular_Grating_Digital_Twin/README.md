# Circular Grating Digital Twin（阶段9–12）

本目录是 Python 结构层、控制层与 MATLAB Engine API 的接口层。阶段9–12完成 Engine 连通、参数回读、圆环实体网格、MATLAB信号联动和离屏/交互可视化入口。

## 运行环境

- MATLAB R2024b（或与 MATLAB Engine API 兼容的版本）
- Python 3.9–3.12（R2024b Engine 不支持 Python 3.13）
- `matlabengine` Python 包

安装本地 Engine 包示例：

```powershell
py -3.12 -m pip install --user "D:\MATLAB\R2024b\extern\engines\python"
```

运行阶段9验收：

```powershell
py -3.12 Circular_Grating_Digital_Twin/tests/stage9_acceptance.py
```

## 分阶段接口

- 阶段9：`ping`，验证 Python 启动 MATLAB 并调用接口。
- 阶段10：`set_parameter` / `get_parameter`，传递 `period/radius/ring_number/height/shift`。
- 阶段11：`run_simulation`，调用既有 motion → optical → signal → error → phase → ADC → serial 流程。
- 阶段12：`TwinController` 和 `TwinViewer`，将网格、四相信号、ADC 和协议帧预览关联起来。

MATLAB 阶段1–8核心文件保持不变；新增适配器位于 `Grating_Digital_Twin/interface/`。

运行阶段9–12验收：

```powershell
py -3.12 Circular_Grating_Digital_Twin/tests/stage9_acceptance.py
py -3.12 Circular_Grating_Digital_Twin/tests/stage10_acceptance.py
py -3.12 Circular_Grating_Digital_Twin/tests/stage11_acceptance.py
py -3.12 Circular_Grating_Digital_Twin/tests/stage12_acceptance.py
```

启动一键联动（默认打开 PyVista 窗口）：

```powershell
py -3.12 Circular_Grating_Digital_Twin/main.py
```

仅运行一次联动、不打开窗口：

```powershell
py -3.12 Circular_Grating_Digital_Twin/main.py --no-gui
```
