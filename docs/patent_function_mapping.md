# 阶段10：专利功能映射与接口冻结

## 1. 文档目的与边界

- 冻结对象：`Grating_Digital_Twin`、`Optical_Grating_Torque_DigitalTwin` 和 `Circular_Grating_Digital_Twin` 之间的物理量语义、通道定义与数据接口。
- 专利依据：用户提供的“一种面向光栅的转动体扭矩在线测量装置”。本阶段采用专利给出的结构名称和功能关系，不从附图比例反推制造尺寸。
- 工程依据：阶段1-9已经验收的 MATLAB 信号链，以及现有 Python 圆光栅、扭矩装配与 MATLAB Engine 桥接代码。
- 本阶段只建立文档和接口约束，不修改阶段1-9核心算法，不新增五通道算法，不改串口帧，不进行阶段11三维机械建模。

## 2. 参数来源标记

| 标记 | 含义 | 使用规则 |
|---|---|---|
| E | 来自现有工程 | 已有变量或代码实体；数值仍可能只是现有工程默认值 |
| P | 来自专利 | 专利明确给出部件、功能或拓扑关系；不等同于给出精确尺寸 |
| U | 尚未知 | 需要专利补充、机械图纸、实物测量或标定后确定 |
| S | 当前仅用于仿真 | 为连通仿真链而设的假定值，不得写成专利参数或实测参数 |

一个参数可以同时标为 `E/S`：表示代码中已经存在，但当前数值只是仿真假设。

## 3. 专利结构与软件变量映射

| 专利结构 | 专利功能 | 当前软件映射 | 来源 | 当前状态与边界 |
|---|---|---|---|---|
| 扭轴 | 承受扭矩并产生扭转角 | `Optical_Grating_Torque_DigitalTwin/model/shaft.py`；`torque`、`shaft_radius`、`shaft_length`、`torsional_stiffness`、`effective_angle` | P + E/S | 几何和集中刚度模型已存在；真实材料、极惯性矩、有效扭转段及标定刚度未知 |
| 测量腔体 | 容纳并保护光栅、光路和检测组件 | `model/housing.py`；`housing_length`、`housing_radius`、`wall_thickness` | P + E/S | 当前为同轴圆筒壳体；默认尺寸是可视化参数，不是专利尺寸 |
| 前、后端盖 | 封闭、防尘并形成装配接口 | `model/flange.py`；`left_flange`、`right_flange`、`flange_radius`、`flange_thickness`、`bolt_number`、`bolt_circle_radius` | P + E/S | 当前以两端法兰近似；孔径硬编码为 1.2 mm，连接方式、密封结构和公差未知 |
| 主光栅 | 随扭轴侧运动，形成相对光栅位移 | `model/grating_disk.py`；MATLAB `p.grating.*`；`disk_radius`、`disk_thickness`、`grating_period`、`line_number` | P + E/S | 已有圆盘和同心纹理显示；光栅截面、材料、有效读数半径与安装基准未知 |
| 指示光栅 | 与主光栅形成相对运动和光强调制 | `model/optical_readout.py` 的 `indicator_grating_housing`；MATLAB 的 `reference_shift`/相对位移概念 | P + E/S | 只有外观壳体和相对位移语义；尚无独立指示光栅实体、间隙和安装参数 |
| 零位传感器 | 提供零位或周期基准 | `optical_readout.py` 的第五个传感器外观；冻结名 `sensor.zero` | P + E | 只有几何占位，没有零位信号生成、触发逻辑、ADC通道或串口字段 |
| 主检测传感器 | 获取主测量信号 | MATLAB 四相信号第1列，冻结名 `sensor.main`，相位偏置 `0` | P + E | 可映射到现有 A 通道；专利中的真实安装相位和极性仍需确认 |
| 1号辨向细分传感器 | 与主检测信号构成辨向/细分关系 | MATLAB 四相信号第2列，冻结名 `sensor.direction_1`，名义相位偏置 `pi/2` | P + E | 可映射到现有 B 通道；真实相位误差由标定确定 |
| 2号辨向细分传感器 | 与其他检测信号构成辨向/细分关系 | MATLAB 四相信号第3列，冻结名 `sensor.direction_2`，名义相位偏置 `pi` | P + E | 可映射到现有 C 通道；真实相位误差由标定确定 |
| 3号辨向细分传感器 | 与其他检测信号构成辨向/细分关系 | MATLAB 四相信号第4列，冻结名 `sensor.direction_3`，名义相位偏置 `3*pi/2` | P + E | 可映射到现有 D 通道；真实相位误差由标定确定 |
| 温度传感器 | 获取温度，供温漂评估或补偿 | `optical_readout.py` 的 `temperature_sensor` 外观；冻结名 `sensor.temperature` | P + E | 只有几何占位；无温度变量、热模型、补偿公式、ADC映射或串口字段 |

