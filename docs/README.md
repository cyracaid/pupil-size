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
| [Review map](reference.html#9-review-map-what-to-read-and-in-what-order) | the files a reviewer must read, in order, with time estimates | in the reference, §9 |
| [`06_faq.md`](06_faq.md) / [`zh/06_常见问题.md`](zh/06_常见问题.md) | the traps that bite most often | **done** |
| [`07_roadmap.md`](07_roadmap.md) / [`zh/07_路线图.md`](zh/07_路线图.md) | what is done, what is next, which decisions are still open — and where each item shows | **living** |

## How to look something up

1. You have a number and want to know what it is → `02`, find the column name.
2. You have a column and want to know how it was computed → `02` gives the formula and the
   file; `03` gives the algorithm behind it.
3. You want to know where a file comes from → the diagram at the top of `02`.
4. You want the per-column detail of a *sampling-level* table (the 21-column sample CSV, the QC
   and issues tables) → [the reference page](https://cyracaid.github.io/pupil-size/reference.html);
   `02` deliberately covers the analysis tables only.

## Keeping this honest

`checkDocs.m` carries its **own** list of expected columns and compares it with the header of
every output CSV. Note what that does and does not buy you: the list lives in the `.m` file, not
in `02`. If a table gains a column and `checkDocs.m` is updated but this folder is not, the check
passes and `02` silently ages. So a table change means three edits in one commit — the pipeline,
`checkDocs.m`, and `02` — and the check only enforces the first two.

`02` and `03` state the commit they were verified against; pages 01, 04, 05 and 06 are about
whatever `HEAD` of this branch is. Last full verification: 2026-11-09, `e1b0aa0`.

`tools/check_docs.py` (run by the Pages workflow before every build, stdlib only) checks the
half that `checkDocs.m` cannot, because it never opens these files: that every relative link
resolves, that every output file named here is one the reference table list actually produces,
that a column count in the prose agrees with that list, and that every page is registered in
`build_site.py`. Run it locally after editing this folder:

```bash
python3 tools/check_docs.py
```

The site at <https://cyracaid.github.io/pupil-size/> is built from this folder by `.github/workflows/pages.yml` on every push that touches `docs/` or `tools/`.
