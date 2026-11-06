# The four data models: inputs and outputs

**English** · [한국어](02-data-models-ko.md) · [中文](02-data-models-zh.md)

Previous: [Getting started: the pipeline, terms, examples](01-getting-started.md) · Index: [README](../README.md) · Next: [Reading the output: result table and exported CSV](03-interpreting-output.md)

---

## Input and output of the four classes

### `RawFileModel` — writes the .mat

```matlab
obj = RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename);
% or construct first, then obj.saveMatFile('x.mat')
```

Input checks (a failed check stops with an `assert` error):
- `diameter` must have the fields `t_ms`, `L`, `R`. `L` or `R` may be empty (eye not measured); if not empty its length must equal `t_ms`.
- `t_ms` must be sorted ascending (`issorted`). It should start at 0.
- `segmentsTable` needs `segmentStart`, `segmentEnd`, `segmentName`. Any other columns (condition, file name …) are carried into the result table unchanged.

Output: one `.mat` with four variables: `diameter`, `diameterUnit`, `zeroTime_ms`, `segmentsTable`.

### `PupilDataModel` — the conductor

| Method | Input | Output | Console message |
|---|---|---|---|
| `PupilDataModel.batchConstructor(folder, dirStruct, settings)` | folder, result of `dir('*.mat')`, settings | array of `PupilDataModel` objects | `Constructing N Data Objects...` / `File i (name): Object constructed.` |
| `filterRawData()` | — | `isValid` stored on each eye | `Filtering the raw data in N files...` |
| `processValidSamples()` | — | `leftPupil_ValidSamples`, `rightPupil_ValidSamples`, plus `meanPupil_ValidSamples` when both eyes exist | `Interpolating and smooting the valid raw data subsets of N files...` |
| `analyzeSegments()` | — | a **cell array**, one result table per object; join with `vertcat(results{:})` | `File i (name): analyzing K segments.` |
| `exportSegments(folder, options)` | output folder, optional options | one CSV per object per eye ([03](03-interpreting-output.md)) | `File i (name) left pupil: wrote N samples to <file>` |
| `plotData()` | — | figure window | — |

Call order is fixed: `processValidSamples` needs `isValid`, `analyzeSegments` needs the smooth signal.

### `RawSamplesModel` — raw samples of one eye

- Properties: `rawSample`, `isValid` (logical vector), `speedFiltData`, `devFiltData` (intermediate filter results, stored only when `keepFilterData=true`).
- Settings: `settings.raw`, defaults from `rawDataFilter()` (called with no arguments it returns the settings struct).

### `ValidSamplesModel` — valid samples of one eye

- Input: `t_ms` and `pupilDiameter` of the valid points, and `validFraction`. Interpolation and low-pass run automatically in the constructor.
- Fewer than 2 valid points raises `Interpolation cannot be performed.`
- Output: a `signal` struct with three equal-length vectors:

| Field | Unit | Meaning |
|---|---|---|
| `t` | s | 1000 Hz time axis |
| `pupilDiameter` | raw unit | smoothed diameter; `NaN` where the gap exceeds `interp_maxGap` |
| `gap_ms` | ms | distance between the two **real valid points** around this instant; 0 if within 0.5 ms (half an upsampling period) of a real point |

---

Previous: [Getting started: the pipeline, terms, examples](01-getting-started.md) · Index: [README](../README.md) · Next: [Reading the output: result table and exported CSV](03-interpreting-output.md)
