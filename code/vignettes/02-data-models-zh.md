# 四个数据模型：输入与输出

[English](02-data-models.md) · [한국어](02-data-models-ko.md) · **中文**

上一篇: [上手：流程、术语、例子](01-getting-started-zh.md) · 目录: [README](../README.md) · 下一篇: [读懂输出：结果表与导出 CSV](03-interpreting-output-zh.md)

---

## 四个类的输入输出

### `RawFileModel` — 写 .mat

```matlab
obj = RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename);
% 或先构造，再 obj.saveMatFile('x.mat')
```

输入检查（不满足会直接 `assert` 报错）：
- `diameter` 必须有 `t_ms`、`L`、`R` 三个字段；`L` 或 `R` 可以为空（没测那只眼），非空时长度必须等于 `t_ms`。
- `t_ms` 必须升序（`issorted`）。官方建议从 0 开始。
- `segmentsTable` 必须有 `segmentStart`、`segmentEnd`、`segmentName`；其他列（条件、文件名等）会原样带到结果表里。

输出：一个 `.mat`，里面是 `diameter`、`diameterUnit`、`zeroTime_ms`、`segmentsTable` 四个变量。

### `PupilDataModel` — 总指挥

| 方法 | 输入 | 输出 | 终端打印 |
|---|---|---|---|
| `PupilDataModel.batchConstructor(folder, dirStruct, settings)` | 文件夹、`dir('*.mat')` 的结果、设置 | `PupilDataModel` 对象数组 | `Constructing N Data Objects...` / `File i (name): Object constructed.` |
| `filterRawData()` | — | 每只眼的 `isValid` 写进对象 | `Filtering the raw data in N files...` |
| `processValidSamples()` | — | `leftPupil_ValidSamples`、`rightPupil_ValidSamples`，两只眼都有时再加 `meanPupil_ValidSamples` | `Interpolating and smooting the valid raw data subsets of N files...` |
| `analyzeSegments()` | — | **cell 数组**，每个对象一个结果表；用 `vertcat(results{:})` 合并 | `File i (name): analyzing K segments.` |
| `exportSegments(folder, options)` | 输出文件夹、可选 options | 每个对象每只眼一个 CSV（见 [03](03-interpreting-output-zh.md)） | `File i (name) left pupil: wrote N samples to <file>` |
| `plotData()` | — | 图形窗口 | — |

必须按固定顺序调：`processValidSamples` 要用 `isValid`，`analyzeSegments` 要用平滑信号。

### `RawSamplesModel` — 一只眼的原始样本

- 属性：`rawSample`、`isValid`（逻辑向量）、`speedFiltData`、`devFiltData`（中间滤波结果，只在 `keepFilterData=true` 时保存）。
- 设置：`settings.raw`，默认值来自 `rawDataFilter()`（无参数调用返回设置结构）。

### `ValidSamplesModel` — 一只眼的 valid 样本

- 输入：valid 点的 `t_ms`、`pupilDiameter`，和 `validFraction`。构造时就自动做插值+低通。
- 少于 2 个 valid 点会报错 `Interpolation cannot be performed.`
- 输出：`signal` 结构，三个等长向量：

| 字段 | 单位 | 含义 |
|---|---|---|
| `t` | 秒 | 1000 Hz 的时间轴 |
| `pupilDiameter` | 同原始单位 | 平滑后的直径；缺口大于 `interp_maxGap` 的位置是 `NaN` |
| `gap_ms` | ms | 这个时刻前后两个**真实 valid 点**之间的间隔。离某个真实点不到 0.5 ms（半个上采样周期）时记 0 |

---

上一篇: [上手：流程、术语、例子](01-getting-started-zh.md) · 目录: [README](../README.md) · 下一篇: [读懂输出：结果表与导出 CSV](03-interpreting-output-zh.md)
