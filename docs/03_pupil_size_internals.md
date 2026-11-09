# 03 · Inside the pupil pipeline

EN: How a raw sample becomes a number: the three artifact filters, interpolation, the 4 Hz low-pass, and segmentation.
KO: 원시 샘플이 수치가 되기까지: 세 가지 아티팩트 필터, 보간, 4 Hz 저역 통과, 구간 분할.
ZH: 一个原始样本如何变成一个数字：三道伪影滤波、插值、4 Hz 低通、分段。

Verified against `ymtc-trk2csv@15b86d2` (2026-11-10), upstream files included. This page cites
**function names and setting names, not line numbers**: the upstream files gained a three-line
header once already, which moved every line number by three and quietly invalidated the old
references. Names survive that; there is no numeric anchor left on this page to rot.

Which file, which symbol:

| symbol | file |
|---|---|
| three artifact filters | `code/helperFunctions/rawDataFilter.m` |
| interpolate / low-pass / per-segment stats | `code/dataModels/ValidSamplesModel.m` |
| segment loop and export | `code/dataModels/PupilDataModel.m` |
| the four segment definitions | `csv2kretmat.m` (with the data, not in this repository) |

The whole thing is four stages, in this order:

```
raw samples ──(1) validate──> valid mask ──(2) filter──> smoother mask
            ──(3) interpolate + low-pass──> 1000 Hz smooth signal
            ──(4) segment + summarise──> 04_all_segments.csv
```

## Stage 1–2 · What counts as a valid sample

`rawDataFilter.m` (main function on its first line) returns one logical vector: which raw samples
are valid. Everything downstream works on that vector; a sample it rejects never comes back.

Every setting below is a field of the `rawFiltSettings` struct that `getDefaultSettings` fills in,
so the name is enough to find it in the file:

| step | function | what it rejects | settings |
|---|---|---|---|
| 1 | `removeOutOfBounds` | diameter outside `[PupilDiameter_Min, PupilDiameter_Max]` | defaults 1.5 / 9 (**mm**), we override with a data-driven px range |
| 2 | `madSpeedFilter` | blinks: sample-to-sample speed above `median + n·MAD` | `dilationSpeedFilter_MadMultiplier = 16`, `dilationSpeedFilter_maxGap_ms = 200` |
| 2b | `expandGaps` | the edges around each blink: 50 ms before and after gaps wider than 75 ms | `gapDetect_minWidth = 75`, `gapDetect_maxWidth = 2000`, padding 50/50 |
| 3 | `madDeviationFilter` | points far from a smooth trend line: `abs(d - trend)` above `median + 16·MAD` | `residualsFilter_MadMultiplier = 16` |
| 3b | `removeLoners` | temporally isolated samples: islands narrower than 50 ms, separated by more than 40 ms | `islandFilter_islandSeperation_ms = 40`, `islandFilter_minIslandWidth_ms = 50` |

Two details worth knowing:

- The trend line is built by interpolating the valid samples, low-passing at 16 Hz and
  averaging over 4 passes (`residualsFilter_passes = 4`). The multi-pass loop is what lets a good
  sample that was rejected because bad neighbours dragged the trend line come back.
- Every threshold is `median + n × MAD`, never mean ± SD: a few huge artifacts would
  inflate an SD enough to hide themselves.

## Stage 3 · From valid samples to a smooth signal

`ValidSamplesModel.interpAndSmooth`. Three steps:

1. **Interpolate** the valid samples onto a regular 1000 Hz grid (`interp1 …, 'linear'`, the
   block that assigns `diaInterp`). `interp_upsamplingFreq = 1000` in `getDefaultSettings`.
2. **Low-pass** the interpolated signal: 4th-order Butterworth, cutoff 4 Hz, applied forward
   and backward (`filtfilt`, zero phase) so peaks are not shifted in time.
3. **Re-mark long gaps as missing**: any stretch interpolated over more than
   `interp_maxGap = 250` ms is set back to NaN (the line `diaInterp(gaps_ms > …) = NaN`). This is
   why `SmoothSig_meanDiam` can be NaN even though the curve looks continuous, and why a 100 ms
   blink leaves no trace in the mean but a 300 ms one does.

The upsample is a grid, not new information: the tracker sampled at ~60 Hz, so the 1000 Hz
curve is an interpolation. Time resolution is still ~17 ms.

## Stage 4 · Segmentation and summary statistics

`PupilDataModel.analyzeSegments` → `ValidSamplesModel.analyze`. The segments themselves are
defined in `csv2kretmat.m` (the block that sets `segmentType`): `baseline` = 0.5 s before the cue,
`countdown` = cue → outcome, `preOutcome` = 2 s before the outcome, `postOutcome` = 2 s after it.
`analyze` then fills the 12 statistics per segment — see
[02_column_dictionary.md](02_column_dictionary.md) §B.

The per-column descriptions you see in the code (`statsTable.Properties.VariableDescriptions` in
`analyze`) are the same text as the dictionary; `writetable` drops them, which is why the
dictionary exists as a separate page.

## Parameters we actually run with

| parameter | value | who sets it |
|---|---|---|
| range filter | data-driven px range (0.5–99.5 pct × 0.8 / 1.2) | `example_kret_pipeline.m` (with the data) |
| speed filter | 16 MAD, 200 ms max gap | paper defaults |
| blink edges | 75–2000 ms gaps, 50 ms padding | paper defaults |
| trend filter | 16 MAD, 4 passes, 16 Hz trendline | paper defaults |
| island filter | 40 / 50 ms | paper defaults |
| interpolation | 1000 Hz, linear | paper defaults |
| low-pass | 4 Hz, 4th order, zero phase | paper defaults |
| missing threshold | 250 ms | paper defaults |

Only the range filter is adapted, and it has to be: the paper's 1.5–9 are millimetres, our
data are camera pixels.

## What this means for the numbers

- **A rejected sample is gone.** Nothing downstream can undo it; `SmoothSig` interpolates
  *over* it, so a segment with many rejections looks smooth but is mostly invented. Read
  `SmoothSig_missingDataPercent` before trusting a mean.
- **The filters run per eye, per recording**, not per trial. A bad stretch of three minutes
  shifts the MAD estimate for the whole file, so trial-level quality is not independent of
  recording-level quality.
- **Nothing is tuned to YMTC.** All values are Kret & Sjak-Shie defaults; the only way to
  set them knowing what they do is `plotData()` in desktop MATLAB, which `-batch` runs skip.
