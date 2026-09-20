# 串口协议

帧格式为 `0xAA 0x55 | uint32 sequence | uint32 timestamp_us | uint16 count | uint32 samples[count] | optional float32 voltage[count] | uint16 CRC`。多字节字段使用 MATLAB 原生小端 `typecast`；CRC 为 CRC-16/CCITT-FALSE，初值 `0xFFFF`，覆盖 payload（不含帧头）。
