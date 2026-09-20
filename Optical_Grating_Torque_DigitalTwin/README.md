# Optical Grating Torque Digital Twin

本 Python 子工程面向机械光栅扭矩传感器结构层和交互层，使用 PyQt5 + VTK 建立壳体、两端固定端盖、中心轴、连接结构、主/指示光栅固定腔、两个独立光栅、光源、聚光镜和五路检测位置。MATLAB `Grating_Digital_Twin` 的既有信号算法保持不变。

## 运行环境

```powershell
py -3.12 -m pip install --user -r Optical_Grating_Torque_DigitalTwin/requirements.txt
py -3.12 -m pip install --user "D:\MATLAB\R2024b\extern\engines\python"
```

MATLAB R2024b Engine支持Python 3.9–3.12，不支持Python 3.13。

## 一键运行

```powershell
py -3.12 Optical_Grating_Torque_DigitalTwin/main.py
```

阶段11默认以纯机械审阅模式启动，不连接MATLAB。鼠标左键旋转、滚轮缩放、中键平移；右侧可隐藏部件、调整壳体透明度，并分别旋转或轴向移动主光栅和指示光栅。点击模型部件会显示actor名称。

如需进入既有MATLAB联动界面，需显式使用：

```powershell
py -3.12 Optical_Grating_Torque_DigitalTwin/main.py --with-matlab
```

该模式执行阶段12链路：`Torque -> theta=T*L/(G*J) -> dx=r*theta -> phase=2*pi*dx/P -> MATLAB既有光电/信号链`。当前 `L=0.012 m`、`G=79 GPa`、`d=0.008 m`、`r=0.007 m` 均标记为 `simulation/default`，不是专利尺寸或实测标定参数。

仅执行一次闭环、不打开GUI：

```powershell
py -3.12 Optical_Grating_Torque_DigitalTwin/main.py --no-gui
```

## 验收

```powershell
$env:QT_QPA_PLATFORM='offscreen'
py -3.12 Optical_Grating_Torque_DigitalTwin/tests/acceptance.py
```

该验收检查GUI/VTK装载、结构组件、`T=kθ`、Engine调用、信号变化、ADC变化和协议帧变化。串口默认不打开物理COM口；协议帧由同一CRC-CCITT规则生成，真实发送仍由MATLAB `serial_output.m`控制。

阶段11独立机械验收（不启动MATLAB）：

```powershell
$env:QT_QPA_PLATFORM='offscreen'
py -3.12 Optical_Grating_Torque_DigitalTwin/tests/stage11_acceptance.py
```

阶段12跨Python/MATLAB验收：

```powershell
py -3.12 Optical_Grating_Torque_DigitalTwin/tests/stage12_acceptance.py
```

## 结构边界

用户提供的CN 120427156 A专利PDF仅作为结构功能参考。当前参数化模型不是专利实物的尺寸复原，也不代表专利权利要求或实测性能。
