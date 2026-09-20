# 平台架构

`grating.simulatePipeline` 依次调用三维网格、相对运动、光学相位、光电转换、非理想误差、ADC 和串口 sink。每个阶段返回带时间向量的结构体；因此可以在任意阶段注入实测数据或替换模型。串口 sink 支持 `simulation`（二进制文件）、`hardware`（MATLAB `serialport`）和 `none` 三种模式。

面向使用者的入口为 `Grating_Simulation/main.m`，其目录与论文/实验常用命名保持一致：`config`、`model`、`signal`、`communication`、`algorithm`、`data`。该入口调用均为普通 MATLAB 函数，单元测试不依赖真实串口。
