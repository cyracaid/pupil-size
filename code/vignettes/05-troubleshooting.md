# Troubleshooting, limitations, further reading

**English** · [한국어](05-troubleshooting-ko.md) · [中文](05-troubleshooting-zh.md)

Previous: [Settings and helper functions](04-settings-and-helpers.md) · Index: [README](../README.md)

---

## Troubleshooting: symptom → cause → fix

| Symptom | Cause | Fix |
|---|---|---|
| `'t_ms' must be sorted!` | timestamps not ascending (duplicate or backward timestamps in the trk) | sort in the converter, do not patch inside the package; record duplicates separately |
| `'L' must be empty, or have the same length as 't_ms'` | diameter and time vectors differ in length | check lengths in the converter |
| `No settings present.` | `PupilDataModel` was built without `settings` | start from `PupilDataModel.getDefaultSettings()` and edit |
| `Interpolation cannot be performed.` | fewer than 2 valid points for that eye (wrong range, or all noise) | check that `PupilDiameter_Min/Max` match the unit |
| almost every sample is invalid | default range 1.5–9 is in mm; pixel data lies outside | set the range in the real unit |
| warning `pupilSize:edgeClamp` | floating-point error put upsampled times outside the valid range; they were clamped | only a notice; investigate if the count is large |
| `ValidSamples_validPercent` identical on every row | it is a whole-recording value by design | use `SmoothSig_missingDataPercent` for per-segment missingness |
| `SmoothSig_meanDiam` looks fine but data is poor | gaps shorter than 250 ms were interpolated over | read `missingDataPercent` and `ValidSamples_sampleCount` too |
| `plotData` does nothing or is skipped | `-batch` has no desktop | run in desktop MATLAB |
| `plotData` shows one file only | `plotMultipleFiles = false` in the source (heavy) | change that switch in `PupilDataModel.m` |
| `addpath` fails in `Examples` | paths written with Windows backslashes `..\..\helperFunctions\` | use `../../helperFunctions/` on macOS / Linux |

## Limitations

- The original README lists the Signal Processing and Statistics toolboxes as requirements, tested on MATLAB 2012b / 2016a / 2017a on Windows 7. This repository patches it for macOS (path separator in `PupilDataModel`, `FALLBACK/`); see `git log`. The batch script `代码_matlab/example_kret_pipeline.m` is outside the repository.
- The filter parameters are the paper's defaults and **have not been tuned for YMTC data**. Tuning needs desktop MATLAB and `plotData()` on the raw traces.
- This page describes what the code does, not whether the results are good. For data quality see [`../docs/05_data_quality.md`](../../docs/05_data_quality.md).

## Further reading

[`../docs/01_pipeline_overview.md`](../../docs/01_pipeline_overview.md) (pipeline on one page) · [`../docs/02_column_dictionary.md`](../../docs/02_column_dictionary.md) (every column) · [`../docs/03_pupil_size_internals.md`](../../docs/03_pupil_size_internals.md) (filters and interpolation) · [`ymtc/README.md`](../ymtc/README.md) and [`../docs/04_our_code.md`](../../docs/04_our_code.md) (our code) · [`../docs/06_faq.md`](../../docs/06_faq.md).

Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.

---

Previous: [Settings and helper functions](04-settings-and-helpers.md) · Index: [README](../README.md)
