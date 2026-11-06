# 设置项与辅助函数

[English](04-settings-and-helpers.md) · [한국어](04-settings-and-helpers-ko.md) · **中文**

上一篇: [读懂输出：结果表与导出 CSV](03-interpreting-output-zh.md) · 目录: [README](../README.md) · 下一篇: [排错、局限、延伸阅读](05-troubleshooting-zh.md)

---

## 设置项一览（改参数就改这里）

### `settings.raw`（来自 `rawDataFilter()`）

| 设置 | 默认 | 作用 |
|---|---|---|
| `PupilDiameter_Min` / `_Max` | 1.5 / 9 | 范围滤波。**这个默认是毫米**，像素数据必须改（`Examples/Dataset_1` 里改成了 0.1 / inf） |
| `islandFilter_islandSeperation_ms` | 40 | 与其他样本隔开多远算"孤岛" |
| `islandFilter_minIslandWidth_ms` | 50 | 孤岛窄于这个宽度就判无效 |
| `dilationSpeedFilter_MadMultiplier` | 16 | 速度超过几倍 MAD 判无效（抓眨眼边缘） |
| `dilationSpeedFilter_maxGap_ms` | 200 | 样本间隔小于它才算速度 |
| `gapDetect_minWidth` / `_maxWidth` | 75 / 2000 ms | 多宽的缺失算一个"缺口" |
| `gapPadding_backward` / `_forward` | 50 / 50 ms | 缺口前后各再剔多远 |
| `residualsFilter_passes` | 4 | 趋势偏差滤波跑几趟 |
| `residualsFilter_MadMultiplier` | 16 | 偏离趋势线几倍 MAD 判无效 |
| `residualsFilter_interpFs` / `_lowpassCF` | 100 Hz / 16 Hz | 生成趋势线用的重采样率和截止频率 |
| `keepFilterData` | `true` | 保存中间滤波结果。**吃内存**，调完参数后设 `false` |

### `settings.valid`（来自 `ValidSamplesModel.getDefaultSettings()`）

| 设置 | 默认 | 作用 |
|---|---|---|
| `interp_upsamplingFreq` | 1000 Hz | 平滑信号的采样率 |
| `LpFilt_B` / `LpFilt_A` | 由 4 阶、4 Hz 截止算出 | 低通滤波器系数（零相位 `filtfilt`） |
| `interp_maxGap` | 250 ms | 真实 valid 点之间间隔超过它，那一段平滑信号置 `NaN` |

## `helperFunctions/` 每个文件

| 文件 | 干什么 |
|---|---|
| `rawDataFilter.m` | 主函数依次调：`removeOutOfBounds`（范围）→ `madSpeedFilter`（速度，抓眨眼）→ `madDeviationFilter`（偏离趋势线）。孤立点清理 `removeLoners` 在三步内部反复调用，`expandGaps`（缺口前后扩剔）在速度滤波里调用；`madCalc` 算 MAD 阈值。无参数调用返回默认设置 |
| `genMeanDiaSamples.m` | 双眼合成平均直径，由 `processValidSamples` 调用；单眼数据用不到 |
| `plotSegments.m` | 把分段表画成色块，由 `plotData` 调用 |
| `printToConsole.m` | 往终端打印进度，内部用 |
| `legacyModeCheck.m` | MATLAB 低于 8.3（没有 `table`）时把 `LEGACY/` 加进路径，新版本什么也不做 |
| `FALLBACK/` | `butter`、`filtfilt`、`histc`、`nanmin` / `nanmax` / `nanmean` / `nanmedian` 的替代实现，用于缺工具箱或函数被移除的 MATLAB |
| `LEGACY/` | 给老 MATLAB 模拟 `table` |

**`FALLBACK` 的陷阱：** `addpath(genpath(...))` 默认把文件夹放到路径**最前面**，FALLBACK 的同名函数会盖住真工具箱函数。想优先用工具箱就用 `addpath(..., '-end')`。本机 MATLAB 没有 Statistics 工具箱，`nan*` 系列走的就是 FALLBACK。

---

上一篇: [读懂输出：结果表与导出 CSV](03-interpreting-output-zh.md) · 目录: [README](../README.md) · 下一篇: [排错、局限、延伸阅读](05-troubleshooting-zh.md)
