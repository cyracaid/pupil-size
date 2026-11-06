# 시작하기: 파이프라인, 용어, 예제

[English](01-getting-started.md) · **한국어** · [中文](01-getting-started-zh.md)

목차: [README](../README.md) · 다음: [네 가지 데이터 모델: 입력과 출력](02-data-models-ko.md)

---

## 전체 흐름 한눈에 보기

```
시선추적기 원본 파일 (EDF / gazedata / trk …)
        │  변환기: 시선추적기마다 하나씩 (Examples/*/batchFileConverter_*.m)
        ▼
RawFileModel ──saveMatFile──▶  <name>.mat
                               ├ diameter      : t_ms, L, R (측정하지 않은 눈은 비워 둠)
                               ├ diameterUnit  : 'mm' / 'px' …
                               ├ zeroTime_ms   : 저장만 하고 패키지에서는 쓰지 않음
                               └ segmentsTable : segmentName, segmentStart, segmentEnd (+ 임의의 추가 열)
        │
        ▼  PupilDataModel.batchConstructor(...)        ← 파일마다 객체 하나
        │
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter
        │                    결과: 원시 샘플마다 isValid 플래그(true/false) 하나
        ▼
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth
        │                    결과: 1000 Hz 평활 신호  signal.t / pupilDiameter / gap_ms
        ▼
 (3) analyzeSegments()       ValidSamplesModel.analyze
        │                    결과: 구간마다 통계량 10개 (눈마다 한 세트)
        ├─▶ (4) exportSegments(folder, options)   구간별 연속 시간 곡선 → CSV
        └─▶ (5) plotData()                         육안 점검 (데스크톱 MATLAB 필요)
```

## 설계 요점

- **표시만 하고 덮어쓰지 않는다.** (1)은 샘플마다 `isValid`만 매기고, 원시 직경 `rawSample`은 그대로 남는다.
- **valid 샘플과 평활 신호는 다른 것이다.** (2)는 valid 샘플을 보간한 뒤 저역통과 필터를 적용한다. 공백이 너무 길면 메우지 않고 `NaN`으로 둔다. (3)에서 `SmoothSig_*`는 평활 신호의 통계, `ValidSamples_*`는 실제로 측정된 점의 통계이다.
- **모든 임계값은 `getDefaultSettings()`에 있다.** 알고리즘을 건드리지 않고 매개변수만 바꾼다.
- **객체마다 자기 설정을 가진다.** `settings.raw`는 필터링, `settings.valid`는 보간과 저역통과를 제어한다.
- **왼쪽, 오른쪽, 평균.** 데이터가 있는 눈을 각각 분석하고, 두 눈 모두 있으면 `mean` 동공을 추가한다.

## 용어

| 용어 | 뜻 | 위치 |
|---|---|---|
| raw sample (원시 샘플) | 시선추적기가 준 직경 점. 눈 깜빡임과 잡음 포함 | `RawSamplesModel.rawSample` |
| valid sample (유효 샘플) | 모든 아티팩트 필터를 통과한 원시 점 | `RawSamplesModel.isValid == true` |
| smooth signal (평활 신호) | valid 점을 1000 Hz로 선형 보간한 뒤 4차 저역통과 | `ValidSamplesModel.signal` |
| gap (공백) | 이웃한 두 valid 점 사이의 시간 간격(ms) | `signal.gap_ms` |
| segment (구간) | 분석할 시간 창. 이름과 시작/끝(**초 단위**)을 가짐 | `segmentsTable` |
| `validFraction` | 비어 있지 않은 원시 점 중 valid 점의 비율. **기록 전체** 기준이며 구간별이 아님 | `PupilDataModel.processValidSamples` |
| MAD | 중앙값 절대 편차. 임계값은 "k × MAD"로 표현 | `rawDataFilter` |

시간 단위: `t_ms`는 **밀리초**, `segmentStart`·`segmentEnd`·`signal.t`는 **초**이다.

## `Examples/`

| 폴더 | 데이터 | 파일 |
|---|---|---|
| `Dataset_1/` | SR-Research Eyelink, **동공 하나** | `batchFileConverter_Dataset1.m` (EDF → .mat), `main_Dataset1.m` (전체 파이프라인) |
| `Dataset_2/` | E-Prime + Tobii, **동공 둘** | `batchFileConverter_Dataset2.m` (.gazedata → .mat), `main_Dataset2.m` (전체 파이프라인) |

`main_Dataset1.m`은 (1)~(5)단계의 가장 짧은 시연이다. 데이터가 임의 단위라 `PupilDiameter_Max = inf`, `PupilDiameter_Min = 0.1`로 두고, 그림을 위해 `keepFilterData = true`로 한 뒤 `filterRawData`, `processValidSamples`, `analyzeSegments`를 호출하고 `vertcat(results{:})`로 합치고 마지막에 `plotData`를 부른다.
우리 YMTC 데이터는 Dataset_1과 같은 한 동공 경로를 따르며 변환기만 `ymtc/`의 `trk2csv`이다. 일괄 실행 스크립트는 `代码_matlab/example_kret_pipeline.m`(저장소 밖, 데이터 옆)이다.

---

목차: [README](../README.md) · 다음: [네 가지 데이터 모델: 입력과 출력](02-data-models-ko.md)
