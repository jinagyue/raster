# Grating Digital Twin

面向中文学报论文的 MATLAB 光栅传感数字仿真平台。项目按“结构模型→运动→光电→误差→ADC→算法→串口→实验评价”分阶段开发，每完成一个阶段先进行物理一致性和论文数据质量验收。

## 工程目录

```text
Grating_Digital_Twin/
├── main.m                         主程序入口（当前运行阶段1至阶段4）
├── config/
│   └── parameter.m                 全部仿真参数的集中入口
├── model/
│   ├── grating_3D_model.m          参数化三维光栅表面（阶段1）
│   ├── motion_model.m              光栅运动模型（阶段2，已验收）
│   └── optical_model.m             光电转换模型（阶段3，已验收）
├── signal/
│   ├── signal_generator.m           四相信号（阶段3，已验收）
│   ├── error_model.m                非理想误差（阶段4，已验收）
│   └── adc_model.m                  ADC（阶段7，已验收）
├── algorithm/
│   └── phase_estimation.m           位移解算（阶段5，已验收）
├── communication/
│   └── serial_output.m              串口输出（阶段8，已验收）
├── experiment/
│   ├── evaluation.m                 实验评价（阶段6，已验收）
│   └── plot_evaluation.m            论文对比图（阶段6，已验收）
├── tests/
│   ├── stage1_acceptance.m          阶段1自动验收
│   ├── stage2_acceptance.m          阶段2自动验收
│   ├── stage3_acceptance.m          阶段3自动验收
│   ├── stage4_acceptance.m          阶段4自动验收
│   └── stage5_acceptance.m          阶段5自动验收
└── data/                            输出数据（原始数据只读）
```

## 推荐开发顺序

1. 阶段1：锁定 P、N、L 和表面数学定义，验收三维几何与相对位移。
2. 阶段2：输入时间和相对运动，验收 x(t)、速度和相位。
3. 阶段3：生成四相信号并验收 90° 相位关系。
4. 阶段4：逐项加入幅值、相位、偏置、噪声和干扰，形成退化工况。
5. 阶段5：实现幅相校正位移算法并与真实位移比较。
6. 阶段6：统一 RMSE、最大误差、分辨率和 SNR 实验。
7. 阶段7：加入采样保持、量化和削顶检查。
8. 阶段8：最后接入固定协议串口输出。

阶段1至阶段8已经通过自动验收，MATLAB 端数字孪生链路已闭环。

阶段8串口帧为 11 字节：`0xAA | A_H A_L | B_H B_L | C_H C_L | D_H D_L | CRC_H CRC_L`。通道数据使用大端 `uint16`，CRC 为 CRC-16/CCITT-FALSE。`serial_output` 支持 `none`、`simulation` 和 `hardware` 三种模式，并按 `send_rate` 固定周期发送。

阶段7 `adc_model` 将任意模拟电压重采样到配置的均匀采样率，再按 0～3.3 V、12 bit 进行限幅和量化，输出模拟输入、采样电压、ADC 码值、重构电压及量化误差。

阶段6 `evaluation` 已包含位移恢复、SNR=30/20/10 dB、相位误差和幅值失配实验，并同时记录直接 `atan2` 与校正算法的 RMSE、最大误差和一倍标准差分辨率。

阶段5算法不依赖过零计数：先对四通道做中值偏置补偿和 RMS 幅值归一化，再用二维协方差椭圆白化联合补偿增益/相位失配，最后使用 `atan2` 与 `unwrap` 恢复相位并换算位移。`estimate.metrics.traditional` 与 `estimate.metrics.improved` 可直接比较两种方法的 RMSE、最大误差和一倍标准差分辨率。

## 阶段3光电转换

```matlab
p = parameter();
theta = linspace(0,8*pi,2001).';
optical = optical_model(theta,p.optical);
signals = signal_generator(optical,p.signal);
plot(theta,signals.channels); grid on;
```

`optical_model` 输出 `I(t)=I0+Im*cos(theta)`；`signal_generator` 输出四路 `channels`、每路 `phase`、`amplitude` 和 `period_phase`。

阶段4的 `error_model` 支持四路独立 `A_i`、`phi_i`、`B_i`、Gaussian noise 以及公共高频干扰，并保留 `ideal_channels`、`deterministic`、`noise` 和 `high_frequency_interference` 分量，便于论文中的误差归因。

## 阶段2运动模型

```matlab
p = parameter();
t = (0:1/p.motion.sample_rate:p.motion.duration).';
p.motion.mode = 'periodic_disturbance';
motion = motion_model(t,p.motion,p.grating.period);
plot_motion_figures(motion);
```

可选模式为 `constant_velocity`、`acceleration` 和 `periodic_disturbance`。输出包含 `x`、`velocity` 和 `theta=2*pi*x/P`。

## 一键运行

```matlab
cd('Grating_Digital_Twin');
addpath(genpath(pwd));
result = main();
```

无图形并保存完整结果：

```matlab
opts = struct('show_figures',false,'save_report',true,'report_file','data/final_result.mat');
result = main([],opts);
```

默认 `p.serial.mode='none'`，不会打开物理串口；需要发送时通过参数覆盖设置 `mode='hardware'`、`port` 和 `send_rate`。
