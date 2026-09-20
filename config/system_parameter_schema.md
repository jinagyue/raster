# 阶段10：系统参数模式冻结

## 1. 约定

- 内部统一采用 SI：m、s、rad、Hz、N、N·m、V；界面显示可换算为 mm、um、deg。
- 规范键采用 `domain.component.parameter`，不得用含义模糊的 `angle`、`shift`、`radius` 跨模块传递。
- 来源：`E`=现有工程，`P`=专利功能/拓扑，`U`=未知待确认，`S`=仿真假设。
- `E/S` 表示变量已经存在，但当前默认数值只用于仿真，不代表专利或实物参数。
- 本文冻结参数语义，不要求本阶段修改现有 MATLAB/Python 字段名。

## 2. 机械结构参数

| 规范键 | 符号 | 单位/类型 | 当前绑定或默认值 | 来源 | 阶段11必需 | 状态说明 |
|---|---|---|---|---|---|---|
| `mechanical.shaft.length` | `L_s` | m, >0 | `shaft_length=0.070` | E/S | 是 | 扭轴总长，待图纸确认 |
| `mechanical.shaft.diameter` | `D_s` | m, >0 | `2*shaft_radius=0.008` | E/S | 是 | 普通轴段外径，待确认 |
| `mechanical.shaft.torsion_length` | `L_t` | m, >0 | 无 | U | 是 | 有效扭转段长度 |
| `mechanical.shaft.torsion_diameter` | `D_t` | m, >0 | 无 | U | 是 | 圆截面；若非圆截面则改用截面参数集 |
| `mechanical.shaft.end_interface` | - | 结构体 | 无 | U | 是 | 键槽、花键、螺纹或联轴器尺寸与基准 |
| `mechanical.housing.length` | `L_h` | m, >0 | `housing_length=0.040` | E/S | 是 | 测量腔体轴向长度 |
| `mechanical.housing.outer_diameter` | `D_ho` | m, >0 | `2*housing_radius=0.030` | E/S | 是 | 腔体外径 |
| `mechanical.housing.inner_diameter` | `D_hi` | m, >0 | `2*(housing_radius-wall_thickness)=0.026` | E/S | 是 | 腔体内径 |
| `mechanical.housing.wall_thickness` | `t_h` | m, >0 | `wall_thickness=0.002` | E/S | 是 | 应满足 `2*t_h=D_ho-D_hi` |
| `mechanical.cover.front.diameter` | `D_cf` | m, >0 | 当前共用 `2*flange_radius=0.042` | E/S | 是 | 前端盖需独立确认 |
| `mechanical.cover.front.thickness` | `t_cf` | m, >0 | 当前共用 `flange_thickness=0.004` | E/S | 是 | 前端盖需独立确认 |
| `mechanical.cover.rear.diameter` | `D_cr` | m, >0 | 当前共用 `2*flange_radius=0.042` | E/S | 是 | 后端盖需独立确认 |
| `mechanical.cover.rear.thickness` | `t_cr` | m, >0 | 当前共用 `flange_thickness=0.004` | E/S | 是 | 后端盖需独立确认 |
| `mechanical.flange.bolt_count` | `N_b` | integer, >=3 | `bolt_number=6` | E/S | 是 | 专利未确认具体孔数 |
| `mechanical.flange.bolt_circle_diameter` | `D_bc` | m, >0 | `2*bolt_circle_radius=0.034` | E/S | 是 | 待图纸确认 |
| `mechanical.flange.bolt_hole_diameter` | `D_bh` | m, >0 | `0.0024`，当前代码隐含 | E/S | 是 | 应从代码常量提升为显式参数 |
| `assembly.cover_fit.depth` | `l_fit` | m, >=0 | 无 | U | 是 | 端盖与腔体装配深度 |
| `assembly.cover_fit.radial_clearance` | `c_fit` | m, >=0 | 无 | U | 是 | 装配间隙 |
| `assembly.datum.axis` | - | enum/vector | 全局 z 轴 | E | 是 | 轴、腔体和光栅的共同基准轴 |

