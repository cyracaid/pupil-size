# pupil-size · YMTC

EN: Turn MRC eye-tracker logs into one analysis table: `.trk` -> per-sample CSV -> event markers -> pupil metrics -> merged table.
KO: MRC 시선추적 로그를 하나의 분석 표로: `.trk` -> 샘플 CSV -> 마커 -> 눈동자 지표 -> 병합표.
ZH: 把 MRC 眼动仪日志变成一张分析表：`.trk` → 逐样本 CSV → 事件 marker → 瞳孔指标 → 合并表。

**[Documentation site](https://cyracaid.github.io/pupil-size/)** · [English](https://cyracaid.github.io/pupil-size/index.html) · [한국어](https://cyracaid.github.io/pupil-size/index.ko.html) · [中文](https://cyracaid.github.io/pupil-size/index.zh.html)
· [Reference: every column](https://cyracaid.github.io/pupil-size/reference.html)

## The pipeline in one picture

```
01_原始trk/*.trk                 eye-tracker logs (names keep the recording date)
        |  trk2csv_batch
        v
02_样本/*.csv                    one row per sample, 21 columns
        |
        +--> 03_事件/            events extracted from the log
        |        |  ymtcEventTable (+ TrialOrder-HK/*.xlsx)
        |        v
        |    05_marker表/        one row per marker, in task order (18 columns)
        |
        +--> 04_瞳孔指标/        Kret pipeline: 04_all_segments.csv and friends
                 |
                 v
06_合并表/06_all_merged.csv      one row per marker + four segments of pupil stats (69 columns)
```

## What this branch adds to upstream

| path | what |
|---|---|
| `code/ymtc/` | `.trk` -> CSV, the event-marker table, the run/timing checks, and `ymtcConfig.m` (no absolute path anywhere) |
| `docs/` | six pages, EN + KO/ZH summaries: pipeline, column dictionary, pupil internals, our code, data quality, FAQ |
| `tools/` | `build_readme.py` (this reference) and `build_site.py` (the static site) |
| `.github/workflows/pages.yml` | publishes `docs/` to GitHub Pages on every push |

The column dictionary is the page to start with if you need to know what a number means:
[`docs/02_column_dictionary.md`](docs/02_column_dictionary.md).

## Quick start

```matlab
cd code/ymtc
T = ymtcEventTable('sub001');            % marker table for one subject
S = ymtcEventTableBatch;                 % every subject, plus a summary
R = ymtcRunCheck;                        % is every run really 21 trials?
```

Paths are configured in `ymtcConfig.m`; copy `ymtc_config.template.m` to
`ymtc_config.m` (git-ignored) to point at data that lives elsewhere.

---

## Upstream

This is a fork of [ElioS-S/pupil-size](https://github.com/ElioS-S/pupil-size) (Kret & Sjak-Shie, 2019,
*Behavior Research Methods*), with the additions above. The original README follows.

# pupil-size
MATLAB scripts for preprocessing pupil size timeseries.

This code assumes that the user is proficient in MATLAB, with knowledge of Object
Oriented Programming and Handle classes.

The code requires the ‘Signal Processing Toolbox’ and the ‘Statistics and Machine Learning Toolbox’, and was tested with MATLAB versions 2012b, 2016a & 2017a, running on Windows 7.

## Data Models:
This repository contains a collection of Matlab classes and helper scripts that can be used for preprocessing pupil size data in an object-oriented manner.

1. **RawFileModel.m**: used to generate standardized matlab files containing raw pupil-size data and segmentation information.

2. **PupilDataModel.m**: this is the main class basic users should interact with, it holds the classes mentioned below, and its methods run the batch segment analysis and plotting functions.

3. **RawSamplesModel.m**: this class manages the raw data of a single pupil, and performs raw-data filtering to remove samples associated with noise and artifacts. The samples that remain after filtering are the *valid samples*.

4. **ValidSamplesModel.m**:  this class handles the valid samples and performs interpolation and smoothing

## Workflow:
The generalized preprocessing pipeline consists of the following steps:

1. Convert eye-tracker output to compatible matlab .mat files containing the pupil size data and metadata, as well as information about how to segments the recording into the desired sections.

2. Instantiate the PupilDataModel objects.

3. Filter the raw data by running the filterRawData() method of the PupilDataModel instances.

4. Process the valid samples and generate smooth interpolated signals by running the processValidSamples() method of the PupilDataModel instances.

5. Analyze each segment by running the analyzeSegments() method of the PupilDataModel instances.

6. Visualize the data by running the plotData() method of the PupilDataModel instances.

NOTE: the abovementioned PupilDataModel methods can be run on PupilDataModel arrays as well as PupilDataModel scalars. See Examples.

## Examples:
The /code/Examples/ folder contains two example applications:
* Dataset 1: Processing monocular pupil size data collected using SR-Research's Eyelink system.
* Dataset 2: Processing binocular pupil size data collected using E-Prime Extensions for Tobii.


## Documentation:
`docs/` holds the column dictionary (every output column: meaning, formula, unit, source)
and the pipeline notes for this fork; see [docs/README.md](docs/README.md).
