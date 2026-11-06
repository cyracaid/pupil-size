# Settings and helper functions

**English** · [한국어](04-settings-and-helpers-ko.md) · [中文](04-settings-and-helpers-zh.md)

Previous: [Reading the output: result table and exported CSV](03-interpreting-output.md) · Index: [README](../README.md) · Next: [Troubleshooting, limitations, further reading](05-troubleshooting.md)

---

## Settings (change parameters here)

### `settings.raw` (from `rawDataFilter()`)

| Setting | Default | Effect |
|---|---|---|
| `PupilDiameter_Min` / `_Max` | 1.5 / 9 | range filter. **These defaults are millimetres**; pixel data must override them (`Examples/Dataset_1` uses 0.1 / inf) |
| `islandFilter_islandSeperation_ms` | 40 | how far from other samples counts as an "island" |
| `islandFilter_minIslandWidth_ms` | 50 | islands narrower than this are invalid |
| `dilationSpeedFilter_MadMultiplier` | 16 | speed above this many MADs is invalid (catches blink edges) |
| `dilationSpeedFilter_maxGap_ms` | 200 | speed is only computed when the sample spacing is below this |
| `gapDetect_minWidth` / `_maxWidth` | 75 / 2000 ms | how wide a missing stretch must be to count as a "gap" |
| `gapPadding_backward` / `_forward` | 50 / 50 ms | extra samples rejected before/after a gap |
| `residualsFilter_passes` | 4 | number of passes of the trend-deviation filter |
| `residualsFilter_MadMultiplier` | 16 | deviation above this many MADs from the trend is invalid |
| `residualsFilter_interpFs` / `_lowpassCF` | 100 Hz / 16 Hz | resampling rate and cutoff used to build the trend line |
| `keepFilterData` | `true` | keep intermediate filter results. **Uses memory**; set `false` after tuning |

### `settings.valid` (from `ValidSamplesModel.getDefaultSettings()`)

| Setting | Default | Effect |
|---|---|---|
| `interp_upsamplingFreq` | 1000 Hz | sampling rate of the smooth signal |
| `LpFilt_B` / `LpFilt_A` | from order 4, cutoff 4 Hz | low-pass coefficients (zero-phase `filtfilt`) |
| `interp_maxGap` | 250 ms | if the distance between real valid points exceeds this, the smooth signal there becomes `NaN` |

## `helperFunctions/`

| File | What it does |
|---|---|
| `rawDataFilter.m` | The main function calls `removeOutOfBounds` (range) → `madSpeedFilter` (speed, catches blinks) → `madDeviationFilter` (deviation from trend). Isolated-point cleanup `removeLoners` is called repeatedly inside all three, `expandGaps` (reject around gaps) inside the speed filter; `madCalc` computes MAD thresholds. With no arguments it returns the default settings |
| `genMeanDiaSamples.m` | combines two eyes into one mean diameter; called by `processValidSamples`; unused for one-eye data |
| `plotSegments.m` | draws the segment table as colour patches; called by `plotData` |
| `printToConsole.m` | progress messages, internal |
| `legacyModeCheck.m` | adds `LEGACY/` to the path for MATLAB older than 8.3 (no `table`); does nothing on newer versions |
| `FALLBACK/` | replacements for `butter`, `filtfilt`, `histc`, `nanmin` / `nanmax` / `nanmean` / `nanmedian`, for MATLAB without the toolbox or with the function removed |
| `LEGACY/` | emulates `table` for very old MATLAB |

**FALLBACK trap:** `addpath(genpath(...))` puts folders at the **front** of the path, so a FALLBACK function shadows the real toolbox function of the same name. Use `addpath(..., '-end')` to prefer the toolbox. This machine's MATLAB has no Statistics toolbox, so the `nan*` functions come from FALLBACK.

---

Previous: [Reading the output: result table and exported CSV](03-interpreting-output.md) · Index: [README](../README.md) · Next: [Troubleshooting, limitations, further reading](05-troubleshooting.md)
