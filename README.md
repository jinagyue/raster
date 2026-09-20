# MATLAB 光栅传感数字仿真平台

本项目实现“光栅三维模型 → 相对运动 → 光电转换 → 非理想误差 → ADC → 串口实时输出”的端到端数字孪生仿真。代码按 MATLAB package 组织，物理模型、采样模型和 I/O 可分别替换，适合论文扫频、误差消融和串口联调。

## 快速开始

在 MATLAB 中将项目根目录加入路径，然后运行：

```matlab
addpath(genpath(pwd));
cfg = grating.config.defaultConfig();
result = grating.simulatePipeline(cfg);
grating.visualizeResult(result);
```

或直接运行 `examples/run_demo.m`。默认配置只使用 MATLAB 基础语法；真实串口输出需设置 `cfg.serial.mode = "hardware"` 并提供端口号（R2020b+ 的 `serialport`）。

## 目录

- `src/+grating/+config`：配置、校验与单位约定
- `src/+grating/+model`：三维光栅网格与光学相位
- `src/+grating/+motion`：相对运动轨迹
- `src/+grating/+opto`：光功率、光电二极管和跨阻输出
- `src/+grating/+errors`：增益、偏置、谐波和噪声
- `src/+grating/+adc`：限幅、量化和 ADC 码流
- `src/+grating/+serial`：二进制定长帧、CRC16 与串口 sink
- `examples`：演示脚本
- `tests`：无硬件单元测试
- `llm-wiki`：项目知识库，记录接口和模型假设

仿真输出是可重复的数字数据，不等价于真实传感器性能。默认随机种子写入结果元数据；原始输出可保存为 MAT，后续实验应保留配置和版本信息。
