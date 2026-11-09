# 03 · Inside the pupil pipeline

EN: How a raw sample becomes a number: the three artifact filters, interpolation, the 4 Hz low-pass, and segmentation.
KO: 원시 샘플이 수치가 되기까지: 세 가지 아티팩트 필터, 보간, 4 Hz 저역 통과, 구간 분할.
ZH: 一个原始样本如何变成一个数字：三道伪影滤波、插值、4 Hz 低通、分段。

Applies to `pupil-size@645cbc6`. Line numbers are from that commit; if the file changes, this page changes with it.

The whole thing is four stages, in this order:

```
raw samples ──(1) validate──> valid mask ──(2) filter──> smoother mask
            ──(3) interpolate + low-pass──> 1000 Hz smooth signal
            ──(4) segment + summarise──> 04_all_segments.csv
```

## Stage 1–2 · What counts as a valid sample

`rawDataFilter.m` (main function, line 1) returns one logical vector: which raw samples
are valid. Everything downstream works on that vector; a sample it rejects never comes
back.

| step | function | what it rejects | settings (line) |
|---|---|---|---|
| 1 | `removeOutOfBounds` (197) | diameter outside `[PupilDiameter_Min, PupilDiameter_Max]` | 67–68 — defaults 1.5 / 9 (**mm**), we override with a data-driven px range |
| 2 | `madSpeedFilter` (229) | blinks: sample-to-sample speed above `median + n·MAD` | `dilationSpeedFilter_MadMultiplier = 16` (89), `maxGap_ms = 200` (93) |
| 2b | `expandGaps` (511) | the edges around each blink: 50 ms before and after gaps wider than 75 ms | `gapDetect_minWidth = 75`, `maxWidth = 2000`, `padding 50/50` (104–110) |
| 3 | `madDeviationFilter` (284) | points far from a smooth trend line: |`d − trend`| above `median + 16·MAD` | `residualsFilter_MadMultiplier = 16` (131) |
| 3b | `removeLoners` (440) | temporally isolated samples: islands narrower than 50 ms, separated by more than 40 ms | `islandFilter_islandSeperation_ms = 40`, `minIslandWidth_ms = 50` (76, 82) |

Two details worth knowing:

- The trend line is built by interpolating the valid samples, low-passing at 16 Hz and
  averaging over 4 passes (`residualsFilter_passes = 4`, line 125). The multi-pass loop is
  what lets a good sample that was rejected because bad neighbours dragged the trend line
  come back.
- Every threshold is `median + n × MAD`, never mean ± SD: a few huge artifacts would
  inflate an SD enough to hide themselves.

## Stage 3 · From valid samples to a smooth signal

`ValidSamplesModel.interpAndSmooth` (line 107). Three steps:

1. **Interpolate** the valid samples onto a regular 1000 Hz grid (`interp1 …, 'linear'`,
   lines 136–142). `interp_upsamplingFreq = 1000` (line 374).
2. **Low-pass** the interpolated signal: 4th-order Butterworth, cutoff 4 Hz, applied forward
   and backward (`filtfilt`, zero phase) so peaks are not shifted in time (lines 383–389,
   193 in `interpAndSmooth`).
3. **Re-mark long gaps as missing**: any stretch interpolated over more than
   `interp_maxGap = 250` ms is set back to NaN (line 193, setting at 392). This is why
   `SmoothSig_meanDiam` can be NaN even though the curve looks continuous, and why a 100 ms
   blink leaves no trace in the mean but a 300 ms one does.

The upsample is a grid, not new information: the tracker sampled at ~60 Hz, so the 1000 Hz
curve is an interpolation. Time resolution is still ~17 ms.

## Stage 4 · Segmentation and summary statistics

`PupilDataModel.analyzeSegments` (390) → `ValidSamplesModel.analyze` (203). The segments
themselves are defined in `csv2kretmat.m` (lines 185–220): `baseline` = 0.5 s before the
cue, `countdown` = cue → outcome, `preOutcome` = 2 s before the outcome, `postOutcome` =
2 s after it. `analyze` then fills the 12 statistics per segment — see
[02_column_dictionary.md](02_column_dictionary.md) §B.

The per-column descriptions you see in the code (`statsTable.Properties.VariableDescriptions`,
line 280) are the same text as the dictionary; `writetable` drops them, which is why the
dictionary exists as a separate page.

## Parameters we actually run with

| parameter | value | who sets it |
|---|---|---|
| range filter | data-driven px range (0.5–99.5 pct × 0.8 / 1.2) | `example_kret_pipeline.m:85–93` |
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
