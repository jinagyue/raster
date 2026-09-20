# 机械光栅扭矩平台最终验收

- 日期：2026-09-05
- 来源：`Optical_Grating_Torque_DigitalTwin/tests/acceptance.py` 实测输出与 MATLAB `run_torque` 联调
- 适用范围：软件数字孪生闭环

最终验收返回 `pass_gui/pass_model/pass_motion/pass_matlab/pass_signal/pass_adc/pass_serial/pass=true`。扭矩从 0 改为 0.5 N·m 时，四相信号最大变化 1.6，ADC最大变化1986；MATLAB `serial_output` 使用 `simulation` 模式实际生成41帧、451字节二进制帧文件。硬件COM口仍需显式配置 `serial_mode='hardware'`，当前结果不宣称STM32实测或专利实物尺寸复原。

2026-09-05复核发现旧运行窗口曾将轴线变换错误地应用到中心轴，导致视觉上横穿壳体；已在 `model/shaft.py` 中固定轴线沿壳体 z 轴，仅保留扭矩角作为绕自身轴线状态，角度变化不再改变中心轴方向。
