# code/ — the original pupil-size code · 원본 pupil-size 코드 · 原版 pupil-size 代码

EN: A guide to the original Kret & Sjak-Shie (2019) MATLAB code, split into five short vignettes, each in English, Korean and Chinese. Our own YMTC code is in [`ymtc/`](ymtc/README.md).
KO: Kret & Sjak-Shie (2019) 원본 MATLAB 코드 안내. 짧은 비네트 다섯 편으로 나누고 각각 영어·한국어·중국어로 썼다. 우리가 추가한 YMTC 코드는 [`ymtc/`](ymtc/README.md)에 있다.
ZH: Kret & Sjak-Shie (2019) 原版 MATLAB 代码的说明，拆成五篇短 vignette，每篇有英、韩、中三个版本。我们自己加的 YMTC 代码在 [`ymtc/`](ymtc/README.md)。

Every statement was written against the source; file and function names are given so you can check. / 모든 내용은 소스를 대조해 작성했고 확인용으로 파일·함수 이름을 적었다. / 每一条都对照源码写成，并给出文件和函数名方便核对。

## Vignettes · 비네트 · Vignette 列表

| # | English | 한국어 | 中文 | What it answers |
|---|---|---|---|---|
| 1 | [Getting started](vignettes/01-getting-started.md) | [시작하기](vignettes/01-getting-started-ko.md) | [上手](vignettes/01-getting-started-zh.md) | Pipeline at a glance, design points, terms, the two official examples |
| 2 | [Data models](vignettes/02-data-models.md) | [데이터 모델](vignettes/02-data-models-ko.md) | [数据模型](vignettes/02-data-models-zh.md) | Input, output and errors of `RawFileModel`, `PupilDataModel`, `RawSamplesModel`, `ValidSamplesModel` |
| 3 | [Interpreting output](vignettes/03-interpreting-output.md) | [출력 읽기](vignettes/03-interpreting-output-ko.md) | [读懂输出](vignettes/03-interpreting-output-zh.md) | The `analyzeSegments` table (10 columns per eye) and the `exportSegments` CSV |
| 4 | [Settings and helpers](vignettes/04-settings-and-helpers.md) | [설정과 보조 함수](vignettes/04-settings-and-helpers-ko.md) | [设置项与辅助函数](vignettes/04-settings-and-helpers-zh.md) | Every default threshold, and what each file in `helperFunctions/` does |
| 5 | [Troubleshooting](vignettes/05-troubleshooting.md) | [문제 해결](vignettes/05-troubleshooting-ko.md) | [排错](vignettes/05-troubleshooting-zh.md) | Symptom → cause → fix, limitations, further reading |

## Where to start · 어디서 시작할까 · 从哪里开始

- You want the big picture → vignette 1. / 전체 그림 → 1번. / 想先看全貌 → 第 1 篇。
- You have a result table and want to know what a column is → vignette 3. / 결과 표의 열이 무엇인지 → 3번. / 手上有结果表想知道某列是什么 → 第 3 篇。
- A number looks wrong or the code errors → vignette 5. / 숫자가 이상하거나 오류가 날 때 → 5번. / 数字不对或代码报错 → 第 5 篇。

Related pages in the repository / 저장소의 관련 문서 / 仓库里的相关页面:
[`../docs/01_pipeline_overview.md`](../docs/01_pipeline_overview.md) ·
[`../docs/02_column_dictionary.md`](../docs/02_column_dictionary.md) ·
[`../docs/03_pupil_size_internals.md`](../docs/03_pupil_size_internals.md) ·
[`../docs/05_data_quality.md`](../docs/05_data_quality.md) ·
[`../docs/06_faq.md`](../docs/06_faq.md)

Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.