## 3. 扭转与位移参数

| 规范键 | 符号 | 单位/类型 | 当前绑定或默认值 | 来源 | 阶段11必需 | 状态说明 |
|---|---|---|---|---|---|---|
| `load.torque` | `T` | N·m | `torque=0` | E | 是 | 外部工况输入，不是结构常数 |
| `mechanics.torsional_stiffness` | `k_t` | N·m/rad, >0 | `torsional_stiffness=0.08` | E/S | 是 | 需理论计算或标定；MATLAB也以0.08回退 |
| `mechanics.torsion_angle` | `theta_torsion` | rad | `effective_angle`/`angle` | E | 是 | 派生量，`T/k_t`；直接角度输入只用于调试 |
| `optical.effective_detection_radius` | `r_eff` | m, >0 | Python控制器硬编码 `1e-3` | E/S | 是 | 决定角位移到线位移的转换，必须显式化 |
| `optical.displacement_bias` | `x_bias` | m | `grating_displacement` | E/S | 是 | 零载安装偏置或调试输入 |
| `optical.grating_relative_displacement` | `x_rel` | m | `x_bias+1e-3*effective_angle` | E/S | 是 | 派生量；规范公式为 `x_bias+r_eff*theta_torsion` |
| `mechanics.rotation_angle_override` | - | rad/null | `rotation_angle`，非0时覆盖扭矩角 | E/S | 否 | GUI调试入口，不属于正常物理链 |

## 4. 光栅与光电参数

| 规范键 | 符号 | 单位/类型 | 当前绑定或默认值 | 来源 | 阶段11必需 | 状态说明 |
|---|---|---|---|---|---|---|
| `optical.grating_period` | `P` | m, >0 | MATLAB/Python均为 `20e-6` | E/S | 是 | 需用实际光栅规格确认 |
| `optical.main_grating.outer_radius` | `R_m` | m, >0 | `disk_radius=0.010` | E/S | 是 | 主光栅外半径 |
| `optical.main_grating.inner_radius` | `r_m` | m, >=0 | 无 | U | 是 | 安装孔或无效中心区 |
| `optical.main_grating.thickness` | `t_m` | m, >0 | `disk_thickness=0.0015` | E/S | 是 | 主光栅厚度 |
| `optical.main_grating.line_count` | `N_m` | integer, >0 | `line_number=500` | E/S | 否 | 当前圆盘显示按同心环处理，物理编码形式待确认 |
| `optical.indicator_grating.outer_radius` | `R_i` | m, >0 | 无独立参数 | U | 是 | 指示光栅外半径 |
| `optical.indicator_grating.inner_radius` | `r_i` | m, >=0 | 无 | U | 是 | 指示光栅内半径 |
| `optical.indicator_grating.thickness` | `t_i` | m, >0 | 无 | U | 是 | 指示光栅厚度 |
| `optical.grating_gap` | `g` | m, >0 | 无 | U | 是 | 主/指示光栅轴向间隙 |
| `optical.grating_direction` | - | enum | 当前显示为同心环 | E/S | 是 | 需确认径向刻线、环形刻线或其他编码 |
| `optical.main_grating.pose` | - | 位置m+姿态rad | 当前由经验 z 偏移计算 | E/S | 是 | 应改为装配基准尺寸 |
| `optical.indicator_grating.pose` | - | 位置m+姿态rad | 仅外观壳体 | E/S | 是 | 独立实体与位姿未知 |
| `optical.phase_zero` | `phi0` | rad | 无，等效为0 | U/S | 是 | 零载光学相位；需装配或标定确定 |
| `optical.phase` | `phi_opt` | rad | MATLAB `motion.theta`/返回 `phase` | E | 是 | 派生量 `2*pi*x_rel/P+phi0` |
| `optical.intensity.dc` | `I0` | a.u. 或 V | MATLAB `I0=1.0` | E/S | 否 | 当前没有真实光功率/电压标定 |
| `optical.intensity.modulation` | `Im` | a.u. 或 V | MATLAB `Im=0.8` | E/S | 否 | 当前没有真实调制度标定 |
| `optical.source.pose_size` | - | 结构体 | 可视化硬编码 | E/S | 否 | 光路模型升级时参数化 |
| `optical.lens.pose_size` | - | 结构体 | 可视化硬编码 | E/S | 否 | 光路模型升级时参数化 |

