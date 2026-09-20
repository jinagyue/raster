# 光栅扭矩数字孪生论文草稿

状态：`DRAFT_NOT_SUBMISSION_READY`

本目录是从当前 MATLAB/Python 工程中独立整理出的 LaTeX 论文初稿，定位为光电测量、智能仪器和数字孪生方向的工程研究型普刊稿件。当前按《电子测量技术》方向组织内容，排版沿用工作区中已有的中文学报模板风格，正式投稿前仍需按目标期刊最新模板复核。

## 编译

在本目录执行：

```powershell
xelatex main.tex
bibtex main.aux
xelatex main.tex
xelatex main.tex
```

## 证据范围

- 阶段14和阶段15的定量结果来自 `Grating_Digital_Twin/data/` 中的 CSV、MAT 和报告文件，属于 `simulation/default` 仿真证据。
- 机械尺寸、材料参数和温度系数尚未由实物图纸、材料证书或标定实验确认。
- 阶段16的 GUI、MATLAB Engine、ADC 和串口帧结果证明软件闭环与协议帧生成/预览，不等同于真实 COM 硬件通信或传感器性能验证。
- 五通道零位/分相信号用于仿真基准；当前实际 ADC 与旧版串口帧仍为四通道。
- 作者、单位、基金、收稿日期和部分参考文献需要在投稿前由作者核实，不能直接作为最终投稿包。

## 文件

- `outline.md`：论文主线、章节职责、图表计划和投稿前补证清单。
- `claim_evidence_map.md`：主张-证据映射和风险标记。
- `main.tex`：可编译中文/英文双语论文初稿。
- `references.bib`：从工作区已有模板复制的候选文献库，需逐条核验。
- `figures/`：从已有阶段14/15结果目录复制的 PDF 图件。
