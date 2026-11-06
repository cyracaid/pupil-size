# 네 가지 데이터 모델: 입력과 출력

[English](02-data-models.md) · **한국어** · [中文](02-data-models-zh.md)

이전: [시작하기: 파이프라인, 용어, 예제](01-getting-started-ko.md) · 목차: [README](../README.md) · 다음: [출력 읽기: 결과 표와 내보낸 CSV](03-interpreting-output-ko.md)

---

## 네 클래스의 입력과 출력

### `RawFileModel` — .mat 저장

```matlab
obj = RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename);
% 또는 먼저 생성한 뒤 obj.saveMatFile('x.mat')
```

입력 검사 (통과하지 못하면 `assert` 오류로 멈춤):
- `diameter`에는 `t_ms`, `L`, `R` 필드가 있어야 한다. `L` 또는 `R`은 비어 있어도 된다(그 눈을 측정하지 않음). 비어 있지 않으면 길이가 `t_ms`와 같아야 한다.
- `t_ms`는 오름차순이어야 한다(`issorted`). 0에서 시작하도록 권장한다.
- `segmentsTable`에는 `segmentStart`, `segmentEnd`, `segmentName`이 필요하다. 그 밖의 열(조건, 파일명 등)은 결과 표에 그대로 따라간다.

출력: `diameter`, `diameterUnit`, `zeroTime_ms`, `segmentsTable` 네 변수가 든 `.mat` 하나.

### `PupilDataModel` — 총괄

| 메서드 | 입력 | 출력 | 콘솔 메시지 |
|---|---|---|---|
| `PupilDataModel.batchConstructor(folder, dirStruct, settings)` | 폴더, `dir('*.mat')` 결과, 설정 | `PupilDataModel` 객체 배열 | `Constructing N Data Objects...` / `File i (name): Object constructed.` |
| `filterRawData()` | — | 각 눈에 `isValid` 저장 | `Filtering the raw data in N files...` |
| `processValidSamples()` | — | `leftPupil_ValidSamples`, `rightPupil_ValidSamples`, 두 눈이 모두 있으면 `meanPupil_ValidSamples`도 | `Interpolating and smooting the valid raw data subsets of N files...` |
| `analyzeSegments()` | — | **cell 배열**, 객체마다 결과 표 하나. `vertcat(results{:})`로 합침 | `File i (name): analyzing K segments.` |
| `exportSegments(folder, options)` | 출력 폴더, 선택적 options | 객체·눈마다 CSV 하나 ([03](03-interpreting-output-ko.md)) | `File i (name) left pupil: wrote N samples to <file>` |
| `plotData()` | — | 그림 창 | — |

호출 순서는 고정이다. `processValidSamples`는 `isValid`가, `analyzeSegments`는 평활 신호가 필요하다.

### `RawSamplesModel` — 한쪽 눈의 원시 샘플

- 속성: `rawSample`, `isValid`(논리 벡터), `speedFiltData`, `devFiltData`(필터 중간 결과, `keepFilterData=true`일 때만 저장).
- 설정: `settings.raw`. 기본값은 `rawDataFilter()`에서 온다(인수 없이 호출하면 설정 구조체를 반환).

### `ValidSamplesModel` — 한쪽 눈의 valid 샘플

- 입력: valid 점의 `t_ms`와 `pupilDiameter`, 그리고 `validFraction`. 생성자에서 보간과 저역통과가 자동으로 실행된다.
- valid 점이 2개 미만이면 `Interpolation cannot be performed.` 오류가 난다.
- 출력: 길이가 같은 벡터 세 개를 가진 `signal` 구조체:

| 필드 | 단위 | 뜻 |
|---|---|---|
| `t` | 초 | 1000 Hz 시간축 |
| `pupilDiameter` | 원시 단위 | 평활된 직경. 공백이 `interp_maxGap`을 넘는 곳은 `NaN` |
| `gap_ms` | ms | 이 시점 앞뒤의 **실제 valid 점** 두 개 사이의 간격. 실제 점에서 0.5 ms(업샘플링 주기의 절반) 이내이면 0 |

---

이전: [시작하기: 파이프라인, 용어, 예제](01-getting-started-ko.md) · 목차: [README](../README.md) · 다음: [출력 읽기: 결과 표와 내보낸 CSV](03-interpreting-output-ko.md)