说明：专利结构中的“零位传感器 + 主检测传感器 + 3个辨向细分传感器”共五路光栅传感通道；温度传感器是独立辅助通道，不计入上述五路光栅通道。

## 4. 冻结的完整物理链

### 4.1 物理量与公式

| 链路 | 冻结变量 | 单位 | 冻结关系 | 当前实现情况 |
|---|---|---:|---|---|
| Torque | `torque`，符号 `T` | N·m | 外部输入 | Python/MATLAB接口已有 |
| torsion angle | `torsion_angle`，符号 `theta_torsion` | rad | `theta_torsion = T / k_t` | 已有 `torsional_stiffness=0.08`，但该数值为 S |
| grating relative displacement | `grating_relative_displacement`，符号 `x_rel` | m | `x_rel = x_bias + r_eff * theta_torsion` | 当前使用硬编码 `r_eff=1e-3 m`，为 S；必须参数化后才能作为物理模型 |
| optical phase | `optical_phase`，符号 `phi_opt` | rad | `phi_opt = 2*pi*x_rel/P + phi0` | MATLAB已有 `2*pi*x/P`；`phi0`待定义 |
| five sensor channels | `five_sensor_channels` | a.u. 或 V | 顺序固定为 `[zero, main, direction_1, direction_2, direction_3]` | 当前只有后四路正交信号；零位波形缺失 |
| ADC | `adc_code` | code | `round((clip(V)-Vmin)/(Vmax-Vmin)*(2^bits-1))` | MATLAB ADC可处理矩阵，但现有调用和验收基于四列 |
| serial | `serial_status`/二进制帧 | byte | 固定采样周期输出 | 现有协议只允许四路 ADC，不包含零位和温度 |

完整链的冻结表达式为：

```text
T [N*m]
  -> theta_torsion = T/k_t [rad]
  -> x_rel = x_bias + r_eff*theta_torsion [m]
  -> phi_opt = 2*pi*x_rel/P + phi0 [rad]
  -> [zero, main, direction_1, direction_2, direction_3]
  -> ADC codes
  -> serial frame
```

四路测量通道的名义模型继续沿用阶段3-5：

```text
s_main       = A0*cos(phi_opt + 0       + delta_phi0) + B0 + n0
s_direction1 = A1*cos(phi_opt + pi/2    + delta_phi1) + B1 + n1
s_direction2 = A2*cos(phi_opt + pi      + delta_phi2) + B2 + n2
s_direction3 = A3*cos(phi_opt + 3*pi/2  + delta_phi3) + B3 + n3
```

零位通道的光学结构、脉冲宽度、有效电平和每转/每周期基准数量尚未知，因此阶段10只冻结通道名称与顺序，不臆造其公式。

### 4.2 通道语义冻结

| 索引 | 规范名称 | 兼容名称 | 名义相位 | 当前可用 |
|---:|---|---|---:|---|
| 1 | `zero` | 无 | U | 否，只有三维占位 |
| 2 | `main` | `A`/四相信号第1列 | 0 | 是 |
| 3 | `direction_1` | `B`/四相信号第2列 | `pi/2` | 是 |
| 4 | `direction_2` | `C`/四相信号第3列 | `pi` | 是 |
| 5 | `direction_3` | `D`/四相信号第4列 | `3*pi/2` | 是 |

