# 上手：流程、术语、例子

[English](01-getting-started.md) · [한국어](01-getting-started-ko.md) · **中文**

目录: [README](../README.md) · 下一篇: [四个数据模型：输入与输出](02-data-models-zh.md)

---

## 一眼看懂：整条流程

```
眼动仪原始文件（EDF / gazedata / trk …）
        │  转换器：每台眼动仪自己写一份（Examples/*/batchFileConverter_*.m）
        ▼
RawFileModel ──saveMatFile──▶  <name>.mat
                               ├ diameter      : t_ms, L, R（左/右瞳孔，没测的那只留空）
                               ├ diameterUnit  : 'mm' / 'px' …
                               ├ zeroTime_ms   : 仅存档，包里不用
                               └ segmentsTable : segmentName, segmentStart, segmentEnd（+ 任意附加列）
        │
        ▼  PupilDataModel.batchConstructor(...)        ← 读 .mat，每个文件一个对象
        │
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter
        │                    产出：每个原始样本一个 isValid（true/false）
        ▼
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth
        │                    产出：1000 Hz 的平滑信号 signal.t / pupilDiameter / gap_ms
        ▼
 (3) analyzeSegments()       ValidSamplesModel.analyze
        │                    产出：每段 10 个统计量（每只眼一组）
        ├─▶ (4) exportSegments(folder, options)   每段的连续时间曲线 → CSV
        └─▶ (5) plotData()                         目视检查（需要桌面 MATLAB）
```

## 设计要点

- **只标记，不改原始数据。** (1) 只是给每个样本打 `isValid`，原始直径 `rawSample` 一直保留。
- **valid 样本和平滑信号是两样东西。** (2) 把 valid 样本插值、低通后得到连续信号；缺口太大的地方不补，直接置 `NaN`。(3) 里 `SmoothSig_*` 算的是平滑信号，`ValidSamples_*` 算的是真正测到的点。
- **所有阈值都在 `getDefaultSettings()` 里。** 改参数不用动算法。
- **每个对象带自己的设置。** `settings.raw` 给滤波，`settings.valid` 给插值和低通。
- **左、右、均值三套结果。** 有哪只眼的数据就分析哪只；两只都有时多出一条 `mean`。

## 术语表

| 术语 | 含义 | 出处 |
|---|---|---|
| raw sample（原始样本） | 眼动仪给的原始直径点，含眨眼、噪声 | `RawSamplesModel.rawSample` |
| valid sample（有效样本） | 通过全部伪影滤波的原始点 | `RawSamplesModel.isValid == true` |
| smooth signal（平滑信号） | valid 点线性插值到 1000 Hz 后做 4 阶低通 | `ValidSamplesModel.signal` |
| gap（缺口） | 相邻两个 valid 点之间的时间间隔（ms） | `signal.gap_ms` |
| segment（分段） | 要分析的一个时间窗，有名字和起止（**单位秒**） | `segmentsTable` |
| `validFraction` | 全程 valid 点数 ÷ 全程非空原始点数，**整段记录的值，不是某一段的** | `PupilDataModel.processValidSamples` |
| MAD | 中位数绝对偏差，阈值写成"几倍 MAD" | `rawDataFilter` |

时间单位注意：`t_ms` 是**毫秒**；`segmentStart` / `segmentEnd` 和 `signal.t` 是**秒**。

## `Examples/`

| 文件夹 | 数据 | 文件 |
|---|---|---|
| `Dataset_1/` | SR-Research Eyelink，**单瞳** | `batchFileConverter_Dataset1.m`（EDF → .mat），`main_Dataset1.m`（完整流水线） |
| `Dataset_2/` | E-Prime + Tobii，**双瞳** | `batchFileConverter_Dataset2.m`（.gazedata → .mat），`main_Dataset2.m`（完整流水线） |

`main_Dataset1.m` 的步骤就是 (1) 到 (5) 的最短示范：设置里把 `PupilDiameter_Max` 设为 `inf`、`PupilDiameter_Min` 设为 0.1（因为该数据是任意单位），`keepFilterData = true` 便于画图，然后依次调 `filterRawData`、`processValidSamples`、`analyzeSegments`，最后 `vertcat(results{:})` 合成总表，`plotData` 看图。
我们的 YMTC 数据走的是和 Dataset_1 同一类单瞳流程，转换器换成了 `ymtc/` 里的 `trk2csv`；批量运行用的是 `代码_matlab/example_kret_pipeline.m`（在仓库外，随数据放在一起）。

---

目录: [README](../README.md) · 下一篇: [四个数据模型：输入与输出](02-data-models-zh.md)
