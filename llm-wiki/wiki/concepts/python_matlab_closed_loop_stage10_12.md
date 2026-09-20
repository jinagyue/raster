# Python-MATLAB 圆光栅闭环阶段10–12

- 日期：2026-09-04
- 来源：用户阶段10–12指令与本地验收结果
- 适用范围：`Circular_Grating_Digital_Twin` 与 `Grating_Digital_Twin`

## 参数接口

MATLAB 新增 `interface/update_parameter.m`，将 `period`、`radius`、`ring_number`、`height`、`shift` 校验并映射到既有 MATLAB 参数结构。`interface/python_control.m` 扩展了 `set_parameter`、`get_parameter` 和 `run_simulation` 命令；阶段1–8核心文件保持不变。

Python `MatlabBridge` 提供对应方法。阶段10验收的最大回读误差为 0，低于 `1e-12`。

## 结构—物理联动

`model/circular_grating.py` 采用极坐标采样构造包含顶面、底面、外圆侧壁和径向槽面片的闭合三角网格，提供 `vertices`、`faces`、体积和 watertight 检查，并生成主/参考光栅。MATLAB `run_simulation` 调用既有运动、光电、误差、相位、ADC 和串口接口链路；Python 不改写这些核心模型。

阶段11验收：P 从 20 um 改为 30 um 时 ADC 最大变化 1986；shift 改变时相位最大变化约 pi，几何网格闭合检查通过。

## 交互层与协议边界

`control/controller.py` 负责参数更新、网格刷新、MATLAB结果缓存和协议帧预览；`visualization/viewer.py` 使用 PyVista 构建双面板结构/四相信号视图，并提供 P、shift、R、N 四个滑块。串口预览帧遵循既有 `0xAA + 4×16-bit + CRC16-CCITT` 格式；真实硬件发送仍由 MATLAB `serial_output.m`负责。

阶段12使用离屏 PyVista 场景验收 GUI 构建和联动，`pass_gui/pass_matlab/pass_model/pass_signal/pass_adc/pass_serial/pass` 全部为 true。该结果证明软件闭环可运行，不等同于硬件串口实测。