## 5. 五路光栅传感器与温度参数

| 规范键 | 单位/类型 | 当前绑定或默认值 | 来源 | 阶段11必需 | 状态说明 |
|---|---|---|---|---|---|
| `sensor.channel_order` | string[5] | `[zero, main, direction_1, direction_2, direction_3]` | P | 是 | 冻结顺序，不得更改 |
| `sensor.zero.pose` | 位置m+姿态rad | 三维外观中与主通道位置重合 | E/S | 是 | 真实安装位姿未知 |
| `sensor.zero.signal_model` | enum/结构体 | 无 | U | 否 | 需明确脉冲/窗口/模拟量形式 |
| `sensor.zero.mark_count` | integer, >0 | 无 | U | 是 | 每转或每周期零位标记数量 |
| `sensor.zero.mark_width` | m 或 rad | 无 | U | 是 | 决定零位脉冲宽度 |
| `sensor.main.pose` | 位置m+姿态rad | 名义方位0 | E/S | 是 | 实际检测中心需确认 |
| `sensor.direction_1.pose` | 位置m+姿态rad | 名义方位 `pi/2` | E/S | 是 | 实际检测中心需确认 |
| `sensor.direction_2.pose` | 位置m+姿态rad | 名义方位 `pi` | E/S | 是 | 实际检测中心需确认 |
| `sensor.direction_3.pose` | 位置m+姿态rad | 名义方位 `3*pi/2` | E/S | 是 | 实际检测中心需确认 |
| `sensor.measurement.phase_offsets` | rad[4] | `[0,pi/2,pi,3*pi/2]` | E + P | 否 | 现有四相信号顺序冻结 |
| `sensor.measurement.amplitude` | number[4] | MATLAB误差配置 | E/S | 否 | 由实物标定后替换 |
| `sensor.measurement.phase_error` | rad[4] | 默认0 | E/S | 否 | 由实物标定后替换 |
| `sensor.measurement.offset` | V或a.u.[4] | 默认0 | E/S | 否 | 由实物标定后替换 |
| `sensor.measurement.noise_rms` | V或a.u.[4] | 默认0 | E/S | 否 | 由实验噪声统计替换 |
| `sensor.temperature.pose_size` | 结构体 | 可视化硬编码 | P + E/S | 否 | 专利有该功能，尺寸和位置待确认 |
| `sensor.temperature.value` | degC | 无 | U | 否 | 尚未进入信号链 |
| `sensor.temperature.compensation` | 结构体 | 无 | U | 否 | 需温度实验建立，不得预设补偿结论 |

## 6. ADC参数

| 规范键 | 单位/类型 | 当前绑定或默认值 | 来源 | 状态说明 |
|---|---|---|---|---|
| `adc.input_channel_order` | string[] | 当前 `[main,direction_1,direction_2,direction_3]` | E | 阶段10保留四路兼容；五路扩展待实现 |
| `adc.bits` | integer, >0 | 12 | E/S | 码值范围0-4095 |
| `adc.vmin` | V | 0 | E/S | 待硬件确认 |
| `adc.vmax` | V | 3.3 | E/S | 待硬件确认 |
| `adc.sample_rate` | Hz, >0 | 20000 | E/S | 当前等于运动采样率 |
| `adc.lsb` | V/code | `(vmax-vmin)/(2^bits-1)` | E | 派生量 |
| `adc.quantization_rule` | enum | nearest/round after clipping | E | 与阶段7保持一致 |

`adc_model.m`本身可对矩阵逐列量化，但现有调用、验收和串口输出仍按四列建立；这不等于五通道链已经实现。

