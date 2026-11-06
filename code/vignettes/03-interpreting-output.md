# Reading the output: result table and exported CSV

**English** · [한국어](03-interpreting-output-ko.md) · [中文](03-interpreting-output-zh.md)

Previous: [The four data models: inputs and outputs](02-data-models.md) · Index: [README](../README.md) · Next: [Settings and helper functions](04-settings-and-helpers.md)

---

## Output of `analyzeSegments`

One table per object: **all columns of your `segmentsTable`, then 10 columns per eye appended to the right**. Prefixes are `leftPupil_`, `rightPupil_`, `meanPupil_`. Our data has one pupil, so only `leftPupil_*` appears.

| Column (prefix removed) | Unit | How it is computed |
|---|---|---|
| `SmoothSig_meanDiam` | raw unit | mean of the smooth signal in the segment, `NaN` ignored |
| `SmoothSig_minDiam` / `SmoothSig_maxDiam` | raw unit | min / max of the smooth signal in the segment |
| `SmoothSig_missingDataPercent` | % | number of `NaN` ÷ number of samples in the segment × 100 |
| `SmoothSig_sampleCount` | count | all 1000 Hz samples in the segment, **`NaN` included** |
| `ValidSamples_meanDiam` | raw unit | mean of the valid raw points in the segment |
| `ValidSamples_minDiam` / `ValidSamples_maxDiam` | raw unit | min / max of the valid raw points in the segment |
| `ValidSamples_validPercent` | % | `validFraction × 100` — **a whole-recording value, not this segment's** |
| `ValidSamples_sampleCount` | count | number of valid raw points in the segment |

A segment is half-open: `[segmentStart, segmentEnd)`.

**When a whole row is `NaN`:**
- `segmentStart` or `segmentEnd` of the segment is itself `NaN` (for example the matching event is missing in the trk).
- No smooth-signal sample falls inside the segment → all `SmoothSig_*` are `NaN`.
- No valid raw point falls inside the segment → all `ValidSamples_*` are `NaN`.

The table header carries `VariableUnits` and `VariableDescriptions` (read them with `PupilResults.Properties.VariableDescriptions`). **They are lost when saved as CSV**, so for column meanings use [`../docs/02_column_dictionary.md`](../../docs/02_column_dictionary.md).

## Files written by `exportSegments`

```matlab
opts.Eyes         = {'left'};          % 'left' 'right' 'mean'; default all
opts.SegmentTypes = {'countdown'};     % needs a segmentType column in segmentsTable; default all
opts.NaNString    = 'NaN';             % how missing values are written; '' writes an empty cell
opts.ZScore       = false;             % true adds the column pupilDiameterZ
hPupilData.exportSegments('out_folder', opts);
```

One file per object per eye, named `<original file name without extension>_<eye>pupil_segments.csv`, e.g. `sub149_leftpupil_segments.csv`.

| Column | Meaning |
|---|---|
| `segmentName` | `segmentsTable.segmentName` |
| `segmentType` | `segmentsTable.segmentType`; empty if there is no such column |
| `segmentStart_s` | start of the segment (s); identical on every row of a segment |
| `tRel_s` | sample time − segment start (s), starts at 0 |
| `pupilDiameter_<unit>` | smoothed diameter, 4 decimals; `NaN` written as `NaNString`. The unit comes from `diameterUnit`, e.g. `pupilDiameter_px` |
| `gap_ms` | the `gap_ms` described above, 1 decimal |
| `pupilDiameterZ` | only with `ZScore=true`: (value − whole-recording mean) ÷ whole-recording SD, computed once per eye over the **entire recording** (Leuchs 2017), not within the segment |

One row = one 1000 Hz sample, so a 10 s segment has about 10000 rows. Segments with no samples are not written.

---

Previous: [The four data models: inputs and outputs](02-data-models.md) · Index: [README](../README.md) · Next: [Settings and helper functions](04-settings-and-helpers.md)