任何后续代码不得仅凭列数猜测通道含义；五通道接口必须附带上述顺序元数据。

### 4.3 串口兼容性冻结

阶段8现有帧保持不变：

```text
AA | A_H A_L | B_H B_L | C_H C_L | D_H D_L | CRC_H CRC_L
```

- 共 11 byte，四路 `uint16` 大端，CRC-16/CCITT-FALSE，波特率默认 115200。
- A/B/C/D固定对应 `main/direction_1/direction_2/direction_3`。
- 零位和温度不得无版本标识地塞入现有帧，否则会破坏阶段8和STM32兼容性。
- 若后续需要传输零位或温度，必须另行设计带版本号/长度/消息类型的新协议，并保留上述旧帧解码路径；该工作不属于阶段10。

## 5. 冻结的软件接口

### 5.1 当前兼容输入（不改代码）

`python_control('run_torque', input_parameter)` 当前接受：

| 字段 | 单位 | 状态 |
|---|---:|---|
| `torque` | N·m | 已实现 |
| `angle` | rad | 已实现；非空时可直接指定 |
| `grating_displacement` | m | 已实现；非空时可直接指定 |
| `grating_period` | m | 已实现 |
| `serial_mode` | - | 已实现 |

### 5.2 阶段11及以后采用的规范输入名

| 规范字段 | 单位 | 必需性 | 当前绑定 |
|---|---:|---|---|
| `torque` | N·m | 必需 | 已绑定 |
| `torsional_stiffness` | N·m/rad | 必需 | Python已有默认值，MATLAB尚未通过载荷传入 |
| `effective_detection_radius` | m | 必需 | 当前被硬编码为 `1e-3` |
| `displacement_bias` | m | 必需，可为0 | 当前对应 `grating_displacement` 的偏置语义 |
| `grating_period` | m | 必需 | 已绑定 |
| `optical_phase_zero` | rad | 必需，可为0 | 未实现 |
| `temperature` | degC | 可选 | 未实现 |
| `serial_mode` | enum | 可选 | 已绑定 |

### 5.3 规范输出语义

后续接口应返回以下语义；本阶段只冻结名称，不实现新字段：

```text
status
torque
torsion_angle
grating_relative_displacement
optical_phase
zero_channel
four_phase_signal
five_sensor_channels          # [zero, main, direction_1, direction_2, direction_3]
adc_code
serial_status
parameter_snapshot
model_validity
```

当前 `run_torque` 已返回的 `angle`、`grating_displacement`、`phase`、`four_phase_signal`、`adc_code` 和 `serial_status`继续保留为兼容字段。新规范字段的真正落地必须在后续阶段单独验收。

## 6. 阶段11机械模型最小尺寸参数清单

以下是建立可装配、可检查干涉且能支撑 `T -> theta -> x_rel` 的最小集合。没有这些尺寸时，只能得到示意外观，不能称为结构数字孪生。

