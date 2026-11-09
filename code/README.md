<a id="top"></a>

**[English](#english) · [한국어](#한국어) · [中文](#中文)**

<a id="english"></a>

# code/ — the pupil-size toolbox and our YMTC layer: everything in one page

One page for the original Kret & Sjak-Shie (2019) code **and** our own `ymtc/` layer. Every output table is listed column by column. Click a triangle to unfold a detail; nothing below is hidden by default except those details. Everything was written against the source or the real files; where something could not be confirmed it says so.

## 1. Map: every table and where it comes from

Folder numbers (`00`–`06`) are the data folders next to this repository. `[ymtc]` = our code in `code/ymtc/`, `[Kret code]` = the original classes in `code/dataModels/`, `[Kret adapter]` = our glue between them.

```
01 raw trk    (01_raw_trk/*.trk)      the recording date lives in these names; never renamed
      │  trk2csv_batch
      ▼
02 samples    (02_samples/subNNN_*.csv, 21 cols) + 02_all_qc_summary.csv + 02_all_issues.csv
      │
      ├──▶ 03 events      (03_events/subNNN_events.csv)
      │        │  ymtcEventTable (+ TrialOrder-HK/*.xlsx)
      │        ▼
      │   05 markers     (05_markers/05_all_markers.csv, 18 cols) · 05_all_markers_5step.csv
      │        ├ ymtcTrialWide    → 05_all_trials_wide.csv (14)
      │        └ ymtcTimingCheck  → 05_all_timing_check.csv (7)
      │
      └──▶ 04 pupil       (04_pupil/) csv2kretmat → .mat → PupilDataModel
               │  04_all_segments.csv (16) · 04_all_trials_qc.csv (19) · 04_all_subjects_qc.csv (5)
               │  segments/subNNN_leftpupil_segments.csv
               ▼
         06 merged      (06_merged/06_all_merged.csv, 69 cols) = 05 markers + 4 segments x 12 stats + 3 QC flags

side check, feeds nothing downstream:
     03 events ──ymtcRunCheck──▶ 07 checks  (07_checks/07_all_run_check.csv, 9)
```

Two branches leave 02 — 03 (events) and 04 (pupil metrics) — and neither depends on the other.
03 feeds 05; 04 and 05 are merged into 06. 07 only inspects 03.

| table | file | rows | columns | produced by |
|---|---|---|---|---|
| per-sample CSV | `02_samples/<name>.csv` | 1 / sample | 21 | trk2csv [ymtc] |
| QC summary | `02_samples/02_all_qc_summary.csv` | 1 / file | 25 | trk2csv_batch [ymtc] |
| issues | `02_samples/02_all_issues.csv` | 1 / anomaly | 5 | trk2csv_batch [ymtc] |
| events | `03_events/<sub>_events.csv` | 1 / event | 3 | event extraction |
| event table | `05_markers/05_<sub>_markers[_5step].csv` | 1 / marker (624 · 372) | 18 | ymtcEventTable [ymtc] |
| event summary | `05_markers/05_all_markers_summary.csv` | 1 / subject | 6 | ymtcEventTableBatch [ymtc] |
| trials wide | `05_markers/05_all_trials_wide.csv` | 1 / trial | 14 | ymtcTrialWide [ymtc] |
| timing check | `05_markers/05_all_timing_check.csv` | 1 / subject × marker | 7 | ymtcTimingCheck [ymtc] |
| run check | `07_checks/07_all_run_check.csv` | 1 / subject | 9 | ymtcRunCheck [ymtc] |
| Kret results | `04_pupil/04_all_segments.csv` | 1 / trial × segment | 16 | analyzeSegments [Kret code] |
| trial QC | `04_pupil/04_all_trials_qc.csv` | 1 / trial × segment | 19 | Kret pipeline script |
| subject QC | `04_pupil/04_all_subjects_qc.csv` | 1 / subject | 5 | Kret pipeline script |
| segment curves | `04_pupil/segments/<name>_leftpupil_segments.csv` | 1 / 1000 Hz sample | 7 | exportSegments [Kret code] |
| final | `06_merged/06_<sub>_merged.csv, 06_all_merged.csv` | 1 / marker | 69 | ymtcMergeResults [ymtc] |

## 2. The Kret & Sjak-Shie pipeline (original code)

Design points: the pipeline only flags (`isValid`), it never overwrites the raw diameter; valid samples and the smooth signal are different objects; every threshold lives in `getDefaultSettings()`; each object carries its own settings; left, right and mean are analysed separately. Time units: `t_ms` is in milliseconds, `segmentStart`, `segmentEnd` and `signal.t` are in seconds.

```
RawFileModel ──saveMatFile──▶ <name>.mat
        │
        ▼  PupilDataModel.batchConstructor(...)        one object per file
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter     gives isValid per raw sample
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth              gives the 1000 Hz smooth signal
 (3) analyzeSegments()       ValidSamplesModel.analyze                      gives 10 statistics per segment per eye
 (4) exportSegments(folder)  continuous time course of every segment → CSV
 (5) plotData()              visual check (needs desktop MATLAB)
```

#### What each stage actually does

| stage | function (file:line) | decision | key settings |
|---|---|---|---|
| 1 range | `removeOutOfBounds` (`rawDataFilter.m:197`) | diameter outside the plausible range becomes invalid | `PupilDiameter_Min/_Max` (defaults 1.5 / 9, **millimetres**) |
| 2 blink | `madSpeedFilter` (`229`) + `expandGaps` (`511`) | sample-to-sample speed above `median + 16 MAD`; plus 50 ms around every gap wider than 75 ms | `dilationSpeedFilter_MadMultiplier=16`, `maxGap_ms=200` |
| 3 trend | `madDeviationFilter` (`284`) | distance from a 16 Hz low-passed trend line above `median + 16 MAD`; 4 passes let wrongly rejected samples come back | `residualsFilter_passes=4`, `MadMultiplier=16` |
| 4 islands | `removeLoners` (`440`) | islands narrower than 50 ms, separated by more than 40 ms | `islandFilter_minIslandWidth_ms=50`, `_islandSeperation_ms=40` |
| 5 smooth | `interpAndSmooth` (`ValidSamplesModel.m:107`) | linear interpolation to 1000 Hz, then a 4th-order Butterworth at 4 Hz, zero phase (`filtfilt`) | `interp_upsamplingFreq=1000`, `LpFilt_cutoffFreq=4` |
| 6 segments | `analyze` (`203`) | per-segment mean / min / max / missing% from the smooth signal **and** from the valid samples | — |

Every threshold is `median + n*MAD`, never mean +/- SD, because a handful of large artifacts would inflate an SD enough to hide themselves. All values above are paper defaults; our pipeline changes only the range filter, since the paper's numbers are millimetres and our data are camera pixels.

The code never edits the diameter. `rawDataFilter` returns one logical vector (`isValid`) and the raw samples stay as recorded; everything downstream works from that mask, which is why a rejected sample can never be recovered later.

### 2.1 What goes in: the .mat file (`RawFileModel`)

`RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename)` checks its input and writes a `.mat` with four variables. Unfold each field:

<details>
<summary><code>diameterUnit</code></summary>

A text label for the unit of the diameters, for example `'mm'` or `'px'`. It is copied into every result and into the exported CSV column name. The package never converts units; the label is only a label.

</details>

<details>
<summary><code>diameter.t_ms</code></summary>

The time of every sample, in milliseconds, as one column vector. Must be sorted ascending (`issorted`) and should start at 0 (the original eye-tracker time goes into `zeroTime_ms`). Duplicate timestamps break the filters, so our converter keeps only the first of duplicates.

</details>

<details>
<summary><code>diameter.L</code></summary>

The pupil diameter of the LEFT eye at each sample, same length as `t_ms`, `NaN` where the tracker gave nothing. Leave it empty (`[]`) if the left eye was not measured. By convention a single measured eye is stored here, as in the EyeLink example; our MRC data (one pupil) goes in `L`.

</details>

<details>
<summary><code>diameter.R</code></summary>

The same for the RIGHT eye. Empty for us. If both `L` and `R` are present the package also builds a `mean` pupil from them.

</details>

<details>
<summary><code>zeroTime_ms</code></summary>

The eye-tracker's own timestamp (ms) that corresponds to `t = 0`. Stored for the record only; the package never uses it.

</details>

<details>
<summary><code>segmentsTable.segmentStart / segmentEnd</code></summary>

Start and end of each segment, in SECONDS (not ms) on the same clock as `t_ms/1000`. A `NaN` start or end makes that segment's statistics `NaN`. Segments may overlap.

</details>

<details>
<summary><code>segmentsTable.segmentName</code></summary>

A name for the segment, for example `countdown_004`. Shown in the plot and copied to the results.

</details>

<details>
<summary><code>segmentsTable (extra columns)</code></summary>

Any other column (participant, trial, segmentType, condition …) is carried unchanged to the left of the result table. `exportSegments` additionally looks for a column called `segmentType`.

</details>

<details>
<summary>Contents of the .mat written by <code>csv2kretmat</code></summary>

`diameterUnit = 'px'`; `diameter.t_ms` (ms, starting at 0), `diameter.L` (pupil size, `NaN` = missing), `diameter.R` empty; `zeroTime_ms` = original MRC timestamp of the first sample; `segmentsTable` with `segmentStart`, `segmentEnd`, `segmentName` plus `segmentType`, `participant`, `trial`. Four segment types per trial: `baseline` `[CueStart − 0.5 s, CueStart)`, `countdown` `[CueStart, StimuliStart)`, `preOutcome` `[StimuliStart − 2 s, StimuliStart)`, `postOutcome` `[StimuliStart, StimuliStart + 2 s)`. The i-th `CueStart` is paired with the i-th `StimuliStart`. The boundaries come from MEASURED markers, not design values.

</details>

### 2.2 The objects and their fields

<details>
<summary><b><code>PupilDataModel</code> — properties</b></summary>

<details>
<summary><code>filename, filepath</code></summary>

Name and folder of the .mat file this object was built from.

</details>

<details>
<summary><code>settings</code></summary>

Struct with two parts: `settings.raw` (artifact filters) and `settings.valid` (interpolation and low-pass). Every object carries its own copy.

</details>

<details>
<summary><code>eyesWithData</code></summary>

Which eyes have data: `{'left'}`, `{'right'}`, `{'left','right'}` or `{}`. Anything else raises an error. Decides which eyes are filtered and analysed.

</details>

<details>
<summary><code>timestamps_RawData_ms</code></summary>

The shared time vector of the raw samples (ms), from `diameter.t_ms`.

</details>

<details>
<summary><code>leftPupil_RawData, rightPupil_RawData</code></summary>

`RawSamplesModel` of each eye (empty if that eye has no data).

</details>

<details>
<summary><code>leftPupil_ValidSamples, rightPupil_ValidSamples, meanPupil_ValidSamples</code></summary>

`ValidSamplesModel` of each eye, created by `processValidSamples`. `meanPupil_ValidSamples` exists only when both eyes have data.

</details>

<details>
<summary><code>segmentsTable, zeroTime_ms, diameterUnit</code></summary>

Copied from the .mat file (see the file contents above).

</details>

</details>

<details>
<summary><b><code>RawSamplesModel</code> — properties</b></summary>

<details>
<summary><code>eye</code></summary>

`'left'` or `'right'`.

</details>

<details>
<summary><code>rawSample</code></summary>

The raw diameter vector of this eye, never modified.

</details>

<details>
<summary><code>isValid</code></summary>

Logical vector, one entry per raw sample: `true` = passed range, speed and deviation filters. This is what `filterRawData` produces. `NaN` raw samples are `false`.

</details>

<details>
<summary><code>speedFiltData</code></summary>

Intermediate results of the speed filter (only kept when `keepFilterData = true`): `maxDilationSpeeds` (for each sample, the larger absolute speed to its two neighbours, `NaN` only if both neighbours are more than 200 ms away), `isValid` (after the speed filter), `mad`, `thresh` (= median + 16 × MAD, the cut-off), `med_d` (the median).

</details>

<details>
<summary><code>devFiltData</code></summary>

Intermediate results of the deviation filter, one column per pass (4 by default): `isValidPerPass`, `residualsPerPass` (distance from the smooth trend line), `threshPerPass`, `smoothBaselinePerPass` (the trend line). If a pass changes nothing, later passes copy it.

</details>

</details>

<details>
<summary><b><code>ValidSamplesModel</code> — properties</b></summary>

<details>
<summary><code>eye</code></summary>

`'left'`, `'right'` or `'mean'`.

</details>

<details>
<summary><code>samples.t_ms, samples.pupilDiameter</code></summary>

Only the valid raw samples: their times (ms) and diameters.

</details>

<details>
<summary><code>validFraction</code></summary>

valid samples divided by non-empty raw samples over the WHOLE recording (0–1). Reported as `ValidSamples_validPercent` × 100 on every row. For the `mean` pupil: the smaller of the two eyes.

</details>

<details>
<summary><code>signal.t</code></summary>

1000 Hz time axis of the smooth signal, in SECONDS.

</details>

<details>
<summary><code>signal.pupilDiameter</code></summary>

The smooth signal: valid samples linearly interpolated onto `signal.t`, then 4th-order 4 Hz Butterworth low-pass (zero phase, `filtfilt`). `NaN` where the gap between real valid points exceeds `interp_maxGap` (250 ms).

</details>

<details>
<summary><code>signal.gap_ms</code></summary>

At each instant, the distance in ms between the two real valid samples around it; 0 within 0.5 ms of a real sample. (The class declares a field `gap`, the code writes `gap_ms`.)

</details>

</details>

### 2.3 Methods: input → output

| method | input | output | console message |
|---|---|---|---|
| `PupilDataModel.batchConstructor(folder, dirStruct, settings)` | folder, `dir('*.mat')` result, settings | array of objects | `Constructing N Data Objects...` |
| `filterRawData()` | — | `isValid` stored on each eye | `Filtering the raw data in N files...` |
| `processValidSamples()` | — (needs `isValid`) | `*_ValidSamples` objects with the smooth signal; plus `mean` for two eyes | `Interpolating and smooting the valid raw data subsets of N files...` |
| `analyzeSegments()` | — (needs the smooth signal) | cell array, one result table per object; join with `vertcat(results{:})` | `File i (name): analyzing K segments.` |
| `exportSegments(folder, options)` | output folder; options `Eyes`, `SegmentTypes`, `NaNString`, `ZScore` | one CSV per object per eye | `File i (name) left pupil: wrote N samples to <file>` |
| `plotData()` | — | figure window | `—` |

## 3. Output tables, column by column

Each table lists every column. A triangle in the last column unfolds how it is computed, traps and known caveats.

<details>
<summary><b>02 · per-sample CSV — <code><name>.csv</code> from <code>trk2csv</code> (21 columns, one row per eye-tracker sample)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant` | – | subject id | <details><summary>details</summary>Taken from the file name (`sub149_...trk` gives `sub149`); if the name does not start with `sub<digits>` the whole base name is used.</details> |
| `run` | – | run number 0–4 | <details><summary>details</summary>Counts `START` events only. Samples before the first `START` are `0`. A file missing its first `START` therefore numbers its runs one too low; this is reported in the issues table, not repaired.</details> |
| `trial` | – | trial number within the file, 0–84 | <details><summary>details</summary>Increments at each `CueStart`; `0` before the first cue.</details> |
| `trial_in_run` | – | trial number within its run, 0–21 | <details><summary>details</summary>Reset to 0 at each `START`.</details> |
| `phase` | – | task phase the sample belongs to | <details><summary>details</summary>Carried forward from the last event. Values: `pre`, `start`, `burn_in`, `cue`, `countdown`, `stimulus`, `whitenoise1`–`whitenoise4`, `rating`, `burn_out`. `CountdownFinish` and unknown events keep the current phase.</details> |
| `time_ms` | ms | raw eye-tracker timestamp of the sample | <details><summary>details</summary>A large running counter (for example `1491312812.2`), not zero-based. Sample spacing is about 16.7 ms (60 Hz). Rows stay in log order even if time runs backwards (`NONMONOTONIC_TIME`).</details> |
| `t_run_s` | s | seconds since the current run's `START` | <details><summary>details</summary>`NaN` before the first `START`.</details> |
| `event` | – | software event attached to this sample, else empty | <details><summary>details</summary>Each event goes on the first sample whose timestamp is at or after the event time, so event times carry up to one sample interval (about 17 ms). Several events on one sample are joined with `;`. Known names: `START`, `BurnInStart`, `CueStart`, `CueFinish`, `CountdownFinish`, `StimuliStart`, `WhitenoiseStart1`–`4`, `RatingStart`, `BurnOutStart`.</details> |
| `sp_pup_x` | camera px | pupil position, x | <details><summary>details</summary>From the log's pupil columns. The prefix `sp_` is not explained in the log. Read as a position in camera-image pixels; not confirmed by the lab.</details> |
| `sp_pup_y` | camera px | pupil position, y |  |
| `sp_glint_x` | camera px | glint (corneal reflection) position, x |  |
| `sp_glint_y` | camera px | glint position, y |  |
| `vector_x` | camera px | pupil minus glint, x | <details><summary>details</summary>The log spells it `vektor`. Checked on one row: `sp_pup_x - sp_glint_x` = 357.3 − 345.7 ≈ 11.58 = `vector_x`.</details> |
| `vector_y` | camera px | pupil minus glint, y |  |
| `gaze_x` | – | gaze position, x | <details><summary>details</summary>Empty (`NaN`) in every file so far: no gaze data is recorded (`NO_GAZE`).</details> |
| `gaze_y` | – | gaze position, y |  |
| `pupil_2a` | camera px | pupil ellipse axis 2a | <details><summary>details</summary>One of the two ellipse axes. The Kret adapter by default averages `pupil_2a` and `pupil_2b` into the pupil size (`PupilMeasure='mean'`). `NaN` means the log said "no pupil geometry".</details> |
| `pupil_2b` | camera px | pupil ellipse axis 2b |  |
| `pupil_angle` | unconfirmed | pupil ellipse orientation | <details><summary>details</summary>The unit is not stated in the log. Values such as 1.64 suggest radians; not confirmed.</details> |
| `pupil_valid` | 0/1 | sample has pupil data | <details><summary>details</summary>`1` when `pupil_2a` is not `NaN`. This is only "the tracker reported something", not the Kret artifact filter's `isValid`.</details> |
| `gaze_valid` | 0/1 | sample has gaze data | <details><summary>details</summary>`1` when `gaze_x` is not `NaN`; all `0` in our files.</details> |

</details>

<details>
<summary><b>02 · <code>trk2csv_qc_summary.csv</code> (25 columns, one row per .trk file)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant, file` | – | subject id; the .trk file name |  |
| `status` | – | `ok` / `warn` / `failed` | <details><summary>details</summary>`warn` if at least one issue has severity `warn`; `failed` is the placeholder for a file that could not be read.</details> |
| `n_samples` | count | number of samples |  |
| `duration_min` | min | recording length | <details><summary>details</summary>(last timestamp − first timestamp) / 60000.</details> |
| `sampling_hz` | Hz | sampling rate | <details><summary>details</summary>1000 / median of the sample spacing. About 59.9 Hz here.</details> |
| `n_events` | count | software events in the log |  |
| `n_START … n_BurnOutStart` | count | count of each event type: `START`, `BurnInStart`, `CueStart`, `CueFinish`, `StimuliStart`, `RatingStart`, `BurnOutStart` | <details><summary>details</summary>Expected: 4 `START`, 4 `BurnInStart`, 84 `CueStart` = `CueFinish` = `StimuliStart`, 4 `BurnOutStart`; `RatingStart` only on some trials (24 for sub119). Seven columns: `n_START`, `n_BurnInStart`, `n_CueStart`, `n_CueFinish`, `n_StimuliStart`, `n_RatingStart`, `n_BurnOutStart`.</details> |
| `pupil_valid_fraction` | 0–1 | share of samples with pupil data | <details><summary>details</summary>Below 0.5 gives a `LOW_PUPIL_VALID` warning. Nothing is dropped.</details> |
| `gaze_valid_fraction` | 0–1 | share of samples with gaze data |  |
| `cue_dur_min_s / _mean_s / _max_s` | s | cue length: `CueStart` → `CueFinish` | <details><summary>details</summary>The task setting is 1.0 s. For sub119 the mean is 0.881 s (0.832–0.96 s).</details> |
| `n_cue_off_setting` | count | cues that differ from 1.0 s by more than 0.001 s | <details><summary>details</summary>84 of 84 for sub119, which is what triggers `CUE_DURATION`.</details> |
| `countdown_min_s / _mean_s / _max_s` | s | `CueStart` → `StimuliStart` | <details><summary>details</summary>Note: this includes the cue. The designed countdown is this minus the 1 s cue (7.5–30 s).</details> |
| `n_malformed_lines` | count | log lines that could not be parsed |  |
| `n_issues` | count | number of rows this file has in the issues table |  |

</details>

<details>
<summary><b>02 · <code>trk2csv_issues.csv</code> (5 columns, one row per anomaly)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant, file` | – | subject id; .trk file name |  |
| `severity` | – | `warn` = deviates from expectation; `info` = a fact worth knowing |  |
| `code` | – | machine-readable code, see the list below |  |
| `message` | – | plain-language description with the numbers |  |

</details>

<details>
<summary><b>Issue codes (column <code>code</code>)</b></summary>

| code | severity | meaning |
|---|---|---|
| `MALFORMED_LINES` | warn | some lines could not be parsed and were skipped |
| `NO_STOP_LINE` | warn | no `stop timecounter` line; the log may be truncated |
| `NONMONOTONIC_TIME` | warn | a timestamp is not later than the previous one |
| `TIME_GAP` | warn | a gap between samples longer than 200 ms |
| `LOW_PUPIL_VALID` | warn | fewer than 50% of samples have pupil data |
| `NO_GAZE` | info | no sample has gaze data |
| `NO_EVENTS` | warn | no `SoftwareEvent` lines; run, trial, phase cannot be filled |
| `START_COUNT` | warn | number of `START` is not 4 |
| `START_BURNIN_MISMATCH` | warn | `START` and `BurnInStart` counts differ (names the `BurnInStart` without a `START`) |
| `TRIAL_COUNT` | warn | number of `CueStart` is not 84 |
| `EVENT_COUNT_MISMATCH` | warn | `CueStart`, `CueFinish`, `StimuliStart` counts are not equal |
| `UNKNOWN_EVENTS` | info | event names outside the known list |
| `CUE_DURATION` | warn | cues differ from the 1.0 s setting by more than 0.001 s (with min / mean / max) |

</details>

<details>
<summary><b>03 · <code><sub>_events.csv</code> (3 columns, one row per software event)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant` | – | subject id |  |
| `time_ms` | ms | raw timestamp of the event | <details><summary>details</summary>The event's own time from the `SoftwareEvent` line, not snapped to a sample.</details> |
| `event` | – | event name |  |

</details>

<details>
<summary><b>05 · event table — <code><sub>_event_table.csv</code>, <code><sub>_event_table_5step.csv</code>, <code>all_subjects_event_table*.csv</code> (18 columns)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant` | – | subject id |  |
| `order` | 1–5 | which of the five trial orders the subject ran | <details><summary>details</summary>Chosen by comparing each trial's countdown length (`StimuliStart − CueStart − 1 s`) with `TrialOrder<o>Run<r>.xlsx`; the best of five wins. The margin is printed (for example 0.80 s against 14.8 s for the runner-up). The order is not recorded anywhere else, so ask the lab to confirm.</details> |
| `run` | 1–4 | run number | <details><summary>details</summary>`ceil(trial / 21)`. Guarded by `ymtcRunCheck`.</details> |
| `trial` | 1–84 | trial number in the subject | <details><summary>details</summary>Counts `CueStart` events. Empty on run-level rows.</details> |
| `trial_in_run` | 1–21 | trial number within its run |  |
| `ymtc_marker` | – | the task's own marker name | <details><summary>details</summary>For example `OnsetPTCTO`, `PredictableTimeCertainThreatOutcome`, `OutcomePTCTO`, `WhiteNoise`, `Rating`; run-level rows carry `START`, `BurnInStart`, `BurnOutStart`.</details> |
| `trk_event` | – | trk event matched to the marker | <details><summary>details</summary>`CueStart` ↔ Onset, `CueFinish` ↔ countdown start, `StimuliStart` ↔ Outcome, `WhitenoiseStart1` ↔ WhiteNoise, `RatingStart` ↔ Rating.</details> |
| `time_ms` | ms | raw timestamp of the matched trk event | <details><summary>details</summary>Empty when the trk lacks that marker (nothing is interpolated).</details> |
| `t_from_onset_s` | s | seconds since this trial's Onset |  |
| `expected_from_onset_s` | s | where the design puts this marker | <details><summary>details</summary>From the `onsets` column of the order workbook, relative to the trial's Onset.</details> |
| `diff_s` | s | measured minus designed | <details><summary>details</summary>`t_from_onset_s − expected_from_onset_s`. A consistent sign shows a systematic offset, for example a cue that runs short.</details> |
| `expected_duration_s` | s | designed length of this marker | <details><summary>details</summary>From the `durations` column: cue 1 s, countdown 7.5–30 s, Outcome 2.7 s, WhiteNoise 2.3 s, Rating 6 s.</details> |
| `condition` | – | `PTCT` `PTCS` `PTUO` `UTCT` `UTCS` `UTUO` | <details><summary>details</summary>The four characters after `Onset` in the first marker name. It is NOT in the trk; it comes from the chosen order file. Whether `PTPT` in lab talk equals `PTCT` here is still to be confirmed.</details> |
| `timing` | P/U | predictable / unpredictable time | <details><summary>details</summary>First letter of `condition`.</details> |
| `certainty` | C/U | outcome known at the cue or not | <details><summary>details</summary>Third letter of `condition`.</details> |
| `outcome` | T/S/O | what the *cue* announced | <details><summary>details</summary>Fourth letter. `T` threat, `S` safe, `O` = not announced. For the two uncertain conditions it is `O` on every row.</details> |
| `actual_outcome` | T/S | what the trial really ended in | <details><summary>details</summary>Equal to `outcome` for certain trials; for the uncertain ones it is the last letter of the Outcome marker (`OutcomeUTUOT` → `T`). Empty on run-level rows.</details> |
| `step` | 1–5 | position inside the trial | <details><summary>details</summary>1 Onset, 2 countdown start, 3 Outcome, 4 WhiteNoise, 5 Rating. Empty on run-level rows. The full version adds `WhiteNoise_part2`–`4` rows, also `step = 4`.</details> |

</details>

<details>
<summary><b>05 · <code>event_table_summary.csv</code> (6 columns, one row per subject)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant` | – | subject id |  |
| `status` | – | `ok` / `skipped_no_file` / `skipped_no_events` / `error` | <details><summary>details</summary>sub124, sub128, sub137 are `skipped_no_events`: their trk has no `SoftwareEvent` lines.</details> |
| `order` | 1–5 | chosen trial order |  |
| `nRows` | count | rows written | <details><summary>details</summary>624 for the full table, 372 for the 5-step version; sub134 is one short (no first `START`).</details> |
| `nTrials` | count | trials found |  |
| `note` | – | free text, empty when fine |  |

</details>

<details>
<summary><b>05 · <code>all_subjects_trials_wide.csv</code> (14 columns, one row per trial)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant, order, run, trial` | – | identity of the trial |  |
| `condition, timing, certainty, outcome` | – | as in the event table |  |
| `onset_s` | s | always 0, the reference point |  |
| `countdown_s` | s | countdown start, seconds from Onset |  |
| `outcome_s` | s | Outcome onset |  |
| `whitenoise_s` | s | white-noise onset |  |
| `rating_s` | s | rating onset; `NaN` when no rating |  |
| `has_rating` | logical | whether the trial has a rating | <details><summary>details</summary>24 of 84 trials.</details> |

</details>

<details>
<summary><b>05 · <code>timing_check.csv</code> (7 columns, one row per subject and marker)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant` | – | subject id |  |
| `phase` | – | `1 Onset` … `5 Rating start` |  |
| `n` | count | markers in this cell |  |
| `mean_s, sd_s` | s | mean and SD of `diff_s` | <details><summary>details</summary>Descriptive only. Reproduce it with `ymtcTimingCheck`.</details> |
| `min_s, max_s` | s | extremes of `diff_s` |  |

</details>

<details>
<summary><b>00 · <code>run_check.csv</code> (9 columns, one row per subject)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant, status` | – | subject id; `ok` / `no_file` / `no_events` |  |
| `nSTART, nBurnInStart, nBurnOutStart, nCueStart` | count | event counts |  |
| `trialsPerRun` | – | for example `21/21/21/21` | <details><summary>details</summary>Counted with `BurnInStart` as the run boundary (not `START`, which can be missing).</details> |
| `runAssignmentOK` | 0/1 | every run has 21 trials and the counts agree | <details><summary>details</summary>This is what guards `run = ceil(trial / 21)`.</details> |
| `note` | – | what is wrong, in words |  |

</details>

<details>
<summary><b>The upstream table: what <code>analyzeSegments</code> returns</b></summary>

One table per object: all columns of your `segmentsTable`, then 10 columns per eye appended on the right, prefixed `leftPupil_`, `rightPupil_`, `meanPupil_`. Our data has one pupil, so only `leftPupil_*` appears. In MATLAB the table header also carries `VariableUnits` and `VariableDescriptions`; they are lost when saved as CSV, which is why this page exists.

| column | unit | meaning | details |
|---|---|---|---|
| `segmentStart, segmentEnd` | s | segment boundaries | <details><summary>details</summary>Seconds from the first sample of the recording (first sample = 0). Half-open `[start, end)`. Both `NaN` when the matching event is missing, which makes the whole statistics row `NaN`.</details> |
| `SmoothSig_meanDiam` | px | mean of the smooth signal in the segment | <details><summary>details</summary>`NaN` points are ignored. Interpolated points are included, so a short gap looks perfectly clean; read it together with `SmoothSig_missingDataPercent`.</details> |
| `SmoothSig_minDiam, SmoothSig_maxDiam` | px | minimum / maximum of the smooth signal |  |
| `SmoothSig_missingDataPercent` | % | share of the segment that is `NaN` | <details><summary>details</summary>Only gaps over 250 ms between real valid points become `NaN`. This is the per-segment missingness; use it for quality control.</details> |
| `SmoothSig_sampleCount` | count | all 1000 Hz samples in the segment | <details><summary>details</summary>`NaN` ones included; about segment length × 1000 (a 0.5 s baseline gives 500).</details> |
| `ValidSamples_meanDiam` | px | mean of the real valid samples in the segment | <details><summary>details</summary>No interpolation, no smoothing: only points that passed the three artifact filters.</details> |
| `ValidSamples_minDiam, ValidSamples_maxDiam` | px | minimum / maximum of the valid samples |  |
| `ValidSamples_validPercent` | % | valid fraction of the WHOLE recording | <details><summary>details</summary>`validFraction × 100`: valid points divided by non-empty raw points over the whole recording. The same number on every row of a subject. It is not about this segment.</details> |
| `ValidSamples_sampleCount` | count | valid samples inside the segment | <details><summary>details</summary>At 60 Hz a 0.5 s baseline holds at most about 30.</details> |

</details>

<details>
<summary><b>04 · <code>kret_results.csv</code> (16 columns, one row per subject × trial × segment = 4 per trial)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `segmentStart, segmentEnd` | s | segment boundaries |  |
| `segmentName` | – | for example `countdown_004` | <details><summary>details</summary>Segment type plus trial number; trial 4's countdown.</details> |
| `segmentType` | – | `baseline` / `countdown` / `preOutcome` / `postOutcome` |  |
| `participant, trial` | – | subject id; trial 1–84 |  |

plus the 10 `leftPupil_*` statistic columns (same names as above, prefixed).

</details>

<details>
<summary><b>04 · <code>trials_qc.csv</code> (19 columns = the 16 above + 3 QC flags, repeated on the 4 segment rows of a trial)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `RejectCountdown` | 0/1 | trial rejected | <details><summary>details</summary>`countdown_SmoothSig_missingDataPercent > 50`. Analysis rule R1.</details> |
| `PreOutcomeMostlyMissing` | 0/1 | flag only, trial kept | <details><summary>details</summary>`preOutcome_SmoothSig_missingDataPercent > 50`. The trial's GLM modulator is not trustworthy. Rule R2.</details> |
| `SubjectExcluded` | 0/1 | whole subject excluded | <details><summary>details</summary>More than 20% of the subject's trials rejected. Rule R3 (Leuchs / Shechner 20% rule).</details> |

The first 16 columns are exactly `kret_results.csv`.

</details>

<details>
<summary><b>04 · <code>subjects_qc.csv</code> (5 columns, one row per subject)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `participant` | – | subject id |  |
| `nTrials, nRejected` | count | trials; rejected by R1 |  |
| `rejectPct` | % | `nRejected / nTrials × 100` |  |
| `subjectExcluded` | 0/1 | rejectPct above 20 |  |

</details>

<details>
<summary><b>04 · <code>segments/<name>_leftpupil_segments.csv</code> (6–7 columns, one row per 1000 Hz sample, from <code>exportSegments</code>)</b></summary>

| column | unit | meaning | details |
|---|---|---|---|
| `segmentName, segmentType` | – | as in `segmentsTable` |  |
| `segmentStart_s` | s | segment start | <details><summary>details</summary>Identical on every row of one segment.</details> |
| `tRel_s` | s | sample time minus segment start |  |
| `pupilDiameter_px` | px | smooth-signal diameter, 4 decimals | <details><summary>details</summary>The unit in the name follows `diameterUnit`. `NaN` where the gap exceeded 250 ms.</details> |
| `gap_ms` | ms | distance between the two real valid points around this instant | <details><summary>details</summary>0 when within 0.5 ms of a real point. 1 decimal.</details> |
| `pupilDiameterZ` | z | only with `ZScore=true` | <details><summary>details</summary>(value − whole-recording mean) / whole-recording SD, once per eye over the entire recording (Leuchs 2017), not within the segment.</details> |

</details>

<details>
<summary><b>06 · <code><sub>_final.csv</code> and <code>all_subjects_final.csv</code> — 69 columns, one row per marker</b></summary>

Built by `ymtcMergeResults` from the 5-step event table. Each segment's statistics sit on the marker row it belongs to: baseline → Onset, countdown and preOutcome → countdown row, postOutcome → Outcome row. WhiteNoise and Rating rows have `NaN` there. Full column list:

**Event columns, same as the event table** (18)

`participant`, `order`, `run`, `trial`, `trial_in_run`, `ymtc_marker`, `trk_event`, `time_ms`, `t_from_onset_s`, `expected_from_onset_s`, `diff_s`, `expected_duration_s`, `condition`, `timing`, `certainty`, `outcome`, `actual_outcome`, `step`

**Segment `baseline` — written on rows with `step = 1`; `NaN` on the other rows of the trial** (12)

`baseline_segmentStart`, `baseline_segmentEnd`, `baseline_SmoothSig_meanDiam`, `baseline_SmoothSig_minDiam`, `baseline_SmoothSig_maxDiam`, `baseline_SmoothSig_missingDataPercent`, `baseline_SmoothSig_sampleCount`, `baseline_ValidSamples_meanDiam`, `baseline_ValidSamples_minDiam`, `baseline_ValidSamples_maxDiam`, `baseline_ValidSamples_validPercent`, `baseline_ValidSamples_sampleCount`

**Segment `countdown` — written on rows with `step = 2`; `NaN` on the other rows of the trial** (12)

`countdown_segmentStart`, `countdown_segmentEnd`, `countdown_SmoothSig_meanDiam`, `countdown_SmoothSig_minDiam`, `countdown_SmoothSig_maxDiam`, `countdown_SmoothSig_missingDataPercent`, `countdown_SmoothSig_sampleCount`, `countdown_ValidSamples_meanDiam`, `countdown_ValidSamples_minDiam`, `countdown_ValidSamples_maxDiam`, `countdown_ValidSamples_validPercent`, `countdown_ValidSamples_sampleCount`

**Segment `preOutcome` — written on rows with `step = 2`; `NaN` on the other rows of the trial** (12)

`preOutcome_segmentStart`, `preOutcome_segmentEnd`, `preOutcome_SmoothSig_meanDiam`, `preOutcome_SmoothSig_minDiam`, `preOutcome_SmoothSig_maxDiam`, `preOutcome_SmoothSig_missingDataPercent`, `preOutcome_SmoothSig_sampleCount`, `preOutcome_ValidSamples_meanDiam`, `preOutcome_ValidSamples_minDiam`, `preOutcome_ValidSamples_maxDiam`, `preOutcome_ValidSamples_validPercent`, `preOutcome_ValidSamples_sampleCount`

**Segment `postOutcome` — written on rows with `step = 3`; `NaN` on the other rows of the trial** (12)

`postOutcome_segmentStart`, `postOutcome_segmentEnd`, `postOutcome_SmoothSig_meanDiam`, `postOutcome_SmoothSig_minDiam`, `postOutcome_SmoothSig_maxDiam`, `postOutcome_SmoothSig_missingDataPercent`, `postOutcome_SmoothSig_sampleCount`, `postOutcome_ValidSamples_meanDiam`, `postOutcome_ValidSamples_minDiam`, `postOutcome_ValidSamples_maxDiam`, `postOutcome_ValidSamples_validPercent`, `postOutcome_ValidSamples_sampleCount`

**Quality control, copied onto every row of the trial (run-level rows: `NaN`)** (3)

`RejectCountdown`, `PreOutcomeMostlyMissing`, `SubjectExcluded`

</details>

## 4. Settings

<details>
<summary><b><code>settings.raw</code> (from <code>rawDataFilter()</code>)</b></summary>

| setting | default | meaning |
|---|---|---|
| `PupilDiameter_Min / _Max` | 1.5 / 9 | Range filter. The defaults are MILLIMETRES; pixel data must override them (`Examples/Dataset_1` uses 0.1 / inf). Our pipeline sets them from the data (0.5–99.5 percentile × 0.8 / 1.2) and prints the values. |
| `islandFilter_islandSeperation_ms` | 40 ms | How far from other samples a cluster must be to count as an island. |
| `islandFilter_minIslandWidth_ms` | 50 ms | Islands narrower than this are invalid. |
| `dilationSpeedFilter_MadMultiplier` | 16 | Speed above median + this × MAD is invalid (catches blink edges). |
| `dilationSpeedFilter_maxGap_ms` | 200 ms | Speed is only computed when two valid samples are closer than this. |
| `gapDetect_minWidth / _maxWidth` | 75 / 2000 ms | A missing stretch of this width counts as a gap whose edges get padded. |
| `gapPadding_backward / _forward` | 50 / 50 ms | Extra samples rejected before / after such a gap. |
| `residualsFilter_passes` | 4 | Passes of the trend-deviation filter. |
| `residualsFilter_MadMultiplier` | 16 | Deviation above median + this × MAD from the trend is invalid. |
| `residualsFilter_interpFs / _lowpassCF` | 100 Hz / 16 Hz | Resampling rate and cut-off used to build the trend line (1st-order Butterworth). |
| `keepFilterData` | true | Keep `speedFiltData` / `devFiltData`. Uses memory; set `false` after tuning. |

</details>

<details>
<summary><b><code>settings.valid</code> (from <code>ValidSamplesModel.getDefaultSettings()</code>)</b></summary>

| setting | default | meaning |
|---|---|---|
| `interp_upsamplingFreq` | 1000 Hz | Sampling rate of the smooth signal. |
| `LpFilt_B / LpFilt_A` | order 4, 4 Hz | Low-pass coefficients computed from order 4 and cut-off 4 Hz at 1000 Hz (zero-phase `filtfilt`). |
| `interp_maxGap` | 250 ms | Gaps between real valid points larger than this become `NaN` in the smooth signal. |

</details>

<details>
<summary><b><code>trk2csv</code> options</b></summary>

| setting | default | meaning |
|---|---|---|
| `OutFolder` | folder of the .trk | Where the csv goes. |
| `Overwrite` | true | Overwrite an existing csv. |
| `WriteReport` | false | Also write `<name>_issues.csv`. |
| `ExpectedRuns` | 4 | Expected number of `START` events. |
| `ExpectedTrialsPerRun` | 21 | Expected trials per run (84 in total). |
| `CueDurationSec / CueToleranceSec` | 1.0 / 0.001 | Cue length in the task setting, and the allowed difference. |
| `MinValidFraction` | 0.5 | Pupil-valid fraction below this is reported (`LOW_PUPIL_VALID`); nothing is dropped. |
| `MaxGapMs` | 200 | Sample spacing above this is reported (`TIME_GAP`). |
| `Quiet` | false | Suppress printing. |

</details>

<details>
<summary><b><code>csv2kretmat</code> options</b></summary>

| setting | default | meaning |
|---|---|---|
| `PupilMeasure` | 'mean' | `'mean'` / `'2a'` / `'2b'`: which ellipse axis (or the mean of both) becomes the pupil size. |
| `BaselineWinSec` | 0.5 | Length of the pre-cue baseline segment; 0 turns it off. |
| `PreOutcomeWinSec / PostOutcomeWinSec` | 2.0 / 2.0 | Length of the segments before and after the outcome; 0 turns the pre-outcome one off. |

</details>

## 5. Files and functions

```
trk2csv_batch ──▶ trk2csv ──▶ private/readTrk ─▶ private/labelSamples ─▶ private/checkTrk
                                  (parse)          (events on samples)      (record only)

ymtcEventTableBatch ──▶ ymtcEventTable ──▶ readOrder()   (subfunction, same file)
         │                    │
         │                    └──▶ 05_markers/05_<sub>_markers[_5step].csv
         └──▶ ymtcTrialWide  / ymtcTimingCheck     (read that table, write one file each)

ymtcRunCheck     standalone: reads 03_events, writes 07_checks/07_all_run_check.csv
ymtcConfig       read by every ymtc* function: where the folders are
checkDocs        compares docs/02 with the real header of every output table
```

| file | lines | what it does | writes |
|---|---|---|---|
| `trk2csv.m` | 87 | one .trk → one per-sample CSV + a report | 02_samples/<name>.csv |
| `trk2csv_batch.m` | 76 | a folder of .trk → the same, plus two QC tables | 02_all_qc_summary.csv, 02_all_issues.csv |
| `private/readTrk.m` | 79 | parse the text log into header / samples / events | in memory |
| `private/labelSamples.m` | 46 | attach events to samples, carry run / trial / phase forward | in memory |
| `private/checkTrk.m` | 134 | compare with what the task should have produced; record, never repair | 02_all_issues.csv rows |
| `ymtcEventTable.m` | 184 | one subject → one row per marker, in task order | 05_markers/05_<sub>_markers[_5step].csv |
| `ymtcEventTableBatch.m` | 122 | loop over subjects, add the summary and the combined tables | 05_all_markers*.csv, 05_all_markers_summary.csv |
| `ymtcTimingCheck.m` | 71 | descriptive diff_s per subject and marker | 05_all_timing_check.csv |
| `ymtcTrialWide.m` | 68 | long marker table → one row per trial | 05_all_trials_wide.csv |
| `ymtcRunCheck.m` | 117 | is every run really 21 trials (BurnInStart as the boundary) | 07_checks/07_all_run_check.csv |
| `ymtcConfig.m` | 40 | folder layout; no path is hard-coded | struct C |
| `checkDocs.m` | 101 | compare docs/02 with the real table headers | console |

<details>
<summary><b>Original code (<code>helperFunctions/</code>)</b></summary>

<details>
<summary><code>rawDataFilter.m</code></summary>

Main function calls `removeOutOfBounds` (range) → `madSpeedFilter` (speed, catches blinks) → `madDeviationFilter` (deviation from trend). `removeLoners` (isolated points) is called repeatedly inside all three, `expandGaps` (reject around gaps) inside the speed filter; `madCalc` computes MAD thresholds. With no arguments it returns the default `settings.raw`.

</details>

<details>
<summary><code>genMeanDiaSamples.m</code></summary>

Combines two eyes into one mean diameter; called by `processValidSamples`; unused for one-eye data.

</details>

<details>
<summary><code>plotSegments.m</code></summary>

Draws the segment table as colour patches; called by `plotData`.

</details>

<details>
<summary><code>printToConsole.m</code></summary>

Progress messages; internal.

</details>

<details>
<summary><code>legacyModeCheck.m</code></summary>

Adds `LEGACY/` to the path for MATLAB older than 8.3 (no `table`); nothing on newer versions.

</details>

<details>
<summary><code>FALLBACK/</code></summary>

Replacements for `butter`, `filtfilt`, `histc`, `nanmin` / `nanmax` / `nanmean` / `nanmedian` for MATLAB without the toolbox or with the function removed. TRAP: `addpath(genpath(...))` puts folders at the FRONT, so a FALLBACK function shadows the real toolbox one; use `addpath(..., '-end')` to prefer the toolbox. This machine has no Statistics toolbox, so the `nan*` ones are always FALLBACK.

</details>

<details>
<summary><code>LEGACY/</code></summary>

Emulates `table` for very old MATLAB.

</details>

</details>

<details>
<summary><b>Our layer (<code>ymtc/</code> and the adapter)</b></summary>

<details>
<summary><code>trk2csv.m</code></summary>

One `.trk` → one per-sample CSV plus a report. Needs no toolbox.

</details>

<details>
<summary><code>trk2csv_batch.m</code></summary>

A folder of `.trk` → `csv/` plus `trk2csv_qc_summary.csv` and `trk2csv_issues.csv`.

</details>

<details>
<summary><code>private/readTrk.m, labelSamples.m, checkTrk.m</code></summary>

Parse the text log; attach events and carry run / trial / phase forward; compare with what the task should have produced (record only).

</details>

<details>
<summary><code>ymtcEventTable.m</code></summary>

One subject → marker table in task order. Picks the trial order by matching countdown lengths.

</details>

<details>
<summary><code>ymtcEventTableBatch.m</code></summary>

All subjects at once, plus `event_table_summary.csv` and the combined tables.

</details>

<details>
<summary><code>ymtcRunCheck.m</code></summary>

Is every run really 21 trials? → `run_check.csv`.

</details>

<details>
<summary><code>ymtcTimingCheck.m, ymtcTrialWide.m</code></summary>

Read the marker table: `timing_check.csv` and `all_subjects_trials_wide.csv`.

</details>

<details>
<summary><code>ymtcMergeResults.m</code></summary>

Joins the 5-step marker table with `kret_results.csv` and `trials_qc.csv` by participant + trial → `06_最终结果/<sub>_final.csv` and `all_subjects_final.csv` (69 columns). Nothing is repaired; a trial with no Kret row stays `NaN`.

</details>

<details>
<summary><code>csv2kretmat.m, example_kret_pipeline.m</code></summary>

Adapter and batch script for the Kret pipeline (in `代码_matlab/`, outside this repository). The adapter re-references time to 0, removes duplicate timestamps (keeps the first), sets `NaN` where `pupil_valid == 0`, and writes `diameterUnit = 'px'`.

</details>

<details>
<summary><code>ymtcConfig.m, checkDocs.m</code></summary>

Folder locations (no absolute path in the repository); `checkDocs` compares the documented columns with the real CSV headers.

</details>

</details>

## 6. The two official examples

`main_Dataset1.m` is the shortest demonstration of steps (1)–(5). Our YMTC data follows the same one-pupil route with `trk2csv` as converter.

<details>
<summary><code>Examples/Dataset_1/</code></summary>

SR-Research Eyelink, ONE pupil. `batchFileConverter_Dataset1.m` (EDF → .mat) and `main_Dataset1.m` (full pipeline). It sets `PupilDiameter_Max = inf`, `PupilDiameter_Min = 0.1` (arbitrary units) and `keepFilterData = true`.

</details>

<details>
<summary><code>Examples/Dataset_2/</code></summary>

E-Prime + Tobii, TWO pupils. `batchFileConverter_Dataset2.m` (.gazedata → .mat) and `main_Dataset2.m`.

</details>

## 7. Troubleshooting: symptom → cause → fix

| symptom | cause | fix |
|---|---|---|
| `'t_ms' must be sorted!` | timestamps not ascending (duplicate or backward timestamps in the trk) | sort / deduplicate in the converter, not inside the package; record the duplicates |
| `'L' must be empty, or have the same length as 't_ms'` | diameter and time vectors differ in length | check lengths in the converter |
| `No settings present.` | `PupilDataModel` built without `settings` | start from `PupilDataModel.getDefaultSettings()` and edit |
| `Interpolation cannot be performed.` | fewer than 2 valid points for that eye (wrong range, or all noise) | check that `PupilDiameter_Min/Max` match the unit |
| `almost every sample is invalid` | default range 1.5–9 is mm, pixel data lies outside | set the range in the real unit |
| `warning pupilSize:edgeClamp` | floating-point error put upsampled times outside the valid range; they were clamped | only a notice; investigate if the count is large |
| `ValidSamples_validPercent identical on every row` | whole-recording value by design | use `SmoothSig_missingDataPercent` for per-segment missingness |
| `SmoothSig_meanDiam looks fine but the data is poor` | gaps shorter than 250 ms were interpolated over | read `missingDataPercent` and `ValidSamples_sampleCount` too |
| `a whole result row is NaN` | segment start/end is `NaN` (missing event), or no samples fall inside | check the event table for the missing marker; nothing is imputed |
| `plotData does nothing / is skipped` | `-batch` has no desktop | run in desktop MATLAB |
| `plotData shows one file only` | `plotMultipleFiles = false` in the source (heavy) | change that switch in `PupilDataModel.m` |
| `addpath fails in Examples` | paths written with Windows backslashes `..\..\helperFunctions\` | use `../../helperFunctions/` on macOS / Linux |
| `MATLAB -batch` fails with several lines | `-batch` takes ONE line of command | put the code in a script file and `run('x.m')` |

## 8. Limitations

- The original README requires the Signal Processing and Statistics toolboxes and was tested on MATLAB 2012b / 2016a / 2017a on Windows 7. This fork patches it for macOS (path separator in `PupilDataModel`, `FALLBACK/`); see `git log`.
- The filter parameters are the paper's defaults and have NOT been tuned for YMTC data. Tuning needs desktop MATLAB and `plotData()` on the raw traces.
- Pupil size is in camera pixels, from one eye; gaze is not recorded; the unit of `pupil_angle` and the meaning of the `sp_` prefix are unconfirmed.
- This page describes what the code does, not whether the results are good. Data quality: [`../docs/05_data_quality.md`](../docs/05_data_quality.md).

## 9. Review map: what to read, and in what order

If you have to check this code yourself, this is the shortest route. Every path below is real; the line counts are taken from the files.

```
code/ymtc/                        in this repository
  ymtcEventTable.m                184   the marker table itself
  trk2csv.m                        87   one .trk -> one csv
  private/readTrk.m                79   the text parser
  private/labelSamples.m           46   events -> samples
  private/checkTrk.m              134   what is recorded as an anomaly
  ymtcEventTableBatch / RunCheck / TimingCheck / TrialWide   wrappers, skim

代码_matlab/                      with the study data, not in this repository
  csv2kretmat.m                   259   the four segment definitions
  example_kret_pipeline.m         140   filter -> interpolate -> segment -> stats
  ymtcTrialQC.m                   110   the three rejection rules
  ymtcMergeResults.m              ~110  how the 69 columns are assembled
```

| read | what to confirm while reading | why it matters | time |
|---|---|---|---|
| 1. `ymtcEventTable.m` | the five marker/event pairs; how the trial order is chosen; where `condition` / `timing` / `certainty` / `outcome` come from; what `diff_s` is; why `run = ceil(trial/21)` | every claim about task conditions rests on this file | 40 min |
| 2. `trk2csv.m` -> `private/readTrk.m` -> `labelSamples.m` -> `checkTrk.m` | how one csv row is built; what is recorded instead of repaired | the input of everything else | 60 min |
| 3. `csv2kretmat.m` | the four segments and their windows; the time-zero convention | decides what "countdown" means in every pupil column | 30 min |
| 4. `example_kret_pipeline.m` + `docs/03` | which filter runs when; what is a paper default and what we changed | the only place a number is produced | 40 min |
| 5. `ymtcTrialQC.m` + `docs/05` | the three rules and their thresholds | decides which trials survive | 20 min |
| 6. `ymtcMergeResults.m` | the join key (`participant` + `run` + `trial`) and the column order | explains the 69-column table | 20 min |

Three routes, depending on how much time you have:

- **30 minutes**: file 1 only, with the dictionary open on `docs/02` - enough to defend every column of the marker table.
- **2 hours**: files 1-2, plus `checkDocs` - enough to defend the whole preparation layer.
- **half a day**: all six - enough to defend every number in the final table.

## 10. Further reading

[`../docs/01_pipeline_overview.md`](../docs/01_pipeline_overview.md) · [`../docs/02_column_dictionary.md`](../docs/02_column_dictionary.md) · [`../docs/03_pupil_size_internals.md`](../docs/03_pupil_size_internals.md) · [`ymtc/README.md`](ymtc/README.md) · [`../docs/04_our_code.md`](../docs/04_our_code.md) · [`../docs/06_faq.md`](../docs/06_faq.md)

Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.

[↑ top](#top) · **[English](#english) · [한국어](#한국어) · [中文](#中文)**

---

<a id="한국어"></a>

# code/ — pupil-size 툴박스와 우리의 YMTC 계층: 한 페이지에 모두

원본 Kret & Sjak-Shie (2019) 코드와 우리의 `ymtc/` 계층을 한 페이지에 담았다. 모든 출력 표를 열 단위로 나열했다. 삼각형을 누르면 세부 설명이 펼쳐진다. 소스나 실제 파일을 대조해 썼고, 확인하지 못한 것은 그렇다고 적었다.

## 1. 지도: 모든 표와 그 출처

폴더 번호(`00`–`06`)는 이 저장소 옆의 데이터 폴더이다. `[ymtc]` = `code/ymtc/`의 우리 코드, `[Kret code]` = `code/dataModels/`의 원본 클래스, `[Kret 어댑터]` = 둘을 잇는 우리 코드.

```
01 원본 trk      01_원본trk/*.trk              녹화 날짜가 파일명에 있음; 이름 변경 금지
      │  trk2csv_batch
      ▼
02 샘플          02_샘플/subNNN_*.csv (21열) + 02_all_qc_summary.csv + 02_all_issues.csv
      │
      ├──▶ 03 이벤트    03_이벤트/subNNN_events.csv
      │        │  ymtcEventTable (+ TrialOrder-HK/*.xlsx)
      │        ▼
      │   05 marker 표  05_all_markers.csv (18열) · 05_all_markers_5step.csv
      │        ├ ymtcTrialWide    → 05_all_trials_wide.csv (14)
      │        └ ymtcTimingCheck  → 05_all_timing_check.csv (7)
      │
      └──▶ 04 눈동자 지표  csv2kretmat → .mat → PupilDataModel
               │  04_all_segments.csv (16) · 04_all_trials_qc.csv (19) · 04_all_subjects_qc.csv (5)
               │  segments/subNNN_leftpupil_segments.csv
               ▼
         06 병합표      06_all_merged.csv (69열) = 05 marker + 4구간 × 12통계 + 3 QC 플래그

별도 점검(다운스트림 없음):
     03 이벤트 ──ymtcRunCheck──▶ 07 점검  07_all_run_check.csv (9)
```

02에서 두 갈래(03 이벤트 / 04 눈동자 지표)로 나뉘고, 03이 05를 만들며,
04와 05가 06에서 합쳐진다. 07은 03만 검사한다.

| 표 | 파일 | 행 | 열 | 생성 |
|---|---|---|---|---|
| per-sample CSV | `02_samples/<name>.csv` | 1 / sample | 21 | trk2csv [ymtc] |
| QC summary | `02_samples/02_all_qc_summary.csv` | 1 / file | 25 | trk2csv_batch [ymtc] |
| issues | `02_samples/02_all_issues.csv` | 1 / anomaly | 5 | trk2csv_batch [ymtc] |
| events | `03_events/<sub>_events.csv` | 1 / event | 3 | event extraction |
| event table | `05_markers/05_<sub>_markers[_5step].csv` | 1 / marker (624 · 372) | 18 | ymtcEventTable [ymtc] |
| event summary | `05_markers/05_all_markers_summary.csv` | 1 / subject | 6 | ymtcEventTableBatch [ymtc] |
| trials wide | `05_markers/05_all_trials_wide.csv` | 1 / trial | 14 | ymtcTrialWide [ymtc] |
| timing check | `05_markers/05_all_timing_check.csv` | 1 / subject × marker | 7 | ymtcTimingCheck [ymtc] |
| run check | `07_checks/07_all_run_check.csv` | 1 / subject | 9 | ymtcRunCheck [ymtc] |
| Kret results | `04_pupil/04_all_segments.csv` | 1 / trial × segment | 16 | analyzeSegments [Kret code] |
| trial QC | `04_pupil/04_all_trials_qc.csv` | 1 / trial × segment | 19 | Kret pipeline script |
| subject QC | `04_pupil/04_all_subjects_qc.csv` | 1 / subject | 5 | Kret pipeline script |
| segment curves | `04_pupil/segments/<name>_leftpupil_segments.csv` | 1 / 1000 Hz sample | 7 | exportSegments [Kret code] |
| final | `06_merged/06_<sub>_merged.csv, 06_all_merged.csv` | 1 / marker | 69 | ymtcMergeResults [ymtc] |

## 2. Kret & Sjak-Shie 파이프라인 (원본 코드)

설계 요점: 파이프라인은 표시(`isValid`)만 하고 원시 직경을 덮어쓰지 않는다. valid 샘플과 평활 신호는 별개의 객체이다. 모든 임계값은 `getDefaultSettings()`에 있고 객체마다 자기 설정을 가진다. 왼쪽·오른쪽·평균을 따로 분석한다. 시간 단위: `t_ms`는 밀리초, `segmentStart`·`segmentEnd`·`signal.t`는 초.

```
RawFileModel ──saveMatFile──▶ <name>.mat
        │
        ▼  PupilDataModel.batchConstructor(...)        파일마다 객체 하나
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter     원시 샘플마다 isValid
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth              1000 Hz 평활 신호
 (3) analyzeSegments()       ValidSamplesModel.analyze                      구간·눈마다 통계량 10개
 (4) exportSegments(folder)  구간별 연속 시간 곡선 → CSV
 (5) plotData()              육안 점검 (데스크톱 MATLAB 필요)
```

#### 각 단계가 실제로 하는 일

| 단계 | 함수 (파일:행) | 판단 | 주요 설정 |
|---|---|---|---|
| 1 범위 | `removeOutOfBounds` (`rawDataFilter.m:197`) | 그럴듯한 범위를 벗어난 직경은 무효 | `PupilDiameter_Min/_Max` (기본 1.5 / 9, **밀리미터**) |
| 2 깜박임 | `madSpeedFilter` (`229`) + `expandGaps` (`511`) | `median + 16 MAD`를 넘는 샘플 간 속도, 그리고 75 ms보다 넓은 간격 주변 50 ms | `dilationSpeedFilter_MadMultiplier=16`, `maxGap_ms=200` |
| 3 추세 | `madDeviationFilter` (`284`) | 16 Hz 저역 통과 추세선에서 `median + 16 MAD` 이상 벗어난 점. 4회 반복으로 잘못 제거된 샘플이 돌아온다 | `residualsFilter_passes=4` |
| 4 고립 | `removeLoners` (`440`) | 50 ms보다 좁고 40 ms 이상 떨어진 섬 | `minIslandWidth_ms=50`, `islandSeperation_ms=40` |
| 5 평활 | `interpAndSmooth` (`ValidSamplesModel.m:107`) | 1000 Hz 선형 보간 후 4차 Butterworth 4 Hz, 영위상(`filtfilt`) | `interp_upsamplingFreq=1000`, `LpFilt_cutoffFreq=4` |
| 6 구간 | `analyze` (`203`) | 구간별 평균/최소/최대/결측%를 평활 신호와 유효 샘플 양쪽에서 | — |

모든 임계값은 `median + n*MAD`이며 평균 ± SD가 아니다. 큰 아티팩트 몇 개가 SD를 부풀려 스스로를 숨기기 때문이다. 위 값은 모두 논문 기본값이고, 우리 파이프라인은 범위 필터만 바꾼다(논문 값은 밀리미터, 우리 데이터는 픽셀).

코드는 직경을 절대 고치지 않는다. `rawDataFilter`는 논리 벡터(`isValid`) 하나를 돌려주고 원시 샘플은 그대로 남는다.

### 2.1 입력: .mat 파일 (`RawFileModel`)

`RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename)`은 입력을 검사하고 변수 네 개가 든 `.mat`을 쓴다. 필드별로 펼쳐 보라:

<details>
<summary><code>diameterUnit</code></summary>

직경 단위를 나타내는 문자열(예: `'mm'`, `'px'`). 모든 결과와 내보낸 CSV 열 이름에 복사된다. 패키지는 단위를 변환하지 않으며 라벨일 뿐이다.

</details>

<details>
<summary><code>diameter.t_ms</code></summary>

모든 샘플의 시각(ms), 열 벡터 하나. 오름차순이어야 하며(`issorted`) 0에서 시작하는 것이 좋다(원래 시선추적기 시각은 `zeroTime_ms`에). 타임스탬프가 중복되면 필터가 깨지므로 우리 변환기는 중복 중 첫 번째만 남긴다.

</details>

<details>
<summary><code>diameter.L</code></summary>

각 샘플의 왼쪽 눈 동공 직경. `t_ms`와 길이가 같고 추적기가 값을 주지 않은 곳은 `NaN`. 왼쪽 눈을 측정하지 않았으면 비워 둔다(`[]`). 눈이 하나만 측정되면 EyeLink 예제처럼 여기에 넣는 것이 관례이며, 우리 MRC 데이터(동공 하나)도 `L`에 넣는다.

</details>

<details>
<summary><code>diameter.R</code></summary>

오른쪽 눈에 대해 동일. 우리 데이터에서는 비어 있다. `L`과 `R`이 모두 있으면 둘의 평균인 `mean` 동공도 만든다.

</details>

<details>
<summary><code>zeroTime_ms</code></summary>

`t = 0`에 해당하는 시선추적기 자체 타임스탬프(ms). 기록용으로만 저장되며 패키지는 쓰지 않는다.

</details>

<details>
<summary><code>segmentsTable.segmentStart / segmentEnd</code></summary>

각 구간의 시작과 끝, **초** 단위(ms 아님), `t_ms/1000`과 같은 시계. 시작 또는 끝이 `NaN`이면 그 구간의 통계도 `NaN`. 구간은 겹쳐도 된다.

</details>

<details>
<summary><code>segmentsTable.segmentName</code></summary>

구간 이름(예: `countdown_004`). 그림에 표시되고 결과로 복사된다.

</details>

<details>
<summary><code>segmentsTable (extra columns)</code></summary>

그 밖의 모든 열(participant, trial, segmentType, condition …)은 결과 표 왼쪽에 그대로 따라온다. `exportSegments`는 `segmentType`이라는 열도 찾는다.

</details>

<details>
<summary><code>csv2kretmat</code>이 쓰는 .mat의 내용</summary>

`diameterUnit = 'px'`; `diameter.t_ms`(ms, 0에서 시작), `diameter.L`(동공 크기, `NaN` = 결측), `diameter.R` 비어 있음; `zeroTime_ms` = 첫 샘플의 원래 MRC 타임스탬프; `segmentsTable`은 `segmentStart`, `segmentEnd`, `segmentName`과 `segmentType`, `participant`, `trial`. trial마다 구간 네 종류: `baseline` `[CueStart − 0.5 s, CueStart)`, `countdown` `[CueStart, StimuliStart)`, `preOutcome` `[StimuliStart − 2 s, StimuliStart)`, `postOutcome` `[StimuliStart, StimuliStart + 2 s)`. i번째 `CueStart`와 i번째 `StimuliStart`를 짝지운다. 경계는 설계값이 아니라 **실측** 마커에서 온다.

</details>

### 2.2 객체와 필드

<details>
<summary><b><code>PupilDataModel</code> — 속성</b></summary>

<details>
<summary><code>filename, filepath</code></summary>

이 객체를 만든 .mat 파일의 이름과 폴더.

</details>

<details>
<summary><code>settings</code></summary>

두 부분으로 된 구조체: `settings.raw`(아티팩트 필터)와 `settings.valid`(보간·저역통과). 객체마다 자기 사본을 가진다.

</details>

<details>
<summary><code>eyesWithData</code></summary>

데이터가 있는 눈: `{'left'}`, `{'right'}`, `{'left','right'}`, `{}`. 그 밖의 값은 오류. 어느 눈을 필터·분석할지 결정한다.

</details>

<details>
<summary><code>timestamps_RawData_ms</code></summary>

원시 샘플의 공통 시간 벡터(ms), `diameter.t_ms`에서.

</details>

<details>
<summary><code>leftPupil_RawData, rightPupil_RawData</code></summary>

각 눈의 `RawSamplesModel`(데이터가 없으면 비어 있음).

</details>

<details>
<summary><code>leftPupil_ValidSamples, rightPupil_ValidSamples, meanPupil_ValidSamples</code></summary>

각 눈의 `ValidSamplesModel`, `processValidSamples`가 만든다. `meanPupil_ValidSamples`는 두 눈 모두 데이터가 있을 때만 존재.

</details>

<details>
<summary><code>segmentsTable, zeroTime_ms, diameterUnit</code></summary>

.mat 파일에서 복사(위의 파일 내용 참조).

</details>

</details>

<details>
<summary><b><code>RawSamplesModel</code> — 속성</b></summary>

<details>
<summary><code>eye</code></summary>

`'left'` 또는 `'right'`.

</details>

<details>
<summary><code>rawSample</code></summary>

이 눈의 원시 직경 벡터, 수정되지 않는다.

</details>

<details>
<summary><code>isValid</code></summary>

논리 벡터, 원시 샘플마다 하나: `true` = 범위·속도·편차 필터 통과. `filterRawData`의 결과. `NaN` 원시 샘플은 `false`.

</details>

<details>
<summary><code>speedFiltData</code></summary>

속도 필터의 중간 결과(`keepFilterData = true`일 때만 보관): `maxDilationSpeeds`(샘플마다 두 이웃과의 절대 속도 중 큰 값, 두 이웃이 모두 200 ms보다 멀 때만 `NaN`), `isValid`(속도 필터 이후), `mad`, `thresh`(중앙값 + 16 × MAD, 기준선), `med_d`(중앙값).

</details>

<details>
<summary><code>devFiltData</code></summary>

편차 필터의 중간 결과, 반복(기본 4회)마다 한 열: `isValidPerPass`, `residualsPerPass`(평활 추세선으로부터의 거리), `threshPerPass`, `smoothBaselinePerPass`(추세선). 어떤 반복이 아무것도 바꾸지 않으면 이후 반복은 그 결과를 복사한다.

</details>

</details>

<details>
<summary><b><code>ValidSamplesModel</code> — 속성</b></summary>

<details>
<summary><code>eye</code></summary>

`'left'`, `'right'`, `'mean'`.

</details>

<details>
<summary><code>samples.t_ms, samples.pupilDiameter</code></summary>

valid 원시 샘플만: 시각(ms)과 직경.

</details>

<details>
<summary><code>validFraction</code></summary>

기록 **전체**에서 비어 있지 않은 원시 샘플 중 valid 샘플의 비율(0–1). 모든 행에 `ValidSamples_validPercent`(×100)로 보고된다. `mean` 동공은 두 눈 중 작은 값.

</details>

<details>
<summary><code>signal.t</code></summary>

평활 신호의 1000 Hz 시간축, **초** 단위.

</details>

<details>
<summary><code>signal.pupilDiameter</code></summary>

평활 신호: valid 샘플을 `signal.t`로 선형 보간한 뒤 4차 4 Hz Butterworth 저역통과(영위상 `filtfilt`). 실제 valid 점 사이 공백이 `interp_maxGap`(250 ms)을 넘는 곳은 `NaN`.

</details>

<details>
<summary><code>signal.gap_ms</code></summary>

각 시점 앞뒤 두 실제 valid 샘플 사이의 거리(ms). 실제 샘플에서 0.5 ms 이내면 0. (클래스는 `gap` 필드를 선언하지만 코드는 `gap_ms`에 쓴다.)

</details>

</details>

### 2.3 메서드: 입력 → 출력

| 메서드 | 입력 | 출력 | 콘솔 메시지 |
|---|---|---|---|
| `PupilDataModel.batchConstructor(folder, dirStruct, settings)` | 폴더, `dir('*.mat')` 결과, 설정 | 객체 배열 | `Constructing N Data Objects...` |
| `filterRawData()` | — | 각 눈에 `isValid` 저장 | `Filtering the raw data in N files...` |
| `processValidSamples()` | — (`isValid` 필요) | 평활 신호를 가진 `*_ValidSamples` 객체; 두 눈이면 `mean`도 | `Interpolating and smooting the valid raw data subsets of N files...` |
| `analyzeSegments()` | — (평활 신호 필요) | cell 배열, 객체마다 결과 표 하나. `vertcat(results{:})`로 합침 | `File i (name): analyzing K segments.` |
| `exportSegments(folder, options)` | 출력 폴더; 옵션 `Eyes`, `SegmentTypes`, `NaNString`, `ZScore` | 객체·눈마다 CSV 하나 | `File i (name) left pupil: wrote N samples to <file>` |
| `plotData()` | — | 그림 창 | `—` |

## 3. 출력 표, 열 단위

각 표는 모든 열을 나열한다. 마지막 열의 삼각형을 누르면 계산 방법, 함정, 알려진 주의점이 펼쳐진다.

<details>
<summary><b>02 · 샘플 단위 CSV — <code>trk2csv</code>가 쓰는 <code><name>.csv</code> (21열, 시선추적기 샘플마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant` | – | 피험자 ID | <details><summary>세부</summary>파일명에서 가져온다(`sub149_...trk` → `sub149`). 이름이 `sub<숫자>`로 시작하지 않으면 확장자를 뺀 전체 이름을 쓴다.</details> |
| `run` | – | run 번호 0–4 | <details><summary>세부</summary>`START` 이벤트만 센다. 첫 `START` 이전 샘플은 `0`. 첫 `START`가 없는 파일은 run 번호가 하나씩 낮아지며, 고치지 않고 이상치 표에 기록한다.</details> |
| `trial` | – | 파일 내 trial 번호 0–84 | <details><summary>세부</summary>`CueStart`마다 1씩 증가. 첫 cue 이전은 `0`.</details> |
| `trial_in_run` | – | run 안의 trial 번호 0–21 | <details><summary>세부</summary>`START`마다 0으로 초기화.</details> |
| `phase` | – | 샘플이 속한 과제 단계 | <details><summary>세부</summary>마지막 이벤트에서 앞으로 이어진다. 값: `pre`, `start`, `burn_in`, `cue`, `countdown`, `stimulus`, `whitenoise1`–`whitenoise4`, `rating`, `burn_out`. `CountdownFinish`와 알 수 없는 이벤트는 현재 단계를 유지.</details> |
| `time_ms` | ms | 샘플의 시선추적기 원시 타임스탬프 | <details><summary>세부</summary>큰 누적 카운터(예: `1491312812.2`)이며 0에서 시작하지 않는다. 샘플 간격은 약 16.7 ms(60 Hz). 시간이 거꾸로 가도 로그 순서대로 둔다(`NONMONOTONIC_TIME`).</details> |
| `t_run_s` | s | 현재 run의 `START` 이후 초 | <details><summary>세부</summary>첫 `START` 이전에는 `NaN`.</details> |
| `event` | – | 이 샘플에 붙은 소프트웨어 이벤트, 없으면 빈칸 | <details><summary>세부</summary>각 이벤트는 타임스탬프가 이벤트 시각 이상인 첫 샘플에 붙으므로 시각 오차가 최대 한 샘플 간격(약 17 ms). 한 샘플에 이벤트가 여럿이면 `;`로 잇는다. 알려진 이름: `START`, `BurnInStart`, `CueStart`, `CueFinish`, `CountdownFinish`, `StimuliStart`, `WhitenoiseStart1`–`4`, `RatingStart`, `BurnOutStart`.</details> |
| `sp_pup_x` | camera px | 동공 위치 x | <details><summary>세부</summary>로그의 동공 열에서 온 값. 접두사 `sp_`는 로그에 설명이 없다. 카메라 영상 픽셀 좌표로 읽지만 실험실 확인은 받지 않았다.</details> |
| `sp_pup_y` | camera px | 동공 위치 y |  |
| `sp_glint_x` | camera px | 글린트(각막 반사) 위치 x |  |
| `sp_glint_y` | camera px | 글린트 위치 y |  |
| `vector_x` | camera px | 동공−글린트 x | <details><summary>세부</summary>로그 표기는 `vektor`. 한 행에서 확인: `sp_pup_x - sp_glint_x` = 357.3 − 345.7 ≈ 11.58 = `vector_x`.</details> |
| `vector_y` | camera px | 동공−글린트 y |  |
| `gaze_x` | – | 시선 위치 x | <details><summary>세부</summary>지금까지 모든 파일에서 비어 있음(`NaN`): 시선 데이터가 기록되지 않았다(`NO_GAZE`).</details> |
| `gaze_y` | – | 시선 위치 y |  |
| `pupil_2a` | camera px | 동공 타원 축 2a | <details><summary>세부</summary>타원의 두 축 중 하나. Kret 어댑터는 기본값으로 `pupil_2a`와 `pupil_2b`의 평균을 동공 크기로 쓴다(`PupilMeasure='mean'`). `NaN`은 로그가 "no pupil geometry"라고 했다는 뜻.</details> |
| `pupil_2b` | camera px | 동공 타원 축 2b |  |
| `pupil_angle` | unconfirmed | 동공 타원 방향 | <details><summary>세부</summary>단위가 로그에 없다. 1.64 같은 값은 라디안으로 보이나 확인되지 않았다.</details> |
| `pupil_valid` | 0/1 | 샘플에 동공 데이터가 있는가 | <details><summary>세부</summary>`pupil_2a`가 `NaN`이 아니면 `1`. "추적기가 값을 냈다"는 뜻일 뿐 Kret 아티팩트 필터의 `isValid`가 아니다.</details> |
| `gaze_valid` | 0/1 | 샘플에 시선 데이터가 있는가 | <details><summary>세부</summary>`gaze_x`가 `NaN`이 아니면 `1`. 우리 파일은 전부 `0`.</details> |

</details>

<details>
<summary><b>02 · <code>trk2csv_qc_summary.csv</code> (25열, .trk 파일마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant, file` | – | 피험자 ID; .trk 파일명 |  |
| `status` | – | `ok` / `warn` / `failed` | <details><summary>세부</summary>이상치 중 하나라도 심각도가 `warn`이면 `warn`. `failed`는 읽지 못한 파일의 자리표시자.</details> |
| `n_samples` | count | 샘플 수 |  |
| `duration_min` | min | 기록 길이 | <details><summary>세부</summary>(마지막 − 첫 타임스탬프) / 60000.</details> |
| `sampling_hz` | Hz | 샘플링 주파수 | <details><summary>세부</summary>1000 / 샘플 간격의 중앙값. 여기서는 약 59.9 Hz.</details> |
| `n_events` | count | 로그의 소프트웨어 이벤트 수 |  |
| `n_START … n_BurnOutStart` | count | 이벤트 종류별 개수 | <details><summary>세부</summary>기대값: `START` 4, `BurnInStart` 4, `CueStart` = `CueFinish` = `StimuliStart` = 84, `BurnOutStart` 4. `RatingStart`는 일부 trial에만(sub119는 24). 일곱 열.</details> |
| `pupil_valid_fraction` | 0–1 | 동공 데이터가 있는 샘플 비율 | <details><summary>세부</summary>0.5 미만이면 `LOW_PUPIL_VALID` 경고. 아무것도 버리지 않는다.</details> |
| `gaze_valid_fraction` | 0–1 | 시선 데이터가 있는 샘플 비율 |  |
| `cue_dur_min_s / _mean_s / _max_s` | s | cue 길이: `CueStart` → `CueFinish` | <details><summary>세부</summary>과제 설정은 1.0 s. sub119는 평균 0.881 s(0.832–0.96 s).</details> |
| `n_cue_off_setting` | count | 1.0 s와 0.001 s 넘게 다른 cue 수 | <details><summary>세부</summary>sub119는 84개 중 84개이며 이것이 `CUE_DURATION`을 일으킨다.</details> |
| `countdown_min_s / _mean_s / _max_s` | s | `CueStart` → `StimuliStart` | <details><summary>세부</summary>주의: cue 시간을 포함한다. 설계상 카운트다운은 이 값에서 cue 1 s를 뺀 것(7.5–30 s).</details> |
| `n_malformed_lines` | count | 파싱하지 못한 로그 줄 수 |  |
| `n_issues` | count | 이 파일이 이상치 표에 가진 행 수 |  |

</details>

<details>
<summary><b>02 · <code>trk2csv_issues.csv</code> (5열, 이상치마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant, file` | – | 피험자 ID; .trk 파일명 |  |
| `severity` | – | `warn` = 기대와 다름; `info` = 알아둘 사실 |  |
| `code` | – | 기계가 읽는 코드, 아래 목록 참조 |  |
| `message` | – | 수치를 포함한 설명문 |  |

</details>

<details>
<summary><b>이상치 코드(열 <code>code</code>)</b></summary>

| 코드 | 심각도 | 의미 |
|---|---|---|
| `MALFORMED_LINES` | warn | 파싱 못 해 건너뛴 줄이 있음 |
| `NO_STOP_LINE` | warn | `stop timecounter` 줄이 없음. 로그가 잘렸을 수 있음 |
| `NONMONOTONIC_TIME` | warn | 타임스탬프가 앞 것보다 늦지 않음 |
| `TIME_GAP` | warn | 샘플 사이 간격이 200 ms 초과 |
| `LOW_PUPIL_VALID` | warn | 동공 데이터가 있는 샘플이 50% 미만 |
| `NO_GAZE` | info | 시선 데이터가 있는 샘플이 없음 |
| `NO_EVENTS` | warn | `SoftwareEvent` 줄이 없음. run·trial·phase를 채울 수 없음 |
| `START_COUNT` | warn | `START` 개수가 4가 아님 |
| `START_BURNIN_MISMATCH` | warn | `START`와 `BurnInStart` 개수가 다름(`START`가 없는 `BurnInStart`를 알려 줌) |
| `TRIAL_COUNT` | warn | `CueStart` 개수가 84가 아님 |
| `EVENT_COUNT_MISMATCH` | warn | `CueStart`, `CueFinish`, `StimuliStart` 개수가 같지 않음 |
| `UNKNOWN_EVENTS` | info | 알려진 목록에 없는 이벤트 이름 |
| `CUE_DURATION` | warn | cue가 1.0 s 설정과 0.001 s 넘게 다름(최소·평균·최대 포함) |

</details>

<details>
<summary><b>03 · <code><sub>_events.csv</code> (3열, 소프트웨어 이벤트마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant` | – | 피험자 ID |  |
| `time_ms` | ms | 이벤트의 원시 타임스탬프 | <details><summary>세부</summary>`SoftwareEvent` 줄의 이벤트 자체 시각이며 샘플에 맞추지 않은 값.</details> |
| `event` | – | 이벤트 이름 |  |

</details>

<details>
<summary><b>05 · 이벤트 표 — <code><sub>_event_table.csv</code>, <code><sub>_event_table_5step.csv</code>, <code>all_subjects_event_table*.csv</code> (18열)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant` | – | 피험자 ID |  |
| `order` | 1–5 | 피험자가 수행한 다섯 trial 순서 중 하나 | <details><summary>세부</summary>각 trial의 카운트다운 길이(`StimuliStart − CueStart − 1 s`)를 `TrialOrder<o>Run<r>.xlsx`와 비교해 다섯 중 가장 맞는 것을 고른다. 차이는 출력된다(예: 0.80 s 대 차선 14.8 s). 다른 곳에 기록된 값이 아니므로 실험실에 확인할 것.</details> |
| `run` | 1–4 | run 번호 | <details><summary>세부</summary>`ceil(trial / 21)`. `ymtcRunCheck`가 검증한다.</details> |
| `trial` | 1–84 | 피험자 내 trial 번호 | <details><summary>세부</summary>`CueStart`를 센다. run 수준 행에서는 비어 있다.</details> |
| `trial_in_run` | 1–21 | run 안의 trial 번호 |  |
| `ymtc_marker` | – | 과제 자체의 마커 이름 | <details><summary>세부</summary>예: `OnsetPTCTO`, `PredictableTimeCertainThreatOutcome`, `OutcomePTCTO`, `WhiteNoise`, `Rating`. run 수준 행은 `START`, `BurnInStart`, `BurnOutStart`.</details> |
| `trk_event` | – | 마커에 대응시킨 trk 이벤트 | <details><summary>세부</summary>`CueStart` ↔ Onset, `CueFinish` ↔ 카운트다운 시작, `StimuliStart` ↔ Outcome, `WhitenoiseStart1` ↔ WhiteNoise, `RatingStart` ↔ Rating.</details> |
| `time_ms` | ms | 대응한 trk 이벤트의 원시 타임스탬프 | <details><summary>세부</summary>trk에 그 마커가 없으면 비어 있다(보간하지 않음).</details> |
| `t_from_onset_s` | s | 이 trial의 Onset 이후 초 |  |
| `expected_from_onset_s` | s | 설계상 이 마커의 위치 | <details><summary>세부</summary>order 워크북의 `onsets` 열, trial의 Onset 기준.</details> |
| `diff_s` | s | 측정값 − 설계값 | <details><summary>세부</summary>`t_from_onset_s − expected_from_onset_s`. 부호가 일정하면 체계적 어긋남(예: cue가 짧음)을 뜻한다.</details> |
| `expected_duration_s` | s | 이 마커의 설계상 길이 | <details><summary>세부</summary>`durations` 열: cue 1 s, 카운트다운 7.5–30 s, Outcome 2.7 s, WhiteNoise 2.3 s, Rating 6 s.</details> |
| `condition` | – | `PTCT` `PTCS` `PTUO` `UTCT` `UTCS` `UTUO` | <details><summary>세부</summary>첫 마커 이름에서 `Onset` 뒤 네 글자. trk에는 없고 선택한 order 파일에서 온다. 실험실에서 말하는 `PTPT`가 여기의 `PTCT`와 같은지는 아직 확인 전.</details> |
| `timing` | P/U | 시간 예측 가능/불가능 | <details><summary>세부</summary>`condition`의 첫 글자.</details> |
| `certainty` | C/U | cue 시점에 결과를 아는가 | <details><summary>세부</summary>`condition`의 세 번째 글자.</details> |
| `outcome` | T/S/O | *cue*가 알린 결과 | <details><summary>세부</summary>네 번째 글자. `T` 위협, `S` 안전, `O` = 알리지 않음. 불확실한 두 조건에서는 모든 행이 `O`.</details> |
| `actual_outcome` | T/S | trial이 실제로 끝난 결과 | <details><summary>세부</summary>확실한 trial은 `outcome`과 같고, 불확실한 trial은 Outcome 마커의 마지막 글자(`OutcomeUTUOT` → `T`). run 수준 행은 비어 있다.</details> |
| `step` | 1–5 | trial 안에서의 위치 | <details><summary>세부</summary>1 Onset, 2 카운트다운 시작, 3 Outcome, 4 WhiteNoise, 5 Rating. run 수준 행은 비어 있다. 전체 버전은 `WhiteNoise_part2`–`4` 행을 더하며 이들도 `step = 4`.</details> |

</details>

<details>
<summary><b>05 · <code>event_table_summary.csv</code> (6열, 피험자마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant` | – | 피험자 ID |  |
| `status` | – | `ok` / `skipped_no_file` / `skipped_no_events` / `error` | <details><summary>세부</summary>sub124, sub128, sub137은 `skipped_no_events`: trk에 `SoftwareEvent` 줄이 없다.</details> |
| `order` | 1–5 | 선택된 trial 순서 |  |
| `nRows` | count | 기록된 행 수 | <details><summary>세부</summary>전체 표는 624, 5단계 버전은 372. sub134는 하나 적다(첫 `START` 없음).</details> |
| `nTrials` | count | 찾은 trial 수 |  |
| `note` | – | 자유 텍스트, 이상 없으면 빈칸 |  |

</details>

<details>
<summary><b>05 · <code>all_subjects_trials_wide.csv</code> (14열, trial마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant, order, run, trial` | – | trial의 식별 정보 |  |
| `condition, timing, certainty, outcome` | – | 이벤트 표와 같음 |  |
| `onset_s` | s | 항상 0, 기준점 |  |
| `countdown_s` | s | 카운트다운 시작, Onset 기준 초 |  |
| `outcome_s` | s | Outcome 시작 |  |
| `whitenoise_s` | s | 백색소음 시작 |  |
| `rating_s` | s | 평정 시작. 평정이 없으면 `NaN` |  |
| `has_rating` | logical | trial에 평정이 있는가 | <details><summary>세부</summary>84개 중 24개.</details> |

</details>

<details>
<summary><b>05 · <code>timing_check.csv</code> (7열, 피험자 × 마커마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant` | – | 피험자 ID |  |
| `phase` | – | `1 Onset` … `5 Rating start` |  |
| `n` | count | 이 칸의 마커 수 |  |
| `mean_s, sd_s` | s | `diff_s`의 평균과 표준편차 | <details><summary>세부</summary>기술 통계일 뿐. `ymtcTimingCheck`로 재현한다.</details> |
| `min_s, max_s` | s | `diff_s`의 극값 |  |

</details>

<details>
<summary><b>00 · <code>run_check.csv</code> (9열, 피험자마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant, status` | – | 피험자 ID; `ok` / `no_file` / `no_events` |  |
| `nSTART, nBurnInStart, nBurnOutStart, nCueStart` | count | 이벤트 개수 |  |
| `trialsPerRun` | – | 예: `21/21/21/21` | <details><summary>세부</summary>`BurnInStart`를 run 경계로 센다(없을 수 있는 `START`는 쓰지 않음).</details> |
| `runAssignmentOK` | 0/1 | 모든 run이 21 trial이고 개수가 일치 | <details><summary>세부</summary>`run = ceil(trial / 21)`을 지키는 장치.</details> |
| `note` | – | 문제점 설명 |  |

</details>

<details>
<summary><b>원본 표: <code>analyzeSegments</code>가 반환하는 것</b></summary>

객체마다 표 하나: `segmentsTable`의 모든 열 뒤에 눈마다 10개 열이 오른쪽으로 붙는다. 접두사는 `leftPupil_`, `rightPupil_`, `meanPupil_`. 우리 데이터는 동공이 하나라 `leftPupil_*`만 나온다. MATLAB에서는 표 머리에 `VariableUnits`와 `VariableDescriptions`도 있지만 CSV로 저장하면 사라진다. 이 문서가 필요한 이유이다.

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `segmentStart, segmentEnd` | s | 구간 경계 | <details><summary>세부</summary>기록 첫 샘플부터의 초(첫 샘플 = 0). 반개구간 `[start, end)`. 대응하는 이벤트가 없으면 둘 다 `NaN`이며 통계 행 전체가 `NaN`이 된다.</details> |
| `SmoothSig_meanDiam` | px | 구간 안 평활 신호의 평균 | <details><summary>세부</summary>`NaN`은 제외. 보간된 점은 포함되므로 짧은 공백은 깨끗해 보인다. `SmoothSig_missingDataPercent`와 함께 읽을 것.</details> |
| `SmoothSig_minDiam, SmoothSig_maxDiam` | px | 평활 신호의 최소 / 최대 |  |
| `SmoothSig_missingDataPercent` | % | 구간 중 `NaN` 비율 | <details><summary>세부</summary>실제 valid 점 사이 공백이 250 ms를 넘는 곳만 `NaN`. 구간별 결측률이며 품질 관리에 쓴다.</details> |
| `SmoothSig_sampleCount` | count | 구간 안 1000 Hz 샘플 전부 | <details><summary>세부</summary>`NaN` 포함. 구간 길이 × 1000 정도(0.5 s 기준선은 500).</details> |
| `ValidSamples_meanDiam` | px | 구간 안 실제 valid 샘플의 평균 | <details><summary>세부</summary>보간·평활 없음. 세 아티팩트 필터를 통과한 점만.</details> |
| `ValidSamples_minDiam, ValidSamples_maxDiam` | px | valid 샘플의 최소 / 최대 |  |
| `ValidSamples_validPercent` | % | 기록 **전체**의 valid 비율 | <details><summary>세부</summary>`validFraction × 100`: 기록 전체에서 비어 있지 않은 원시 점 중 valid 점의 비율. 한 피험자의 모든 행에서 같다. 이 구간의 값이 아니다.</details> |
| `ValidSamples_sampleCount` | count | 구간 안 valid 샘플 수 | <details><summary>세부</summary>60 Hz에서 0.5 s 기준선은 최대 약 30.</details> |

</details>

<details>
<summary><b>04 · <code>kret_results.csv</code> (16열, 피험자 × trial × 구간마다 한 행 = trial당 4행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `segmentStart, segmentEnd` | s | 구간 경계 |  |
| `segmentName` | – | 예: `countdown_004` | <details><summary>세부</summary>구간 종류 + trial 번호. trial 4의 카운트다운.</details> |
| `segmentType` | – | `baseline` / `countdown` / `preOutcome` / `postOutcome` |  |
| `participant, trial` | – | 피험자 ID; trial 1–84 |  |

그리고 `leftPupil_*` 통계 열 10개(위와 같은 이름, 접두사 포함).

</details>

<details>
<summary><b>04 · <code>trials_qc.csv</code> (19열 = 위 16열 + QC 표시 3개, trial의 4개 구간 행에 반복)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `RejectCountdown` | 0/1 | trial 제외 | <details><summary>세부</summary>`countdown_SmoothSig_missingDataPercent > 50`. 분석 규칙 R1.</details> |
| `PreOutcomeMostlyMissing` | 0/1 | 표시만 하고 trial은 유지 | <details><summary>세부</summary>`preOutcome_SmoothSig_missingDataPercent > 50`. 그 trial의 GLM 조절 변수는 믿을 수 없다. 규칙 R2.</details> |
| `SubjectExcluded` | 0/1 | 피험자 전체 제외 | <details><summary>세부</summary>피험자 trial의 20% 초과가 제외됨. 규칙 R3(Leuchs / Shechner 20% 규칙).</details> |

앞 16열은 `kret_results.csv`와 완전히 같다.

</details>

<details>
<summary><b>04 · <code>subjects_qc.csv</code> (5열, 피험자마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `participant` | – | 피험자 ID |  |
| `nTrials, nRejected` | count | trial 수; R1로 제외된 수 |  |
| `rejectPct` | % | `nRejected / nTrials × 100` |  |
| `subjectExcluded` | 0/1 | rejectPct가 20 초과 |  |

</details>

<details>
<summary><b>04 · <code>segments/<name>_leftpupil_segments.csv</code> (6–7열, <code>exportSegments</code>가 쓰는 1000 Hz 샘플마다 한 행)</b></summary>

| 열 | 단위 | 의미 | 세부 |
|---|---|---|---|
| `segmentName, segmentType` | – | `segmentsTable`과 같음 |  |
| `segmentStart_s` | s | 구간 시작 | <details><summary>세부</summary>한 구간의 모든 행에서 동일.</details> |
| `tRel_s` | s | 샘플 시각 − 구간 시작 |  |
| `pupilDiameter_px` | px | 평활 신호 직경, 소수 4자리 | <details><summary>세부</summary>이름의 단위는 `diameterUnit`을 따른다. 공백이 250 ms를 넘은 곳은 `NaN`.</details> |
| `gap_ms` | ms | 이 시점 앞뒤 실제 valid 점 사이 간격 | <details><summary>세부</summary>실제 점에서 0.5 ms 이내면 0. 소수 1자리.</details> |
| `pupilDiameterZ` | z | `ZScore=true`일 때만 | <details><summary>세부</summary>(값 − 기록 전체 평균) / 기록 전체 표준편차. 눈마다 기록 전체에서 한 번 계산(Leuchs 2017)하며 구간 안 z가 아님.</details> |

</details>

<details>
<summary><b>06 · <code><sub>_final.csv</code>와 <code>all_subjects_final.csv</code> — 69열, 마커마다 한 행</b></summary>

`ymtcMergeResults`가 5단계 이벤트 표로 만든다. 각 구간의 통계는 그 구간이 속한 마커 행에 놓인다: baseline → Onset, countdown·preOutcome → 카운트다운 행, postOutcome → Outcome 행. WhiteNoise와 Rating 행은 거기가 `NaN`. 전체 열 목록:

**이벤트 열(이벤트 표와 동일)** (18)

`participant`, `order`, `run`, `trial`, `trial_in_run`, `ymtc_marker`, `trk_event`, `time_ms`, `t_from_onset_s`, `expected_from_onset_s`, `diff_s`, `expected_duration_s`, `condition`, `timing`, `certainty`, `outcome`, `actual_outcome`, `step`

**구간 `baseline` — `step = 1`인 행에만 값이 있고 같은 trial의 다른 행은 `NaN`** (12)

`baseline_segmentStart`, `baseline_segmentEnd`, `baseline_SmoothSig_meanDiam`, `baseline_SmoothSig_minDiam`, `baseline_SmoothSig_maxDiam`, `baseline_SmoothSig_missingDataPercent`, `baseline_SmoothSig_sampleCount`, `baseline_ValidSamples_meanDiam`, `baseline_ValidSamples_minDiam`, `baseline_ValidSamples_maxDiam`, `baseline_ValidSamples_validPercent`, `baseline_ValidSamples_sampleCount`

**구간 `countdown` — `step = 2`인 행에만 값이 있고 같은 trial의 다른 행은 `NaN`** (12)

`countdown_segmentStart`, `countdown_segmentEnd`, `countdown_SmoothSig_meanDiam`, `countdown_SmoothSig_minDiam`, `countdown_SmoothSig_maxDiam`, `countdown_SmoothSig_missingDataPercent`, `countdown_SmoothSig_sampleCount`, `countdown_ValidSamples_meanDiam`, `countdown_ValidSamples_minDiam`, `countdown_ValidSamples_maxDiam`, `countdown_ValidSamples_validPercent`, `countdown_ValidSamples_sampleCount`

**구간 `preOutcome` — `step = 2`인 행에만 값이 있고 같은 trial의 다른 행은 `NaN`** (12)

`preOutcome_segmentStart`, `preOutcome_segmentEnd`, `preOutcome_SmoothSig_meanDiam`, `preOutcome_SmoothSig_minDiam`, `preOutcome_SmoothSig_maxDiam`, `preOutcome_SmoothSig_missingDataPercent`, `preOutcome_SmoothSig_sampleCount`, `preOutcome_ValidSamples_meanDiam`, `preOutcome_ValidSamples_minDiam`, `preOutcome_ValidSamples_maxDiam`, `preOutcome_ValidSamples_validPercent`, `preOutcome_ValidSamples_sampleCount`

**구간 `postOutcome` — `step = 3`인 행에만 값이 있고 같은 trial의 다른 행은 `NaN`** (12)

`postOutcome_segmentStart`, `postOutcome_segmentEnd`, `postOutcome_SmoothSig_meanDiam`, `postOutcome_SmoothSig_minDiam`, `postOutcome_SmoothSig_maxDiam`, `postOutcome_SmoothSig_missingDataPercent`, `postOutcome_SmoothSig_sampleCount`, `postOutcome_ValidSamples_meanDiam`, `postOutcome_ValidSamples_minDiam`, `postOutcome_ValidSamples_maxDiam`, `postOutcome_ValidSamples_validPercent`, `postOutcome_ValidSamples_sampleCount`

**품질 관리 — trial의 모든 행에 복사(run 수준 행은 `NaN`)** (3)

`RejectCountdown`, `PreOutcomeMostlyMissing`, `SubjectExcluded`

</details>

## 4. 설정

<details>
<summary><b><code>settings.raw</code> (<code>rawDataFilter()</code>에서)</b></summary>

| 설정 | default | 의미 |
|---|---|---|
| `PupilDiameter_Min / _Max` | 1.5 / 9 | 범위 필터. 기본값은 **밀리미터** 기준이므로 픽셀 데이터는 바꿔야 한다(`Examples/Dataset_1`은 0.1 / inf). 우리 파이프라인은 데이터에서 정하고(0.5–99.5 백분위 × 0.8 / 1.2) 값을 출력한다. |
| `islandFilter_islandSeperation_ms` | 40 ms | 다른 샘플에서 얼마나 떨어져야 섬으로 보는가. |
| `islandFilter_minIslandWidth_ms` | 50 ms | 이보다 좁은 섬은 무효. |
| `dilationSpeedFilter_MadMultiplier` | 16 | 속도가 중앙값 + 이 값 × MAD를 넘으면 무효(눈 깜빡임 가장자리 포착). |
| `dilationSpeedFilter_maxGap_ms` | 200 ms | 두 valid 샘플이 이보다 가까울 때만 속도를 계산. |
| `gapDetect_minWidth / _maxWidth` | 75 / 2000 ms | 이 폭의 결측 구간을 공백으로 보고 가장자리를 추가로 버린다. |
| `gapPadding_backward / _forward` | 50 / 50 ms | 그런 공백 앞/뒤로 추가로 버리는 길이. |
| `residualsFilter_passes` | 4 | 추세 편차 필터의 반복 횟수. |
| `residualsFilter_MadMultiplier` | 16 | 추세에서 중앙값 + 이 값 × MAD 이상 벗어나면 무효. |
| `residualsFilter_interpFs / _lowpassCF` | 100 Hz / 16 Hz | 추세선을 만들 때의 재표본화율과 차단 주파수(1차 Butterworth). |
| `keepFilterData` | true | `speedFiltData` / `devFiltData` 보관. 메모리를 많이 쓰므로 조정 후 `false`. |

</details>

<details>
<summary><b><code>settings.valid</code> (<code>ValidSamplesModel.getDefaultSettings()</code>에서)</b></summary>

| 설정 | default | 의미 |
|---|---|---|
| `interp_upsamplingFreq` | 1000 Hz | 평활 신호의 샘플링 주파수. |
| `LpFilt_B / LpFilt_A` | order 4, 4 Hz | 4차, 1000 Hz에서 차단 4 Hz로 계산한 저역통과 계수(영위상 `filtfilt`). |
| `interp_maxGap` | 250 ms | 실제 valid 점 사이 공백이 이보다 크면 평활 신호에서 `NaN`. |

</details>

<details>
<summary><b><code>trk2csv</code> 옵션</b></summary>

| 설정 | default | 의미 |
|---|---|---|
| `OutFolder` | folder of the .trk | csv를 쓸 폴더. |
| `Overwrite` | true | 기존 csv 덮어쓰기. |
| `WriteReport` | false | `<name>_issues.csv`도 쓰기. |
| `ExpectedRuns` | 4 | 기대하는 `START` 개수. |
| `ExpectedTrialsPerRun` | 21 | run당 기대 trial 수(총 84). |
| `CueDurationSec / CueToleranceSec` | 1.0 / 0.001 | 과제 설정의 cue 길이와 허용 오차. |
| `MinValidFraction` | 0.5 | 동공 유효 비율이 이보다 낮으면 보고(`LOW_PUPIL_VALID`). 아무것도 버리지 않는다. |
| `MaxGapMs` | 200 | 샘플 간격이 이보다 크면 보고(`TIME_GAP`). |
| `Quiet` | false | 출력 억제. |

</details>

<details>
<summary><b><code>csv2kretmat</code> 옵션</b></summary>

| 설정 | default | 의미 |
|---|---|---|
| `PupilMeasure` | 'mean' | `'mean'` / `'2a'` / `'2b'`: 어느 타원 축(또는 평균)을 동공 크기로 쓰는가. |
| `BaselineWinSec` | 0.5 | cue 이전 기준선 구간 길이. 0이면 끈다. |
| `PreOutcomeWinSec / PostOutcomeWinSec` | 2.0 / 2.0 | 결과 전/후 구간 길이. 0이면 결과 전 구간을 끈다. |

</details>

## 5. 파일과 함수

```
trk2csv_batch ──▶ trk2csv ──▶ private/readTrk ─▶ private/labelSamples ─▶ private/checkTrk
                                  (파싱)            (샘플에 이벤트)          (기록만)

ymtcEventTableBatch ──▶ ymtcEventTable ──▶ readOrder()   (같은 파일의 하위 함수)
         │                    │
         │                    └──▶ 05_markers/05_<sub>_markers[_5step].csv
         └──▶ ymtcTrialWide  / ymtcTimingCheck     (표를 읽고 파일 하나씩 씀)

ymtcRunCheck     독립: 03_events를 읽고 07_checks/07_all_run_check.csv를 씀
ymtcConfig       모든 ymtc* 함수가 읽음: 폴더 위치
checkDocs        docs/02와 실제 표 헤더를 비교
```

| 파일 | 행 | 하는 일 | 출력 |
|---|---|---|---|
| `trk2csv.m` | 87 | trk 하나 → 샘플 CSV 하나 + 보고서 | 02_samples/<name>.csv |
| `trk2csv_batch.m` | 76 | trk 폴더 → 같은 것 + QC 표 두 개 | 02_all_qc_summary.csv, 02_all_issues.csv |
| `private/readTrk.m` | 79 | 텍스트 로그를 헤더/샘플/이벤트로 파싱 | 메모리 |
| `private/labelSamples.m` | 46 | 이벤트를 샘플에 붙이고 run/trial/phase를 이어감 | 메모리 |
| `private/checkTrk.m` | 134 | 과제가 만들어야 할 것과 비교; 기록만 | 02_all_issues.csv 행 |
| `ymtcEventTable.m` | 184 | 피험자 한 명 → 마커 한 줄씩, 과제 순서 | 05_markers/05_<sub>_markers[_5step].csv |
| `ymtcEventTableBatch.m` | 122 | 피험자 반복 + 요약표와 통합표 | 05_all_markers*.csv, 05_all_markers_summary.csv |
| `ymtcTimingCheck.m` | 71 | 피험자×마커별 diff_s 요약 | 05_all_timing_check.csv |
| `ymtcTrialWide.m` | 68 | 긴 마커 표 → trial 한 줄 | 05_all_trials_wide.csv |
| `ymtcRunCheck.m` | 117 | 모든 run이 21 trial인가 (BurnInStart 기준) | 07_checks/07_all_run_check.csv |
| `ymtcConfig.m` | 40 | 폴더 위치; 경로 하드코딩 없음 | 구조체 C |
| `checkDocs.m` | 101 | docs/02와 실제 표 헤더 비교 | 콘솔 |

<details>
<summary><b>원본 코드(<code>helperFunctions/</code>)</b></summary>

<details>
<summary><code>rawDataFilter.m</code></summary>

메인 함수가 `removeOutOfBounds`(범위) → `madSpeedFilter`(속도, 눈 깜빡임) → `madDeviationFilter`(추세 이탈) 순으로 호출. 고립점 정리 `removeLoners`는 세 단계 안에서 반복 호출되고 공백 확장 `expandGaps`는 속도 필터 안에서 호출됨. `madCalc`는 MAD 임계값 계산. 인수 없이 호출하면 기본 `settings.raw` 반환.

</details>

<details>
<summary><code>genMeanDiaSamples.m</code></summary>

두 눈을 합쳐 평균 직경을 만든다. `processValidSamples`가 호출. 한 눈 데이터에서는 쓰이지 않음.

</details>

<details>
<summary><code>plotSegments.m</code></summary>

구간 표를 색 블록으로 그린다. `plotData`가 호출.

</details>

<details>
<summary><code>printToConsole.m</code></summary>

진행 메시지, 내부용.

</details>

<details>
<summary><code>legacyModeCheck.m</code></summary>

MATLAB이 8.3보다 오래돼 `table`이 없으면 `LEGACY/`를 경로에 추가. 새 버전에서는 아무 일도 안 함.

</details>

<details>
<summary><code>FALLBACK/</code></summary>

툴박스가 없거나 함수가 제거된 MATLAB용 `butter`, `filtfilt`, `histc`, `nanmin` / `nanmax` / `nanmean` / `nanmedian` 대체 구현. 함정: `addpath(genpath(...))`는 폴더를 **맨 앞**에 넣어 FALLBACK이 진짜 툴박스 함수를 가린다. 툴박스를 우선하려면 `addpath(..., '-end')`. 이 컴퓨터에는 Statistics 툴박스가 없어 `nan*`는 항상 FALLBACK.

</details>

<details>
<summary><code>LEGACY/</code></summary>

아주 오래된 MATLAB에서 `table`을 흉내 냄.

</details>

</details>

<details>
<summary><b>우리 계층(<code>ymtc/</code>와 어댑터)</b></summary>

<details>
<summary><code>trk2csv.m</code></summary>

`.trk` 하나 → 샘플 단위 CSV 하나와 보고서. 툴박스 불필요.

</details>

<details>
<summary><code>trk2csv_batch.m</code></summary>

`.trk` 폴더 → `csv/`와 `trk2csv_qc_summary.csv`, `trk2csv_issues.csv`.

</details>

<details>
<summary><code>private/readTrk.m, labelSamples.m, checkTrk.m</code></summary>

텍스트 로그 파싱; 이벤트를 붙이고 run / trial / phase를 이어 간다; 과제가 만들어야 할 것과 비교(기록만).

</details>

<details>
<summary><code>ymtcEventTable.m</code></summary>

피험자 한 명 → 과제 순서의 마커 표. 카운트다운 길이를 맞춰 trial 순서를 고른다.

</details>

<details>
<summary><code>ymtcEventTableBatch.m</code></summary>

모든 피험자를 한 번에, 그리고 `event_table_summary.csv`와 합본 표.

</details>

<details>
<summary><code>ymtcRunCheck.m</code></summary>

모든 run이 정말 21 trial인가? → `run_check.csv`.

</details>

<details>
<summary><code>ymtcTimingCheck.m, ymtcTrialWide.m</code></summary>

마커 표를 읽는다: `timing_check.csv`, `all_subjects_trials_wide.csv`.

</details>

<details>
<summary><code>ymtcMergeResults.m</code></summary>

5단계 마커 표를 participant + trial 기준으로 `kret_results.csv`, `trials_qc.csv`와 결합 → `06_最终结果/<sub>_final.csv`, `all_subjects_final.csv`(69열). 아무것도 고치지 않으며 Kret 행이 없는 trial은 `NaN`.

</details>

<details>
<summary><code>csv2kretmat.m, example_kret_pipeline.m</code></summary>

Kret 파이프라인용 어댑터와 일괄 실행 스크립트(`代码_matlab/`, 이 저장소 밖). 어댑터는 시간을 0 기준으로 바꾸고, 중복 타임스탬프를 제거(첫 번째 유지)하고, `pupil_valid == 0`인 곳을 `NaN`으로 하며 `diameterUnit = 'px'`를 쓴다.

</details>

<details>
<summary><code>ymtcConfig.m, checkDocs.m</code></summary>

폴더 위치(저장소에 절대 경로 없음); `checkDocs`는 문서화된 열과 실제 CSV 헤더를 비교.

</details>

</details>

## 6. 공식 예제 두 개

`main_Dataset1.m`은 (1)~(5)단계의 가장 짧은 시연이다. 우리 YMTC 데이터는 `trk2csv`를 변환기로 하여 같은 한 동공 경로를 따른다.

<details>
<summary><code>Examples/Dataset_1/</code></summary>

SR-Research Eyelink, **동공 하나**. `batchFileConverter_Dataset1.m`(EDF → .mat), `main_Dataset1.m`(전체 파이프라인). `PupilDiameter_Max = inf`, `PupilDiameter_Min = 0.1`(임의 단위), `keepFilterData = true`로 설정.

</details>

<details>
<summary><code>Examples/Dataset_2/</code></summary>

E-Prime + Tobii, **동공 둘**. `batchFileConverter_Dataset2.m`(.gazedata → .mat), `main_Dataset2.m`.

</details>

## 7. 문제 해결: 증상 → 원인 → 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| `'t_ms' must be sorted!` | 타임스탬프가 오름차순이 아님(trk의 중복·역행 타임스탬프) | 변환기에서 정렬·중복 제거(패키지 안에서 고치지 않음); 중복은 기록 |
| `'L' must be empty, or have the same length as 't_ms'` | 직경과 시간 벡터의 길이가 다름 | 변환기에서 길이 확인 |
| `No settings present.` | `settings` 없이 `PupilDataModel`을 만듦 | `PupilDataModel.getDefaultSettings()`로 받아서 수정 |
| `Interpolation cannot be performed.` | 그 눈의 valid 점이 2개 미만(범위 오설정 또는 전부 잡음) | `PupilDiameter_Min/Max`가 단위에 맞는지 확인 |
| `almost every sample is invalid` | 기본 범위 1.5–9는 mm 기준, 픽셀 데이터는 범위 밖 | 실제 단위로 범위 설정 |
| `warning pupilSize:edgeClamp` | 부동소수점 오차로 업샘플 시각이 valid 범위 밖에 놓여 경계로 보정됨 | 알림일 뿐. 개수가 많을 때만 조사 |
| `ValidSamples_validPercent identical on every row` | 설계상 기록 전체 값 | 구간별 결측은 `SmoothSig_missingDataPercent` |
| `SmoothSig_meanDiam looks fine but the data is poor` | 250 ms 미만 공백이 보간으로 메워짐 | `missingDataPercent`와 `ValidSamples_sampleCount`도 함께 본다 |
| `a whole result row is NaN` | 구간 시작/끝이 `NaN`(이벤트 없음) 또는 구간 안에 샘플이 없음 | 이벤트 표에서 빠진 마커 확인. 대체값은 넣지 않는다 |
| `plotData does nothing / is skipped` | `-batch`에는 데스크톱이 없음 | 데스크톱 MATLAB에서 실행 |
| `plotData shows one file only` | 소스에 `plotMultipleFiles = false`(무거움) | `PupilDataModel.m`에서 그 스위치 변경 |
| `addpath fails in Examples` | 경로가 Windows 역슬래시로 적혀 있음 | macOS / Linux에서는 `../../helperFunctions/` |
| `MATLAB -batch` fails with several lines | `-batch`는 한 줄 명령만 받음 | 코드를 스크립트 파일에 넣고 `run('x.m')` |

## 8. 한계

- 원본 README는 Signal Processing과 Statistics 툴박스를 요구하며 Windows 7의 MATLAB 2012b / 2016a / 2017a에서 테스트했다. 이 포크는 macOS용으로 패치했다(`PupilDataModel`의 경로 구분자, `FALLBACK/`). `git log` 참조.
- 필터 매개변수는 논문 기본값이며 YMTC 데이터에 맞춰 조정하지 않았다. 조정하려면 데스크톱 MATLAB에서 `plotData()`로 원시 궤적을 봐야 한다.
- 동공 크기는 카메라 픽셀 단위, 한쪽 눈 기준이다. 시선은 기록되지 않았다. `pupil_angle`의 단위와 `sp_` 접두사의 뜻은 확인되지 않았다.
- 이 문서는 코드가 무엇을 하는지만 설명하며 결과가 좋은지는 판단하지 않는다. 데이터 품질: [`../docs/05_data_quality.md`](../docs/05_data_quality.md).

## 9. 검토 지도: 무엇을 어떤 순서로 읽을까

이 코드를 직접 확인해야 한다면, 가장 짧은 경로는 이것이다. 아래 경로는 모두 실제 파일이고 줄 수는 파일에서 센 값이다.

```
code/ymtc/                        이 저장소
  ymtcEventTable.m                184   마커 표 자체
  trk2csv.m                        87   .trk 하나 -> csv 하나
  private/readTrk.m                79   텍스트 파서
  private/labelSamples.m           46   이벤트 -> 샘플
  private/checkTrk.m              134   무엇을 이상치로 기록하는가
  ymtcEventTableBatch / RunCheck / TimingCheck / TrialWide   래퍼, 훑어보기

代码_matlab/                      연구 데이터와 함께, 저장소에는 없음
  csv2kretmat.m                   259   네 구간 정의
  example_kret_pipeline.m         140   필터 -> 보간 -> 구간 -> 통계
  ymtcTrialQC.m                   110   세 가지 제외 규칙
  ymtcMergeResults.m              ~110  69개 열이 만들어지는 방식
```

| 읽기 | 읽으면서 확인할 것 | 왜 중요한가 | 시간 |
|---|---|---|---|
| 1. `ymtcEventTable.m` | 다섯 마커/이벤트 쌍; trial order 선택 방식; `condition`/`timing`/`certainty`/`outcome`의 출처; `diff_s`의 의미; `run = ceil(trial/21)`인 이유 | 조건에 관한 모든 주장이 이 파일에 달려 있다 | 40분 |
| 2. `trk2csv.m` -> `readTrk.m` -> `labelSamples.m` -> `checkTrk.m` | csv 한 행이 만들어지는 과정; 고치지 않고 기록하는 것 | 나머지 전부의 입력 | 60분 |
| 3. `csv2kretmat.m` | 네 구간과 창; 시간 0 기준 | 모든 눈동자 열에서 "countdown"의 의미를 결정 | 30분 |
| 4. `example_kret_pipeline.m` + `docs/03` | 어느 필터가 언제; 무엇이 논문 기본값이고 무엇을 바꿨는지 | 숫자가 생기는 유일한 곳 | 40분 |
| 5. `ymtcTrialQC.m` + `docs/05` | 세 규칙과 임계값 | 어떤 trial이 살아남는지 결정 | 20분 |
| 6. `ymtcMergeResults.m` | 조인 키(`participant`+`run`+`trial`)와 열 순서 | 69열 표를 설명 | 20분 |

시간에 따른 세 가지 경로:

- **30분**: 1번 파일만, `docs/02` 사전을 옆에 두고 - 마커 표의 모든 열을 방어할 수 있다.
- **2시간**: 1-2번 + `checkDocs` - 준비 계층 전체를 방어할 수 있다.
- **반나절**: 여섯 개 전부 - 최종 표의 모든 숫자를 방어할 수 있다.

## 10. 더 읽을 거리

[`../docs/01_pipeline_overview.md`](../docs/01_pipeline_overview.md) · [`../docs/02_column_dictionary.md`](../docs/02_column_dictionary.md) · [`../docs/03_pupil_size_internals.md`](../docs/03_pupil_size_internals.md) · [`ymtc/README.md`](ymtc/README.md) · [`../docs/04_our_code.md`](../docs/04_our_code.md) · [`../docs/06_faq.md`](../docs/06_faq.md)

Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.

[↑ top](#top) · **[English](#english) · [한국어](#한국어) · [中文](#中文)**

---

<a id="中文"></a>

# code/ — pupil-size 工具箱与我们的 YMTC 层：一页讲完

原版 Kret & Sjak-Shie (2019) 代码和我们自己的 `ymtc/` 层，都放在这一页。每张输出表都逐列列出。点三角形展开细节。内容都对照源码或真实文件写成；没能确认的地方会直接写明。

## 1. 总图：每张表和它的来源

文件夹编号（`00`–`06`）是本仓库旁边的数据文件夹。`[ymtc]` = `code/ymtc/` 里我们的代码，`[Kret code]` = `code/dataModels/` 里的原版类，`[Kret 适配器]` = 我们在两者之间的衔接代码。

```
01 原始 trk      01_raw_trk/*.trk              录制日期在文件名里，永不改名
      │  trk2csv_batch
      ▼
02 样本          02_samples/subNNN_*.csv（21 列）+ 02_all_qc_summary.csv + 02_all_issues.csv
      │
      ├──▶ 03 事件      03_events/subNNN_events.csv
      │        │  ymtcEventTable（+ TrialOrder-HK/*.xlsx）
      │        ▼
      │   05 marker 表  05_all_markers.csv（18 列）· 05_all_markers_5step.csv
      │        ├ ymtcTrialWide    → 05_all_trials_wide.csv（14）
      │        └ ymtcTimingCheck  → 05_all_timing_check.csv（7）
      │
      └──▶ 04 瞳孔指标  csv2kretmat → .mat → PupilDataModel
               │  04_all_segments.csv（16）· 04_all_trials_qc.csv（19）· 04_all_subjects_qc.csv（5）
               │  segments/subNNN_leftpupil_segments.csv
               ▼
         06 合并表     06_all_merged.csv（69 列）= 05 marker + 4 段 × 12 统计 + 3 个质控列

旁路检查（不喂给下游）：
     03 事件 ──ymtcRunCheck──▶ 07 检查  07_all_run_check.csv（9）
```

02 之后分成两路：03 事件、04 瞳孔指标，互不依赖；03 喂给 05，04 和 05 在 06 合并；07 只检查 03。

| 表 | 文件 | 行 | 列 | 由谁生成 |
|---|---|---|---|---|
| per-sample CSV | `02_samples/<name>.csv` | 1 / sample | 21 | trk2csv [ymtc] |
| QC summary | `02_samples/02_all_qc_summary.csv` | 1 / file | 25 | trk2csv_batch [ymtc] |
| issues | `02_samples/02_all_issues.csv` | 1 / anomaly | 5 | trk2csv_batch [ymtc] |
| events | `03_events/<sub>_events.csv` | 1 / event | 3 | event extraction |
| event table | `05_markers/05_<sub>_markers[_5step].csv` | 1 / marker (624 · 372) | 18 | ymtcEventTable [ymtc] |
| event summary | `05_markers/05_all_markers_summary.csv` | 1 / subject | 6 | ymtcEventTableBatch [ymtc] |
| trials wide | `05_markers/05_all_trials_wide.csv` | 1 / trial | 14 | ymtcTrialWide [ymtc] |
| timing check | `05_markers/05_all_timing_check.csv` | 1 / subject × marker | 7 | ymtcTimingCheck [ymtc] |
| run check | `07_checks/07_all_run_check.csv` | 1 / subject | 9 | ymtcRunCheck [ymtc] |
| Kret results | `04_pupil/04_all_segments.csv` | 1 / trial × segment | 16 | analyzeSegments [Kret code] |
| trial QC | `04_pupil/04_all_trials_qc.csv` | 1 / trial × segment | 19 | Kret pipeline script |
| subject QC | `04_pupil/04_all_subjects_qc.csv` | 1 / subject | 5 | Kret pipeline script |
| segment curves | `04_pupil/segments/<name>_leftpupil_segments.csv` | 1 / 1000 Hz sample | 7 | exportSegments [Kret code] |
| final | `06_merged/06_<sub>_merged.csv, 06_all_merged.csv` | 1 / marker | 69 | ymtcMergeResults [ymtc] |

## 2. Kret & Sjak-Shie 流水线（原版代码）

设计要点：流水线只做标记（`isValid`），从不覆盖原始直径；valid 样本和平滑信号是两个不同的对象；所有阈值都在 `getDefaultSettings()` 里，每个对象带自己的设置；左、右、均值分开分析。时间单位：`t_ms` 是毫秒，`segmentStart`、`segmentEnd`、`signal.t` 是秒。

```
RawFileModel ──saveMatFile──▶ <name>.mat
        │
        ▼  PupilDataModel.batchConstructor(...)        每个文件一个对象
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter     产出每个原始样本的 isValid
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth              产出 1000 Hz 平滑信号
 (3) analyzeSegments()       ValidSamplesModel.analyze                      产出每段每只眼 10 个统计量
 (4) exportSegments(folder)  每段的连续时间曲线 → CSV
 (5) plotData()              目视检查（需要桌面 MATLAB）
```

#### 每一阶段到底做了什么

| 阶段 | 函数（文件:行） | 判断什么 | 关键设置 |
|---|---|---|---|
| 1 范围 | `removeOutOfBounds`（`rawDataFilter.m:197`） | 直径超出合理范围即无效 | `PupilDiameter_Min/_Max`（默认 1.5 / 9，**毫米**） |
| 2 眨眼 | `madSpeedFilter`（`229`）+ `expandGaps`（`511`） | 相邻样本速度超过 `median + 16 MAD`；再把宽于 75 ms 的缺口前后各 50 ms 去掉 | `dilationSpeedFilter_MadMultiplier=16`、`maxGap_ms=200` |
| 3 趋势 | `madDeviationFilter`（`284`） | 离 16 Hz 低通趋势线超过 `median + 16 MAD` 的点；**回扫 4 趟**让被误删的好样本复活 | `residualsFilter_passes=4` |
| 4 孤立 | `removeLoners`（`440`） | 窄于 50 ms、且与邻段隔开 40 ms 以上的孤岛 | `minIslandWidth_ms=50`、`islandSeperation_ms=40` |
| 5 平滑 | `interpAndSmooth`（`ValidSamplesModel.m:107`） | 线性插值到 1000 Hz，再走 4 阶 Butterworth 4 Hz、零相位（`filtfilt`） | `interp_upsamplingFreq=1000`、`LpFilt_cutoffFreq=4` |
| 6 分段 | `analyze`（`203`） | 每段的均值/最小/最大/缺失%，平滑信号和有效样本各算一套 | — |

所有阈值都是 `median + n*MAD`，不是均值 ± SD——少数巨大伪影会把 SD 撑大，反而把自己藏起来。上面全是论文默认值；我们的管线只改了范围滤波，因为论文的数字是毫米、我们的数据是相机像素。

**代码从不修改直径**：`rawDataFilter` 只返回一个逻辑向量（`isValid`），原始样本原样保留；下游全部基于这个掩码，所以被否掉的样本后面救不回来。

### 2.1 输入：.mat 文件（`RawFileModel`）

`RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename)` 会检查输入，写出一个含四个变量的 `.mat`。逐个字段展开看：

<details>
<summary><code>diameterUnit</code></summary>

直径单位的文字标签，例如 `'mm'`、`'px'`。会被复制到所有结果和导出 CSV 的列名里。包不会做单位换算，它只是个标签。

</details>

<details>
<summary><code>diameter.t_ms</code></summary>

每个样本的时刻，单位毫秒，一个列向量。必须升序（`issorted`），最好从 0 开始（原始眼动仪时刻放进 `zeroTime_ms`）。重复时间戳会让滤波出错，所以我们的转换器只保留重复项里的第一个。

</details>

<details>
<summary><code>diameter.L</code></summary>

每个样本的左眼瞳孔直径，长度与 `t_ms` 相同，眼动仪没给值的地方是 `NaN`。左眼没测就留空（`[]`）。约定只测一只眼时放在这里（EyeLink 例子就这样）；我们的 MRC 数据（单瞳孔）放在 `L`。

</details>

<details>
<summary><code>diameter.R</code></summary>

右眼同理。我们的数据里是空的。`L` 和 `R` 都有时，包还会据此生成 `mean` 瞳孔。

</details>

<details>
<summary><code>zeroTime_ms</code></summary>

对应 `t = 0` 的眼动仪自己的时间戳（毫秒）。只是存档，包本身不用。

</details>

<details>
<summary><code>segmentsTable.segmentStart / segmentEnd</code></summary>

每个分段的起止，单位是**秒**（不是毫秒），与 `t_ms/1000` 同一个时钟。起点或终点是 `NaN` 时，该段统计也是 `NaN`。分段可以重叠。

</details>

<details>
<summary><code>segmentsTable.segmentName</code></summary>

分段名，例如 `countdown_004`。会显示在图上并复制到结果里。

</details>

<details>
<summary><code>segmentsTable (extra columns)</code></summary>

其他任何列（participant、trial、segmentType、condition …）都会原样带到结果表的左侧。`exportSegments` 还会找名为 `segmentType` 的列。

</details>

<details>
<summary><code>csv2kretmat</code> 写出的 .mat 的内容</summary>

`diameterUnit = 'px'`；`diameter.t_ms`（毫秒，从 0 开始）、`diameter.L`（瞳孔大小，`NaN` = 缺失）、`diameter.R` 为空；`zeroTime_ms` = 第一个样本的原始 MRC 时间戳；`segmentsTable` 含 `segmentStart`、`segmentEnd`、`segmentName`，以及 `segmentType`、`participant`、`trial`。每个 trial 四种分段：`baseline` `[CueStart − 0.5 s, CueStart)`、`countdown` `[CueStart, StimuliStart)`、`preOutcome` `[StimuliStart − 2 s, StimuliStart)`、`postOutcome` `[StimuliStart, StimuliStart + 2 s)`。第 i 个 `CueStart` 与第 i 个 `StimuliStart` 配对。边界来自**实测** marker，不是设计值。

</details>

### 2.2 对象与字段

<details>
<summary><b><code>PupilDataModel</code> —— 属性</b></summary>

<details>
<summary><code>filename, filepath</code></summary>

构造该对象所用的 .mat 文件的名字和文件夹。

</details>

<details>
<summary><code>settings</code></summary>

有两部分的结构体：`settings.raw`（伪影滤波）和 `settings.valid`（插值与低通）。每个对象各带一份。

</details>

<details>
<summary><code>eyesWithData</code></summary>

哪些眼有数据：`{'left'}`、`{'right'}`、`{'left','right'}` 或 `{}`，别的值会报错。决定对哪只眼做滤波和分析。

</details>

<details>
<summary><code>timestamps_RawData_ms</code></summary>

原始样本共用的时间向量（毫秒），来自 `diameter.t_ms`。

</details>

<details>
<summary><code>leftPupil_RawData, rightPupil_RawData</code></summary>

每只眼的 `RawSamplesModel`（没有数据则为空）。

</details>

<details>
<summary><code>leftPupil_ValidSamples, rightPupil_ValidSamples, meanPupil_ValidSamples</code></summary>

每只眼的 `ValidSamplesModel`，由 `processValidSamples` 生成。`meanPupil_ValidSamples` 只在双眼都有数据时存在。

</details>

<details>
<summary><code>segmentsTable, zeroTime_ms, diameterUnit</code></summary>

复制自 .mat 文件（见上面的文件内容）。

</details>

</details>

<details>
<summary><b><code>RawSamplesModel</code> —— 属性</b></summary>

<details>
<summary><code>eye</code></summary>

`'left'` 或 `'right'`。

</details>

<details>
<summary><code>rawSample</code></summary>

该眼的原始直径向量，从不被修改。

</details>

<details>
<summary><code>isValid</code></summary>

逻辑向量，每个原始样本一项：`true` = 通过范围、速度、偏离三道滤波。这是 `filterRawData` 的产出。`NaN` 原始样本为 `false`。

</details>

<details>
<summary><code>speedFiltData</code></summary>

速度滤波的中间结果（仅在 `keepFilterData = true` 时保存）：`maxDilationSpeeds`（每个样本与两侧邻点的绝对速度中较大的一个，仅当两侧邻点都相隔超过 200 ms 时才为 `NaN`）、`isValid`（速度滤波之后）、`mad`、`thresh`（= 中位数 + 16 × MAD，截断线）、`med_d`（中位数）。

</details>

<details>
<summary><code>devFiltData</code></summary>

偏离滤波的中间结果，每趟一列（默认 4 趟）：`isValidPerPass`、`residualsPerPass`（到平滑趋势线的距离）、`threshPerPass`、`smoothBaselinePerPass`（趋势线）。某一趟没有改变任何东西时，后面几趟直接复制它。

</details>

</details>

<details>
<summary><b><code>ValidSamplesModel</code> —— 属性</b></summary>

<details>
<summary><code>eye</code></summary>

`'left'`、`'right'` 或 `'mean'`。

</details>

<details>
<summary><code>samples.t_ms, samples.pupilDiameter</code></summary>

只含 valid 原始样本：它们的时刻（毫秒）和直径。

</details>

<details>
<summary><code>validFraction</code></summary>

**整段记录**里 valid 样本数 ÷ 非空原始样本数（0–1）。每行都以 `ValidSamples_validPercent`（×100）报告。`mean` 瞳孔取两只眼里较小的那个。

</details>

<details>
<summary><code>signal.t</code></summary>

平滑信号的 1000 Hz 时间轴，单位**秒**。

</details>

<details>
<summary><code>signal.pupilDiameter</code></summary>

平滑信号：valid 样本线性插值到 `signal.t`，再做 4 阶 4 Hz Butterworth 低通（零相位，`filtfilt`）。真实 valid 点之间的缺口超过 `interp_maxGap`（250 ms）的位置为 `NaN`。

</details>

<details>
<summary><code>signal.gap_ms</code></summary>

每个时刻前后两个真实 valid 样本之间的距离（毫秒）；距真实样本 0.5 ms 以内为 0。（类里声明的字段叫 `gap`，代码实际写入的是 `gap_ms`。）

</details>

</details>

### 2.3 方法：输入 → 输出

| 方法 | 输入 | 输出 | 终端打印 |
|---|---|---|---|
| `PupilDataModel.batchConstructor(folder, dirStruct, settings)` | 文件夹、`dir('*.mat')` 的结果、设置 | 对象数组 | `Constructing N Data Objects...` |
| `filterRawData()` | — | 每只眼的 `isValid` 写进对象 | `Filtering the raw data in N files...` |
| `processValidSamples()` | —（需要 `isValid`） | 带平滑信号的 `*_ValidSamples` 对象；双眼时再加 `mean` | `Interpolating and smooting the valid raw data subsets of N files...` |
| `analyzeSegments()` | —（需要平滑信号） | cell 数组，每个对象一张结果表；用 `vertcat(results{:})` 合并 | `File i (name): analyzing K segments.` |
| `exportSegments(folder, options)` | 输出文件夹；选项 `Eyes`、`SegmentTypes`、`NaNString`、`ZScore` | 每个对象每只眼一个 CSV | `File i (name) left pupil: wrote N samples to <file>` |
| `plotData()` | — | 图形窗口 | `—` |

## 3. 输出表，逐列说明

每张表列出每一列。最后一列的三角形展开后是计算方法、陷阱和已知注意事项。

<details>
<summary><b>02 · 逐样本 CSV —— <code>trk2csv</code> 写出的 <code><name>.csv</code>（21 列，每个眼动仪样本一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant` | – | 被试编号 | <details><summary>细节</summary>取自文件名（`sub149_...trk` 得 `sub149`）；文件名不以 `sub<数字>` 开头时用整个文件名。</details> |
| `run` | – | run 编号 0–4 | <details><summary>细节</summary>只数 `START` 事件。第一个 `START` 之前的样本是 `0`。缺第一个 `START` 的文件，run 编号会整体少 1；只记入异常表，不修补。</details> |
| `trial` | – | 文件内的 trial 编号 0–84 | <details><summary>细节</summary>每遇到一个 `CueStart` 加 1；第一个 cue 之前为 `0`。</details> |
| `trial_in_run` | – | run 内的 trial 编号 0–21 | <details><summary>细节</summary>每个 `START` 处归零。</details> |
| `phase` | – | 样本所处的任务阶段 | <details><summary>细节</summary>从上一个事件向后延续。取值：`pre`、`start`、`burn_in`、`cue`、`countdown`、`stimulus`、`whitenoise1`–`whitenoise4`、`rating`、`burn_out`。`CountdownFinish` 和未知事件不改变阶段。</details> |
| `time_ms` | ms | 样本的眼动仪原始时间戳 | <details><summary>细节</summary>一个很大的累计计数（如 `1491312812.2`），不是从 0 开始。样本间隔约 16.7 ms（60 Hz）。时间倒退时行仍按日志顺序保留（`NONMONOTONIC_TIME`）。</details> |
| `t_run_s` | s | 距当前 run 的 `START` 的秒数 | <details><summary>细节</summary>第一个 `START` 之前为 `NaN`。</details> |
| `event` | – | 挂在这个样本上的软件事件，没有则为空 | <details><summary>细节</summary>每个事件挂在时间戳不早于事件时刻的第一个样本上，所以事件时刻最多有一个采样间隔（约 17 ms）的误差。一个样本上有多个事件时用 `;` 连接。已知事件名：`START`、`BurnInStart`、`CueStart`、`CueFinish`、`CountdownFinish`、`StimuliStart`、`WhitenoiseStart1`–`4`、`RatingStart`、`BurnOutStart`。</details> |
| `sp_pup_x` | camera px | 瞳孔位置 x | <details><summary>细节</summary>来自日志的瞳孔列。日志没有解释前缀 `sp_`。按相机图像像素坐标理解，尚未向实验室确认。</details> |
| `sp_pup_y` | camera px | 瞳孔位置 y |  |
| `sp_glint_x` | camera px | 角膜反光点（glint）位置 x |  |
| `sp_glint_y` | camera px | 角膜反光点位置 y |  |
| `vector_x` | camera px | 瞳孔减反光点 x | <details><summary>细节</summary>日志里拼作 `vektor`。在一行上核对过：`sp_pup_x - sp_glint_x` = 357.3 − 345.7 ≈ 11.58 = `vector_x`。</details> |
| `vector_y` | camera px | 瞳孔减反光点 y |  |
| `gaze_x` | – | 注视位置 x | <details><summary>细节</summary>目前所有文件里都是空（`NaN`）：没有记录注视数据（`NO_GAZE`）。</details> |
| `gaze_y` | – | 注视位置 y |  |
| `pupil_2a` | camera px | 瞳孔椭圆轴 2a | <details><summary>细节</summary>椭圆的两个轴之一。Kret 适配器默认取 `pupil_2a` 与 `pupil_2b` 的平均作为瞳孔大小（`PupilMeasure='mean'`）。`NaN` 表示日志写的是 "no pupil geometry"。</details> |
| `pupil_2b` | camera px | 瞳孔椭圆轴 2b |  |
| `pupil_angle` | unconfirmed | 瞳孔椭圆朝向 | <details><summary>细节</summary>日志没写单位。1.64 这类数值像弧度；未确认。</details> |
| `pupil_valid` | 0/1 | 该样本有瞳孔数据 | <details><summary>细节</summary>`pupil_2a` 不是 `NaN` 时为 `1`。只表示“眼动仪给了值”，不是 Kret 伪影滤波的 `isValid`。</details> |
| `gaze_valid` | 0/1 | 该样本有注视数据 | <details><summary>细节</summary>`gaze_x` 不是 `NaN` 时为 `1`；我们的文件里全是 `0`。</details> |

</details>

<details>
<summary><b>02 · <code>trk2csv_qc_summary.csv</code>（25 列，每个 .trk 文件一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant, file` | – | 被试编号；.trk 文件名 |  |
| `status` | – | `ok` / `warn` / `failed` | <details><summary>细节</summary>只要有一条异常的严重度是 `warn` 就是 `warn`；`failed` 是读不出来的文件的占位值。</details> |
| `n_samples` | count | 样本数 |  |
| `duration_min` | min | 记录时长 | <details><summary>细节</summary>（最后一个时间戳 − 第一个时间戳）/ 60000。</details> |
| `sampling_hz` | Hz | 采样率 | <details><summary>细节</summary>1000 / 样本间隔的中位数。这里约 59.9 Hz。</details> |
| `n_events` | count | 日志中的软件事件数 |  |
| `n_START … n_BurnOutStart` | count | 每类事件的个数 | <details><summary>细节</summary>期望值：`START` 4、`BurnInStart` 4、`CueStart` = `CueFinish` = `StimuliStart` = 84、`BurnOutStart` 4；`RatingStart` 只出现在部分 trial（sub119 是 24）。共七列。</details> |
| `pupil_valid_fraction` | 0–1 | 有瞳孔数据的样本比例 | <details><summary>细节</summary>低于 0.5 给出 `LOW_PUPIL_VALID` 警告；不会删除任何样本。</details> |
| `gaze_valid_fraction` | 0–1 | 有注视数据的样本比例 |  |
| `cue_dur_min_s / _mean_s / _max_s` | s | cue 时长：`CueStart` → `CueFinish` | <details><summary>细节</summary>任务设定是 1.0 s。sub119 的均值是 0.881 s（0.832–0.96 s）。</details> |
| `n_cue_off_setting` | count | 与 1.0 s 相差超过 0.001 s 的 cue 个数 | <details><summary>细节</summary>sub119 是 84 个里的 84 个，这就是 `CUE_DURATION` 的来源。</details> |
| `countdown_min_s / _mean_s / _max_s` | s | `CueStart` → `StimuliStart` | <details><summary>细节</summary>注意：包含 cue 的时间。设计的倒计时 = 这个值 − 1 s 的 cue（7.5–30 s）。</details> |
| `n_malformed_lines` | count | 无法解析的日志行数 |  |
| `n_issues` | count | 该文件在异常表中的行数 |  |

</details>

<details>
<summary><b>02 · <code>trk2csv_issues.csv</code>（5 列，每条异常一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant, file` | – | 被试编号；.trk 文件名 |  |
| `severity` | – | `warn` = 偏离预期；`info` = 值得知道的事实 |  |
| `code` | – | 机器可读的代码，见下表 |  |
| `message` | – | 带数字的说明文字 |  |

</details>

<details>
<summary><b>异常代码（列 <code>code</code>）</b></summary>

| 代码 | 严重度 | 含义 |
|---|---|---|
| `MALFORMED_LINES` | warn | 有行无法解析而被跳过 |
| `NO_STOP_LINE` | warn | 没有 `stop timecounter` 行，日志可能被截断 |
| `NONMONOTONIC_TIME` | warn | 有时间戳不晚于前一个 |
| `TIME_GAP` | warn | 样本间隔超过 200 ms |
| `LOW_PUPIL_VALID` | warn | 有瞳孔数据的样本不足 50% |
| `NO_GAZE` | info | 没有任何样本有注视数据 |
| `NO_EVENTS` | warn | 没有 `SoftwareEvent` 行，无法填 run / trial / phase |
| `START_COUNT` | warn | `START` 个数不是 4 |
| `START_BURNIN_MISMATCH` | warn | `START` 与 `BurnInStart` 个数不一致（会指出缺 `START` 的那个 `BurnInStart`） |
| `TRIAL_COUNT` | warn | `CueStart` 个数不是 84 |
| `EVENT_COUNT_MISMATCH` | warn | `CueStart`、`CueFinish`、`StimuliStart` 个数不相等 |
| `UNKNOWN_EVENTS` | info | 出现了已知名单之外的事件名 |
| `CUE_DURATION` | warn | cue 与 1.0 s 设定相差超过 0.001 s（附最小 / 均值 / 最大） |

</details>

<details>
<summary><b>03 · <code><sub>_events.csv</code>（3 列，每个软件事件一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant` | – | 被试编号 |  |
| `time_ms` | ms | 事件的原始时间戳 | <details><summary>细节</summary>`SoftwareEvent` 行里事件自己的时刻，没有对齐到样本。</details> |
| `event` | – | 事件名 |  |

</details>

<details>
<summary><b>05 · 事件表 —— <code><sub>_event_table.csv</code>、<code><sub>_event_table_5step.csv</code>、<code>all_subjects_event_table*.csv</code>（18 列）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant` | – | 被试编号 |  |
| `order` | 1–5 | 被试做的是五种试次顺序中的哪一种 | <details><summary>细节</summary>把每个 trial 的倒计时长度（`StimuliStart − CueStart − 1 s`）与 `TrialOrder<o>Run<r>.xlsx` 比较，取五个里最吻合的。差距会打印出来（例如 0.80 s 对次优 14.8 s）。别处没有记录这个顺序，需要向实验室确认。</details> |
| `run` | 1–4 | run 编号 | <details><summary>细节</summary>`ceil(trial / 21)`，由 `ymtcRunCheck` 验证。</details> |
| `trial` | 1–84 | 被试内的 trial 编号 | <details><summary>细节</summary>数 `CueStart`。run 级的行为空。</details> |
| `trial_in_run` | 1–21 | run 内的 trial 编号 |  |
| `ymtc_marker` | – | 任务自己的 marker 名 | <details><summary>细节</summary>例如 `OnsetPTCTO`、`PredictableTimeCertainThreatOutcome`、`OutcomePTCTO`、`WhiteNoise`、`Rating`；run 级的行是 `START`、`BurnInStart`、`BurnOutStart`。</details> |
| `trk_event` | – | 与该 marker 对应的 trk 事件 | <details><summary>细节</summary>`CueStart` ↔ Onset，`CueFinish` ↔ 倒计时开始，`StimuliStart` ↔ Outcome，`WhitenoiseStart1` ↔ WhiteNoise，`RatingStart` ↔ Rating。</details> |
| `time_ms` | ms | 对应 trk 事件的原始时间戳 | <details><summary>细节</summary>trk 里缺该 marker 时为空（不插值）。</details> |
| `t_from_onset_s` | s | 距本 trial 的 Onset 的秒数 |  |
| `expected_from_onset_s` | s | 设计上该 marker 的位置 | <details><summary>细节</summary>来自 order 工作簿的 `onsets` 列，以 trial 的 Onset 为基准。</details> |
| `diff_s` | s | 实测 − 设计 | <details><summary>细节</summary>`t_from_onset_s − expected_from_onset_s`。符号一致说明有系统偏移，例如 cue 偏短。</details> |
| `expected_duration_s` | s | 该 marker 的设计时长 | <details><summary>细节</summary>来自 `durations` 列：cue 1 s、倒计时 7.5–30 s、Outcome 2.7 s、WhiteNoise 2.3 s、Rating 6 s。</details> |
| `condition` | – | `PTCT` `PTCS` `PTUO` `UTCT` `UTCS` `UTUO` | <details><summary>细节</summary>第一个 marker 名里 `Onset` 之后的四个字符。trk 里没有，来自选定的 order 文件。实验室口头说的 `PTPT` 是否等于这里的 `PTCT` 尚待确认。</details> |
| `timing` | P/U | 时间可预测 / 不可预测 | <details><summary>细节</summary>`condition` 的第 1 个字母。</details> |
| `certainty` | C/U | cue 时是否已知结果 | <details><summary>细节</summary>`condition` 的第 3 个字母。</details> |
| `outcome` | T/S/O | *cue* 所宣告的结果 | <details><summary>细节</summary>第 4 个字母。`T` 威胁、`S` 安全、`O` = 未宣告。两个不确定条件下每一行都是 `O`。</details> |
| `actual_outcome` | T/S | 该 trial 实际的结果 | <details><summary>细节</summary>确定型 trial 等于 `outcome`；不确定型取 Outcome marker 的最后一个字母（`OutcomeUTUOT` → `T`）。run 级的行为空。</details> |
| `step` | 1–5 | 在 trial 内的位置 | <details><summary>细节</summary>1 Onset、2 倒计时开始、3 Outcome、4 WhiteNoise、5 Rating。run 级的行为空。完整版多出 `WhiteNoise_part2`–`4` 行，同样 `step = 4`。</details> |

</details>

<details>
<summary><b>05 · <code>event_table_summary.csv</code>（6 列，每个被试一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant` | – | 被试编号 |  |
| `status` | – | `ok` / `skipped_no_file` / `skipped_no_events` / `error` | <details><summary>细节</summary>sub124、sub128、sub137 是 `skipped_no_events`：它们的 trk 里没有 `SoftwareEvent` 行。</details> |
| `order` | 1–5 | 选中的试次顺序 |  |
| `nRows` | count | 写出的行数 | <details><summary>细节</summary>完整表 624，5 步版 372；sub134 少 1 行（缺第一个 `START`）。</details> |
| `nTrials` | count | 找到的 trial 数 |  |
| `note` | – | 说明文字，正常时为空 |  |

</details>

<details>
<summary><b>05 · <code>all_subjects_trials_wide.csv</code>（14 列，每个 trial 一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant, order, run, trial` | – | trial 的标识 |  |
| `condition, timing, certainty, outcome` | – | 同事件表 |  |
| `onset_s` | s | 恒为 0，参考点 |  |
| `countdown_s` | s | 倒计时开始，距 Onset 的秒数 |  |
| `outcome_s` | s | Outcome 开始 |  |
| `whitenoise_s` | s | 白噪声开始 |  |
| `rating_s` | s | 评分开始；没有评分时为 `NaN` |  |
| `has_rating` | logical | 该 trial 是否有评分 | <details><summary>细节</summary>84 个里 24 个。</details> |

</details>

<details>
<summary><b>05 · <code>timing_check.csv</code>（7 列，每个被试 × marker 一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant` | – | 被试编号 |  |
| `phase` | – | `1 Onset` … `5 Rating start` |  |
| `n` | count | 该格中的 marker 数 |  |
| `mean_s, sd_s` | s | `diff_s` 的均值和标准差 | <details><summary>细节</summary>仅是描述性数字。用 `ymtcTimingCheck` 复现。</details> |
| `min_s, max_s` | s | `diff_s` 的极值 |  |

</details>

<details>
<summary><b>00 · <code>run_check.csv</code>（9 列，每个被试一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant, status` | – | 被试编号；`ok` / `no_file` / `no_events` |  |
| `nSTART, nBurnInStart, nBurnOutStart, nCueStart` | count | 事件个数 |  |
| `trialsPerRun` | – | 例如 `21/21/21/21` | <details><summary>细节</summary>以 `BurnInStart` 作为 run 边界来数（不用可能缺失的 `START`）。</details> |
| `runAssignmentOK` | 0/1 | 每个 run 都是 21 个 trial 且个数一致 | <details><summary>细节</summary>`run = ceil(trial / 21)` 靠它把关。</details> |
| `note` | – | 哪里不对的说明 |  |

</details>

<details>
<summary><b>原版的表：<code>analyzeSegments</code> 返回什么</b></summary>

每个对象一张表：先是你的 `segmentsTable` 全部列，再向右接上每只眼的 10 列，前缀为 `leftPupil_`、`rightPupil_`、`meanPupil_`。我们的数据只有一只瞳孔，所以只有 `leftPupil_*`。在 MATLAB 里表头还带 `VariableUnits` 和 `VariableDescriptions`，存成 CSV 时会丢，这就是本页存在的原因。

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `segmentStart, segmentEnd` | s | 分段边界 | <details><summary>细节</summary>距记录第一个样本的秒数（第一个样本 = 0）。左闭右开 `[start, end)`。缺对应事件时两者都是 `NaN`，整行统计也就是 `NaN`。</details> |
| `SmoothSig_meanDiam` | px | 段内平滑信号的均值 | <details><summary>细节</summary>忽略 `NaN`。插值出来的点也计入，所以短缺口看起来很干净；要和 `SmoothSig_missingDataPercent` 一起看。</details> |
| `SmoothSig_minDiam, SmoothSig_maxDiam` | px | 平滑信号的最小 / 最大 |  |
| `SmoothSig_missingDataPercent` | % | 段内为 `NaN` 的比例 | <details><summary>细节</summary>只有真实 valid 点之间超过 250 ms 的缺口才会变成 `NaN`。这是每段的缺失率，质控用它。</details> |
| `SmoothSig_sampleCount` | count | 段内所有 1000 Hz 样本 | <details><summary>细节</summary>含 `NaN`；约等于段长 × 1000（0.5 s 的 baseline 是 500）。</details> |
| `ValidSamples_meanDiam` | px | 段内真实 valid 样本的均值 | <details><summary>细节</summary>没有插值和平滑：只含通过三道伪影滤波的点。</details> |
| `ValidSamples_minDiam, ValidSamples_maxDiam` | px | valid 样本的最小 / 最大 |  |
| `ValidSamples_validPercent` | % | **整段记录**的 valid 比例 | <details><summary>细节</summary>`validFraction × 100`：整段记录里 valid 点数 ÷ 非空原始点数。同一被试每行都一样，与这一段无关。</details> |
| `ValidSamples_sampleCount` | count | 段内 valid 样本数 | <details><summary>细节</summary>60 Hz 下 0.5 s 的 baseline 最多约 30 个。</details> |

</details>

<details>
<summary><b>04 · <code>kret_results.csv</code>（16 列，每个被试 × trial × 分段一行 = 每 trial 4 行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `segmentStart, segmentEnd` | s | 分段边界 |  |
| `segmentName` | – | 例如 `countdown_004` | <details><summary>细节</summary>分段类型 + trial 编号；trial 4 的倒计时。</details> |
| `segmentType` | – | `baseline` / `countdown` / `preOutcome` / `postOutcome` |  |
| `participant, trial` | – | 被试编号；trial 1–84 |  |

再加 10 个 `leftPupil_*` 统计列（名字同上，加前缀）。

</details>

<details>
<summary><b>04 · <code>trials_qc.csv</code>（19 列 = 上面 16 列 + 3 个质控标记，在 trial 的 4 个分段行上重复）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `RejectCountdown` | 0/1 | 该 trial 被剔除 | <details><summary>细节</summary>`countdown_SmoothSig_missingDataPercent > 50`。分析规则 R1。</details> |
| `PreOutcomeMostlyMissing` | 0/1 | 只标记，trial 保留 | <details><summary>细节</summary>`preOutcome_SmoothSig_missingDataPercent > 50`。该 trial 的 GLM 调节量不可信。规则 R2。</details> |
| `SubjectExcluded` | 0/1 | 整个被试被排除 | <details><summary>细节</summary>该被试被剔除的 trial 超过 20%。规则 R3（Leuchs / Shechner 20% 规则）。</details> |

前 16 列与 `kret_results.csv` 完全一致。

</details>

<details>
<summary><b>04 · <code>subjects_qc.csv</code>（5 列，每个被试一行）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `participant` | – | 被试编号 |  |
| `nTrials, nRejected` | count | trial 数；被 R1 剔除的数 |  |
| `rejectPct` | % | `nRejected / nTrials × 100` |  |
| `subjectExcluded` | 0/1 | rejectPct 超过 20 |  |

</details>

<details>
<summary><b>04 · <code>segments/<name>_leftpupil_segments.csv</code>（6–7 列，每个 1000 Hz 样本一行，由 <code>exportSegments</code> 写出）</b></summary>

| 列 | 单位 | 含义 | 细节 |
|---|---|---|---|
| `segmentName, segmentType` | – | 同 `segmentsTable` |  |
| `segmentStart_s` | s | 段起点 | <details><summary>细节</summary>同一段的每一行相同。</details> |
| `tRel_s` | s | 样本时刻 − 段起点 |  |
| `pupilDiameter_px` | px | 平滑信号的直径，4 位小数 | <details><summary>细节</summary>列名里的单位随 `diameterUnit`。缺口超过 250 ms 的位置为 `NaN`。</details> |
| `gap_ms` | ms | 该时刻前后两个真实 valid 点之间的间隔 | <details><summary>细节</summary>距真实点 0.5 ms 以内为 0；1 位小数。</details> |
| `pupilDiameterZ` | z | 仅在 `ZScore=true` 时有 | <details><summary>细节</summary>（值 − 整段记录均值）/ 整段记录标准差，每只眼在整段记录上算一次（Leuchs 2017），不是段内 z。</details> |

</details>

<details>
<summary><b>06 · <code><sub>_final.csv</code> 与 <code>all_subjects_final.csv</code> —— 69 列，每个 marker 一行</b></summary>

由 `ymtcMergeResults` 基于 5 步事件表合并而成。每个分段的统计量放在它所属的 marker 行上：baseline → Onset，countdown 和 preOutcome → 倒计时行，postOutcome → Outcome 行；WhiteNoise 和 Rating 行在这些列上是 `NaN`。完整列表：

**事件列（同事件表）** (18)

`participant`, `order`, `run`, `trial`, `trial_in_run`, `ymtc_marker`, `trk_event`, `time_ms`, `t_from_onset_s`, `expected_from_onset_s`, `diff_s`, `expected_duration_s`, `condition`, `timing`, `certainty`, `outcome`, `actual_outcome`, `step`

**分段 `baseline` —— 只写在 `step = 1` 的行上，同一 trial 的其他行为 `NaN`** (12)

`baseline_segmentStart`, `baseline_segmentEnd`, `baseline_SmoothSig_meanDiam`, `baseline_SmoothSig_minDiam`, `baseline_SmoothSig_maxDiam`, `baseline_SmoothSig_missingDataPercent`, `baseline_SmoothSig_sampleCount`, `baseline_ValidSamples_meanDiam`, `baseline_ValidSamples_minDiam`, `baseline_ValidSamples_maxDiam`, `baseline_ValidSamples_validPercent`, `baseline_ValidSamples_sampleCount`

**分段 `countdown` —— 只写在 `step = 2` 的行上，同一 trial 的其他行为 `NaN`** (12)

`countdown_segmentStart`, `countdown_segmentEnd`, `countdown_SmoothSig_meanDiam`, `countdown_SmoothSig_minDiam`, `countdown_SmoothSig_maxDiam`, `countdown_SmoothSig_missingDataPercent`, `countdown_SmoothSig_sampleCount`, `countdown_ValidSamples_meanDiam`, `countdown_ValidSamples_minDiam`, `countdown_ValidSamples_maxDiam`, `countdown_ValidSamples_validPercent`, `countdown_ValidSamples_sampleCount`

**分段 `preOutcome` —— 只写在 `step = 2` 的行上，同一 trial 的其他行为 `NaN`** (12)

`preOutcome_segmentStart`, `preOutcome_segmentEnd`, `preOutcome_SmoothSig_meanDiam`, `preOutcome_SmoothSig_minDiam`, `preOutcome_SmoothSig_maxDiam`, `preOutcome_SmoothSig_missingDataPercent`, `preOutcome_SmoothSig_sampleCount`, `preOutcome_ValidSamples_meanDiam`, `preOutcome_ValidSamples_minDiam`, `preOutcome_ValidSamples_maxDiam`, `preOutcome_ValidSamples_validPercent`, `preOutcome_ValidSamples_sampleCount`

**分段 `postOutcome` —— 只写在 `step = 3` 的行上，同一 trial 的其他行为 `NaN`** (12)

`postOutcome_segmentStart`, `postOutcome_segmentEnd`, `postOutcome_SmoothSig_meanDiam`, `postOutcome_SmoothSig_minDiam`, `postOutcome_SmoothSig_maxDiam`, `postOutcome_SmoothSig_missingDataPercent`, `postOutcome_SmoothSig_sampleCount`, `postOutcome_ValidSamples_meanDiam`, `postOutcome_ValidSamples_minDiam`, `postOutcome_ValidSamples_maxDiam`, `postOutcome_ValidSamples_validPercent`, `postOutcome_ValidSamples_sampleCount`

**质控列 —— 复制到该 trial 的每一行（run 级的行为 `NaN`）** (3)

`RejectCountdown`, `PreOutcomeMostlyMissing`, `SubjectExcluded`

</details>

## 4. 设置项

<details>
<summary><b><code>settings.raw</code>（来自 <code>rawDataFilter()</code>）</b></summary>

| 设置 | default | 含义 |
|---|---|---|
| `PupilDiameter_Min / _Max` | 1.5 / 9 | 范围滤波。默认值是**毫米**，像素数据必须覆盖（`Examples/Dataset_1` 用 0.1 / inf）。我们的管线按数据设定（0.5–99.5 百分位 × 0.8 / 1.2）并打印数值。 |
| `islandFilter_islandSeperation_ms` | 40 ms | 一簇样本离其他样本多远才算“孤岛”。 |
| `islandFilter_minIslandWidth_ms` | 50 ms | 比这窄的孤岛判无效。 |
| `dilationSpeedFilter_MadMultiplier` | 16 | 速度超过 中位数 + 该倍数 × MAD 判无效（抓眨眼边缘）。 |
| `dilationSpeedFilter_maxGap_ms` | 200 ms | 只有两个 valid 样本相隔小于它时才计算速度。 |
| `gapDetect_minWidth / _maxWidth` | 75 / 2000 ms | 这个宽度范围的缺失段算“缺口”，缺口边缘会再被剔除一小段。 |
| `gapPadding_backward / _forward` | 50 / 50 ms | 这种缺口前 / 后额外剔除的长度。 |
| `residualsFilter_passes` | 4 | 趋势偏离滤波的趟数。 |
| `residualsFilter_MadMultiplier` | 16 | 偏离趋势线超过 中位数 + 该倍数 × MAD 判无效。 |
| `residualsFilter_interpFs / _lowpassCF` | 100 Hz / 16 Hz | 生成趋势线用的重采样率和截止频率（1 阶 Butterworth）。 |
| `keepFilterData` | true | 保存 `speedFiltData` / `devFiltData`。占内存，调完参数后设 `false`。 |

</details>

<details>
<summary><b><code>settings.valid</code>（来自 <code>ValidSamplesModel.getDefaultSettings()</code>）</b></summary>

| 设置 | default | 含义 |
|---|---|---|
| `interp_upsamplingFreq` | 1000 Hz | 平滑信号的采样率。 |
| `LpFilt_B / LpFilt_A` | order 4, 4 Hz | 由 4 阶、1000 Hz 下截止 4 Hz 算出的低通系数（零相位 `filtfilt`）。 |
| `interp_maxGap` | 250 ms | 真实 valid 点之间超过它的缺口，在平滑信号里变成 `NaN`。 |

</details>

<details>
<summary><b><code>trk2csv</code> 选项</b></summary>

| 设置 | default | 含义 |
|---|---|---|
| `OutFolder` | folder of the .trk | csv 写到哪里。 |
| `Overwrite` | true | 覆盖已有 csv。 |
| `WriteReport` | false | 同时写 `<name>_issues.csv`。 |
| `ExpectedRuns` | 4 | 预期的 `START` 个数。 |
| `ExpectedTrialsPerRun` | 21 | 每个 run 预期的 trial 数（共 84）。 |
| `CueDurationSec / CueToleranceSec` | 1.0 / 0.001 | 任务设定的 cue 时长及允许的差。 |
| `MinValidFraction` | 0.5 | 有瞳孔数据的比例低于它就报告（`LOW_PUPIL_VALID`）；不删任何东西。 |
| `MaxGapMs` | 200 | 样本间隔超过它就报告（`TIME_GAP`）。 |
| `Quiet` | false | 不打印。 |

</details>

<details>
<summary><b><code>csv2kretmat</code> 选项</b></summary>

| 设置 | default | 含义 |
|---|---|---|
| `PupilMeasure` | 'mean' | `'mean'` / `'2a'` / `'2b'`：用哪个椭圆轴（或两者平均）作为瞳孔大小。 |
| `BaselineWinSec` | 0.5 | cue 前 baseline 段的长度；0 表示关闭。 |
| `PreOutcomeWinSec / PostOutcomeWinSec` | 2.0 / 2.0 | Outcome 前 / 后分段的长度；设 0 可关闭 outcome 前的那段。 |

</details>

## 5. 文件与函数

```
trk2csv_batch ──▶ trk2csv ──▶ private/readTrk ─▶ private/labelSamples ─▶ private/checkTrk
                                  （解析）          （事件挂到样本）        （只记录）

ymtcEventTableBatch ──▶ ymtcEventTable ──▶ readOrder()   （同文件末尾的子函数）
         │                    │
         │                    └──▶ 05_markers/05_<sub>_markers[_5step].csv
         └──▶ ymtcTrialWide  / ymtcTimingCheck     （读那张表，各写一个文件）

ymtcRunCheck     独立：读 03_events，写 07_checks/07_all_run_check.csv
ymtcConfig       所有 ymtc* 函数都读它：文件夹在哪
checkDocs        比对 docs/02 和每张输出表的真实表头
```

| 文件 | 行数 | 做什么 | 写出 |
|---|---|---|---|
| `trk2csv.m` | 87 | 一个 .trk → 一个逐样本 CSV + 报告 | 02_samples/<name>.csv |
| `trk2csv_batch.m` | 76 | 整个文件夹 → 同上，另加两张 QC 表 | 02_all_qc_summary.csv、02_all_issues.csv |
| `private/readTrk.m` | 79 | 把文本日志解析成表头/样本/事件 | 内存 |
| `private/labelSamples.m` | 46 | 事件挂到样本，向后填 run/trial/phase | 内存 |
| `private/checkTrk.m` | 134 | 与任务应有状态对比；只记录不修补 | 02_all_issues.csv 的行 |
| `ymtcEventTable.m` | 184 | 一个被试 → 每 marker 一行，按任务顺序 | 05_markers/05_<sub>_markers[_5step].csv |
| `ymtcEventTableBatch.m` | 122 | 循环被试，加汇总表和合并表 | 05_all_markers*.csv、05_all_markers_summary.csv |
| `ymtcTimingCheck.m` | 71 | 按被试 × marker 汇总 diff_s | 05_all_timing_check.csv |
| `ymtcTrialWide.m` | 68 | 长表 → 一 trial 一行 | 05_all_trials_wide.csv |
| `ymtcRunCheck.m` | 117 | 每个 run 是否 21 trial（用 BurnInStart 分界） | 07_checks/07_all_run_check.csv |
| `ymtcConfig.m` | 40 | 文件夹位置；不写死路径 | 结构体 C |
| `checkDocs.m` | 101 | 比对 docs/02 与真实表头 | 终端 |

<details>
<summary><b>原版代码（<code>helperFunctions/</code>）</b></summary>

<details>
<summary><code>rawDataFilter.m</code></summary>

主函数依次调用 `removeOutOfBounds`（范围）→ `madSpeedFilter`（速度，抓眨眼）→ `madDeviationFilter`（偏离趋势）。孤立点清理 `removeLoners` 在三步内部反复调用，`expandGaps`（缺口前后扩剔）在速度滤波里调用；`madCalc` 算 MAD 阈值。无参数调用返回默认的 `settings.raw`。

</details>

<details>
<summary><code>genMeanDiaSamples.m</code></summary>

把双眼合成一条平均直径；由 `processValidSamples` 调用；单眼数据用不到。

</details>

<details>
<summary><code>plotSegments.m</code></summary>

把分段表画成色块；由 `plotData` 调用。

</details>

<details>
<summary><code>printToConsole.m</code></summary>

打印进度，内部用。

</details>

<details>
<summary><code>legacyModeCheck.m</code></summary>

MATLAB 低于 8.3（没有 `table`）时把 `LEGACY/` 加进路径；新版本什么也不做。

</details>

<details>
<summary><code>FALLBACK/</code></summary>

给没有工具箱或函数已被移除的 MATLAB 用的 `butter`、`filtfilt`、`histc`、`nanmin` / `nanmax` / `nanmean` / `nanmedian` 替代实现。陷阱：`addpath(genpath(...))` 把文件夹放到路径**最前面**，FALLBACK 会盖住真工具箱函数；想优先用工具箱就用 `addpath(..., '-end')`。本机没有 Statistics 工具箱，所以 `nan*` 一直是 FALLBACK。

</details>

<details>
<summary><code>LEGACY/</code></summary>

给很老的 MATLAB 模拟 `table`。

</details>

</details>

<details>
<summary><b>我们的层（<code>ymtc/</code> 与适配器）</b></summary>

<details>
<summary><code>trk2csv.m</code></summary>

一个 `.trk` → 一个逐样本 CSV 和一份报告。不需要工具箱。

</details>

<details>
<summary><code>trk2csv_batch.m</code></summary>

一个 `.trk` 文件夹 → `csv/`，外加 `trk2csv_qc_summary.csv` 与 `trk2csv_issues.csv`。

</details>

<details>
<summary><code>private/readTrk.m, labelSamples.m, checkTrk.m</code></summary>

解析文本日志；挂事件并向后延续 run / trial / phase；与任务应有的样子对比（只记录）。

</details>

<details>
<summary><code>ymtcEventTable.m</code></summary>

单个被试 → 按任务顺序排列的 marker 表。通过匹配倒计时长度选 trial 顺序。

</details>

<details>
<summary><code>ymtcEventTableBatch.m</code></summary>

一次处理所有被试，并产出 `event_table_summary.csv` 与合并表。

</details>

<details>
<summary><code>ymtcRunCheck.m</code></summary>

每个 run 真的是 21 个 trial 吗？→ `run_check.csv`。

</details>

<details>
<summary><code>ymtcTimingCheck.m, ymtcTrialWide.m</code></summary>

读取 marker 表：生成 `timing_check.csv` 与 `all_subjects_trials_wide.csv`。

</details>

<details>
<summary><code>ymtcMergeResults.m</code></summary>

按 participant + trial 把 5 步 marker 表与 `kret_results.csv`、`trials_qc.csv` 合并 → `06_最终结果/<sub>_final.csv` 和 `all_subjects_final.csv`（69 列）。不做修补，没有 Kret 行的 trial 保持 `NaN`。

</details>

<details>
<summary><code>csv2kretmat.m, example_kret_pipeline.m</code></summary>

Kret 管线的适配器和批量脚本（在 `代码_matlab/`，不在本仓库内）。适配器把时间重新参考到 0、去掉重复时间戳（保留第一个）、把 `pupil_valid == 0` 处设为 `NaN`，并写入 `diameterUnit = 'px'`。

</details>

<details>
<summary><code>ymtcConfig.m, checkDocs.m</code></summary>

文件夹位置（仓库里没有绝对路径）；`checkDocs` 把文档里的列与真实 CSV 表头对比。

</details>

</details>

## 6. 两个官方例子

`main_Dataset1.m` 是 (1)–(5) 步的最短演示。我们的 YMTC 数据走同样的单瞳孔路线，转换器是 `trk2csv`。

<details>
<summary><code>Examples/Dataset_1/</code></summary>

SR-Research Eyelink，**单瞳孔**。`batchFileConverter_Dataset1.m`（EDF → .mat）与 `main_Dataset1.m`（完整流水线）。设置了 `PupilDiameter_Max = inf`、`PupilDiameter_Min = 0.1`（任意单位）、`keepFilterData = true`。

</details>

<details>
<summary><code>Examples/Dataset_2/</code></summary>

E-Prime + Tobii，**双瞳孔**。`batchFileConverter_Dataset2.m`（.gazedata → .mat）与 `main_Dataset2.m`。

</details>

## 7. 排错：症状 → 原因 → 修法

| 症状 | 原因 | 修法 |
|---|---|---|
| `'t_ms' must be sorted!` | 时间戳不升序（trk 里有重复或倒退的时间戳） | 在转换器里排序、去重，不要改包内部；重复项要记录下来 |
| `'L' must be empty, or have the same length as 't_ms'` | 直径向量和时间向量长度不一致 | 在转换器里检查长度 |
| `No settings present.` | 构造 `PupilDataModel` 时没传 `settings` | 用 `PupilDataModel.getDefaultSettings()` 取一份再改 |
| `Interpolation cannot be performed.` | 该眼 valid 点少于 2 个（范围设错或全是噪声） | 检查 `PupilDiameter_Min/Max` 是否匹配单位 |
| `almost every sample is invalid` | 默认范围 1.5–9 是毫米，像素数据全在范围外 | 按实际单位设范围 |
| `warning pupilSize:edgeClamp` | 浮点误差让上采样时刻落在 valid 区间外，被夹回边界 | 只是提示；个数多才需要查 |
| `ValidSamples_validPercent identical on every row` | 按设计就是整段记录的值 | 看每段缺失率用 `SmoothSig_missingDataPercent` |
| `SmoothSig_meanDiam looks fine but the data is poor` | 小于 250 ms 的缺口被插值填平了 | 同时看 `missingDataPercent` 和 `ValidSamples_sampleCount` |
| `a whole result row is NaN` | 分段起 / 止是 `NaN`（缺事件），或段内没有样本 | 去事件表里找缺的 marker；不会补值 |
| `plotData does nothing / is skipped` | `-batch` 没有桌面 | 在桌面 MATLAB 里运行 |
| `plotData shows one file only` | 源码里 `plotMultipleFiles = false`（很吃资源） | 改 `PupilDataModel.m` 里的这个开关 |
| `addpath fails in Examples` | 路径写成 Windows 反斜杠 | macOS / Linux 改成 `../../helperFunctions/` |
| `MATLAB -batch` fails with several lines | `-batch` 后面只能写一行命令 | 把代码放进脚本文件，再 `run('x.m')` |

## 8. 局限

- 原版 README 要求 Signal Processing 和 Statistics 两个工具箱，测试环境是 Windows 7 上的 MATLAB 2012b / 2016a / 2017a。本 fork 为 macOS 做了补丁（`PupilDataModel` 的路径分隔符、`FALLBACK/`），见 `git log`。
- 滤波参数是论文默认值，**没有针对 YMTC 数据调过**。要调需要桌面 MATLAB，用 `plotData()` 看原始轨迹。
- 瞳孔大小是相机像素、单眼；没有记录注视；`pupil_angle` 的单位和 `sp_` 前缀的含义未确认。
- 本页只描述代码做了什么，不判断结果好坏。数据质量见 [`../docs/05_data_quality.md`](../docs/05_data_quality.md)。

## 9. 审阅地图：读哪些文件、按什么顺序

如果要自己核一遍代码，这是最短路线。下面的路径都是真实的，行数是从文件里数出来的。

```
code/ymtc/                        在本仓库里
  ymtcEventTable.m                184   marker 表本身
  trk2csv.m                        87   .trk → csv
  private/readTrk.m                79   文本解析
  private/labelSamples.m           46   事件 → 样本
  private/checkTrk.m              134   什么会被记成异常
  ymtcEventTableBatch / RunCheck / TimingCheck / TrialWide   外围，扫一眼

代码_matlab/                      和研究数据放在一起，不在仓库里
  csv2kretmat.m                   259   四个段的定义
  example_kret_pipeline.m         140   滤波 → 插值 → 分段 → 统计
  ymtcTrialQC.m                   110   三条剔除规则
  ymtcMergeResults.m              ~110  69 列是怎么拼出来的
```

| 读 | 读的时候确认什么 | 为什么重要 | 时间 |
|---|---|---|---|
| 1. `ymtcEventTable.m` | 五组 marker↔事件；order 怎么选；`condition`/`timing`/`certainty`/`outcome` 从哪来；`diff_s` 是什么；为什么 `run = ceil(trial/21)` | 所有关于条件的说法都压在这个文件上 | 40 分钟 |
| 2. `trk2csv.m` → `readTrk.m` → `labelSamples.m` → `checkTrk.m` | 一行 csv 怎么产生；什么只记录不修补 | 后面全部环节的输入 | 60 分钟 |
| 3. `csv2kretmat.m` | 四个段和它们的窗口；时间零点约定 | 决定每个瞳孔列里“countdown”指什么 | 30 分钟 |
| 4. `example_kret_pipeline.m` + `docs/03` | 哪个滤波在哪一步；哪些是论文默认、哪些是我们改的 | 唯一产生数字的地方 | 40 分钟 |
| 5. `ymtcTrialQC.m` + `docs/05` | 三条规则和阈值 | 决定哪些 trial 能留下 | 20 分钟 |
| 6. `ymtcMergeResults.m` | 合并键（`participant`+`run`+`trial`）和列顺序 | 解释那张 69 列的表 | 20 分钟 |

按你能投入的时间，三条路线：

- **30 分钟**：只读第 1 个，旁边开着 `docs/02` 列字典——足够守住 marker 表的每一列。
- **2 小时**：第 1–2 项，外加跑一次 `checkDocs`——足够守住整个数据准备层。
- **半天**：六项全读——足够守住最终表里的每一个数字。

## 10. 延伸阅读

[`../docs/01_pipeline_overview.md`](../docs/01_pipeline_overview.md) · [`../docs/02_column_dictionary.md`](../docs/02_column_dictionary.md) · [`../docs/03_pupil_size_internals.md`](../docs/03_pupil_size_internals.md) · [`ymtc/README.md`](ymtc/README.md) · [`../docs/04_our_code.md`](../docs/04_our_code.md) · [`../docs/06_faq.md`](../docs/06_faq.md)

Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.

[↑ top](#top) · **[English](#english) · [한국어](#한국어) · [中文](#中文)**
