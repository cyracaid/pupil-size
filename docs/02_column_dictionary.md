# 02 · Column dictionary

EN: Every column of the analysis tables: what it means, how it is computed, its unit, and where it comes from.
KO: 분석 표의 모든 열: 의미, 계산 방법, 단위, 출처.
ZH: 分析用表的每一列：含义、怎么算、单位、从哪儿来。

Verified against `ymtc-trk2csv@e1b0aa0` (2026-11-09; contains the `code/ymtc` of `e574fce` and upstream
`pupil-size@645cbc6`, whose pupil parameters are unchanged since). If a table gains a column, update this
page in the same commit.

Scope: the eight tables an analysis touches (§A–§H). The sampling-level tables — the 21-column
`02_samples/*.csv`, `02_all_qc_summary.csv`, `02_all_issues.csv` — are documented on the
[reference page](https://cyracaid.github.io/pupil-size/reference.html), not here.

The tables, and how they relate:

```
.trk ──trk2csv──> 02_samples/*.csv ──csv2kretmat + example_kret_pipeline──> 04_pupil/
                        │                                                       04_all_segments.csv (16 cols)
                        └──ymtcEventTable──> 05_markers/*_event_table.csv (18 cols)
                                                    │
                                                    ├── ymtcTrialWide ──> 05_all_trials_wide.csv (14 cols)
                                                    ├── ymtcTimingCheck ─> 05_all_timing_check.csv (7 cols)
                                                    └── ymtcMergeResults ─> 06_merged/06_all_merged.csv (69 cols)
```

---

## A. Event table — `05_<sub>_markers.csv` / `05_all_markers.csv` (18 columns)

One row per marker. In the 5-step version each trial has 4–5 rows; the full version adds
`WhiteNoise_part2-4`. The per-subject names are `05_<sub>_markers.csv` and
`05_<sub>_markers_5step.csv`; the stacked versions are `05_all_markers.csv` and
`05_all_markers_5step.csv` (`ymtcEventTable.m` / `ymtcEventTableBatch.m`).

| column | meaning | how | unit |
|---|---|---|---|
| `participant` | subject id | from the file name | – |
| `order` | which trial order (1–5) the subject ran | chosen by matching countdown lengths against `TrialOrder<1-5>Run<1-4>.xlsx` | – |
| `run` | run number 1–4 | `ceil(trial / 21)`; verified by `ymtcRunCheck` | – |
| `trial` | trial number within the subject, 1–84 | count of `CueStart` events | – |
| `trial_in_run` | trial within its run, 1–21 | `trial - (run-1)*21` | – |
| `ymtc_marker` | the task's own marker name, e.g. `OnsetPTCTO`, `Rating` | read from the order workbook | – |
| `trk_event` | the trk event that was matched to it | fixed mapping, see §H | – |
| `time_ms` | raw eye-tracker timestamp | copied from the trk | ms |
| `t_from_onset_s` | seconds from this trial's Onset | `(time_ms - onset_ms)/1000` | s |
| `expected_from_onset_s` | where the design puts this marker | order workbook `onsets` | s |
| `diff_s` | measured minus designed | `t_from_onset_s - expected_from_onset_s` | s |
| `expected_duration_s` | how long this marker should last | order workbook `durations` | s |
| `condition` | condition code: `PTCT` `PTCS` `PTUO` `UTCT` `UTCS` `UTUO` | first 4 characters after `Onset` | – |
| `timing` | predictable / unpredictable time | `condition(1)`: `P` / `U` | – |
| `certainty` | outcome known at cue or not | `condition(3)`: `C` / `U` | – |
| `outcome` | what the *cue* announced | `condition(4)`: `T` / `S` / `O` (`O` = not announced) | – |
| `actual_outcome` | what the trial actually ended in | `T` / `S`; equals `outcome` when certainty is `C`, read off `OutcomePTUOT` / `OutcomePTUOS` when `U` | – |
| `step` | position in the trial | 1 Onset, 2 countdown start, 3 Outcome, 4 WhiteNoise, 5 Rating | – |

`O` in `outcome` is the one trap here: for the two uncertain-outcome conditions the cue
cannot tell threat from safe, so `outcome` is `O` and only `actual_outcome` resolves it.

## B. Segment statistics — 12 concepts, used with 4 prefixes

Any column of the form `<segment>_<stat>`, where `<segment>` is `baseline`, `countdown`,
`preOutcome` or `postOutcome`. The four segments are, in seconds from the trial's Onset:

| segment | window | what it is for |
|---|---|---|
| `baseline` | `[Onset − 0.5, Onset)` | pre-cue level, for baseline correction |
| `countdown` | `[Onset, Outcome)` | the waiting period, the window of interest |
| `preOutcome` | `[Outcome − 2.0, Outcome)` | the 2 s before the outcome, GLM modulator |
| `postOutcome` | `[Outcome, Outcome + 2.0)` | the response to the outcome |

Two families of statistics are computed per segment, from two different signals:

- **`SmoothSig_*`** — the interpolated and low-pass filtered signal: valid samples are
  linearly interpolated onto 1000 Hz and filtered with a 4th-order Butterworth at 4 Hz
  (zero phase, `filtfilt`). Gaps longer than 250 ms are not interpolated and stay missing.
- **`ValidSamples_*`** — only the samples that survived the three artifact filters; no
  interpolation, no smoothing.

| stat | meaning | how | unit |
|---|---|---|---|
| `segmentStart` / `segmentEnd` | segment boundaries | seconds from the start of the recording (first sample = 0) | s |
| `SmoothSig_meanDiam` | mean diameter of the smooth signal in this segment | segment mean | px |
| `SmoothSig_minDiam` / `SmoothSig_maxDiam` | extremes of the smooth signal | segment min / max | px |
| `SmoothSig_missingDataPercent` | share of the segment with no usable data | missing samples / segment samples | % |
| `SmoothSig_sampleCount` | segment length in samples | segment samples at 1000 Hz (≈ duration × 1000) | count |
| `ValidSamples_meanDiam` | mean of the real (un-interpolated) samples | segment mean over valid samples | px |
| `ValidSamples_minDiam` / `ValidSamples_maxDiam` | extremes of the real samples | segment min / max | px |
| `ValidSamples_validPercent` | **whole-recording** valid fraction for this eye | valid samples / all samples of the recording | % |
| `ValidSamples_sampleCount` | valid samples inside this segment | count | count |

Three traps, in order of how often they bite:

1. `ValidSamples_validPercent` is **not** per segment — it is one number per subject, repeated
   on every row. For "how much is missing *here*", use `SmoothSig_missingDataPercent`.
2. `SmoothSig_meanDiam` includes interpolated points. A 100 ms gap looks perfectly clean
   because it was filled; only gaps > 250 ms become missing. Always read it next to
   `SmoothSig_missingDataPercent`.
3. The unit is **camera pixels**, not millimetres. The range filter is set from the data
   (0.5–99.5 percentile × 0.8 / 1.2), not from the paper's 1.5–9 mm.

## C. Quality-control columns

| column | table | meaning | rule |
|---|---|---|---|
| `RejectCountdown` | `04_all_trials_qc.csv`, final | trial is rejected | `countdown_SmoothSig_missingDataPercent > 50` |
| `PreOutcomeMostlyMissing` | same | flag only, the trial is kept | `preOutcome_SmoothSig_missingDataPercent > 50` |
| `SubjectExcluded` | same | the whole subject is excluded | more than 20% of the subject's trials rejected |
| `nTrials` / `nRejected` / `rejectPct` | `04_all_subjects_qc.csv` | per-subject counts and rate | from the three rules above |

## D. `04_all_segments.csv` (16 columns)

One row per subject × trial × segment (4 per trial). Columns 1–6 are the segment's identity,
7–16 are the statistics from §B.

| column | meaning |
|---|---|
| `segmentStart` / `segmentEnd` | boundaries in seconds from the recording start |
| `segmentName` | `countdown_004` = segment `countdown` of trial 4 |
| `segmentType` | `baseline` / `countdown` / `preOutcome` / `postOutcome` |
| `participant` / `trial` | subject id, trial 1–84 |
| the ten `leftPupil_*` columns | §B, unprefixed |

## E. `05_all_trials_wide.csv` (14 columns)

One row per trial; the long event table collapsed to one line per trial.

| column | meaning | unit |
|---|---|---|
| `participant`, `order`, `run`, `trial` | identity | – |
| `condition`, `timing`, `certainty`, `outcome` | as in §A | – |
| `onset_s` | always 0 — the reference point | s |
| `countdown_s` | countdown start (end of the cue) | s |
| `outcome_s` | outcome onset | s |
| `whitenoise_s` | white-noise onset | s |
| `rating_s` | rating onset; `NaN` when the trial has no rating | s |
| `has_rating` | whether this trial has a rating (24 of 84) | logical |

## F. `05_all_timing_check.csv` (7 columns)

One row per subject × marker; the descriptive answer to "is the task on schedule?".

| column | meaning |
|---|---|
| `participant` | subject id |
| `phase` | `1 Onset` … `5 Rating start` |
| `n` | number of markers in this cell |
| `mean_s` / `sd_s` | mean and SD of `diff_s` |
| `min_s` / `max_s` | extremes of `diff_s` |

## G. `07_all_run_check.csv` (9 columns)

One row per subject; guards the `run = ceil(trial/21)` assumption.

| column | meaning |
|---|---|
| `participant`, `status` | id; `ok` / `no_file` / `no_events` |
| `nSTART`, `nBurnInStart`, `nBurnOutStart`, `nCueStart` | event counts |
| `trialsPerRun` | e.g. `21/21/21/21`, counted with BurnInStart as the boundary |
| `runAssignmentOK` | true when every run has 21 trials and the counts agree |
| `note` | what is wrong, in plain words |

## H. The merged final table — `06_merged/06_all_merged.csv` (69 columns)

One row per marker. **The statistics of a segment sit on the row of that segment's own start marker** (`baseline` on `step == 1`, `countdown` on `step == 2`, `preOutcome` / `postOutcome` on theirs), so a single row is not a complete trial - join the rows that share `participant` + `run` + `trial` to get one row per trial. The column count is:

```
18 event columns (§A)  +  4 segments x 12 statistics (§B)  +  3 QC columns (§C)  =  69
```

The segment columns are the §B names with the segment as a prefix, e.g.
`countdown_SmoothSig_meanDiam`, `preOutcome_ValidSamples_sampleCount`.

## I. Marker ↔ trk event mapping

| trk event | marker step | notes |
|---|---|---|
| `CueStart` | 1 Onset | the cue, nominally 1 s |
| `CueFinish` | 2 countdown start | when the cue disappears |
| `StimuliStart` | 3 Outcome | outcome display, nominally 2.7 s |
| `WhitenoiseStart1` | 4 WhiteNoise | parts 2–4 are further marks of the same noise |
| `RatingStart` | 5 Rating | present on 24 of 84 trials |
| `START` / `BurnInStart` / `BurnOutStart` | – | run-level rows, no trial, no condition |
| `CountdownFinish` | – | tick of the countdown digits, not a marker |

## J. Check this page against the data

`checkDocs.m` compares the header of every output CSV with an expected column list **that is
written inside `checkDocs.m`**, not with this page. It therefore catches "the pipeline changed"
but not "this page was left behind": if you update `checkDocs.m` without updating §A–§H, the check
still passes. Treat the two as one edit — table, `checkDocs.m`, this page — and run `checkDocs` after
every pipeline run.
