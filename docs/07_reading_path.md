# 07 · Reading path

EN: The order to read the upstream code and our own in, what to look at in each file, and where the statistics live.
KO: 업스트림 코드와 우리 코드를 어떤 순서로 읽고, 각 파일에서 무엇을 보고, 통계가 어디 있는지.
ZH: 上游代码和我们自己的代码按什么顺序读、每个文件看什么、统计在哪里。

This is the *review* page. What is done and what is next is the other page:
[08 · Roadmap and to-do](08_roadmap.md).

Why an order at all: the repository is two codebases glued at one seam. Upstream decides what a
*valid sample* is; our layer decides what a *marker* is. Read them in data order, not in folder
order, and every number you meet later has a visible origin.

## 0 · Before any code (10 min)

1. [01](01_pipeline_overview.md) — the five layers, so you know which layer you are looking at.
2. [02](02_column_dictionary.md) §A–§H — the eight tables and their columns. Skim, do not study.
3. `code/ymtc/README.md` — the call chain of our layer, one screen.

After this you should be able to say where a number in `06_merged/06_all_merged.csv` came from
without opening a file.

## 1 · Upstream: four functions carry everything (45–60 min)

Read in this order; each one only makes sense after the previous.

| # | file | read | what you are checking |
|---|---|---|---|
| 1 | `code/helperFunctions/rawDataFilter.m` | `getDefaultSettings`, then `removeOutOfBounds` → `madSpeedFilter` → `expandGaps` → `madDeviationFilter` → `removeLoners` | **This file decides what a valid sample is.** Check the five thresholds, that every one is `median + n·MAD` and not mean ± SD, and that `isValid` is only ever narrowed, never widened |
| 2 | `code/dataModels/ValidSamplesModel.m` | `interpAndSmooth` | 1000 Hz grid, 4th-order Butterworth at 4 Hz with `filtfilt`, and the step that turns gaps longer than `interp_maxGap` back into NaN. This is where "the curve looks smooth but the mean is invented" comes from |
| 3 | same file | `analyze` + `getDefaultSettings` | the 12 per-segment statistics — see §4 below |
| 4 | `code/dataModels/PupilDataModel.m` | `filterRawData` → `processValidSamples` → `analyzeSegments` → `exportSegments` | the batch loop and the column layout of `04_all_segments.csv`; `analyzeSegments` is the only place that walks segments × subjects |

Skim only: `RawSamplesModel.m`, `RawFileModel.m` (mat file shape, `segmentData`), `plotData`
(desktop-only sanity check), `helperFunctions/plotSegments.m`.

Skip: `helperFunctions/FALLBACK/` and `LEGACY/` (shims for old MATLAB), `importEDF/` (Windows
mex files), `code/Examples/` (Eyelink and Tobii demos; neither is the YMTC path).

## 2 · Our layer: three stages, in data order (30 min)

| # | file | read | what you are checking |
|---|---|---|---|
| 1 | `code/ymtc/trk2csv.m` | the whole file, then `private/readTrk.m` → `private/labelSamples.m` → `private/checkTrk.m` | one csv row per sample; events attached to the **first sample at or after** their timestamp (~17 ms late); `run` counts `START` only, so a missing `START` gives run 0; nothing is repaired, everything is recorded |
| 2 | `code/ymtc/exportEvents.m` | the whole file | the same events, but with their own timestamp — this is the input of the marker table, and the reason `diff_s` is not biased by the sample grid |
| 3 | `code/ymtc/ymtcEventTable.m` | `readOrder` at the bottom first, then the main loop | how the trial order is picked (countdown-length match), where `condition` comes from (`Onset<cond>`), what `expected_*` and `diff_s` are, and why `run = ceil(trial/21)` needs `ymtcRunCheck` |
| 4 | `ymtcEventTableBatch.m` | structure only | the status per subject; `skipped_no_events` is a normal outcome, not an error |
| 5 | `ymtcRunCheck.m`, `ymtcTimingCheck.m`, `ymtcTrialWide.m` | the verdict lines | three independent checks; if one of them is green the assumption it guards holds |

## 3 · The seam between the two codebases (20 min)

Three things are only *conventions*, and all three are the first place a review goes wrong:

1. **the four segment definitions** live in `csv2kretmat.m`, which is **not in this repository**
   (see [04](04_our_code.md)). Until you have read that file, `countdown_SmoothSig_meanDiam` is an
   unverified claim, not a definition;
2. **the join key** `participant` + `run` + `trial`, and the row semantics of the merged table —
   a segment's statistics sit on the row of that segment's own start marker, and run-level rows
   have no `trial` at all ([02](02_column_dictionary.md) §H);
3. **the unit**: camera pixels, not millimetres. The paper's range filter (1.5–9) is mm and is
   overridden with a data-driven pixel range; comparing a diameter here with a published mm value
   is meaningless ([03](03_pupil_size_internals.md)).

## 4 · Where the statistics are

Five places, in the order they touch a number:

| # | where | what it computes | in this repository? |
|---|---|---|---|
| 1 | `rawDataFilter.m` — `madCalc`, `deviationCalculator` | median and MAD, the trend line the deviation filter compares against | yes |
| 2 | `ValidSamplesModel.analyze` | the 12 statistics per segment: `SmoothSig_{mean,min,max,missingDataPercent,sampleCount}` and `ValidSamples_{mean,min,max,validPercent,sampleCount}` + `segmentStart/End` | yes |
| 3 | `PupilDataModel.analyzeSegments` / `exportSegments` | loops the segments and writes them out; no arithmetic of its own | yes |
| 4 | `ymtcTrialQC.m` (data side) | the analysis plan's three rejection rules — R1/R2/R3 in [05](05_data_quality.md) | **no** |
| 5 | the lab's statistics scripts (Fretz) | the inferential layer: the numbers that end up in a figure or a test | **no** — add the entry point here once its location is confirmed |

Two traps that belong to the statistics, not to the filters:

- `ValidSamples_validPercent` is a **whole-recording** figure repeated on every row; the per-segment
  share is `SmoothSig_missingDataPercent`;
- `min` / `max` are single-sample statistics: one surviving artifact sets them. Read a mean next to
  `SmoothSig_missingDataPercent` and `ValidSamples_sampleCount`, never alone.

If you want to re-derive one number by hand: pick a segment row from `04_all_segments.csv`, take the
window from [02](02_column_dictionary.md) §B, and recompute the mean from the smooth signal
(`segments/<name>_leftpupil_segments.csv`). If your number and the table disagree, the segment
boundaries in `csv2kretmat.m` are where to look.

## 5 · A review pass that takes one afternoon

| step | time | done when |
|---|---|---|
| 0 · coordinate system (§0) | 10 min | you can name the eight output tables and their roles |
| 1 · upstream (§1) | 45–60 min | you can draw raw → valid → smooth → segment and say which file each arrow is |
| 2 · our layer (§2) | 30 min | you can describe one marker row end to end without opening a file |
| 3 · seam (§3) | 20 min | you have three questions written down for whoever owns the data side |
| 4 · statistics (§4) | 20 min | you know which of the 12 statistics are per-segment and which is per-recording |
| 5 · spot-check | 20 min | one cell of one table reproduced by hand, deliberately picking a row with missing data |

The five questions that are worth asking early, because no amount of reading here can answer them:
what exactly defines the four segments; which pixel range was used and why; whether the merge keeps
run-level rows; which of the analysis-side scripts are frozen; and where the Fretz statistics live.
