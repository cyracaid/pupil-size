# 04 · Our code, and what lives where

EN: The sample layer, the event layer and the marker layer are in this repository; the analysis layer that produces the final table lives with the study data.
KO: 샘플 계층, 이벤트 계층, 마커 계층이 이 저장소에 있고, 최종 표를 만드는 분석 계층은 연구 데이터와 함께 있습니다.
ZH: 样本层、事件层、marker 层都在这个仓库里；产出最终表的分析层跟研究数据放在一起。

## In this repository — `code/ymtc/`

| file | role |
|---|---|
| `trk2csv.m` / `trk2csv_batch.m` | `.trk` → one CSV per participant; anomalies recorded, never repaired |
| `exportEvents.m` | `.trk` (or a folder) → `03_事件/<sub>_events.csv`, one row per event, exact event time |
| `private/readTrk.m`, `labelSamples.m`, `checkTrk.m` | parse, attach events to samples, compare with the task's expectations |
| `ymtcEventTable.m` / `ymtcEventTableBatch.m` | one row per marker, in task order; conditions read off the marker names |
| `ymtcRunCheck.m` | is every run really 21 trials (counted with BurnInStart) |
| `ymtcTimingCheck.m` / `ymtcTrialWide.m` | descriptive summary of `diff_s`; long table → one row per trial |
| `ymtcConfig.m` / `ymtc_config.template.m` | where the folders are; no path in the code |
| `checkDocs.m` | expected columns (kept in the `.m`) vs the real table headers |

Call chain and reading order: [`code/ymtc/README.md`](../code/ymtc/README.md). Everything
above runs with base MATLAB and needs no toolbox.

## Not in this repository — the analysis layer

These files sit with the study data (they read the participant folders and the Kret `.mat`
files), so they are not shipped here:

| file | role |
|---|---|
| `csv2kretmat.m` | sample CSV → Kret-format `.mat`, and defines the four segments per trial |
| `example_kret_pipeline.m` | runs the pupil-size model: filter → interpolate → segment → statistics → QC → export |
| `ymtcTrialQC.m` | the analysis plan's three rejection rules |
| `ymtcMergeResults.m` | event row + four segments → `06_merged/06_all_merged.csv` (69 columns) |
| `ymtcManipulationCheck.m`, `ymtcLayer1Bins.m`, `ymtc_param_sensitivity.m` | analysis-side scripts, not part of the data pipeline |

If you need them, they belong with the data, not here: they encode this study's folder
layout and its analysis decisions.

## How the two layers meet

They only agree on two things, and both are written down:

1. **the four segment definitions** (`csv2kretmat.m`), which is what makes
   `countdown_SmoothSig_meanDiam` comparable across the two sides;
2. **`participant` + `run` + `trial`**, the join key used by `ymtcMergeResults.m`.

Change either of those and the merged table silently stops meaning what the dictionary says.
