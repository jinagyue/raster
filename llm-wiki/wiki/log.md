# 更新日志

- 2026-09-04：初始化 MATLAB 光栅传感数字仿真平台工程和知识页。
- 2026-09-04：按用户指定目录新增 `Grating_Simulation` 模块化入口、四相解算和独立 smoke tests。
- 2026-09-04：建立 `Circular_Grating_Model` Python 子工程阶段A，完成目录预留、集中参数数据类、物理范围校验与 JSON 交换接口；尚未进入实体建模。
- 2026-09-04：完成阶段9 Python-MATLAB Engine 接口，新增 `matlab_bridge.py`、`python_control.m` 和阶段9验收脚本；Python 3.12 调用 MATLAB R2024b ping 通过，未进入参数传递。
- 2026-09-04：完成阶段10–12参数传递、圆光栅闭合网格、结构驱动 MATLAB 信号和 PyVista 离屏交互验收；阶段10–12测试全部通过，未修改阶段1–8核心文件。
- 2026-09-05：读取用户提供的 CN 120427156 A 专利 PDF，依据图1/图2/图5/图6补充扭矩传感器光学读取结构和温度传感器组件；记录为结构参考，不把默认尺寸或软件验收升级为实物结论。
- 2026-09-05：完成 `Optical_Grating_Torque_DigitalTwin` 机械结构、PyQt5/VTK界面、扭矩控制器、MATLAB `run_torque` 接口和STL导出；端到端 acceptance 全部通过，保留“软件闭环而非硬件实测”的证据边界。
- 2026-09-05：将 `run_torque` 默认串口模式设为 simulation，原有 `serial_output.m` 实际生成41帧/451字节协议文件；最终 acceptance 的七项子检查和总检查均为 true。
- 2026-09-05：修复中心轴变换顺序导致的横向穿轴显示，中心轴现始终与壳体同轴；角度仅作为绕自身轴线的机械状态，验收再次全部通过。
- 2026-09-16：依据《赤峰学院学报（自然科学版）规范格式论文模板》完成论文规范审查，并基于平台阶段1-16的机理模型、14类测试工况、Stage 14算法横评对比与Stage 15温漂补偿成果，完成主论文 `main.tex` 完整技术内容编写与 `references.bib` 规范著录，实现 XeLaTeX + BibTeX 零误差编译出刊级 PDF。