| 优先级 | 参数 | 规范键 | 单位 | 当前值/来源 | 阶段11要求 |
|---|---|---|---:|---|---|
| 必需 | 扭轴总长 | `mechanical.shaft.length` | m | 0.070，E/S | 用图纸或实测替换 |
| 必需 | 扭轴外径 | `mechanical.shaft.diameter` | m | 0.008，E/S | 用图纸或实测替换 |
| 必需 | 有效扭转段长度 | `mechanical.shaft.torsion_length` | m | U | 必须补齐 |
| 必需 | 有效扭转段直径/截面 | `mechanical.shaft.torsion_diameter` | m | U | 必须补齐 |
| 必需 | 轴端连接尺寸与基准 | `mechanical.shaft.end_interface` | m | U | 必须补齐 |
| 必需 | 腔体内径、外径、轴向长度 | `mechanical.housing.inner_diameter/outer_diameter/length` | m | 可由现有默认值推得，E/S | 用图纸或实测替换 |
| 必需 | 前后端盖外径与厚度 | `mechanical.covers.front/rear.*` | m | 当前共用法兰参数，E/S | 分别确认 |
| 必需 | 端盖/腔体配合深度及间隙 | `assembly.cover_fit.*` | m | U | 必须补齐 |
| 必需 | 法兰直径、厚度、孔数、孔径、分度圆 | `mechanical.flange.*` | m/- | 部分E/S；孔径代码内固定 | 全部显式参数化 |
| 必需 | 主光栅外径、内孔、厚度 | `optical.main_grating.*` | m | 仅外径/厚度有E/S | 补内孔和安装基准 |
| 必需 | 指示光栅外径、内孔、厚度 | `optical.indicator_grating.*` | m | U | 必须补齐 |
| 必需 | 两光栅轴向间隙 | `optical.grating_gap` | m | U | 必须补齐 |
| 必需 | 光栅节距及纹线方向 | `optical.grating_period/direction` | m/enum | 节距20e-6，E/S；方向U | 确认实际编码形式 |
| 必需 | 主/指示光栅安装面轴向位置 | `assembly.grating_z.*` | m | 当前由经验偏移计算，E/S | 改为装配尺寸 |
| 必需 | 有效检测半径 | `optical.effective_detection_radius` | m | 1e-3，代码硬编码S | 图纸/光路确定 |
| 必需 | 五个光栅传感器的中心位置和安装角 | `sensor.grating[i].pose` | m/rad | 仅示意位置，E/S | 明确5组位姿 |
| 必需 | 零位标记的几何宽度与数量 | `optical.zero_mark.*` | m/- | U | 决定零位信号模型 |
| 建议 | 光源和聚光镜尺寸、轴向距离 | `optical.source/lens.*` | m | 当前为E/S | 光路可信度所需 |
| 建议 | 温度传感器封装尺寸和安装位置 | `sensor.temperature.pose/size` | m | 当前为E/S | 热耦合建模所需 |
| 建议 | 材料、弹性模量、泊松比 | `material.*` | SI | U | 从集中刚度升级到结构模型时必需 |
| 建议 | 装配公差、同轴度和端面跳动 | `assembly.tolerance.*` | m/rad | U | 误差敏感性研究所需 |

阶段11开始前，至少应获得上述“必需”项的图纸值、实测值或明确的仿真假设版本；每个假设都必须保留 `S` 标记。

## 7. 已识别的接口缺口

1. 现有光电、误差、相位解算和串口链均为四通道；专利光栅检测拓扑为五通道。
2. 零位传感器只有可视化实体，没有信号定义、ADC和通信字段。
3. 温度传感器只有可视化实体，没有热漂移模型和数据接口。
4. `effective_detection_radius=1e-3 m` 当前在 Python 控制器中硬编码。
5. `torsional_stiffness=0.08 N*m/rad` 是仿真默认值，MATLAB接口还存在相同数值的回退计算；尚无实物标定依据。
6. 指示光栅尚未形成独立实体参数集，主/指示光栅间隙未知。
7. 当前串口协议严格限制四路数据；五路与温度传输必须采用版本化协议。

## 8. 阶段10验收结论

- [x] 三个现有工程已完成只读接口审计。
- [x] 用户指定的10类专利结构已映射到软件实体或明确标为缺失。
- [x] `Torque -> torsion angle -> grating relative displacement -> optical phase -> five sensor channels -> ADC -> serial` 已冻结。
- [x] 参数来源已按 E/P/U/S 分类。
- [x] 阶段11最小机械尺寸清单已给出。
- [x] 阶段1-9核心算法和现有四通道串口协议未修改。

**阶段10结论：通过（文档与接口语义冻结通过）。** 五通道零位信号、温度补偿和新版串口协议仍属于后续实现项，不能视为本阶段已实现功能。
