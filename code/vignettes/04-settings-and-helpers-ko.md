# 설정과 보조 함수

[English](04-settings-and-helpers.md) · **한국어** · [中文](04-settings-and-helpers-zh.md)

이전: [출력 읽기: 결과 표와 내보낸 CSV](03-interpreting-output-ko.md) · 목차: [README](../README.md) · 다음: [문제 해결, 한계, 더 읽을 거리](05-troubleshooting-ko.md)

---

## 설정 항목 (매개변수는 여기서 바꾼다)

### `settings.raw` (`rawDataFilter()`에서)

| 설정 | 기본값 | 역할 |
|---|---|---|
| `PupilDiameter_Min` / `_Max` | 1.5 / 9 | 범위 필터. **기본값은 밀리미터 기준**이므로 픽셀 데이터는 반드시 바꿔야 한다(`Examples/Dataset_1`은 0.1 / inf 사용) |
| `islandFilter_islandSeperation_ms` | 40 | 다른 샘플과 얼마나 떨어져야 "섬"으로 보는가 |
| `islandFilter_minIslandWidth_ms` | 50 | 이보다 좁은 섬은 무효 |
| `dilationSpeedFilter_MadMultiplier` | 16 | 속도가 MAD의 이 배수를 넘으면 무효 (눈 깜빡임 가장자리 포착) |
| `dilationSpeedFilter_maxGap_ms` | 200 | 샘플 간격이 이보다 작을 때만 속도를 계산 |
| `gapDetect_minWidth` / `_maxWidth` | 75 / 2000 ms | 결측 구간이 얼마나 넓어야 "공백"으로 보는가 |
| `gapPadding_backward` / `_forward` | 50 / 50 ms | 공백 앞뒤로 추가로 버리는 길이 |
| `residualsFilter_passes` | 4 | 추세 편차 필터의 반복 횟수 |
| `residualsFilter_MadMultiplier` | 16 | 추세선에서 MAD의 이 배수 이상 벗어나면 무효 |
| `residualsFilter_interpFs` / `_lowpassCF` | 100 Hz / 16 Hz | 추세선을 만들 때의 재표본화율과 차단 주파수 |
| `keepFilterData` | `true` | 필터 중간 결과 보관. **메모리를 많이 씀**. 조정이 끝나면 `false` |

### `settings.valid` (`ValidSamplesModel.getDefaultSettings()`에서)

| 설정 | 기본값 | 역할 |
|---|---|---|
| `interp_upsamplingFreq` | 1000 Hz | 평활 신호의 샘플링 주파수 |
| `LpFilt_B` / `LpFilt_A` | 4차, 차단 4 Hz로 계산 | 저역통과 계수 (영위상 `filtfilt`) |
| `interp_maxGap` | 250 ms | 실제 valid 점 사이 간격이 이보다 크면 그 구간의 평활 신호를 `NaN`으로 |

## `helperFunctions/`

| 파일 | 하는 일 |
|---|---|
| `rawDataFilter.m` | 메인 함수가 `removeOutOfBounds`(범위) → `madSpeedFilter`(속도, 눈 깜빡임 포착) → `madDeviationFilter`(추세 이탈) 순으로 호출. 고립점 정리 `removeLoners`는 세 단계 안에서 반복 호출되고, 공백 확장 `expandGaps`는 속도 필터 안에서 호출됨. `madCalc`는 MAD 임계값 계산. 인수 없이 호출하면 기본 설정 반환 |
| `genMeanDiaSamples.m` | 두 눈을 합쳐 평균 직경을 만든다. `processValidSamples`가 호출하며 한 눈 데이터에는 쓰이지 않음 |
| `plotSegments.m` | 구간 표를 색 블록으로 그린다. `plotData`가 호출 |
| `printToConsole.m` | 진행 메시지 출력, 내부용 |
| `legacyModeCheck.m` | MATLAB이 8.3보다 오래돼 `table`이 없으면 `LEGACY/`를 경로에 추가. 새 버전에서는 아무 일도 안 함 |
| `FALLBACK/` | `butter`, `filtfilt`, `histc`, `nanmin` / `nanmax` / `nanmean` / `nanmedian` 대체 구현. 툴박스가 없거나 함수가 제거된 MATLAB용 |
| `LEGACY/` | 아주 오래된 MATLAB에서 `table`을 흉내 냄 |

**FALLBACK 함정:** `addpath(genpath(...))`는 폴더를 경로의 **맨 앞**에 넣으므로, 같은 이름의 진짜 툴박스 함수를 FALLBACK이 가린다. 툴박스를 우선하려면 `addpath(..., '-end')`를 쓴다. 이 컴퓨터의 MATLAB에는 Statistics 툴박스가 없어서 `nan*` 계열은 FALLBACK 것을 쓴다.

---

이전: [출력 읽기: 결과 표와 내보낸 CSV](03-interpreting-output-ko.md) · 목차: [README](../README.md) · 다음: [문제 해결, 한계, 더 읽을 거리](05-troubleshooting-ko.md)
