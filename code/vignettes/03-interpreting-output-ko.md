# 출력 읽기: 결과 표와 내보낸 CSV

[English](03-interpreting-output.md) · **한국어** · [中文](03-interpreting-output-zh.md)

이전: [네 가지 데이터 모델: 입력과 출력](02-data-models-ko.md) · 목차: [README](../README.md) · 다음: [설정과 보조 함수](04-settings-and-helpers-ko.md)

---

## `analyzeSegments`의 출력 표

객체마다 표 하나: **`segmentsTable`의 모든 열 뒤에 눈마다 10개 열이 오른쪽으로 붙는다.** 접두사는 `leftPupil_`, `rightPupil_`, `meanPupil_`. 우리 데이터는 동공이 하나라 `leftPupil_*`만 나온다.

| 열 (접두사 제외) | 단위 | 계산 방법 |
|---|---|---|
| `SmoothSig_meanDiam` | 원시 단위 | 구간 안 평활 신호의 평균 (`NaN` 제외) |
| `SmoothSig_minDiam` / `SmoothSig_maxDiam` | 원시 단위 | 구간 안 평활 신호의 최소 / 최대 |
| `SmoothSig_missingDataPercent` | % | `NaN` 개수 ÷ 구간 샘플 수 × 100 |
| `SmoothSig_sampleCount` | 개 | 구간 안 1000 Hz 샘플 전체 (**`NaN` 포함**) |
| `ValidSamples_meanDiam` | 원시 단위 | 구간 안 valid 원시 점의 평균 |
| `ValidSamples_minDiam` / `ValidSamples_maxDiam` | 원시 단위 | 구간 안 valid 원시 점의 최소 / 최대 |
| `ValidSamples_validPercent` | % | `validFraction × 100` — **기록 전체의 값이며 이 구간의 값이 아님** |
| `ValidSamples_sampleCount` | 개 | 구간 안 valid 원시 점의 수 |

구간은 반개구간이다: `[segmentStart, segmentEnd)`.

**행 전체가 `NaN`이 되는 경우:**
- 해당 구간의 `segmentStart` 또는 `segmentEnd` 자체가 `NaN`일 때(예: trk에 대응하는 이벤트가 없음).
- 구간 안에 평활 신호 샘플이 하나도 없을 때 → `SmoothSig_*` 전부 `NaN`.
- 구간 안에 valid 원시 점이 하나도 없을 때 → `ValidSamples_*` 전부 `NaN`.

표 머리에는 `VariableUnits`와 `VariableDescriptions`가 들어 있다(`PupilResults.Properties.VariableDescriptions`로 확인). **CSV로 저장하면 사라지므로** 열의 뜻은 [`../docs/02_column_dictionary.md`](../../docs/02_column_dictionary.md)를 보라.

## `exportSegments`가 쓰는 파일

```matlab
opts.Eyes         = {'left'};          % 'left' 'right' 'mean'; 기본값은 전부
opts.SegmentTypes = {'countdown'};     % segmentsTable에 segmentType 열이 있어야 함; 기본값은 전부
opts.NaNString    = 'NaN';             % 결측 표기; '' 이면 빈 칸
opts.ZScore       = false;             % true 이면 pupilDiameterZ 열 추가
hPupilData.exportSegments('out_folder', opts);
```

객체·눈마다 파일 하나. 이름은 `<확장자 뺀 원본 파일명>_<eye>pupil_segments.csv`, 예: `sub149_leftpupil_segments.csv`.

| 열 | 뜻 |
|---|---|
| `segmentName` | `segmentsTable.segmentName` |
| `segmentType` | `segmentsTable.segmentType`. 그 열이 없으면 비어 있음 |
| `segmentStart_s` | 구간 시작(초). 같은 구간의 모든 행에서 동일 |
| `tRel_s` | 샘플 시각 − 구간 시작(초). 0에서 시작 |
| `pupilDiameter_<unit>` | 평활된 직경, 소수 4자리. `NaN`은 `NaNString`으로 기록. 단위는 `diameterUnit`에서 오며 예: `pupilDiameter_px` |
| `gap_ms` | 위에서 설명한 `gap_ms`, 소수 1자리 |
| `pupilDiameterZ` | `ZScore=true`일 때만: (값 − 기록 전체 평균) ÷ 기록 전체 표준편차. 눈마다 **기록 전체**에서 한 번 계산(Leuchs 2017)하며 구간 안 z가 아님 |

한 행 = 1000 Hz 샘플 하나이므로 10초 구간은 약 10000행이다. 샘플이 없는 구간은 쓰지 않는다.

---

이전: [네 가지 데이터 모델: 입력과 출력](02-data-models-ko.md) · 목차: [README](../README.md) · 다음: [설정과 보조 함수](04-settings-and-helpers-ko.md)
