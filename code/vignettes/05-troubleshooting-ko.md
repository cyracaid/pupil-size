# 문제 해결, 한계, 더 읽을 거리

[English](05-troubleshooting.md) · **한국어** · [中文](05-troubleshooting-zh.md)

이전: [설정과 보조 함수](04-settings-and-helpers-ko.md) · 목차: [README](../README.md)

---

## 문제 해결: 증상 → 원인 → 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| `'t_ms' must be sorted!` | 타임스탬프가 오름차순이 아님 (trk의 중복·역행 타임스탬프) | 변환기에서 정렬한다. 패키지 안에서 고치지 말고, 중복은 따로 기록 |
| `'L' must be empty, or have the same length as 't_ms'` | 직경 벡터와 시간 벡터 길이가 다름 | 변환기에서 길이 확인 |
| `No settings present.` | `settings` 없이 `PupilDataModel`을 만듦 | `PupilDataModel.getDefaultSettings()`로 받아서 수정 |
| `Interpolation cannot be performed.` | 그 눈의 valid 점이 2개 미만 (범위 오설정이거나 전부 잡음) | `PupilDiameter_Min/Max`가 단위에 맞는지 확인 |
| 거의 모든 샘플이 무효 | 기본 범위 1.5–9는 mm 기준이라 픽셀 데이터가 범위 밖 | 실제 단위로 범위 설정 |
| 경고 `pupilSize:edgeClamp` | 부동소수점 오차로 업샘플 시각이 valid 범위 밖에 놓여 경계로 보정됨 | 알림일 뿐. 개수가 많을 때만 데이터를 조사 |
| `ValidSamples_validPercent`가 모든 행에서 같음 | 설계상 기록 전체 값 | 구간별 결측은 `SmoothSig_missingDataPercent`로 |
| `SmoothSig_meanDiam`은 멀쩡해 보이는데 데이터는 나쁨 | 250 ms 미만 공백이 보간으로 메워짐 | `missingDataPercent`와 `ValidSamples_sampleCount`도 함께 본다 |
| `plotData`가 반응 없음/건너뜀 | `-batch`에는 데스크톱이 없음 | 데스크톱 MATLAB에서 실행 |
| `plotData`가 파일 하나만 그림 | 소스에 `plotMultipleFiles = false` (무거움) | `PupilDataModel.m`에서 그 스위치를 바꿈 |
| `Examples`에서 `addpath` 실패 | 경로가 Windows 역슬래시 `..\..\helperFunctions\`로 적혀 있음 | macOS / Linux에서는 `../../helperFunctions/` |

## 한계

- 원본 README는 Signal Processing과 Statistics 툴박스를 요구하며, Windows 7의 MATLAB 2012b / 2016a / 2017a에서 테스트했다고 적혀 있다. 이 저장소는 macOS용으로 패치했다(`PupilDataModel`의 경로 구분자, `FALLBACK/`). 변경은 `git log` 참조. 일괄 실행 스크립트 `代码_matlab/example_kret_pipeline.m`은 저장소 밖에 있다.
- 필터 매개변수는 논문 기본값이며 **YMTC 데이터에 맞춰 조정하지 않았다.** 조정하려면 데스크톱 MATLAB에서 `plotData()`로 원시 궤적을 봐야 한다.
- 이 문서는 코드가 무엇을 하는지만 설명하며 결과가 좋은지는 판단하지 않는다. 데이터 품질은 [`../docs/05_data_quality.md`](../../docs/05_data_quality.md)를 보라.

## 더 읽을 거리

[`../docs/01_pipeline_overview.md`](../../docs/01_pipeline_overview.md) (파이프라인 한 페이지) · [`../docs/02_column_dictionary.md`](../../docs/02_column_dictionary.md) (모든 열) · [`../docs/03_pupil_size_internals.md`](../../docs/03_pupil_size_internals.md) (필터와 보간) · [`ymtc/README.md`](../ymtc/README.md), [`../docs/04_our_code.md`](../../docs/04_our_code.md) (우리 코드) · [`../docs/06_faq.md`](../../docs/06_faq.md).

Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.

---

이전: [설정과 보조 함수](04-settings-and-helpers-ko.md) · 목차: [README](../README.md)
