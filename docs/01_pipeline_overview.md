# 01 · Pipeline overview

EN: Five layers from the eye-tracker log to the analysis table, and what each layer hands to the next.
KO: 안구추적 로그에서 분석 표까지 다섯 단계, 그리고 각 단계가 다음 단계에 넘기는 것.
ZH: 从眼动仪日志到分析表的五层，以及每层交给下一层什么。

```
01_原始trk_9人/*.trk                  raw text logs, ~60 Hz, SoftwareEvent lines
        │  trk2csv.m / trk2csv_batch.m
        ▼
02_逐样本csv/*.csv                    one row per sample, 21 columns, anomalies recorded
        │                                    │
        │  csv2kretmat.m                     │  ymtcEventTable.m / ymtcEventTableBatch.m
        ▼                                    ▼
04_Kret流水线输出/*.mat              05_事件对照表/*_event_table.csv      one row per marker
        │  example_kret_pipeline.m           │
        ▼                                    │  ymtcTrialWide.m      → all_subjects_trials_wide.csv
04_Kret流水线输出/                          │  ymtcTimingCheck.m    → timing_check.csv
  kret_results.csv  (segment stats)         │  ymtcRunCheck.m       → run_check.csv
  trials_qc.csv     (reject flags)          │
  subjects_qc.csv   (per subject)           │
        └──────────────┬─────────────────────┘
                       │  ymtcMergeResults.m
                       ▼
06_最终结果/all_subjects_final.csv     69 columns: event row + 4 segments x 12 stats + 3 QC flags
```

## Layer 1 — the recording

`01_原始trk_9人/*.trk` are MRC eye-tracker text logs. One line per sample, plus
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

`ymtcTrialQC.m` then applies the analysis plan's three rules and writes `trials_qc.csv` /
`subjects_qc.csv`.

## Layer 5 — one table

`ymtcMergeResults.m` joins the event row and the four segments of the same trial into one
row: 18 event columns + 4 × 12 statistics + 3 QC flags = 69. This is the table an analysis
actually starts from.

## Three checks that are cheap and catch most mistakes

| check | what it protects | output |
|---|---|---|
| `ymtcRunCheck` | the `run = ceil(trial/21)` assumption | `00_数据检查报告/run_check.csv` |
| `ymtcTimingCheck` | that the task ran on schedule | `05_事件对照表/timing_check.csv` |
| `checkDocs` | that the dictionary still matches the tables | console |

## What is deliberately not done here

- No baseline correction. The `baseline` segment exists so that the analysis can subtract
  it, but the pipeline does not decide for you.
- No outlier removal at the trial level. `RejectCountdown` flags; whether to drop is a
  decision recorded in the analysis plan.
- No modelling. Everything above produces tables, not tests.
