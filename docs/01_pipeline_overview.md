# 01 · Pipeline overview

EN: Five layers from the eye-tracker log to the analysis table, and what each layer hands to the next.
KO: 안구추적 로그에서 분석 표까지 다섯 단계, 그리고 각 단계가 다음 단계에 넘기는 것.
ZH: 从眼动仪日志到分析表的五层，以及每层交给下一层什么。

```
01_原始trk/*.trk                    raw logs, ~60 Hz, SoftwareEvent lines (never renamed)
        │  trk2csv_batch.m
        ▼
02_样本/*.csv                        one row per sample, 21 columns, anomalies recorded
        │                                    │
        │  csv2kretmat.m                     │  ymtcEventTable.m / ymtcEventTableBatch.m
        ▼                                    ▼
04_瞳孔指标/                         05_marker表/05_all_markers*.csv   one row per marker
  *.mat (Kret format)                        │
        │  example_kret_pipeline.m           │  ymtcTrialWide.m   → 05_all_trials_wide.csv
        ▼                                    │  ymtcTimingCheck.m → 05_all_05_all_timing_check.csv
04_瞳孔指标/                                 │
  04_all_segments.csv (segment stats)       │
  04_all_04_all_trials_qc.csv (reject flags)       │
  04_all_04_all_subjects_qc.csv (per subject)      │
        └──────────────┬─────────────────────┘
                       │  ymtcMergeResults.m
                       ▼
06_合并表/06_all_merged.csv          69 columns: event row + 4 segments x 12 stats + 3 QC flags

side check, feeds nothing downstream:
  03_事件/subNNN_events.csv ──ymtcRunCheck──▶ 07_检查/07_all_07_all_run_check.csv
```

## Layer 1 — the recording

`01_原始trk/*.trk` are MRC eye-tracker text logs. One line per sample, plus
`SoftwareEvent` lines where the task program fired a marker. Nothing here is produced by
us; the files are never modified.

## Layer 2 — samples

`trk2csv.m` turns one log into one CSV: a row per sample, a `pupil_valid` flag, and the
event that happened at that sample. Anomalies (missing `START`, gaps, non-monotonic time,
cue length off) are **recorded** in `trk2csv_issues.csv`, never fixed.

Key point: the tracker's own columns (`pupil_2a/2b`, `gaze_x/y`) are kept as they are.
`participant`, `run`, `trial`, `phase` are derived; `run` counts `START` events only, which
is why a file missing its first `START` gets run 0.

## Layer 3 — markers

Two independent paths out of layer 2, and they do not depend on each other:

- **to the pupil metrics**: `csv2kretmat.m` rewrites each sample CSV into the Kret format
  (`.mat`, time from 0, one eye, px) and adds the four segment definitions per trial.
- **to the event table**: `ymtcEventTable.m` reads the trk events and the task's
  `TrialOrder` workbooks, picks which order the subject ran, and writes one row per marker
  in the order `Onset → countdown → Outcome → WhiteNoise → Rating`.

## Layer 4 — numbers

`example_kret_pipeline.m` runs the pupil-size model: three artifact filters → interpolation
to 1000 Hz → 4 Hz zero-phase low-pass → per-segment statistics. Details in
[03_pupil_size_internals.md](03_pupil_size_internals.md); every column in
[02_column_dictionary.md](02_column_dictionary.md).

`ymtcTrialQC.m` then applies the analysis plan's three rules and writes `04_all_trials_qc.csv` /
`04_all_subjects_qc.csv`.

## Layer 5 — one table

`ymtcMergeResults.m` joins the event row and the four segments of the same trial into one
row: 18 event columns + 4 × 12 statistics + 3 QC flags = 69. This is the table an analysis
actually starts from.

## Three checks that are cheap and catch most mistakes

| check | what it protects | output |
|---|---|---|
| `ymtcRunCheck` | the `run = ceil(trial/21)` assumption | `07_检查/07_all_run_check.csv` |
| `ymtcTimingCheck` | that the task ran on schedule | `05_marker表/05_all_timing_check.csv` |
| `checkDocs` | that the dictionary still matches the tables | console |

## What is deliberately not done here

- No baseline correction. The `baseline` segment exists so that the analysis can subtract
  it, but the pipeline does not decide for you.
- No outlier removal at the trial level. `RejectCountdown` flags; whether to drop is a
  decision recorded in the analysis plan.
- No modelling. Everything above produces tables, not tests.
