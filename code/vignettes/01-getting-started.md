# Getting started: the pipeline, terms, examples

**English** · [한국어](01-getting-started-ko.md) · [中文](01-getting-started-zh.md)

Index: [README](../README.md) · Next: [The four data models: inputs and outputs](02-data-models.md)

---

## The pipeline at a glance

```
Eye-tracker raw file (EDF / gazedata / trk …)
        │  converter: one per eye tracker (Examples/*/batchFileConverter_*.m)
        ▼
RawFileModel ──saveMatFile──▶  <name>.mat
                               ├ diameter      : t_ms, L, R (leave the unmeasured eye empty)
                               ├ diameterUnit  : 'mm' / 'px' …
                               ├ zeroTime_ms   : stored only, not used by the package
                               └ segmentsTable : segmentName, segmentStart, segmentEnd (+ any extra columns)
        │
        ▼  PupilDataModel.batchConstructor(...)        ← one object per file
        │
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter
        │                    gives: one isValid flag (true/false) per raw sample
        ▼
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth
        │                    gives: 1000 Hz smooth signal  signal.t / pupilDiameter / gap_ms
        ▼
 (3) analyzeSegments()       ValidSamplesModel.analyze
        │                    gives: 10 statistics per segment (one set per eye)
        ├─▶ (4) exportSegments(folder, options)   continuous time course of every segment → CSV
        └─▶ (5) plotData()                         visual check (needs desktop MATLAB)
```

## Design points

- **Flag, never overwrite.** Step (1) only sets `isValid` per sample; the raw diameter `rawSample` is always kept.
- **Valid samples and the smooth signal are different things.** Step (2) interpolates and low-passes the valid samples; where a gap is too long it sets `NaN` instead of filling. In step (3), `SmoothSig_*` describes the smooth signal and `ValidSamples_*` describes the points that were really measured.
- **Every threshold lives in `getDefaultSettings()`.** Change parameters without touching the algorithm.
- **Each object carries its own settings.** `settings.raw` drives filtering; `settings.valid` drives interpolation and the low-pass.
- **Left, right and mean.** Whichever eye has data is analysed; if both have data a `mean` pupil is added.

## Terminology

| Term | Meaning | Where |
|---|---|---|
| raw sample | a diameter point as the eye tracker gave it, blinks and noise included | `RawSamplesModel.rawSample` |
| valid sample | a raw point that passed every artifact filter | `RawSamplesModel.isValid == true` |
| smooth signal | valid points linearly interpolated to 1000 Hz, then 4th-order low-pass | `ValidSamplesModel.signal` |
| gap | time between two neighbouring valid points (ms) | `signal.gap_ms` |
| segment | a time window to analyse, with a name and start/end (**in seconds**) | `segmentsTable` |
| `validFraction` | valid points over non-empty raw points for the **whole recording**, not per segment | `PupilDataModel.processValidSamples` |
| MAD | median absolute deviation; thresholds are written as "k × MAD" | `rawDataFilter` |

Time units: `t_ms` is in **milliseconds**; `segmentStart`, `segmentEnd` and `signal.t` are in **seconds**.

## `Examples/`

| Folder | Data | Files |
|---|---|---|
| `Dataset_1/` | SR-Research Eyelink, **one pupil** | `batchFileConverter_Dataset1.m` (EDF → .mat), `main_Dataset1.m` (full pipeline) |
| `Dataset_2/` | E-Prime + Tobii, **two pupils** | `batchFileConverter_Dataset2.m` (.gazedata → .mat), `main_Dataset2.m` (full pipeline) |

`main_Dataset1.m` is the shortest demonstration of steps (1)–(5): it sets `PupilDiameter_Max = inf` and `PupilDiameter_Min = 0.1` (the data is in arbitrary units), `keepFilterData = true` for plotting, then calls `filterRawData`, `processValidSamples`, `analyzeSegments`, joins with `vertcat(results{:})`, and finally `plotData`.
Our YMTC data follows the same one-pupil route as Dataset_1, with `trk2csv` from `ymtc/` as the converter; the batch script is `代码_matlab/example_kret_pipeline.m` (outside this repository, next to the data).

---

Index: [README](../README.md) · Next: [The four data models: inputs and outputs](02-data-models.md)