## 7. 串口参数与协议

| 规范键 | 单位/类型 | 当前绑定或默认值 | 来源 | 状态说明 |
|---|---|---|---|---|
| `serial.mode` | enum | `none/simulation/hardware` | E | 扭矩接口默认使用simulation且关闭实时等待 |
| `serial.port` | string | `COM5` | E/S | 设备相关，运行时配置 |
| `serial.baud_rate` | bit/s | 115200 | E/S | 后续STM32联调时确认 |
| `serial.send_rate` | frame/s | 20000 | E/S | 当前默认等于ADC采样率；需校验链路带宽 |
| `serial.legacy.header` | uint8 | `0xAA` | E | 阶段8兼容协议冻结 |
| `serial.legacy.channel_order` | string[4] | `[main,direction_1,direction_2,direction_3]` | E | 对应A/B/C/D |
| `serial.legacy.endianness` | enum | big-endian uint16 | E | 每通道高字节在前 |
| `serial.legacy.crc` | enum | CRC-16/CCITT-FALSE | E | 覆盖帧头和8字节数据 |
| `serial.legacy.frame_length` | byte | 11 | E | 不允许直接增加第五通道 |
| `serial.extended.version` | integer | 无 | U | 五通道/温度扩展前必须设计 |

链路带宽提醒：11 byte帧在115200 bit/s、8N1条件下的理论上限约为1047 frame/s，现有 `send_rate=20000 frame/s` 只能用于文件仿真，不能作为115200波特率硬件实时发送的可实现配置。真实串口发送率必须在阶段8协议不变的前提下另行限速和验收。

## 8. 现有隐含假设清单

| 隐含假设 | 代码位置/现象 | 冻结处理 |
|---|---|---|
| `r_eff=1e-3 m` | Python扭矩控制器用 `1e-3*effective_angle` | 标为S；阶段11前提升为显式参数 |
| `k_t=0.08 N*m/rad` | Python参数默认值和MATLAB扭矩回退相同 | 标为S；必须由结构计算或标定替换 |
| 非零角度覆盖扭矩角 | `effective_angle`属性 | 仅保留为调试规则，不作为正常测量链 |
| 主/指示光栅相对位移等同切向位移 | 当前接口直接传 `grating_displacement` | 在明确检测半径和光栅编码方向前仅为S |
| 五个传感器外观等于五通道信号已实现 | Python装配已有五个圆柱标记 | 明确否定；目前信号、ADC调用和串口仍为四通道 |
| 温度传感器外观等于已温补 | Python装配有温度圆柱标记 | 明确否定；热模型和数据链均缺失 |
| 20 kframe/s可通过115200串口 | `send_rate=sample_rate=20000` | 仅文件仿真可用；硬件链路不成立 |

## 9. 接口冻结规则

1. `torque`、`torsion_angle`、`grating_relative_displacement`和`optical_phase`必须分别使用 N·m、rad、m、rad，禁止在接口中混用 deg 或 um。
2. `angle`、`grating_displacement`和`phase`作为现有兼容字段保留；新代码应同时提供规范字段并说明二者等价关系。
3. 五通道矩阵固定为 `N x 5`，顺序固定为 `[zero, main, direction_1, direction_2, direction_3]`。
4. 现有四相信号矩阵固定为 `N x 4`，顺序固定为 `[main, direction_1, direction_2, direction_3]`。
5. 现有11字节串口帧继续只承载四路测量通道；任何扩展必须采用可识别的新协议版本。
6. 所有输出必须携带参数快照及来源标记；`S`参数不得用于声称专利尺寸、实测精度或硬件性能。
7. 在零位信号规律、温度模型和机械尺寸补齐前，不得将可视化占位体描述为已完成的功能数字孪生。

## 10. 阶段10状态

参数语义、来源分类、兼容字段、五通道顺序和串口兼容边界已经冻结。本文不改变任何现有运行代码；阶段11只应在上述最小尺寸参数补齐后开展机械模型工作。
