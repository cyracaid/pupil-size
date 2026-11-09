# 08 · Roadmap and to-do

EN: What is done, what is next, and what is still an open decision — each item placed where it is visible in the repository.
KO: 무엇이 끝났고, 다음이 무엇이며, 무엇이 아직 결정 대기인지 — 각 항목이 저장소 어디에 보이는지와 함께.
ZH: 什么做完了、下一步是什么、哪些还等决定 —— 每条都标出它在仓库里的可见位置。

Status legend: **done** shipped and used · **next** agreed, not done · **open** needs a decision ·
**blocked** needs something outside this repository.

This is the *to-do* page. The order to read the code in is a different page: [07 · Reading path](07_reading_path.md).

## 1. Done

| item | where it is visible |
|---|---|
| `.trk` → one per-sample csv, anomalies recorded, never repaired | `code/ymtc/trk2csv.m`, `trk2csv_batch.m` |
| the event timeline `03_events/<sub>_events.csv` with exact event times | `code/ymtc/exportEvents.m`, [01](01_pipeline_overview.md) §Layer 3 |
| the marker table, its batch run, the run check | `ymtcEventTable.m`, `ymtcEventTableBatch.m`, `ymtcRunCheck.m` |
| one row per trial, and `diff_s` per subject × marker | `ymtcTrialWide.m`, `ymtcTimingCheck.m` |
| six guide pages in EN and ZH, plus the one-page reference | this folder, `tools/build_readme.py` |
| the docs check in CI (links, output names, column counts, page registration) | `tools/check_docs.py`, `.github/workflows/pages.yml` |
| a test suite that runs with base MATLAB, no toolboxes | `code/ymtc/tests/`, 12 tests |

## 2. Next

| item | why | where it shows |
|---|---|---|
| `checkDocs.m` should read `02` instead of a hard-kept copy | today it cannot notice that the page fell behind | [02](02_column_dictionary.md) §J |
| settle the merged table's row semantics (372 = every event row with NaN stats, or 360 = run-level rows dropped) | the number is not derivable from this repository | [02](02_column_dictionary.md) §H |
| re-measure the countdown range in `05` §4 | the old `13–31 s` could not be reproduced from anything here | [05](05_data_quality.md) |
| a second sensitivity column at 40% | the current evidence only relaxes the threshold in one direction | [05](05_data_quality.md) §3 |
| Korean guide pages, or an explicit statement that only the reference is translated | the switcher has a Korean entry that leads home | `tools/build_site.py` |
| MATLAB tests in CI | GitHub's runners have no MATLAB; it needs a self-hosted runner or a licence | `.github/workflows/pages.yml` |

## 3. Open decisions

| decision | the options | cost of each |
|---|---|---|
| where `03_events` is produced | in this repository (`exportEvents`, reproducible from a clone) or on the data side (keeps the analysis layer together) | in-repo needs the file kept in step with `ymtcEventTable`'s expectations |
| how `checkDocs` learns the schema | `<!-- cols: … -->` anchors in `02` that it parses, or the current hand-kept list plus a review rule | the anchor route is ~20 lines and removes the class of drift entirely |
| Korean | translate six guides, or keep one line per page plus the Korean reference | six pages × two languages to maintain on every change |

## 4. Analysis side — exists with the data, not in this repository

These are real files that `04` lists as living next to the study data; none of them is in this
repository, and none is documented here beyond its one-line role:

- `csv2kretmat.m`, `example_kret_pipeline.m` — the Kret adapter and batch script;
- `ymtcTrialQC.m`, `ymtcMergeResults.m` — the analysis plan's rules and the merge;
- `ymtcManipulationCheck.m` — joins the rows of one trial and runs the manipulation check; it runs, its numbers are not recorded yet;
- `ymtcFilterPlots.m` — filter diagnostics, writes PNG;
- `ymtc_param_sensitivity.m` — analysis-side script. (`ymtcLayer1Bins.m` / `ymtcMergeConditions.m` were deleted on 2026-11-10.)

**To fill in**: which of these are finished, which feed which figure, and the order they run in.
This page deliberately leaves that blank — a roadmap invented here would be the one part of this
documentation not checked against anything.
