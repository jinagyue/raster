# 主张-证据映射

状态：`DRAFT_NOT_SUBMISSION_READY`

| ID | 拟写主张 | 类型 | 证据 | 范围与边界 | 风险 |
|---|---|---|---|---|---|
| C01 | 平台实现了扭矩到机械位移、光学相位、四相信号、ADC 和串口帧预览的模块化链路。 | 观察/实现 | `README.md`；`Grating_Digital_Twin/model/`、`signal/`、`interface/`、`communication/`；`Optical_Grating_Torque_DigitalTwin/data_stage16_acceptance.md` | 软件仿真链；不等于实物传感器。 | 中 |
| C02 | 平台支持五通道仿真基线，其中零位通道用于相位参考，实际旧版 ADC/串口链仍是四通道。 | 观察/接口边界 | `patent_five_channel_signal.m`；`patent_baseline_decoder.m`；`docs/patent_function_mapping.md`；`config/system_parameter_schema.md` | 仿真模型与现有通信协议分开。 | 低 |
| C03 | 14 类工况共生成 70 条方法-工况记录，当前 CSV 中 69 条为 ok、1 条为 warning，没有按结果删除记录。 | 观察 | `stage14_results.csv`；`stage14_report.md`；`stage14_comparison.m` | 当前随机种子和 2001 点、1 s 配置。 | 低 |
| C04 | 五通道 1/32 计数基线的全工况平均 RMSE 为 0.384 um，最差 RMSE 为 0.728 um，最差工况为 SNR=10 dB。 | 比较 | `stage14_method_summary.csv`；`stage14_results.csv`；图2 | 仅对当前仿真默认参数和 14 类工况成立。 | 中 |
| C05 | 直接 atan2 和改进法在当前反向扭矩工况下出现较大最差 RMSE。 | 比较 | `stage14_method_summary.csv`；图2、图3 | 最差工况为 `torque_neg1Nm`；不是所有工况的普遍结论。 | 中 |
| C06 | 零扭矩静态点触发改进法的秩亏警告。 | 观察/机制解释 | `stage14_results.csv` 中 `torque_0Nm` 行；`stage14_comparison.m`；`phase_estimation.m` | “静态点导致轨迹退化”是基于模型的机制解释，需实验验证。 | 中 |
| C07 | 温度模型在 -20 到 80 degC 范围内给出 -1.186% 到 +1.833% 的灵敏度变化，未补偿最大扭矩 RMSE 为 0.084655 N.m。 | 观察 | `stage15_temperature_summary.csv`；`stage15_report.md`；图5、图6 | 一阶线性温度系数，全部 `simulation/default`。 | 中 |
| C08 | 在同一内部模型中使用温度参数进行逆补偿后，扭矩误差返回到数值计算零附近。 | 比较 | `stage15_temperature_summary.csv`；`temperature_model.m` | 只证明模型内部一致性，不证明真实温补精度。 | 高 |
| C09 | 阶段16完成 GUI/VTK、MATLAB Engine、信号、ADC 和协议帧预览的自动验收。 | 观察/实现 | `data_stage16_acceptance.md`；`tests/stage16_acceptance.py` | 串口为帧生成/预览，未验证真实 COM 硬件通信。 | 中 |
| C10 | 当前机械尺寸、材料参数和温度系数不能写成专利实测或器件标定值。 | 边界声明 | `docs/patent_function_mapping.md`；`config/system_parameter_schema.md`；`stage15_report.md` | 必须保留在摘要、方法和讨论中。 | 低 |

## 暂不允许写入正文的主张

1. “已达到某商业传感器的测量精度”。
2. “已完成 STM32/真实 COM 端口硬件通信验证”。
3. “已复原专利装置的真实尺寸和结构”。
4. “温度补偿完全消除了实际温漂”。
5. “协方差白化算法等同于完整 Heydemann 椭圆拟合”，除非代码和引用进一步补齐。
