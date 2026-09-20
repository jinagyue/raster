# Python-MATLAB Engine 接口阶段9

- 日期：2026-09-04
- 来源：用户阶段9要求与本地联调结果
- 适用范围：`Circular_Grating_Digital_Twin` 与 `Grating_Digital_Twin` 的连接层

## 接口边界

阶段9只负责 MATLAB Engine 生命周期和连通性验证。Python 侧 `matlab/matlab_bridge.py` 启动一个 MATLAB Engine 会话，将 MATLAB 项目的 `interface/` 目录加入路径，并调用 `python_control('ping')`。参数传递、信号计算和实时闭环留给阶段10及以后。

MATLAB 新增 `interface/python_control.m`，其 `ping` 命令返回 `status`、`stage`、`interface` 和 MATLAB 版本信息；不修改阶段1–8核心模型文件。

## 环境约束与证据

MATLAB R2024b Engine 支持 Python 3.9–3.12，不支持 Python 3.13。本机使用 Python 3.12 安装 `D:\MATLAB\R2024b\extern\engines\python` 后，`tests/stage9_acceptance.py` 返回 `pass_engine=true`、`pass_interface=true`、`pass=true`；MATLAB 端独立 `ping` 检查同样通过。

## 后续边界

阶段10应在此桥接层之上增加参数结构传递与回读校验；不得把阶段9的 `ping` 连通性结果表述为已实现三维结构驱动信号。
