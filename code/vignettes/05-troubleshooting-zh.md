# 排错、局限、延伸阅读

[English](05-troubleshooting.md) · [한국어](05-troubleshooting-ko.md) · **中文**

上一篇: [设置项与辅助函数](04-settings-and-helpers-zh.md) · 目录: [README](../README.md)

---

## 常见问题：症状 → 原因 → 修法

| 症状 | 原因 | 修法 |
|---|---|---|
| `'t_ms' must be sorted!` | 时间戳不升序（trk 里有重复或倒退的时间戳） | 转换器里先排序，不要在包里补；重复时间戳要单独记录 |
| `'L' must be empty, or have the same length as 't_ms'` | 直径向量和时间向量长度不一致 | 转换器里检查长度 |
| `No settings present.` | 构造 `PupilDataModel` 时没传 `settings` | 用 `PupilDataModel.getDefaultSettings()` 取一份再改 |
| `Interpolation cannot be performed.` | 这只眼 valid 点少于 2 个（范围设错或数据全是噪声） | 检查 `PupilDiameter_Min/Max` 是否匹配单位 |
| 几乎所有样本都被判无效 | 默认范围 1.5–9 是毫米，像素数据全在范围外 | 按实际单位改范围 |
| `pupilSize:edgeClamp` 警告 | 上采样时间点浮点误差落到 valid 区间外，被夹回边界 | 只是提示；个数多才需要查数据 |
| `ValidSamples_validPercent` 每行都一样 | 它本来就是全程值 | 看某段缺失多少用 `SmoothSig_missingDataPercent` |
| `SmoothSig_meanDiam` 正常但数据其实很差 | 小于 250 ms 的缺口被插值填平了 | 同时看 `missingDataPercent` 和 `ValidSamples_sampleCount` |
| `plotData` 没反应或被跳过 | `-batch` 没有桌面 | 在桌面 MATLAB 里跑 |
| `plotData` 只画一个文件 | 源码里 `plotMultipleFiles = false`，多文件很吃资源 | 想画多个就改 `PupilDataModel.m` 里的这个开关 |
| `Examples` 里 `addpath` 报找不到路径 | 路径写成 `..\..\helperFunctions\`（Windows 反斜杠） | macOS / Linux 改成 `../../helperFunctions/` |

## 局限

- 原版 README 写明依赖 Signal Processing 和 Statistics 两个工具箱，测试环境是 Windows 7 上的 MATLAB 2012b / 2016a / 2017a。本仓库为 macOS 做了补丁（`PupilDataModel` 的路径分隔符、`FALLBACK/`），改动见 `git log`；批量运行脚本 `代码_matlab/example_kret_pipeline.m` 在仓库外。
- 滤波参数是论文默认值，**没有针对 YMTC 数据调过**。要调需要桌面 MATLAB 用 `plotData()` 看原始轨迹。
- 本页只描述代码做了什么，不判断结果好坏。数据质量见 [`../docs/05_data_quality.md`](../../docs/05_data_quality.md)。

## 延伸阅读

[`../docs/01_pipeline_overview.md`](../../docs/01_pipeline_overview.md)（一页看懂流水线）· [`../docs/02_column_dictionary.md`](../../docs/02_column_dictionary.md)（每列的定义）· [`../docs/03_pupil_size_internals.md`](../../docs/03_pupil_size_internals.md)（滤波和插值原理）· [`ymtc/README.md`](../ymtc/README.md)、[`../docs/04_our_code.md`](../../docs/04_our_code.md)（我们加的代码）· [`../docs/06_faq.md`](../../docs/06_faq.md)（常见坑）。

Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.

---

上一篇: [设置项与辅助函数](04-settings-and-helpers-zh.md) · 目录: [README](../README.md)
