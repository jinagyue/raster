# 机械光栅扭矩传感器数字孪生平台

- 日期：2026-09-05
- 来源：[专利结构参考来源](../../raw_sources/patent_torque_grating_2025-09-05.md)与本地 `Optical_Grating_Torque_DigitalTwin`
- 适用范围：机械结构、PyQt5/VTK和 MATLAB Engine 联动

## 已实现范围

Python 结构层包含参数化圆柱壳体、两端法兰和螺栓孔标记、中心轴、弹性扭转梁、实体同心环光栅盘、主/指示光栅固定腔、光源、聚光镜、五路光栅检测阵列和温度传感器。VTK模型通过PyQt5窗口显示，控制器将扭矩映射为 `theta=T/k`，并以 `x=r*theta+grating_displacement` 传给 MATLAB。

MATLAB 新增 `run_torque` 接口调用既有运动、光电、四相、误差、ADC和串口模块；核心算法文件未修改。Python端提供协议帧预览，实际COM发送仍由原 `serial_output.m` 控制。

## 验收证据

`tests/acceptance.py` 在 Python 3.12、MATLAB R2024b和PyQt5/VTK环境下返回 `pass_gui/pass_model/pass_motion/pass_matlab/pass_signal/pass_adc/pass_serial/pass=true`；扭矩变化的 ADC最大差异为1986，四相信号最大差异为1.6。上述是软件仿真证据，不等同于专利实物尺寸复原或硬件测量性能。
