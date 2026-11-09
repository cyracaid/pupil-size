# Documentation

EN: Start here. `01` is the pipeline in one page, `02` is the column dictionary, `03` is how the pupil numbers are computed.
KO: 여기서 시작하십시오. `01` 파이프라인 개요, `02` 열 사전, `03` 눈동자 수치 계산법.
ZH: 从这里开始。`01` 一页看懂流水线，`02` 列字典，`03` 瞳孔数字怎么算出来。

| page | what it answers | state |
|---|---|---|
| [`02_column_dictionary.md`](02_column_dictionary.md) | every column of every output table: meaning, formula, unit, source | **done** |
| [`zh/02_列字典.md`](zh/02_列字典.md) | 同上，中文全文 | **done** |
| [`01_pipeline_overview.md`](01_pipeline_overview.md) / [`zh/01_流程总览.md`](zh/01_流程总览.md) | the five layers and what flows between them | **done** |
| [`03_pupil_size_internals.md`](03_pupil_size_internals.md) / [`zh/03_瞳孔算法.md`](zh/03_瞳孔算法.md) | the three artifact filters, interpolation, 4 Hz low-pass, segmentation | **done** |
| [`04_our_code.md`](04_our_code.md) / [`zh/04_我们的代码.md`](zh/04_我们的代码.md) | what is in this repository, what stays with the data, and where the two meet | **done** |
| [`05_data_quality.md`](05_data_quality.md) / [`zh/05_数据质量.md`](zh/05_数据质量.md) | missing-data structure, rejection rules, threshold sensitivity | **done** |
| [`06_faq.md`](06_faq.md) / [`zh/06_常见问题.md`](zh/06_常见问题.md) | the traps that bite most often | **done** |

## How to look something up

1. You have a number and want to know what it is → `02`, find the column name.
2. You have a column and want to know how it was computed → `02` gives the formula and the
   file; `03` (once written) gives the algorithm behind it.
3. You want to know where a file comes from → the diagram at the top of `02`.

## Keeping this honest

Every page states the commit it was written against. `checkDocs.m` compares the column
names listed in `02` with the header of every output CSV, so a pipeline change that adds or
drops a column fails the check instead of silently ageing the documentation.

The site at <https://cyracaid.github.io/pupil-size/> is built from this folder by `.github/workflows/pages.yml` on every push that touches `docs/` or `tools/`.
