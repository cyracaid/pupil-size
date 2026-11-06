# 读懂输出：结果表与导出 CSV

[English](03-interpreting-output.md) · [한국어](03-interpreting-output-ko.md) · **中文**

上一篇: [四个数据模型：输入与输出](02-data-models-zh.md) · 目录: [README](../README.md) · 下一篇: [设置项与辅助函数](04-settings-and-helpers-zh.md)

---

## `analyzeSegments` 的输出表

每个对象一张表：**先是你的 `segmentsTable` 全部列，再横向接上每只眼的 10 列**。列名前缀按眼：`leftPupil_`、`rightPupil_`、`meanPupil_`。我们的数据只有一只瞳孔，所以只有 `leftPupil_*`。

| 列（去掉前缀） | 单位 | 怎么算 |
|---|---|---|
| `SmoothSig_meanDiam` | 原始单位 | 段内平滑信号的均值，`NaN` 不计 |
| `SmoothSig_minDiam` / `SmoothSig_maxDiam` | 原始单位 | 段内平滑信号最小 / 最大 |
| `SmoothSig_missingDataPercent` | % | 段内 `NaN` 的个数 ÷ 段内样本数 × 100 |
| `SmoothSig_sampleCount` | 个 | 段内 1000 Hz 样本总数，**含 `NaN`** |
| `ValidSamples_meanDiam` | 原始单位 | 段内 valid 原始点的均值 |
| `ValidSamples_minDiam` / `ValidSamples_maxDiam` | 原始单位 | 段内 valid 原始点最小 / 最大 |
| `ValidSamples_validPercent` | % | `validFraction × 100`，**整段记录的值，不是这一段的** |
| `ValidSamples_sampleCount` | 个 | 段内 valid 原始点数 |

段的取值区间是左闭右开：`[segmentStart, segmentEnd)`。

**什么时候整行是 `NaN`：**
- 该段 `segmentStart` 或 `segmentEnd` 本身是 `NaN`（例如 trk 里缺了对应事件）。
- 该段时间范围内没有任何平滑信号样本 → `SmoothSig_*` 全 `NaN`。
- 该段时间范围内没有任何 valid 点 → `ValidSamples_*` 全 `NaN`。

表头还带 `VariableUnits` 和 `VariableDescriptions`，在 MATLAB 里用 `PupilResults.Properties.VariableDescriptions` 可以直接看到每列的英文定义。**存成 CSV 时这两项会丢**，所以要看列的含义，请看 [`../docs/02_column_dictionary.md`](../../docs/02_column_dictionary.md)。

## `exportSegments` 的输出文件

```matlab
opts.Eyes         = {'left'};          % 可选 'left' 'right' 'mean'，默认全部
opts.SegmentTypes = {'countdown'};     % 需要 segmentsTable 里有 segmentType 列；默认全部
opts.NaNString    = 'NaN';             % 缺失怎么写；'' 写空格子
opts.ZScore       = false;             % true 多一列 pupilDiameterZ
hPupilData.exportSegments('out_folder', opts);
```

每个对象、每只眼写一个文件，名字是 `<原文件名去扩展名>_<eye>pupil_segments.csv`，例如 `sub149_leftpupil_segments.csv`。

| 列 | 含义 |
|---|---|
| `segmentName` | `segmentsTable.segmentName` |
| `segmentType` | `segmentsTable.segmentType`；没有这一列则为空 |
| `segmentStart_s` | 该段起点（秒），同一段所有行相同 |
| `tRel_s` | 样本时刻 − 段起点（秒），从 0 开始 |
| `pupilDiameter_<unit>` | 平滑后的直径，4 位小数；`NaN` 按 `NaNString` 写。列名里的单位来自 `diameterUnit`，如 `pupilDiameter_px` |
| `gap_ms` | 同上面的 `gap_ms`，1 位小数 |
| `pupilDiameterZ` | 仅 `ZScore=true`：(值 − 全程均值) ÷ 全程标准差，**整段记录、每只眼各算一次**（Leuchs 2017），不是段内 z |

一行 = 一个 1000 Hz 样本，所以一个 10 秒的段约有 10000 行。没有任何样本的段不写。

---

上一篇: [四个数据模型：输入与输出](02-data-models-zh.md) · 目录: [README](../README.md) · 下一篇: [设置项与辅助函数](04-settings-and-helpers-zh.md)
