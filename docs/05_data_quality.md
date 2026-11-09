# 05 · Data quality and the rejection rules

EN: Where the missing data comes from, what gets rejected, and whether the answer changes if you move the threshold.
KO: 결측이 어디서 오는지, 무엇이 제외되는지, 기준을 옮기면 결론이 바뀌는지.
ZH: 缺失从哪来、什么被剔除、换阈值结论变不变。

Numbers below are from the YMTC dataset as processed on 2026-11-03 (6 participants with events, 84 trials each, 504 trials total). Re-run `ymtcTrialQC` + `ymtcTimingCheck` if the data change.

## 1. The three rules

From the analysis plan, applied by `ymtcTrialQC.m`:

| rule | condition | effect | option |
|---|---|---|---|
| R1 | `countdown_SmoothSig_missingDataPercent > 50` | trial rejected | `MaxMissingPct` |
| R2 | `preOutcome_SmoothSig_missingDataPercent > 50` | trial **flagged**, kept | `MaxMissingPreOut` |
| R3 | more than 20% of a subject's trials rejected | subject excluded | `MaxSubjectLossPct` |

R1/R2 test the countdown and preOutcome segments because those are the windows the
analysis uses. The baseline segment is deliberately not a rejection criterion — a bad
baseline is handled by the analysis, not by dropping the trial.

## 2. What the numbers are (threshold 50%)

| subject | rejected | rate | excluded |
|---|---|---|---|
| sub119 | 69/84 | 82.1% | yes |
| sub134 | 12/84 | 14.3% | no |
| sub139 | 84/84 | 100% | yes |
| sub140 | 78/84 | 92.9% | yes |
| sub141 | 5/84 | 6.0% | no |
| sub149 | 0/84 | 0% | no |
| **all** | **248/504** | **49.2%** | 3 of 6 |

49.2% is over all 504 trials. Over the five participants that had events before sub149 was
added it is 248/420 = 59% — the number quoted in older notes.

The flag-only rule is large too: `preOutcome` is mostly missing in **227/504 (45%)** of trials.
Those trials stay in the table with `PreOutcomeMostlyMissing = true`; their preOutcome value
should not be used as a GLM modulator.

## 3. Does the threshold matter?

Measured 2026-11-06 by running the same rule at 60%:

| subject | 50% | 60% |
|---|---|---|
| sub119 | 69 (82.1%) | 56 (66.7%) |
| sub134 | 12 (14.3%) | 7 (8.3%) |
| sub139 | 84 (100%) | 84 (100%) |
| sub140 | 78 (92.9%) | 72 (85.7%) |
| sub141 | 5 (6.0%) | 3 (3.6%) |
| sub149 | 0 (0%) | 0 (0%) |
| **all** | **248 (49.2%)** | **222 (44.0%)** |

Loosening the cut-off by 10 points recovers 26 trials (5.2%) and changes **no** subject-level
decision: the same three participants stay excluded. So the "this data is too gappy" conclusion
does not depend on where exactly the line is drawn.

## 4. Where the missing data sits

Mean `SmoothSig_missingDataPercent` per segment, by subject:

| subject | baseline | countdown | preOutcome | postOutcome |
|---|---|---|---|---|
| sub119 | 37.1 | 67.2 | 71.5 | 46.5 |
| sub134 | 25.5 | 29.2 | 19.1 | 17.6 |
| sub139 | 100 | 100 | 100 | 100 |
| sub140 | 79.0 | 84.9 | 71.3 | 74.6 |
| sub141 | 19.5 | 29.6 | 26.9 | 31.6 |
| sub149 | 15.2 | 19.4 | 16.6 | 21.4 |

Three patterns worth noting:

- **Countdown is usually the worst segment** (sub119, sub140, sub141, sub149). It is also the
  longest — 13–31 s — so it accumulates more chances to lose the pupil.
- **sub139 is 100% everywhere**: the recording has essentially no valid pupil. This is a
  recording problem, not a threshold problem; no cut-off can rescue it.
- **sub134 is the only subject where the later segments are cleaner than the baseline**, which
  fits the earlier finding that its timestamps are the noisiest.

## 5. Why the gaps are there

The rejections are not caused by the filters being strict. The pupil-size filters run on
`median + 16 MAD`, which is deliberately permissive; the gap structure comes from the
recording (long pupil dropouts, look-aways, blinks in a dim room, one eye only). The
threshold-sensitivity result in §3 is the evidence: moving the cut-off barely moves the counts.

This is also why the right response is to *report* the loss rather than tune it away:
`04_all_subjects_qc.csv` carries `nTrials`, `nRejected`, `rejectPct`, `subjectExcluded`, and the
analysis should quote them.

## 6. What to report

For a methods section, four numbers suffice:

1. participants recorded (9), with events (6), analysed (3);
2. trials rejected at the plan's threshold (248/504 = 49.2%);
3. the same count at 60% (222/504 = 44.0%) as a sensitivity note;
4. the three excluded participants and why (82.1%, 100%, 92.9% rejection).

Nothing above should be described as "cleaning": no trial was repaired, values were not
imputed, and the rejected trials remain in `04_all_trials_qc.csv` with their flags.
