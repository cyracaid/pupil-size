# 06 · FAQ — the traps that bite most often

EN: Six questions that come up every time someone touches these tables.
KO: 이 표를 다룰 때마다 나오는 여섯 가지 질문.
ZH: 每次动这些表都会遇到的六个问题。

**Q1. Why is `ValidSamples_validPercent` the same on every row of a subject?**
Because it is not per segment. It is the share of the whole recording that passed the
artifact filters, repeated on each row. For "how much of *this* segment is missing", use
`SmoothSig_missingDataPercent`.

**Q2. Why does a segment with an obvious blink still have a normal-looking mean?**
`SmoothSig_*` is computed on the interpolated signal. Gaps up to 250 ms are filled by
interpolation and leave no trace in the mean; only longer gaps are set back to NaN. Two
segments with the same mean can have very different data underneath — always read the mean
next to `SmoothSig_missingDataPercent` and `ValidSamples_sampleCount`.

**Q3. Why are the numbers in pixels, and why is the range filter not 1.5–9?**
The MRC log stores an ellipse in camera pixels, not millimetres. The paper's default range
(1.5–9) assumes millimetres and would reject everything. `example_kret_pipeline.m` derives
the range from the data (0.5–99.5 percentile of valid pupil × 0.8 / 1.2) and prints it at
run time. Do not compare these diameters with published mm values.

**Q4. Why is `outcome` sometimes `O`, and what is `actual_outcome` for?**
For the two uncertain-outcome conditions the cue cannot announce threat or safe, so
`outcome` is `O` for the whole trial. `actual_outcome` reads the `Outcome` marker
(`OutcomePTUOT` vs `OutcomePTUOS`) and gives `T` or `S`. Group by `actual_outcome` when you
need threat vs safe; use `certainty` when the question is whether the subject knew.

**Q5. Why 84 trials and only 24 ratings?**
4 runs × 21 trials, and the task asks for a rating on 24 of the 84. `RatingStart` is absent
for the rest — that is the design, not missing data. In the wide table this shows up as
`has_rating = false` and `rating_s = NaN`.

**Q6. Why does a file with no events still produce a CSV?**
`trk2csv` converts whatever it is given and records `NO_EVENTS`; `run` / `trial` / `phase` /
`event` stay empty. Three of the nine participants are like this, so they are skipped by the
event-table step and marked `skipped_no_events` in `05_all_markers_summary.csv`. Nothing is
invented to fill them.

---

**Q7. Can I re-run one subject without touching the others?**
`ymtcEventTableBatch('Subjects', "sub149")` does exactly that; it overwrites only that
subject's file, plus the summary and combined tables. Point it at a scratch folder via
`ymtc_config.m` if you want to experiment without touching the real outputs.
