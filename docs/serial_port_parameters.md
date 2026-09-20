# MATLAB 串口输出参数

## 串口配置

| 参数 | 设置 |
|---|---|
| 端口 | `COM5`（仿真默认，按实际设备修改） |
| 波特率 | `115200` bit/s |
| 数据位 | 8 |
| 校验位 | None |
| 停止位 | 1 |
| 流控 | None |
| 显示方式 | HEX/十六进制接收 |
| 帧率 | 500 frame/s |
| 帧周期 | 2 ms |
| 字节序 | 通道数据高字节在前 |

内部 ADC 采样率为 20 kHz。串口从 ADC 序列中抽取数据，以 500 frame/s
发送。每帧 11 字节，采用 8N1 时需要 110 个线路比特；115200 baud 的
理论上限约为 1047 frame/s，因此不能直接以 20 kframe/s 发送。

## 数据帧

```text
AA A_H A_L B_H B_L C_H C_L D_H D_L CRC_H CRC_L
```

- 帧头：`0xAA`
- A/B/C/D：四路 12 位 ADC 码值，以 16 位无符号数发送
- CRC：CRC-16/CCITT-FALSE
- 多项式：`0x1021`
- 初值：`0xFFFF`
- RefIn/RefOut：False
- XorOut：`0x0000`
- CRC覆盖范围：前9字节，即帧头和四路数据

## 串口助手查看

同一个 COM 端口不能同时被 MATLAB 和串口助手打开。推荐建立虚拟串口对：

```text
MATLAB：COM5  →  虚拟连接  →  串口助手：COM6
```

串口助手配置为 `115200 / 8 / None / 1 / No flow control`，启用HEX接收，
关闭自动换行和文本编码解释。

MATLAB测试命令：

```matlab
cd('F:\MATLAB\MATLAB 光栅数字孪生仿真平台\Grating_Digital_Twin');
addpath(genpath(pwd));
info = serial_hardware_demo('COM5')
```

当前 PyQt5 界面的串口页面显示协议帧预览；只有 MATLAB
`serial_output.m` 使用 `mode='hardware'` 时才会打开真实 COM 端口。
