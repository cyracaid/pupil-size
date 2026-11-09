"""Generates code/README.md (EN / KO / ZH in one page) from the column and field tables below.

Run: python3 tools/build_readme.py
The tables are the single source of truth for the documented columns; edit them here, not in README.md.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "code" / "README.md"
LANGS = ["en", "ko", "zh"]
IDX = {"en": 0, "ko": 1, "zh": 2}


def det(summary, body):
    import re as _re
    summary = _re.sub(r"`([^`]+)`", r"<code>\1</code>", summary)
    return "<details>\n<summary>%s</summary>\n\n%s\n\n</details>\n" % (summary, body.strip("\n"))


def idet(summary, body):
    """single-line details for use inside a table cell"""
    return "<details><summary>%s</summary>%s</details>" % (summary, body.replace("\n", "<br>").replace("|", "/"))


# ---------------------------------------------------------------------------
# per-language UI strings
# ---------------------------------------------------------------------------
UI = {
    "title": ("code/ — the pupil-size toolbox and our YMTC layer: everything in one page",
              "code/ — pupil-size 툴박스와 우리의 YMTC 계층: 한 페이지에 모두",
              "code/ — pupil-size 工具箱与我们的 YMTC 层：一页讲完"),
    "intro": (
        "One page for the original Kret & Sjak-Shie (2019) code **and** our own `ymtc/` layer. Every output table is listed column by column. Click a triangle to unfold a detail; nothing below is hidden by default except those details. Everything was written against the source or the real files; where something could not be confirmed it says so.",
        "원본 Kret & Sjak-Shie (2019) 코드와 우리의 `ymtc/` 계층을 한 페이지에 담았다. 모든 출력 표를 열 단위로 나열했다. 삼각형을 누르면 세부 설명이 펼쳐진다. 소스나 실제 파일을 대조해 썼고, 확인하지 못한 것은 그렇다고 적었다.",
        "原版 Kret & Sjak-Shie (2019) 代码和我们自己的 `ymtc/` 层，都放在这一页。每张输出表都逐列列出。点三角形展开细节。内容都对照源码或真实文件写成；没能确认的地方会直接写明。"),
    "toc": ("Contents", "목차", "目录"),
    "tbl_col": ("column", "열", "列"),
    "tbl_unit": ("unit", "단위", "单位"),
    "tbl_mean": ("meaning", "의미", "含义"),
    "tbl_more": ("details", "세부", "细节"),
    "tbl_field": ("field", "필드", "字段"),
    "tbl_what": ("what it is", "무엇인가", "是什么"),
}


def u(key, lang):
    return UI[key][IDX[lang]]


# ---------------------------------------------------------------------------
# column specs: (name, unit, (en,ko,zh) meaning, (en,ko,zh) more or None)
# ---------------------------------------------------------------------------
def T(en, ko, zh):
    return (en, ko, zh)


SAMPLE_COLS = [
    ("participant", "–", T("subject id", "피험자 ID", "被试编号"), T("Taken from the file name (`sub149_...trk` gives `sub149`); if the name does not start with `sub<digits>` the whole base name is used.", "파일명에서 가져온다(`sub149_...trk` → `sub149`). 이름이 `sub<숫자>`로 시작하지 않으면 확장자를 뺀 전체 이름을 쓴다.", "取自文件名（`sub149_...trk` 得 `sub149`）；文件名不以 `sub<数字>` 开头时用整个文件名。")),
    ("run", "–", T("run number 0–4", "run 번호 0–4", "run 编号 0–4"), T("Counts `START` events only. Samples before the first `START` are `0`. A file missing its first `START` therefore numbers its runs one too low; this is reported in the issues table, not repaired.", "`START` 이벤트만 센다. 첫 `START` 이전 샘플은 `0`. 첫 `START`가 없는 파일은 run 번호가 하나씩 낮아지며, 고치지 않고 이상치 표에 기록한다.", "只数 `START` 事件。第一个 `START` 之前的样本是 `0`。缺第一个 `START` 的文件，run 编号会整体少 1；只记入异常表，不修补。")),
    ("trial", "–", T("trial number within the file, 0–84", "파일 내 trial 번호 0–84", "文件内的 trial 编号 0–84"), T("Increments at each `CueStart`; `0` before the first cue.", "`CueStart`마다 1씩 증가. 첫 cue 이전은 `0`.", "每遇到一个 `CueStart` 加 1；第一个 cue 之前为 `0`。")),
    ("trial_in_run", "–", T("trial number within its run, 0–21", "run 안의 trial 번호 0–21", "run 内的 trial 编号 0–21"), T("Reset to 0 at each `START`.", "`START`마다 0으로 초기화.", "每个 `START` 处归零。")),
    ("phase", "–", T("task phase the sample belongs to", "샘플이 속한 과제 단계", "样本所处的任务阶段"), T("Carried forward from the last event. Values: `pre`, `start`, `burn_in`, `cue`, `countdown`, `stimulus`, `whitenoise1`–`whitenoise4`, `rating`, `burn_out`. `CountdownFinish` and unknown events keep the current phase.", "마지막 이벤트에서 앞으로 이어진다. 값: `pre`, `start`, `burn_in`, `cue`, `countdown`, `stimulus`, `whitenoise1`–`whitenoise4`, `rating`, `burn_out`. `CountdownFinish`와 알 수 없는 이벤트는 현재 단계를 유지.", "从上一个事件向后延续。取值：`pre`、`start`、`burn_in`、`cue`、`countdown`、`stimulus`、`whitenoise1`–`whitenoise4`、`rating`、`burn_out`。`CountdownFinish` 和未知事件不改变阶段。")),
    ("time_ms", "ms", T("raw eye-tracker timestamp of the sample", "샘플의 시선추적기 원시 타임스탬프", "样本的眼动仪原始时间戳"), T("A large running counter (for example `1491312812.2`), not zero-based. Sample spacing is about 16.7 ms (60 Hz). Rows stay in log order even if time runs backwards (`NONMONOTONIC_TIME`).", "큰 누적 카운터(예: `1491312812.2`)이며 0에서 시작하지 않는다. 샘플 간격은 약 16.7 ms(60 Hz). 시간이 거꾸로 가도 로그 순서대로 둔다(`NONMONOTONIC_TIME`).", "一个很大的累计计数（如 `1491312812.2`），不是从 0 开始。样本间隔约 16.7 ms（60 Hz）。时间倒退时行仍按日志顺序保留（`NONMONOTONIC_TIME`）。")),
    ("t_run_s", "s", T("seconds since the current run's `START`", "현재 run의 `START` 이후 초", "距当前 run 的 `START` 的秒数"), T("`NaN` before the first `START`.", "첫 `START` 이전에는 `NaN`.", "第一个 `START` 之前为 `NaN`。")),
    ("event", "–", T("software event attached to this sample, else empty", "이 샘플에 붙은 소프트웨어 이벤트, 없으면 빈칸", "挂在这个样本上的软件事件，没有则为空"), T("Each event goes on the first sample whose timestamp is at or after the event time, so event times carry up to one sample interval (about 17 ms). Several events on one sample are joined with `;`. Known names: `START`, `BurnInStart`, `CueStart`, `CueFinish`, `CountdownFinish`, `StimuliStart`, `WhitenoiseStart1`–`4`, `RatingStart`, `BurnOutStart`.", "각 이벤트는 타임스탬프가 이벤트 시각 이상인 첫 샘플에 붙으므로 시각 오차가 최대 한 샘플 간격(약 17 ms). 한 샘플에 이벤트가 여럿이면 `;`로 잇는다. 알려진 이름: `START`, `BurnInStart`, `CueStart`, `CueFinish`, `CountdownFinish`, `StimuliStart`, `WhitenoiseStart1`–`4`, `RatingStart`, `BurnOutStart`.", "每个事件挂在时间戳不早于事件时刻的第一个样本上，所以事件时刻最多有一个采样间隔（约 17 ms）的误差。一个样本上有多个事件时用 `;` 连接。已知事件名：`START`、`BurnInStart`、`CueStart`、`CueFinish`、`CountdownFinish`、`StimuliStart`、`WhitenoiseStart1`–`4`、`RatingStart`、`BurnOutStart`。")),
    ("sp_pup_x", "camera px", T("pupil position, x", "동공 위치 x", "瞳孔位置 x"), T("From the log's pupil columns. The prefix `sp_` is not explained in the log. Read as a position in camera-image pixels; not confirmed by the lab.", "로그의 동공 열에서 온 값. 접두사 `sp_`는 로그에 설명이 없다. 카메라 영상 픽셀 좌표로 읽지만 실험실 확인은 받지 않았다.", "来自日志的瞳孔列。日志没有解释前缀 `sp_`。按相机图像像素坐标理解，尚未向实验室确认。")),
    ("sp_pup_y", "camera px", T("pupil position, y", "동공 위치 y", "瞳孔位置 y"), None),
    ("sp_glint_x", "camera px", T("glint (corneal reflection) position, x", "글린트(각막 반사) 위치 x", "角膜反光点（glint）位置 x"), None),
    ("sp_glint_y", "camera px", T("glint position, y", "글린트 위치 y", "角膜反光点位置 y"), None),
    ("vector_x", "camera px", T("pupil minus glint, x", "동공−글린트 x", "瞳孔减反光点 x"), T("The log spells it `vektor`. Checked on one row: `sp_pup_x - sp_glint_x` = 357.3 − 345.7 ≈ 11.58 = `vector_x`.", "로그 표기는 `vektor`. 한 행에서 확인: `sp_pup_x - sp_glint_x` = 357.3 − 345.7 ≈ 11.58 = `vector_x`.", "日志里拼作 `vektor`。在一行上核对过：`sp_pup_x - sp_glint_x` = 357.3 − 345.7 ≈ 11.58 = `vector_x`。")),
    ("vector_y", "camera px", T("pupil minus glint, y", "동공−글린트 y", "瞳孔减反光点 y"), None),
    ("gaze_x", "–", T("gaze position, x", "시선 위치 x", "注视位置 x"), T("Empty (`NaN`) in every file so far: no gaze data is recorded (`NO_GAZE`).", "지금까지 모든 파일에서 비어 있음(`NaN`): 시선 데이터가 기록되지 않았다(`NO_GAZE`).", "目前所有文件里都是空（`NaN`）：没有记录注视数据（`NO_GAZE`）。")),
    ("gaze_y", "–", T("gaze position, y", "시선 위치 y", "注视位置 y"), None),
    ("pupil_2a", "camera px", T("pupil ellipse axis 2a", "동공 타원 축 2a", "瞳孔椭圆轴 2a"), T("One of the two ellipse axes. The Kret adapter by default averages `pupil_2a` and `pupil_2b` into the pupil size (`PupilMeasure='mean'`). `NaN` means the log said \"no pupil geometry\".", "타원의 두 축 중 하나. Kret 어댑터는 기본값으로 `pupil_2a`와 `pupil_2b`의 평균을 동공 크기로 쓴다(`PupilMeasure='mean'`). `NaN`은 로그가 \"no pupil geometry\"라고 했다는 뜻.", "椭圆的两个轴之一。Kret 适配器默认取 `pupil_2a` 与 `pupil_2b` 的平均作为瞳孔大小（`PupilMeasure='mean'`）。`NaN` 表示日志写的是 \"no pupil geometry\"。")),
    ("pupil_2b", "camera px", T("pupil ellipse axis 2b", "동공 타원 축 2b", "瞳孔椭圆轴 2b"), None),
    ("pupil_angle", "unconfirmed", T("pupil ellipse orientation", "동공 타원 방향", "瞳孔椭圆朝向"), T("The unit is not stated in the log. Values such as 1.64 suggest radians; not confirmed.", "단위가 로그에 없다. 1.64 같은 값은 라디안으로 보이나 확인되지 않았다.", "日志没写单位。1.64 这类数值像弧度；未确认。")),
    ("pupil_valid", "0/1", T("sample has pupil data", "샘플에 동공 데이터가 있는가", "该样本有瞳孔数据"), T("`1` when `pupil_2a` is not `NaN`. This is only \"the tracker reported something\", not the Kret artifact filter's `isValid`.", "`pupil_2a`가 `NaN`이 아니면 `1`. \"추적기가 값을 냈다\"는 뜻일 뿐 Kret 아티팩트 필터의 `isValid`가 아니다.", "`pupil_2a` 不是 `NaN` 时为 `1`。只表示“眼动仪给了值”，不是 Kret 伪影滤波的 `isValid`。")),
    ("gaze_valid", "0/1", T("sample has gaze data", "샘플에 시선 데이터가 있는가", "该样本有注视数据"), T("`1` when `gaze_x` is not `NaN`; all `0` in our files.", "`gaze_x`가 `NaN`이 아니면 `1`. 우리 파일은 전부 `0`.", "`gaze_x` 不是 `NaN` 时为 `1`；我们的文件里全是 `0`。")),
]

QC_COLS = [
    ("participant, file", "–", T("subject id; the .trk file name", "피험자 ID; .trk 파일명", "被试编号；.trk 文件名"), None),
    ("status", "–", T("`ok` / `warn` / `failed`", "`ok` / `warn` / `failed`", "`ok` / `warn` / `failed`"), T("`warn` if at least one issue has severity `warn`; `failed` is the placeholder for a file that could not be read.", "이상치 중 하나라도 심각도가 `warn`이면 `warn`. `failed`는 읽지 못한 파일의 자리표시자.", "只要有一条异常的严重度是 `warn` 就是 `warn`；`failed` 是读不出来的文件的占位值。")),
    ("n_samples", "count", T("number of samples", "샘플 수", "样本数"), None),
    ("duration_min", "min", T("recording length", "기록 길이", "记录时长"), T("(last timestamp − first timestamp) / 60000.", "(마지막 − 첫 타임스탬프) / 60000.", "（最后一个时间戳 − 第一个时间戳）/ 60000。")),
    ("sampling_hz", "Hz", T("sampling rate", "샘플링 주파수", "采样率"), T("1000 / median of the sample spacing. About 59.9 Hz here.", "1000 / 샘플 간격의 중앙값. 여기서는 약 59.9 Hz.", "1000 / 样本间隔的中位数。这里约 59.9 Hz。")),
    ("n_events", "count", T("software events in the log", "로그의 소프트웨어 이벤트 수", "日志中的软件事件数"), None),
    ("n_START … n_BurnOutStart", "count", T("count of each event type: `START`, `BurnInStart`, `CueStart`, `CueFinish`, `StimuliStart`, `RatingStart`, `BurnOutStart`", "이벤트 종류별 개수", "每类事件的个数"), T("Expected: 4 `START`, 4 `BurnInStart`, 84 `CueStart` = `CueFinish` = `StimuliStart`, 4 `BurnOutStart`; `RatingStart` only on some trials (24 for sub119). Seven columns: `n_START`, `n_BurnInStart`, `n_CueStart`, `n_CueFinish`, `n_StimuliStart`, `n_RatingStart`, `n_BurnOutStart`.", "기대값: `START` 4, `BurnInStart` 4, `CueStart` = `CueFinish` = `StimuliStart` = 84, `BurnOutStart` 4. `RatingStart`는 일부 trial에만(sub119는 24). 일곱 열.", "期望值：`START` 4、`BurnInStart` 4、`CueStart` = `CueFinish` = `StimuliStart` = 84、`BurnOutStart` 4；`RatingStart` 只出现在部分 trial（sub119 是 24）。共七列。")),
    ("pupil_valid_fraction", "0–1", T("share of samples with pupil data", "동공 데이터가 있는 샘플 비율", "有瞳孔数据的样本比例"), T("Below 0.5 gives a `LOW_PUPIL_VALID` warning. Nothing is dropped.", "0.5 미만이면 `LOW_PUPIL_VALID` 경고. 아무것도 버리지 않는다.", "低于 0.5 给出 `LOW_PUPIL_VALID` 警告；不会删除任何样本。")),
    ("gaze_valid_fraction", "0–1", T("share of samples with gaze data", "시선 데이터가 있는 샘플 비율", "有注视数据的样本比例"), None),
    ("cue_dur_min_s / _mean_s / _max_s", "s", T("cue length: `CueStart` → `CueFinish`", "cue 길이: `CueStart` → `CueFinish`", "cue 时长：`CueStart` → `CueFinish`"), T("The task setting is 1.0 s. For sub119 the mean is 0.881 s (0.832–0.96 s).", "과제 설정은 1.0 s. sub119는 평균 0.881 s(0.832–0.96 s).", "任务设定是 1.0 s。sub119 的均值是 0.881 s（0.832–0.96 s）。")),
    ("n_cue_off_setting", "count", T("cues that differ from 1.0 s by more than 0.001 s", "1.0 s와 0.001 s 넘게 다른 cue 수", "与 1.0 s 相差超过 0.001 s 的 cue 个数"), T("84 of 84 for sub119, which is what triggers `CUE_DURATION`.", "sub119는 84개 중 84개이며 이것이 `CUE_DURATION`을 일으킨다.", "sub119 是 84 个里的 84 个，这就是 `CUE_DURATION` 的来源。")),
    ("countdown_min_s / _mean_s / _max_s", "s", T("`CueStart` → `StimuliStart`", "`CueStart` → `StimuliStart`", "`CueStart` → `StimuliStart`"), T("Note: this includes the cue. The designed countdown is this minus the 1 s cue (7.5–30 s).", "주의: cue 시간을 포함한다. 설계상 카운트다운은 이 값에서 cue 1 s를 뺀 것(7.5–30 s).", "注意：包含 cue 的时间。设计的倒计时 = 这个值 − 1 s 的 cue（7.5–30 s）。")),
    ("n_malformed_lines", "count", T("log lines that could not be parsed", "파싱하지 못한 로그 줄 수", "无法解析的日志行数"), None),
    ("n_issues", "count", T("number of rows this file has in the issues table", "이 파일이 이상치 표에 가진 행 수", "该文件在异常表中的行数"), None),
]

ISSUE_COLS = [
    ("participant, file", "–", T("subject id; .trk file name", "피험자 ID; .trk 파일명", "被试编号；.trk 文件名"), None),
    ("severity", "–", T("`warn` = deviates from expectation; `info` = a fact worth knowing", "`warn` = 기대와 다름; `info` = 알아둘 사실", "`warn` = 偏离预期；`info` = 值得知道的事实"), None),
    ("code", "–", T("machine-readable code, see the list below", "기계가 읽는 코드, 아래 목록 참조", "机器可读的代码，见下表"), None),
    ("message", "–", T("plain-language description with the numbers", "수치를 포함한 설명문", "带数字的说明文字"), None),
]

ISSUE_CODES = [
    ("MALFORMED_LINES", "warn", T("some lines could not be parsed and were skipped", "파싱 못 해 건너뛴 줄이 있음", "有行无法解析而被跳过")),
    ("NO_STOP_LINE", "warn", T("no `stop timecounter` line; the log may be truncated", "`stop timecounter` 줄이 없음. 로그가 잘렸을 수 있음", "没有 `stop timecounter` 行，日志可能被截断")),
    ("NONMONOTONIC_TIME", "warn", T("a timestamp is not later than the previous one", "타임스탬프가 앞 것보다 늦지 않음", "有时间戳不晚于前一个")),
    ("TIME_GAP", "warn", T("a gap between samples longer than 200 ms", "샘플 사이 간격이 200 ms 초과", "样本间隔超过 200 ms")),
    ("LOW_PUPIL_VALID", "warn", T("fewer than 50% of samples have pupil data", "동공 데이터가 있는 샘플이 50% 미만", "有瞳孔数据的样本不足 50%")),
    ("NO_GAZE", "info", T("no sample has gaze data", "시선 데이터가 있는 샘플이 없음", "没有任何样本有注视数据")),
    ("NO_EVENTS", "warn", T("no `SoftwareEvent` lines; run, trial, phase cannot be filled", "`SoftwareEvent` 줄이 없음. run·trial·phase를 채울 수 없음", "没有 `SoftwareEvent` 行，无法填 run / trial / phase")),
    ("START_COUNT", "warn", T("number of `START` is not 4", "`START` 개수가 4가 아님", "`START` 个数不是 4")),
    ("START_BURNIN_MISMATCH", "warn", T("`START` and `BurnInStart` counts differ (names the `BurnInStart` without a `START`)", "`START`와 `BurnInStart` 개수가 다름(`START`가 없는 `BurnInStart`를 알려 줌)", "`START` 与 `BurnInStart` 个数不一致（会指出缺 `START` 的那个 `BurnInStart`）")),
    ("TRIAL_COUNT", "warn", T("number of `CueStart` is not 84", "`CueStart` 개수가 84가 아님", "`CueStart` 个数不是 84")),
    ("EVENT_COUNT_MISMATCH", "warn", T("`CueStart`, `CueFinish`, `StimuliStart` counts are not equal", "`CueStart`, `CueFinish`, `StimuliStart` 개수가 같지 않음", "`CueStart`、`CueFinish`、`StimuliStart` 个数不相等")),
    ("UNKNOWN_EVENTS", "info", T("event names outside the known list", "알려진 목록에 없는 이벤트 이름", "出现了已知名单之外的事件名")),
    ("CUE_DURATION", "warn", T("cues differ from the 1.0 s setting by more than 0.001 s (with min / mean / max)", "cue가 1.0 s 설정과 0.001 s 넘게 다름(최소·평균·최대 포함)", "cue 与 1.0 s 设定相差超过 0.001 s（附最小 / 均值 / 最大）")),
]

EVENT03_COLS = [
    ("participant", "–", T("subject id", "피험자 ID", "被试编号"), None),
    ("time_ms", "ms", T("raw timestamp of the event", "이벤트의 원시 타임스탬프", "事件的原始时间戳"), T("The event's own time from the `SoftwareEvent` line, not snapped to a sample.", "`SoftwareEvent` 줄의 이벤트 자체 시각이며 샘플에 맞추지 않은 값.", "`SoftwareEvent` 行里事件自己的时刻，没有对齐到样本。")),
    ("event", "–", T("event name", "이벤트 이름", "事件名"), None),
]

EVENT_COLS = [
    ("participant", "–", T("subject id", "피험자 ID", "被试编号"), None),
    ("order", "1–5", T("which of the five trial orders the subject ran", "피험자가 수행한 다섯 trial 순서 중 하나", "被试做的是五种试次顺序中的哪一种"), T("Chosen by comparing each trial's countdown length (`StimuliStart − CueStart − 1 s`) with `TrialOrder<o>Run<r>.xlsx`; the best of five wins. The margin is printed (for example 0.80 s against 14.8 s for the runner-up). The order is not recorded anywhere else, so ask the lab to confirm.", "각 trial의 카운트다운 길이(`StimuliStart − CueStart − 1 s`)를 `TrialOrder<o>Run<r>.xlsx`와 비교해 다섯 중 가장 맞는 것을 고른다. 차이는 출력된다(예: 0.80 s 대 차선 14.8 s). 다른 곳에 기록된 값이 아니므로 실험실에 확인할 것.", "把每个 trial 的倒计时长度（`StimuliStart − CueStart − 1 s`）与 `TrialOrder<o>Run<r>.xlsx` 比较，取五个里最吻合的。差距会打印出来（例如 0.80 s 对次优 14.8 s）。别处没有记录这个顺序，需要向实验室确认。")),
    ("run", "1–4", T("run number", "run 번호", "run 编号"), T("`ceil(trial / 21)`. Guarded by `ymtcRunCheck`.", "`ceil(trial / 21)`. `ymtcRunCheck`가 검증한다.", "`ceil(trial / 21)`，由 `ymtcRunCheck` 验证。")),
    ("trial", "1–84", T("trial number in the subject", "피험자 내 trial 번호", "被试内的 trial 编号"), T("Counts `CueStart` events. Empty on run-level rows.", "`CueStart`를 센다. run 수준 행에서는 비어 있다.", "数 `CueStart`。run 级的行为空。")),
    ("trial_in_run", "1–21", T("trial number within its run", "run 안의 trial 번호", "run 内的 trial 编号"), None),
    ("ymtc_marker", "–", T("the task's own marker name", "과제 자체의 마커 이름", "任务自己的 marker 名"), T("For example `OnsetPTCTO`, `PredictableTimeCertainThreatOutcome`, `OutcomePTCTO`, `WhiteNoise`, `Rating`; run-level rows carry `START`, `BurnInStart`, `BurnOutStart`.", "예: `OnsetPTCTO`, `PredictableTimeCertainThreatOutcome`, `OutcomePTCTO`, `WhiteNoise`, `Rating`. run 수준 행은 `START`, `BurnInStart`, `BurnOutStart`.", "例如 `OnsetPTCTO`、`PredictableTimeCertainThreatOutcome`、`OutcomePTCTO`、`WhiteNoise`、`Rating`；run 级的行是 `START`、`BurnInStart`、`BurnOutStart`。")),
    ("trk_event", "–", T("trk event matched to the marker", "마커에 대응시킨 trk 이벤트", "与该 marker 对应的 trk 事件"), T("`CueStart` ↔ Onset, `CueFinish` ↔ countdown start, `StimuliStart` ↔ Outcome, `WhitenoiseStart1` ↔ WhiteNoise, `RatingStart` ↔ Rating.", "`CueStart` ↔ Onset, `CueFinish` ↔ 카운트다운 시작, `StimuliStart` ↔ Outcome, `WhitenoiseStart1` ↔ WhiteNoise, `RatingStart` ↔ Rating.", "`CueStart` ↔ Onset，`CueFinish` ↔ 倒计时开始，`StimuliStart` ↔ Outcome，`WhitenoiseStart1` ↔ WhiteNoise，`RatingStart` ↔ Rating。")),
    ("time_ms", "ms", T("raw timestamp of the matched trk event", "대응한 trk 이벤트의 원시 타임스탬프", "对应 trk 事件的原始时间戳"), T("Empty when the trk lacks that marker (nothing is interpolated).", "trk에 그 마커가 없으면 비어 있다(보간하지 않음).", "trk 里缺该 marker 时为空（不插值）。")),
    ("t_from_onset_s", "s", T("seconds since this trial's Onset", "이 trial의 Onset 이후 초", "距本 trial 的 Onset 的秒数"), None),
    ("expected_from_onset_s", "s", T("where the design puts this marker", "설계상 이 마커의 위치", "设计上该 marker 的位置"), T("From the `onsets` column of the order workbook, relative to the trial's Onset.", "order 워크북의 `onsets` 열, trial의 Onset 기준.", "来自 order 工作簿的 `onsets` 列，以 trial 的 Onset 为基准。")),
    ("diff_s", "s", T("measured minus designed", "측정값 − 설계값", "实测 − 设计"), T("`t_from_onset_s − expected_from_onset_s`. A consistent sign shows a systematic offset, for example a cue that runs short.", "`t_from_onset_s − expected_from_onset_s`. 부호가 일정하면 체계적 어긋남(예: cue가 짧음)을 뜻한다.", "`t_from_onset_s − expected_from_onset_s`。符号一致说明有系统偏移，例如 cue 偏短。")),
    ("expected_duration_s", "s", T("designed length of this marker", "이 마커의 설계상 길이", "该 marker 的设计时长"), T("From the `durations` column: cue 1 s, countdown 7.5–30 s, Outcome 2.7 s, WhiteNoise 2.3 s, Rating 6 s.", "`durations` 열: cue 1 s, 카운트다운 7.5–30 s, Outcome 2.7 s, WhiteNoise 2.3 s, Rating 6 s.", "来自 `durations` 列：cue 1 s、倒计时 7.5–30 s、Outcome 2.7 s、WhiteNoise 2.3 s、Rating 6 s。")),
    ("condition", "–", T("`PTCT` `PTCS` `PTUO` `UTCT` `UTCS` `UTUO`", "`PTCT` `PTCS` `PTUO` `UTCT` `UTCS` `UTUO`", "`PTCT` `PTCS` `PTUO` `UTCT` `UTCS` `UTUO`"), T("The four characters after `Onset` in the first marker name. It is NOT in the trk; it comes from the chosen order file. Whether `PTPT` in lab talk equals `PTCT` here is still to be confirmed.", "첫 마커 이름에서 `Onset` 뒤 네 글자. trk에는 없고 선택한 order 파일에서 온다. 실험실에서 말하는 `PTPT`가 여기의 `PTCT`와 같은지는 아직 확인 전.", "第一个 marker 名里 `Onset` 之后的四个字符。trk 里没有，来自选定的 order 文件。实验室口头说的 `PTPT` 是否等于这里的 `PTCT` 尚待确认。")),
    ("timing", "P/U", T("predictable / unpredictable time", "시간 예측 가능/불가능", "时间可预测 / 不可预测"), T("First letter of `condition`.", "`condition`의 첫 글자.", "`condition` 的第 1 个字母。")),
    ("certainty", "C/U", T("outcome known at the cue or not", "cue 시점에 결과를 아는가", "cue 时是否已知结果"), T("Third letter of `condition`.", "`condition`의 세 번째 글자.", "`condition` 的第 3 个字母。")),
    ("outcome", "T/S/O", T("what the *cue* announced", "*cue*가 알린 결과", "*cue* 所宣告的结果"), T("Fourth letter. `T` threat, `S` safe, `O` = not announced. For the two uncertain conditions it is `O` on every row.", "네 번째 글자. `T` 위협, `S` 안전, `O` = 알리지 않음. 불확실한 두 조건에서는 모든 행이 `O`.", "第 4 个字母。`T` 威胁、`S` 安全、`O` = 未宣告。两个不确定条件下每一行都是 `O`。")),
    ("actual_outcome", "T/S", T("what the trial really ended in", "trial이 실제로 끝난 결과", "该 trial 实际的结果"), T("Equal to `outcome` for certain trials; for the uncertain ones it is the last letter of the Outcome marker (`OutcomeUTUOT` → `T`). Empty on run-level rows.", "확실한 trial은 `outcome`과 같고, 불확실한 trial은 Outcome 마커의 마지막 글자(`OutcomeUTUOT` → `T`). run 수준 행은 비어 있다.", "确定型 trial 等于 `outcome`；不确定型取 Outcome marker 的最后一个字母（`OutcomeUTUOT` → `T`）。run 级的行为空。")),
    ("step", "1–5", T("position inside the trial", "trial 안에서의 위치", "在 trial 内的位置"), T("1 Onset, 2 countdown start, 3 Outcome, 4 WhiteNoise, 5 Rating. Empty on run-level rows. The full version adds `WhiteNoise_part2`–`4` rows, also `step = 4`.", "1 Onset, 2 카운트다운 시작, 3 Outcome, 4 WhiteNoise, 5 Rating. run 수준 행은 비어 있다. 전체 버전은 `WhiteNoise_part2`–`4` 행을 더하며 이들도 `step = 4`.", "1 Onset、2 倒计时开始、3 Outcome、4 WhiteNoise、5 Rating。run 级的行为空。完整版多出 `WhiteNoise_part2`–`4` 行，同样 `step = 4`。")),
]

EVSUM_COLS = [
    ("participant", "–", T("subject id", "피험자 ID", "被试编号"), None),
    ("status", "–", T("`ok` / `skipped_no_file` / `skipped_no_events` / `error`", "`ok` / `skipped_no_file` / `skipped_no_events` / `error`", "`ok` / `skipped_no_file` / `skipped_no_events` / `error`"), T("sub124, sub128, sub137 are `skipped_no_events`: their trk has no `SoftwareEvent` lines.", "sub124, sub128, sub137은 `skipped_no_events`: trk에 `SoftwareEvent` 줄이 없다.", "sub124、sub128、sub137 是 `skipped_no_events`：它们的 trk 里没有 `SoftwareEvent` 行。")),
    ("order", "1–5", T("chosen trial order", "선택된 trial 순서", "选中的试次顺序"), None),
    ("nRows", "count", T("rows written", "기록된 행 수", "写出的行数"), T("624 for the full table, 372 for the 5-step version; sub134 is one short (no first `START`).", "전체 표는 624, 5단계 버전은 372. sub134는 하나 적다(첫 `START` 없음).", "完整表 624，5 步版 372；sub134 少 1 行（缺第一个 `START`）。")),
    ("nTrials", "count", T("trials found", "찾은 trial 수", "找到的 trial 数"), None),
    ("note", "–", T("free text, empty when fine", "자유 텍스트, 이상 없으면 빈칸", "说明文字，正常时为空"), None),
]

WIDE_COLS = [
    ("participant, order, run, trial", "–", T("identity of the trial", "trial의 식별 정보", "trial 的标识"), None),
    ("condition, timing, certainty, outcome", "–", T("as in the event table", "이벤트 표와 같음", "同事件表"), None),
    ("onset_s", "s", T("always 0, the reference point", "항상 0, 기준점", "恒为 0，参考点"), None),
    ("countdown_s", "s", T("countdown start, seconds from Onset", "카운트다운 시작, Onset 기준 초", "倒计时开始，距 Onset 的秒数"), None),
    ("outcome_s", "s", T("Outcome onset", "Outcome 시작", "Outcome 开始"), None),
    ("whitenoise_s", "s", T("white-noise onset", "백색소음 시작", "白噪声开始"), None),
    ("rating_s", "s", T("rating onset; `NaN` when no rating", "평정 시작. 평정이 없으면 `NaN`", "评分开始；没有评分时为 `NaN`"), None),
    ("has_rating", "logical", T("whether the trial has a rating", "trial에 평정이 있는가", "该 trial 是否有评分"), T("24 of 84 trials.", "84개 중 24개.", "84 个里 24 个。")),
]

TIMING_COLS = [
    ("participant", "–", T("subject id", "피험자 ID", "被试编号"), None),
    ("phase", "–", T("`1 Onset` … `5 Rating start`", "`1 Onset` … `5 Rating start`", "`1 Onset` … `5 Rating start`"), None),
    ("n", "count", T("markers in this cell", "이 칸의 마커 수", "该格中的 marker 数"), None),
    ("mean_s, sd_s", "s", T("mean and SD of `diff_s`", "`diff_s`의 평균과 표준편차", "`diff_s` 的均值和标准差"), T("Descriptive only. Reproduce it with `ymtcTimingCheck`.", "기술 통계일 뿐. `ymtcTimingCheck`로 재현한다.", "仅是描述性数字。用 `ymtcTimingCheck` 复现。")),
    ("min_s, max_s", "s", T("extremes of `diff_s`", "`diff_s`의 극값", "`diff_s` 的极值"), None),
]

RUNCHK_COLS = [
    ("participant, status", "–", T("subject id; `ok` / `no_file` / `no_events`", "피험자 ID; `ok` / `no_file` / `no_events`", "被试编号；`ok` / `no_file` / `no_events`"), None),
    ("nSTART, nBurnInStart, nBurnOutStart, nCueStart", "count", T("event counts", "이벤트 개수", "事件个数"), None),
    ("trialsPerRun", "–", T("for example `21/21/21/21`", "예: `21/21/21/21`", "例如 `21/21/21/21`"), T("Counted with `BurnInStart` as the run boundary (not `START`, which can be missing).", "`BurnInStart`를 run 경계로 센다(없을 수 있는 `START`는 쓰지 않음).", "以 `BurnInStart` 作为 run 边界来数（不用可能缺失的 `START`）。")),
    ("runAssignmentOK", "0/1", T("every run has 21 trials and the counts agree", "모든 run이 21 trial이고 개수가 일치", "每个 run 都是 21 个 trial 且个数一致"), T("This is what guards `run = ceil(trial / 21)`.", "`run = ceil(trial / 21)`을 지키는 장치.", "`run = ceil(trial / 21)` 靠它把关。")),
    ("note", "–", T("what is wrong, in words", "문제점 설명", "哪里不对的说明"), None),
]

SEG_UP = [
    ("segmentStart, segmentEnd", "s", T("segment boundaries", "구간 경계", "分段边界"), T("Seconds from the first sample of the recording (first sample = 0). Half-open `[start, end)`. Both `NaN` when the matching event is missing, which makes the whole statistics row `NaN`.", "기록 첫 샘플부터의 초(첫 샘플 = 0). 반개구간 `[start, end)`. 대응하는 이벤트가 없으면 둘 다 `NaN`이며 통계 행 전체가 `NaN`이 된다.", "距记录第一个样本的秒数（第一个样本 = 0）。左闭右开 `[start, end)`。缺对应事件时两者都是 `NaN`，整行统计也就是 `NaN`。")),
    ("SmoothSig_meanDiam", "px", T("mean of the smooth signal in the segment", "구간 안 평활 신호의 평균", "段内平滑信号的均值"), T("`NaN` points are ignored. Interpolated points are included, so a short gap looks perfectly clean; read it together with `SmoothSig_missingDataPercent`.", "`NaN`은 제외. 보간된 점은 포함되므로 짧은 공백은 깨끗해 보인다. `SmoothSig_missingDataPercent`와 함께 읽을 것.", "忽略 `NaN`。插值出来的点也计入，所以短缺口看起来很干净；要和 `SmoothSig_missingDataPercent` 一起看。")),
    ("SmoothSig_minDiam, SmoothSig_maxDiam", "px", T("minimum / maximum of the smooth signal", "평활 신호의 최소 / 최대", "平滑信号的最小 / 最大"), None),
    ("SmoothSig_missingDataPercent", "%", T("share of the segment that is `NaN`", "구간 중 `NaN` 비율", "段内为 `NaN` 的比例"), T("Only gaps over 250 ms between real valid points become `NaN`. This is the per-segment missingness; use it for quality control.", "실제 valid 점 사이 공백이 250 ms를 넘는 곳만 `NaN`. 구간별 결측률이며 품질 관리에 쓴다.", "只有真实 valid 点之间超过 250 ms 的缺口才会变成 `NaN`。这是每段的缺失率，质控用它。")),
    ("SmoothSig_sampleCount", "count", T("all 1000 Hz samples in the segment", "구간 안 1000 Hz 샘플 전부", "段内所有 1000 Hz 样本"), T("`NaN` ones included; about segment length × 1000 (a 0.5 s baseline gives 500).", "`NaN` 포함. 구간 길이 × 1000 정도(0.5 s 기준선은 500).", "含 `NaN`；约等于段长 × 1000（0.5 s 的 baseline 是 500）。")),
    ("ValidSamples_meanDiam", "px", T("mean of the real valid samples in the segment", "구간 안 실제 valid 샘플의 평균", "段内真实 valid 样本的均值"), T("No interpolation, no smoothing: only points that passed the three artifact filters.", "보간·평활 없음. 세 아티팩트 필터를 통과한 점만.", "没有插值和平滑：只含通过三道伪影滤波的点。")),
    ("ValidSamples_minDiam, ValidSamples_maxDiam", "px", T("minimum / maximum of the valid samples", "valid 샘플의 최소 / 최대", "valid 样本的最小 / 最大"), None),
    ("ValidSamples_validPercent", "%", T("valid fraction of the WHOLE recording", "기록 **전체**의 valid 비율", "**整段记录**的 valid 比例"), T("`validFraction × 100`: valid points divided by non-empty raw points over the whole recording. The same number on every row of a subject. It is not about this segment.", "`validFraction × 100`: 기록 전체에서 비어 있지 않은 원시 점 중 valid 점의 비율. 한 피험자의 모든 행에서 같다. 이 구간의 값이 아니다.", "`validFraction × 100`：整段记录里 valid 点数 ÷ 非空原始点数。同一被试每行都一样，与这一段无关。")),
    ("ValidSamples_sampleCount", "count", T("valid samples inside the segment", "구간 안 valid 샘플 수", "段内 valid 样本数"), T("At 60 Hz a 0.5 s baseline holds at most about 30.", "60 Hz에서 0.5 s 기준선은 최대 약 30.", "60 Hz 下 0.5 s 的 baseline 最多约 30 个。")),
]

KRET_ID = [
    ("segmentStart, segmentEnd", "s", T("segment boundaries", "구간 경계", "分段边界"), None),
    ("segmentName", "–", T("for example `countdown_004`", "예: `countdown_004`", "例如 `countdown_004`"), T("Segment type plus trial number; trial 4's countdown.", "구간 종류 + trial 번호. trial 4의 카운트다운.", "分段类型 + trial 编号；trial 4 的倒计时。")),
    ("segmentType", "–", T("`baseline` / `countdown` / `preOutcome` / `postOutcome`", "`baseline` / `countdown` / `preOutcome` / `postOutcome`", "`baseline` / `countdown` / `preOutcome` / `postOutcome`"), None),
    ("participant, trial", "–", T("subject id; trial 1–84", "피험자 ID; trial 1–84", "被试编号；trial 1–84"), None),
]

TRIALS_QC = [
    ("RejectCountdown", "0/1", T("trial rejected", "trial 제외", "该 trial 被剔除"), T("`countdown_SmoothSig_missingDataPercent > 50`. Analysis rule R1.", "`countdown_SmoothSig_missingDataPercent > 50`. 분석 규칙 R1.", "`countdown_SmoothSig_missingDataPercent > 50`。分析规则 R1。")),
    ("PreOutcomeMostlyMissing", "0/1", T("flag only, trial kept", "표시만 하고 trial은 유지", "只标记，trial 保留"), T("`preOutcome_SmoothSig_missingDataPercent > 50`. The trial's GLM modulator is not trustworthy. Rule R2.", "`preOutcome_SmoothSig_missingDataPercent > 50`. 그 trial의 GLM 조절 변수는 믿을 수 없다. 규칙 R2.", "`preOutcome_SmoothSig_missingDataPercent > 50`。该 trial 的 GLM 调节量不可信。规则 R2。")),
    ("SubjectExcluded", "0/1", T("whole subject excluded", "피험자 전체 제외", "整个被试被排除"), T("More than 20% of the subject's trials rejected. Rule R3 (Leuchs / Shechner 20% rule).", "피험자 trial의 20% 초과가 제외됨. 규칙 R3(Leuchs / Shechner 20% 규칙).", "该被试被剔除的 trial 超过 20%。规则 R3（Leuchs / Shechner 20% 规则）。")),
]

SUBJ_QC = [
    ("participant", "–", T("subject id", "피험자 ID", "被试编号"), None),
    ("nTrials, nRejected", "count", T("trials; rejected by R1", "trial 수; R1로 제외된 수", "trial 数；被 R1 剔除的数"), None),
    ("rejectPct", "%", T("`nRejected / nTrials × 100`", "`nRejected / nTrials × 100`", "`nRejected / nTrials × 100`"), None),
    ("subjectExcluded", "0/1", T("rejectPct above 20", "rejectPct가 20 초과", "rejectPct 超过 20"), None),
]

SEGCSV = [
    ("segmentName, segmentType", "–", T("as in `segmentsTable`", "`segmentsTable`과 같음", "同 `segmentsTable`"), None),
    ("segmentStart_s", "s", T("segment start", "구간 시작", "段起点"), T("Identical on every row of one segment.", "한 구간의 모든 행에서 동일.", "同一段的每一行相同。")),
    ("tRel_s", "s", T("sample time minus segment start", "샘플 시각 − 구간 시작", "样本时刻 − 段起点"), None),
    ("pupilDiameter_px", "px", T("smooth-signal diameter, 4 decimals", "평활 신호 직경, 소수 4자리", "平滑信号的直径，4 位小数"), T("The unit in the name follows `diameterUnit`. `NaN` where the gap exceeded 250 ms.", "이름의 단위는 `diameterUnit`을 따른다. 공백이 250 ms를 넘은 곳은 `NaN`.", "列名里的单位随 `diameterUnit`。缺口超过 250 ms 的位置为 `NaN`。")),
    ("gap_ms", "ms", T("distance between the two real valid points around this instant", "이 시점 앞뒤 실제 valid 점 사이 간격", "该时刻前后两个真实 valid 点之间的间隔"), T("0 when within 0.5 ms of a real point. 1 decimal.", "실제 점에서 0.5 ms 이내면 0. 소수 1자리.", "距真实点 0.5 ms 以内为 0；1 位小数。")),
    ("pupilDiameterZ", "z", T("only with `ZScore=true`", "`ZScore=true`일 때만", "仅在 `ZScore=true` 时有"), T("(value − whole-recording mean) / whole-recording SD, once per eye over the entire recording (Leuchs 2017), not within the segment.", "(값 − 기록 전체 평균) / 기록 전체 표준편차. 눈마다 기록 전체에서 한 번 계산(Leuchs 2017)하며 구간 안 z가 아님.", "（值 − 整段记录均值）/ 整段记录标准差，每只眼在整段记录上算一次（Leuchs 2017），不是段内 z。")),
]


def table(cols, lang, with_more=True):
    i = IDX[lang]
    head = "| %s | %s | %s | %s |" % (u("tbl_col", lang), u("tbl_unit", lang), u("tbl_mean", lang), u("tbl_more", lang))
    rows = [head, "|---|---|---|---|"]
    for name, unit, mean, more in cols:
        more_cell = "" if more is None else idet(u("tbl_more", lang), more[i])
        rows.append("| `%s` | %s | %s | %s |" % (name, unit, mean[i], more_cell))
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------------------
# final 69-column listing
# ---------------------------------------------------------------------------
STATS = ["segmentStart", "segmentEnd", "SmoothSig_meanDiam", "SmoothSig_minDiam", "SmoothSig_maxDiam",
         "SmoothSig_missingDataPercent", "SmoothSig_sampleCount", "ValidSamples_meanDiam", "ValidSamples_minDiam",
         "ValidSamples_maxDiam", "ValidSamples_validPercent", "ValidSamples_sampleCount"]
SEGS = [("baseline", 1), ("countdown", 2), ("preOutcome", 2), ("postOutcome", 3)]
EVNAMES = ["participant", "order", "run", "trial", "trial_in_run", "ymtc_marker", "trk_event", "time_ms",
           "t_from_onset_s", "expected_from_onset_s", "diff_s", "expected_duration_s", "condition", "timing",
           "certainty", "outcome", "actual_outcome", "step"]
QCN = ["RejectCountdown", "PreOutcomeMostlyMissing", "SubjectExcluded"]
assert len(EVNAMES) + len(SEGS) * len(STATS) + len(QCN) == 69


def final_list(lang):
    out = []
    n = 0
    out.append("**%s** (%d)" % ({"en": "Event columns, same as the event table", "ko": "이벤트 열(이벤트 표와 동일)", "zh": "事件列（同事件表）"}[lang], len(EVNAMES)))
    out.append("")
    out.append(", ".join("`%s`" % c for c in EVNAMES))
    out.append("")
    for seg, step in SEGS:
        lab = {"en": "Segment `%s` — written on rows with `step = %d`; `NaN` on the other rows of the trial",
               "ko": "구간 `%s` — `step = %d`인 행에만 값이 있고 같은 trial의 다른 행은 `NaN`",
               "zh": "分段 `%s` —— 只写在 `step = %d` 的行上，同一 trial 的其他行为 `NaN`"}[lang] % (seg, step)
        out.append("**%s** (%d)" % (lab, len(STATS)))
        out.append("")
        out.append(", ".join("`%s_%s`" % (seg, s) for s in STATS))
        out.append("")
    out.append("**%s** (%d)" % ({"en": "Quality control, copied onto every row of the trial (run-level rows: `NaN`)",
                                  "ko": "품질 관리 — trial의 모든 행에 복사(run 수준 행은 `NaN`)",
                                  "zh": "质控列 —— 复制到该 trial 的每一行（run 级的行为 `NaN`）"}[lang], len(QCN)))
    out.append("")
    out.append(", ".join("`%s`" % c for c in QCN))
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# upstream object fields: (name, (en,ko,zh))
# ---------------------------------------------------------------------------
RAWFILE_FIELDS = [
    ("diameterUnit", T("A text label for the unit of the diameters, for example `'mm'` or `'px'`. It is copied into every result and into the exported CSV column name. The package never converts units; the label is only a label.",
                       "직경 단위를 나타내는 문자열(예: `'mm'`, `'px'`). 모든 결과와 내보낸 CSV 열 이름에 복사된다. 패키지는 단위를 변환하지 않으며 라벨일 뿐이다.",
                       "直径单位的文字标签，例如 `'mm'`、`'px'`。会被复制到所有结果和导出 CSV 的列名里。包不会做单位换算，它只是个标签。")),
    ("diameter.t_ms", T("The time of every sample, in milliseconds, as one column vector. Must be sorted ascending (`issorted`) and should start at 0 (the original eye-tracker time goes into `zeroTime_ms`). Duplicate timestamps break the filters, so our converter keeps only the first of duplicates.",
                        "모든 샘플의 시각(ms), 열 벡터 하나. 오름차순이어야 하며(`issorted`) 0에서 시작하는 것이 좋다(원래 시선추적기 시각은 `zeroTime_ms`에). 타임스탬프가 중복되면 필터가 깨지므로 우리 변환기는 중복 중 첫 번째만 남긴다.",
                        "每个样本的时刻，单位毫秒，一个列向量。必须升序（`issorted`），最好从 0 开始（原始眼动仪时刻放进 `zeroTime_ms`）。重复时间戳会让滤波出错，所以我们的转换器只保留重复项里的第一个。")),
    ("diameter.L", T("The pupil diameter of the LEFT eye at each sample, same length as `t_ms`, `NaN` where the tracker gave nothing. Leave it empty (`[]`) if the left eye was not measured. By convention a single measured eye is stored here, as in the EyeLink example; our MRC data (one pupil) goes in `L`.",
                     "각 샘플의 왼쪽 눈 동공 직경. `t_ms`와 길이가 같고 추적기가 값을 주지 않은 곳은 `NaN`. 왼쪽 눈을 측정하지 않았으면 비워 둔다(`[]`). 눈이 하나만 측정되면 EyeLink 예제처럼 여기에 넣는 것이 관례이며, 우리 MRC 데이터(동공 하나)도 `L`에 넣는다.",
                     "每个样本的左眼瞳孔直径，长度与 `t_ms` 相同，眼动仪没给值的地方是 `NaN`。左眼没测就留空（`[]`）。约定只测一只眼时放在这里（EyeLink 例子就这样）；我们的 MRC 数据（单瞳孔）放在 `L`。")),
    ("diameter.R", T("The same for the RIGHT eye. Empty for us. If both `L` and `R` are present the package also builds a `mean` pupil from them.",
                     "오른쪽 눈에 대해 동일. 우리 데이터에서는 비어 있다. `L`과 `R`이 모두 있으면 둘의 평균인 `mean` 동공도 만든다.",
                     "右眼同理。我们的数据里是空的。`L` 和 `R` 都有时，包还会据此生成 `mean` 瞳孔。")),
    ("zeroTime_ms", T("The eye-tracker's own timestamp (ms) that corresponds to `t = 0`. Stored for the record only; the package never uses it.",
                      "`t = 0`에 해당하는 시선추적기 자체 타임스탬프(ms). 기록용으로만 저장되며 패키지는 쓰지 않는다.",
                      "对应 `t = 0` 的眼动仪自己的时间戳（毫秒）。只是存档，包本身不用。")),
    ("segmentsTable.segmentStart / segmentEnd", T("Start and end of each segment, in SECONDS (not ms) on the same clock as `t_ms/1000`. A `NaN` start or end makes that segment's statistics `NaN`. Segments may overlap.",
                                                  "각 구간의 시작과 끝, **초** 단위(ms 아님), `t_ms/1000`과 같은 시계. 시작 또는 끝이 `NaN`이면 그 구간의 통계도 `NaN`. 구간은 겹쳐도 된다.",
                                                  "每个分段的起止，单位是**秒**（不是毫秒），与 `t_ms/1000` 同一个时钟。起点或终点是 `NaN` 时，该段统计也是 `NaN`。分段可以重叠。")),
    ("segmentsTable.segmentName", T("A name for the segment, for example `countdown_004`. Shown in the plot and copied to the results.",
                                    "구간 이름(예: `countdown_004`). 그림에 표시되고 결과로 복사된다.",
                                    "分段名，例如 `countdown_004`。会显示在图上并复制到结果里。")),
    ("segmentsTable (extra columns)", T("Any other column (participant, trial, segmentType, condition …) is carried unchanged to the left of the result table. `exportSegments` additionally looks for a column called `segmentType`.",
                                        "그 밖의 모든 열(participant, trial, segmentType, condition …)은 결과 표 왼쪽에 그대로 따라온다. `exportSegments`는 `segmentType`이라는 열도 찾는다.",
                                        "其他任何列（participant、trial、segmentType、condition …）都会原样带到结果表的左侧。`exportSegments` 还会找名为 `segmentType` 的列。")),
]

PDM_PROPS = [
    ("filename, filepath", T("Name and folder of the .mat file this object was built from.", "이 객체를 만든 .mat 파일의 이름과 폴더.", "构造该对象所用的 .mat 文件的名字和文件夹。")),
    ("settings", T("Struct with two parts: `settings.raw` (artifact filters) and `settings.valid` (interpolation and low-pass). Every object carries its own copy.", "두 부분으로 된 구조체: `settings.raw`(아티팩트 필터)와 `settings.valid`(보간·저역통과). 객체마다 자기 사본을 가진다.", "有两部分的结构体：`settings.raw`（伪影滤波）和 `settings.valid`（插值与低通）。每个对象各带一份。")),
    ("eyesWithData", T("Which eyes have data: `{'left'}`, `{'right'}`, `{'left','right'}` or `{}`. Anything else raises an error. Decides which eyes are filtered and analysed.", "데이터가 있는 눈: `{'left'}`, `{'right'}`, `{'left','right'}`, `{}`. 그 밖의 값은 오류. 어느 눈을 필터·분석할지 결정한다.", "哪些眼有数据：`{'left'}`、`{'right'}`、`{'left','right'}` 或 `{}`，别的值会报错。决定对哪只眼做滤波和分析。")),
    ("timestamps_RawData_ms", T("The shared time vector of the raw samples (ms), from `diameter.t_ms`.", "원시 샘플의 공통 시간 벡터(ms), `diameter.t_ms`에서.", "原始样本共用的时间向量（毫秒），来自 `diameter.t_ms`。")),
    ("leftPupil_RawData, rightPupil_RawData", T("`RawSamplesModel` of each eye (empty if that eye has no data).", "각 눈의 `RawSamplesModel`(데이터가 없으면 비어 있음).", "每只眼的 `RawSamplesModel`（没有数据则为空）。")),
    ("leftPupil_ValidSamples, rightPupil_ValidSamples, meanPupil_ValidSamples", T("`ValidSamplesModel` of each eye, created by `processValidSamples`. `meanPupil_ValidSamples` exists only when both eyes have data.", "각 눈의 `ValidSamplesModel`, `processValidSamples`가 만든다. `meanPupil_ValidSamples`는 두 눈 모두 데이터가 있을 때만 존재.", "每只眼的 `ValidSamplesModel`，由 `processValidSamples` 生成。`meanPupil_ValidSamples` 只在双眼都有数据时存在。")),
    ("segmentsTable, zeroTime_ms, diameterUnit", T("Copied from the .mat file (see the file contents above).", ".mat 파일에서 복사(위의 파일 내용 참조).", "复制自 .mat 文件（见上面的文件内容）。")),
]

RAWSAMP_PROPS = [
    ("eye", T("`'left'` or `'right'`.", "`'left'` 또는 `'right'`.", "`'left'` 或 `'right'`。")),
    ("rawSample", T("The raw diameter vector of this eye, never modified.", "이 눈의 원시 직경 벡터, 수정되지 않는다.", "该眼的原始直径向量，从不被修改。")),
    ("isValid", T("Logical vector, one entry per raw sample: `true` = passed range, speed and deviation filters. This is what `filterRawData` produces. `NaN` raw samples are `false`.", "논리 벡터, 원시 샘플마다 하나: `true` = 범위·속도·편차 필터 통과. `filterRawData`의 결과. `NaN` 원시 샘플은 `false`.", "逻辑向量，每个原始样本一项：`true` = 通过范围、速度、偏离三道滤波。这是 `filterRawData` 的产出。`NaN` 原始样本为 `false`。")),
    ("speedFiltData", T("Intermediate results of the speed filter (only kept when `keepFilterData = true`): `maxDilationSpeeds` (for each sample, the larger absolute speed to its two neighbours, `NaN` only if both neighbours are more than 200 ms away), `isValid` (after the speed filter), `mad`, `thresh` (= median + 16 × MAD, the cut-off), `med_d` (the median).", "속도 필터의 중간 결과(`keepFilterData = true`일 때만 보관): `maxDilationSpeeds`(샘플마다 두 이웃과의 절대 속도 중 큰 값, 두 이웃이 모두 200 ms보다 멀 때만 `NaN`), `isValid`(속도 필터 이후), `mad`, `thresh`(중앙값 + 16 × MAD, 기준선), `med_d`(중앙값).", "速度滤波的中间结果（仅在 `keepFilterData = true` 时保存）：`maxDilationSpeeds`（每个样本与两侧邻点的绝对速度中较大的一个，仅当两侧邻点都相隔超过 200 ms 时才为 `NaN`）、`isValid`（速度滤波之后）、`mad`、`thresh`（= 中位数 + 16 × MAD，截断线）、`med_d`（中位数）。")),
    ("devFiltData", T("Intermediate results of the deviation filter, one column per pass (4 by default): `isValidPerPass`, `residualsPerPass` (distance from the smooth trend line), `threshPerPass`, `smoothBaselinePerPass` (the trend line). If a pass changes nothing, later passes copy it.", "편차 필터의 중간 결과, 반복(기본 4회)마다 한 열: `isValidPerPass`, `residualsPerPass`(평활 추세선으로부터의 거리), `threshPerPass`, `smoothBaselinePerPass`(추세선). 어떤 반복이 아무것도 바꾸지 않으면 이후 반복은 그 결과를 복사한다.", "偏离滤波的中间结果，每趟一列（默认 4 趟）：`isValidPerPass`、`residualsPerPass`（到平滑趋势线的距离）、`threshPerPass`、`smoothBaselinePerPass`（趋势线）。某一趟没有改变任何东西时，后面几趟直接复制它。")),
]

VALID_PROPS = [
    ("eye", T("`'left'`, `'right'` or `'mean'`.", "`'left'`, `'right'`, `'mean'`.", "`'left'`、`'right'` 或 `'mean'`。")),
    ("samples.t_ms, samples.pupilDiameter", T("Only the valid raw samples: their times (ms) and diameters.", "valid 원시 샘플만: 시각(ms)과 직경.", "只含 valid 原始样本：它们的时刻（毫秒）和直径。")),
    ("validFraction", T("valid samples divided by non-empty raw samples over the WHOLE recording (0–1). Reported as `ValidSamples_validPercent` × 100 on every row. For the `mean` pupil: the smaller of the two eyes.", "기록 **전체**에서 비어 있지 않은 원시 샘플 중 valid 샘플의 비율(0–1). 모든 행에 `ValidSamples_validPercent`(×100)로 보고된다. `mean` 동공은 두 눈 중 작은 값.", "**整段记录**里 valid 样本数 ÷ 非空原始样本数（0–1）。每行都以 `ValidSamples_validPercent`（×100）报告。`mean` 瞳孔取两只眼里较小的那个。")),
    ("signal.t", T("1000 Hz time axis of the smooth signal, in SECONDS.", "평활 신호의 1000 Hz 시간축, **초** 단위.", "平滑信号的 1000 Hz 时间轴，单位**秒**。")),
    ("signal.pupilDiameter", T("The smooth signal: valid samples linearly interpolated onto `signal.t`, then 4th-order 4 Hz Butterworth low-pass (zero phase, `filtfilt`). `NaN` where the gap between real valid points exceeds `interp_maxGap` (250 ms).", "평활 신호: valid 샘플을 `signal.t`로 선형 보간한 뒤 4차 4 Hz Butterworth 저역통과(영위상 `filtfilt`). 실제 valid 점 사이 공백이 `interp_maxGap`(250 ms)을 넘는 곳은 `NaN`.", "平滑信号：valid 样本线性插值到 `signal.t`，再做 4 阶 4 Hz Butterworth 低通（零相位，`filtfilt`）。真实 valid 点之间的缺口超过 `interp_maxGap`（250 ms）的位置为 `NaN`。")),
    ("signal.gap_ms", T("At each instant, the distance in ms between the two real valid samples around it; 0 within 0.5 ms of a real sample. (The class declares a field `gap`, the code writes `gap_ms`.)", "각 시점 앞뒤 두 실제 valid 샘플 사이의 거리(ms). 실제 샘플에서 0.5 ms 이내면 0. (클래스는 `gap` 필드를 선언하지만 코드는 `gap_ms`에 쓴다.)", "每个时刻前后两个真实 valid 样本之间的距离（毫秒）；距真实样本 0.5 ms 以内为 0。（类里声明的字段叫 `gap`，代码实际写入的是 `gap_ms`。）")),
]


def props(plist, lang):
    i = IDX[lang]
    return "\n".join(det("<code>%s</code>" % n, d[i]) for n, d in plist)


# ---------------------------------------------------------------------------
# settings (upstream) and trk2csv options
# ---------------------------------------------------------------------------
RAW_SET = [
    ("PupilDiameter_Min / _Max", "1.5 / 9", T("Range filter. The defaults are MILLIMETRES; pixel data must override them (`Examples/Dataset_1` uses 0.1 / inf). Our pipeline sets them from the data (0.5–99.5 percentile × 0.8 / 1.2) and prints the values.", "범위 필터. 기본값은 **밀리미터** 기준이므로 픽셀 데이터는 바꿔야 한다(`Examples/Dataset_1`은 0.1 / inf). 우리 파이프라인은 데이터에서 정하고(0.5–99.5 백분위 × 0.8 / 1.2) 값을 출력한다.", "范围滤波。默认值是**毫米**，像素数据必须覆盖（`Examples/Dataset_1` 用 0.1 / inf）。我们的管线按数据设定（0.5–99.5 百分位 × 0.8 / 1.2）并打印数值。")),
    ("islandFilter_islandSeperation_ms", "40 ms", T("How far from other samples a cluster must be to count as an island.", "다른 샘플에서 얼마나 떨어져야 섬으로 보는가.", "一簇样本离其他样本多远才算“孤岛”。")),
    ("islandFilter_minIslandWidth_ms", "50 ms", T("Islands narrower than this are invalid.", "이보다 좁은 섬은 무효.", "比这窄的孤岛判无效。")),
    ("dilationSpeedFilter_MadMultiplier", "16", T("Speed above median + this × MAD is invalid (catches blink edges).", "속도가 중앙값 + 이 값 × MAD를 넘으면 무효(눈 깜빡임 가장자리 포착).", "速度超过 中位数 + 该倍数 × MAD 判无效（抓眨眼边缘）。")),
    ("dilationSpeedFilter_maxGap_ms", "200 ms", T("Speed is only computed when two valid samples are closer than this.", "두 valid 샘플이 이보다 가까울 때만 속도를 계산.", "只有两个 valid 样本相隔小于它时才计算速度。")),
    ("gapDetect_minWidth / _maxWidth", "75 / 2000 ms", T("A missing stretch of this width counts as a gap whose edges get padded.", "이 폭의 결측 구간을 공백으로 보고 가장자리를 추가로 버린다.", "这个宽度范围的缺失段算“缺口”，缺口边缘会再被剔除一小段。")),
    ("gapPadding_backward / _forward", "50 / 50 ms", T("Extra samples rejected before / after such a gap.", "그런 공백 앞/뒤로 추가로 버리는 길이.", "这种缺口前 / 后额外剔除的长度。")),
    ("residualsFilter_passes", "4", T("Passes of the trend-deviation filter.", "추세 편차 필터의 반복 횟수.", "趋势偏离滤波的趟数。")),
    ("residualsFilter_MadMultiplier", "16", T("Deviation above median + this × MAD from the trend is invalid.", "추세에서 중앙값 + 이 값 × MAD 이상 벗어나면 무효.", "偏离趋势线超过 中位数 + 该倍数 × MAD 判无效。")),
    ("residualsFilter_interpFs / _lowpassCF", "100 Hz / 16 Hz", T("Resampling rate and cut-off used to build the trend line (1st-order Butterworth).", "추세선을 만들 때의 재표본화율과 차단 주파수(1차 Butterworth).", "生成趋势线用的重采样率和截止频率（1 阶 Butterworth）。")),
    ("keepFilterData", "true", T("Keep `speedFiltData` / `devFiltData`. Uses memory; set `false` after tuning.", "`speedFiltData` / `devFiltData` 보관. 메모리를 많이 쓰므로 조정 후 `false`.", "保存 `speedFiltData` / `devFiltData`。占内存，调完参数后设 `false`。")),
]
VALID_SET = [
    ("interp_upsamplingFreq", "1000 Hz", T("Sampling rate of the smooth signal.", "평활 신호의 샘플링 주파수.", "平滑信号的采样率。")),
    ("LpFilt_B / LpFilt_A", "order 4, 4 Hz", T("Low-pass coefficients computed from order 4 and cut-off 4 Hz at 1000 Hz (zero-phase `filtfilt`).", "4차, 1000 Hz에서 차단 4 Hz로 계산한 저역통과 계수(영위상 `filtfilt`).", "由 4 阶、1000 Hz 下截止 4 Hz 算出的低通系数（零相位 `filtfilt`）。")),
    ("interp_maxGap", "250 ms", T("Gaps between real valid points larger than this become `NaN` in the smooth signal.", "실제 valid 점 사이 공백이 이보다 크면 평활 신호에서 `NaN`.", "真实 valid 点之间超过它的缺口，在平滑信号里变成 `NaN`。")),
]
TRK_OPT = [
    ("OutFolder", "folder of the .trk", T("Where the csv goes.", "csv를 쓸 폴더.", "csv 写到哪里。")),
    ("Overwrite", "true", T("Overwrite an existing csv.", "기존 csv 덮어쓰기.", "覆盖已有 csv。")),
    ("WriteReport", "false", T("Also write `<name>_issues.csv`.", "`<name>_issues.csv`도 쓰기.", "同时写 `<name>_issues.csv`。")),
    ("ExpectedRuns", "4", T("Expected number of `START` events.", "기대하는 `START` 개수.", "预期的 `START` 个数。")),
    ("ExpectedTrialsPerRun", "21", T("Expected trials per run (84 in total).", "run당 기대 trial 수(총 84).", "每个 run 预期的 trial 数（共 84）。")),
    ("CueDurationSec / CueToleranceSec", "1.0 / 0.001", T("Cue length in the task setting, and the allowed difference.", "과제 설정의 cue 길이와 허용 오차.", "任务设定的 cue 时长及允许的差。")),
    ("MinValidFraction", "0.5", T("Pupil-valid fraction below this is reported (`LOW_PUPIL_VALID`); nothing is dropped.", "동공 유효 비율이 이보다 낮으면 보고(`LOW_PUPIL_VALID`). 아무것도 버리지 않는다.", "有瞳孔数据的比例低于它就报告（`LOW_PUPIL_VALID`）；不删任何东西。")),
    ("MaxGapMs", "200", T("Sample spacing above this is reported (`TIME_GAP`).", "샘플 간격이 이보다 크면 보고(`TIME_GAP`).", "样本间隔超过它就报告（`TIME_GAP`）。")),
    ("Quiet", "false", T("Suppress printing.", "출력 억제.", "不打印。")),
]
KRET_OPT = [
    ("PupilMeasure", "'mean'", T("`'mean'` / `'2a'` / `'2b'`: which ellipse axis (or the mean of both) becomes the pupil size.", "`'mean'` / `'2a'` / `'2b'`: 어느 타원 축(또는 평균)을 동공 크기로 쓰는가.", "`'mean'` / `'2a'` / `'2b'`：用哪个椭圆轴（或两者平均）作为瞳孔大小。")),
    ("BaselineWinSec", "0.5", T("Length of the pre-cue baseline segment; 0 turns it off.", "cue 이전 기준선 구간 길이. 0이면 끈다.", "cue 前 baseline 段的长度；0 表示关闭。")),
    ("PreOutcomeWinSec / PostOutcomeWinSec", "2.0 / 2.0", T("Length of the segments before and after the outcome; 0 turns the pre-outcome one off.", "결과 전/후 구간 길이. 0이면 결과 전 구간을 끈다.", "Outcome 前 / 后分段的长度；设 0 可关闭 outcome 前的那段。")),
]


def set_table(rows, lang):
    i = IDX[lang]
    head = "| %s | default | %s |\n|---|---|---|\n" % ({"en": "setting", "ko": "설정", "zh": "设置"}[lang], u("tbl_mean", lang))
    return head + "\n".join("| `%s` | %s | %s |" % (n, d, m[i]) for n, d, m in rows) + "\n"


# ---------------------------------------------------------------------------
# helper-function table, examples, troubleshooting, limitations
# ---------------------------------------------------------------------------
HELPERS = [
    ("rawDataFilter.m", T("Main function calls `removeOutOfBounds` (range) → `madSpeedFilter` (speed, catches blinks) → `madDeviationFilter` (deviation from trend). `removeLoners` (isolated points) is called repeatedly inside all three, `expandGaps` (reject around gaps) inside the speed filter; `madCalc` computes MAD thresholds. With no arguments it returns the default `settings.raw`.", "메인 함수가 `removeOutOfBounds`(범위) → `madSpeedFilter`(속도, 눈 깜빡임) → `madDeviationFilter`(추세 이탈) 순으로 호출. 고립점 정리 `removeLoners`는 세 단계 안에서 반복 호출되고 공백 확장 `expandGaps`는 속도 필터 안에서 호출됨. `madCalc`는 MAD 임계값 계산. 인수 없이 호출하면 기본 `settings.raw` 반환.", "主函数依次调用 `removeOutOfBounds`（范围）→ `madSpeedFilter`（速度，抓眨眼）→ `madDeviationFilter`（偏离趋势）。孤立点清理 `removeLoners` 在三步内部反复调用，`expandGaps`（缺口前后扩剔）在速度滤波里调用；`madCalc` 算 MAD 阈值。无参数调用返回默认的 `settings.raw`。")),
    ("genMeanDiaSamples.m", T("Combines two eyes into one mean diameter; called by `processValidSamples`; unused for one-eye data.", "두 눈을 합쳐 평균 직경을 만든다. `processValidSamples`가 호출. 한 눈 데이터에서는 쓰이지 않음.", "把双眼合成一条平均直径；由 `processValidSamples` 调用；单眼数据用不到。")),
    ("plotSegments.m", T("Draws the segment table as colour patches; called by `plotData`.", "구간 표를 색 블록으로 그린다. `plotData`가 호출.", "把分段表画成色块；由 `plotData` 调用。")),
    ("printToConsole.m", T("Progress messages; internal.", "진행 메시지, 내부용.", "打印进度，内部用。")),
    ("legacyModeCheck.m", T("Adds `LEGACY/` to the path for MATLAB older than 8.3 (no `table`); nothing on newer versions.", "MATLAB이 8.3보다 오래돼 `table`이 없으면 `LEGACY/`를 경로에 추가. 새 버전에서는 아무 일도 안 함.", "MATLAB 低于 8.3（没有 `table`）时把 `LEGACY/` 加进路径；新版本什么也不做。")),
    ("FALLBACK/", T("Replacements for `butter`, `filtfilt`, `histc`, `nanmin` / `nanmax` / `nanmean` / `nanmedian` for MATLAB without the toolbox or with the function removed. TRAP: `addpath(genpath(...))` puts folders at the FRONT, so a FALLBACK function shadows the real toolbox one; use `addpath(..., '-end')` to prefer the toolbox. This machine has no Statistics toolbox, so the `nan*` ones are always FALLBACK.", "툴박스가 없거나 함수가 제거된 MATLAB용 `butter`, `filtfilt`, `histc`, `nanmin` / `nanmax` / `nanmean` / `nanmedian` 대체 구현. 함정: `addpath(genpath(...))`는 폴더를 **맨 앞**에 넣어 FALLBACK이 진짜 툴박스 함수를 가린다. 툴박스를 우선하려면 `addpath(..., '-end')`. 이 컴퓨터에는 Statistics 툴박스가 없어 `nan*`는 항상 FALLBACK.", "给没有工具箱或函数已被移除的 MATLAB 用的 `butter`、`filtfilt`、`histc`、`nanmin` / `nanmax` / `nanmean` / `nanmedian` 替代实现。陷阱：`addpath(genpath(...))` 把文件夹放到路径**最前面**，FALLBACK 会盖住真工具箱函数；想优先用工具箱就用 `addpath(..., '-end')`。本机没有 Statistics 工具箱，所以 `nan*` 一直是 FALLBACK。")),
    ("LEGACY/", T("Emulates `table` for very old MATLAB.", "아주 오래된 MATLAB에서 `table`을 흉내 냄.", "给很老的 MATLAB 模拟 `table`。")),
]

YMTC_CHAIN = {
 "en": """```
trk2csv_batch ──▶ trk2csv ──▶ private/readTrk ─▶ private/labelSamples ─▶ private/checkTrk
                                  (parse)          (events on samples)      (record only)

ymtcEventTableBatch ──▶ ymtcEventTable ──▶ readOrder()   (subfunction, same file)
         │                    │
         │                    └──▶ 05_markers/05_<sub>_markers[_5step].csv
         └──▶ ymtcTrialWide  / ymtcTimingCheck     (read that table, write one file each)

ymtcRunCheck     standalone: reads 03_events, writes 07_checks/07_all_run_check.csv
ymtcConfig       read by every ymtc* function: where the folders are
checkDocs        compares docs/02 with the real header of every output table
```""",
 "ko": """```
trk2csv_batch ──▶ trk2csv ──▶ private/readTrk ─▶ private/labelSamples ─▶ private/checkTrk
                                  (파싱)            (샘플에 이벤트)          (기록만)

ymtcEventTableBatch ──▶ ymtcEventTable ──▶ readOrder()   (같은 파일의 하위 함수)
         │                    │
         │                    └──▶ 05_markers/05_<sub>_markers[_5step].csv
         └──▶ ymtcTrialWide  / ymtcTimingCheck     (표를 읽고 파일 하나씩 씀)

ymtcRunCheck     독립: 03_events를 읽고 07_checks/07_all_run_check.csv를 씀
ymtcConfig       모든 ymtc* 함수가 읽음: 폴더 위치
checkDocs        docs/02와 실제 표 헤더를 비교
```""",
 "zh": """```
trk2csv_batch ──▶ trk2csv ──▶ private/readTrk ─▶ private/labelSamples ─▶ private/checkTrk
                                  （解析）          （事件挂到样本）        （只记录）

ymtcEventTableBatch ──▶ ymtcEventTable ──▶ readOrder()   （同文件末尾的子函数）
         │                    │
         │                    └──▶ 05_markers/05_<sub>_markers[_5step].csv
         └──▶ ymtcTrialWide  / ymtcTimingCheck     （读那张表，各写一个文件）

ymtcRunCheck     独立：读 03_events，写 07_checks/07_all_run_check.csv
ymtcConfig       所有 ymtc* 函数都读它：文件夹在哪
checkDocs        比对 docs/02 和每张输出表的真实表头
```""",
}

YMTC_TABLE = [
 ("trk2csv.m", "87", T("one .trk → one per-sample CSV + a report", "trk 하나 → 샘플 CSV 하나 + 보고서", "一个 .trk → 一个逐样本 CSV + 报告"), T("02_samples/<name>.csv", "02_samples/<name>.csv", "02_samples/<name>.csv")),
 ("trk2csv_batch.m", "76", T("a folder of .trk → the same, plus two QC tables", "trk 폴더 → 같은 것 + QC 표 두 개", "整个文件夹 → 同上，另加两张 QC 表"), T("02_all_qc_summary.csv, 02_all_issues.csv", "02_all_qc_summary.csv, 02_all_issues.csv", "02_all_qc_summary.csv、02_all_issues.csv")),
 ("private/readTrk.m", "79", T("parse the text log into header / samples / events", "텍스트 로그를 헤더/샘플/이벤트로 파싱", "把文本日志解析成表头/样本/事件"), T("in memory", "메모리", "内存")),
 ("private/labelSamples.m", "46", T("attach events to samples, carry run / trial / phase forward", "이벤트를 샘플에 붙이고 run/trial/phase를 이어감", "事件挂到样本，向后填 run/trial/phase"), T("in memory", "메모리", "内存")),
 ("private/checkTrk.m", "134", T("compare with what the task should have produced; record, never repair", "과제가 만들어야 할 것과 비교; 기록만", "与任务应有状态对比；只记录不修补"), T("02_all_issues.csv rows", "02_all_issues.csv 행", "02_all_issues.csv 的行")),
 ("ymtcEventTable.m", "184", T("one subject → one row per marker, in task order", "피험자 한 명 → 마커 한 줄씩, 과제 순서", "一个被试 → 每 marker 一行，按任务顺序"), T("05_markers/05_<sub>_markers[_5step].csv", "05_markers/05_<sub>_markers[_5step].csv", "05_markers/05_<sub>_markers[_5step].csv")),
 ("ymtcEventTableBatch.m", "122", T("loop over subjects, add the summary and the combined tables", "피험자 반복 + 요약표와 통합표", "循环被试，加汇总表和合并表"), T("05_all_markers*.csv, 05_all_markers_summary.csv", "05_all_markers*.csv, 05_all_markers_summary.csv", "05_all_markers*.csv、05_all_markers_summary.csv")),
 ("ymtcTimingCheck.m", "71", T("descriptive diff_s per subject and marker", "피험자×마커별 diff_s 요약", "按被试 × marker 汇总 diff_s"), T("05_all_timing_check.csv", "05_all_timing_check.csv", "05_all_timing_check.csv")),
 ("ymtcTrialWide.m", "68", T("long marker table → one row per trial", "긴 마커 표 → trial 한 줄", "长表 → 一 trial 一行"), T("05_all_trials_wide.csv", "05_all_trials_wide.csv", "05_all_trials_wide.csv")),
 ("ymtcRunCheck.m", "117", T("is every run really 21 trials (BurnInStart as the boundary)", "모든 run이 21 trial인가 (BurnInStart 기준)", "每个 run 是否 21 trial（用 BurnInStart 分界）"), T("07_checks/07_all_run_check.csv", "07_checks/07_all_run_check.csv", "07_checks/07_all_run_check.csv")),
 ("ymtcConfig.m", "40", T("folder layout; no path is hard-coded", "폴더 위치; 경로 하드코딩 없음", "文件夹位置；不写死路径"), T("struct C", "구조체 C", "结构体 C")),
 ("checkDocs.m", "101", T("compare docs/02 with the real table headers", "docs/02와 실제 표 헤더 비교", "比对 docs/02 与真实表头"), T("console", "콘솔", "终端")),
]

YMTC_FILES = [
    ("trk2csv.m", T("One `.trk` → one per-sample CSV plus a report. Needs no toolbox.", "`.trk` 하나 → 샘플 단위 CSV 하나와 보고서. 툴박스 불필요.", "一个 `.trk` → 一个逐样本 CSV 和一份报告。不需要工具箱。")),
    ("trk2csv_batch.m", T("A folder of `.trk` → `csv/` plus `trk2csv_qc_summary.csv` and `trk2csv_issues.csv`.", "`.trk` 폴더 → `csv/`와 `trk2csv_qc_summary.csv`, `trk2csv_issues.csv`.", "一个 `.trk` 文件夹 → `csv/`，外加 `trk2csv_qc_summary.csv` 与 `trk2csv_issues.csv`。")),
    ("private/readTrk.m, labelSamples.m, checkTrk.m", T("Parse the text log; attach events and carry run / trial / phase forward; compare with what the task should have produced (record only).", "텍스트 로그 파싱; 이벤트를 붙이고 run / trial / phase를 이어 간다; 과제가 만들어야 할 것과 비교(기록만).", "解析文本日志；挂事件并向后延续 run / trial / phase；与任务应有的样子对比（只记录）。")),
    ("ymtcEventTable.m", T("One subject → marker table in task order. Picks the trial order by matching countdown lengths.", "피험자 한 명 → 과제 순서의 마커 표. 카운트다운 길이를 맞춰 trial 순서를 고른다.", "单个被试 → 按任务顺序排列的 marker 表。通过匹配倒计时长度选 trial 顺序。")),
    ("ymtcEventTableBatch.m", T("All subjects at once, plus `event_table_summary.csv` and the combined tables.", "모든 피험자를 한 번에, 그리고 `event_table_summary.csv`와 합본 표.", "一次处理所有被试，并产出 `event_table_summary.csv` 与合并表。")),
    ("ymtcRunCheck.m", T("Is every run really 21 trials? → `run_check.csv`.", "모든 run이 정말 21 trial인가? → `run_check.csv`.", "每个 run 真的是 21 个 trial 吗？→ `run_check.csv`。")),
    ("ymtcTimingCheck.m, ymtcTrialWide.m", T("Read the marker table: `timing_check.csv` and `all_subjects_trials_wide.csv`.", "마커 표를 읽는다: `timing_check.csv`, `all_subjects_trials_wide.csv`.", "读取 marker 表：生成 `timing_check.csv` 与 `all_subjects_trials_wide.csv`。")),
    ("ymtcMergeResults.m", T("Joins the 5-step marker table with `kret_results.csv` and `trials_qc.csv` by participant + trial → `06_最终结果/<sub>_final.csv` and `all_subjects_final.csv` (69 columns). Nothing is repaired; a trial with no Kret row stays `NaN`.", "5단계 마커 표를 participant + trial 기준으로 `kret_results.csv`, `trials_qc.csv`와 결합 → `06_最终结果/<sub>_final.csv`, `all_subjects_final.csv`(69열). 아무것도 고치지 않으며 Kret 행이 없는 trial은 `NaN`.", "按 participant + trial 把 5 步 marker 表与 `kret_results.csv`、`trials_qc.csv` 合并 → `06_最终结果/<sub>_final.csv` 和 `all_subjects_final.csv`（69 列）。不做修补，没有 Kret 行的 trial 保持 `NaN`。")),
    ("csv2kretmat.m, example_kret_pipeline.m", T("Adapter and batch script for the Kret pipeline (in `代码_matlab/`, outside this repository). The adapter re-references time to 0, removes duplicate timestamps (keeps the first), sets `NaN` where `pupil_valid == 0`, and writes `diameterUnit = 'px'`.", "Kret 파이프라인용 어댑터와 일괄 실행 스크립트(`代码_matlab/`, 이 저장소 밖). 어댑터는 시간을 0 기준으로 바꾸고, 중복 타임스탬프를 제거(첫 번째 유지)하고, `pupil_valid == 0`인 곳을 `NaN`으로 하며 `diameterUnit = 'px'`를 쓴다.", "Kret 管线的适配器和批量脚本（在 `代码_matlab/`，不在本仓库内）。适配器把时间重新参考到 0、去掉重复时间戳（保留第一个）、把 `pupil_valid == 0` 处设为 `NaN`，并写入 `diameterUnit = 'px'`。")),
    ("ymtcConfig.m, checkDocs.m", T("Folder locations (no absolute path in the repository); `checkDocs` compares the documented columns with the real CSV headers.", "폴더 위치(저장소에 절대 경로 없음); `checkDocs`는 문서화된 열과 실제 CSV 헤더를 비교.", "文件夹位置（仓库里没有绝对路径）；`checkDocs` 把文档里的列与真实 CSV 表头对比。")),
]
EXAMPLES = [
    ("Dataset_1", T("SR-Research Eyelink, ONE pupil. `batchFileConverter_Dataset1.m` (EDF → .mat) and `main_Dataset1.m` (full pipeline). It sets `PupilDiameter_Max = inf`, `PupilDiameter_Min = 0.1` (arbitrary units) and `keepFilterData = true`.", "SR-Research Eyelink, **동공 하나**. `batchFileConverter_Dataset1.m`(EDF → .mat), `main_Dataset1.m`(전체 파이프라인). `PupilDiameter_Max = inf`, `PupilDiameter_Min = 0.1`(임의 단위), `keepFilterData = true`로 설정.", "SR-Research Eyelink，**单瞳孔**。`batchFileConverter_Dataset1.m`（EDF → .mat）与 `main_Dataset1.m`（完整流水线）。设置了 `PupilDiameter_Max = inf`、`PupilDiameter_Min = 0.1`（任意单位）、`keepFilterData = true`。")),
    ("Dataset_2", T("E-Prime + Tobii, TWO pupils. `batchFileConverter_Dataset2.m` (.gazedata → .mat) and `main_Dataset2.m`.", "E-Prime + Tobii, **동공 둘**. `batchFileConverter_Dataset2.m`(.gazedata → .mat), `main_Dataset2.m`.", "E-Prime + Tobii，**双瞳孔**。`batchFileConverter_Dataset2.m`（.gazedata → .mat）与 `main_Dataset2.m`。")),
]
TROUBLE = [
    ("'t_ms' must be sorted!", T("timestamps not ascending (duplicate or backward timestamps in the trk)", "타임스탬프가 오름차순이 아님(trk의 중복·역행 타임스탬프)", "时间戳不升序（trk 里有重复或倒退的时间戳）"), T("sort / deduplicate in the converter, not inside the package; record the duplicates", "변환기에서 정렬·중복 제거(패키지 안에서 고치지 않음); 중복은 기록", "在转换器里排序、去重，不要改包内部；重复项要记录下来")),
    ("'L' must be empty, or have the same length as 't_ms'", T("diameter and time vectors differ in length", "직경과 시간 벡터의 길이가 다름", "直径向量和时间向量长度不一致"), T("check lengths in the converter", "변환기에서 길이 확인", "在转换器里检查长度")),
    ("No settings present.", T("`PupilDataModel` built without `settings`", "`settings` 없이 `PupilDataModel`을 만듦", "构造 `PupilDataModel` 时没传 `settings`"), T("start from `PupilDataModel.getDefaultSettings()` and edit", "`PupilDataModel.getDefaultSettings()`로 받아서 수정", "用 `PupilDataModel.getDefaultSettings()` 取一份再改")),
    ("Interpolation cannot be performed.", T("fewer than 2 valid points for that eye (wrong range, or all noise)", "그 눈의 valid 점이 2개 미만(범위 오설정 또는 전부 잡음)", "该眼 valid 点少于 2 个（范围设错或全是噪声）"), T("check that `PupilDiameter_Min/Max` match the unit", "`PupilDiameter_Min/Max`가 단위에 맞는지 확인", "检查 `PupilDiameter_Min/Max` 是否匹配单位")),
    ("almost every sample is invalid", T("default range 1.5–9 is mm, pixel data lies outside", "기본 범위 1.5–9는 mm 기준, 픽셀 데이터는 범위 밖", "默认范围 1.5–9 是毫米，像素数据全在范围外"), T("set the range in the real unit", "실제 단위로 범위 설정", "按实际单位设范围")),
    ("warning pupilSize:edgeClamp", T("floating-point error put upsampled times outside the valid range; they were clamped", "부동소수점 오차로 업샘플 시각이 valid 범위 밖에 놓여 경계로 보정됨", "浮点误差让上采样时刻落在 valid 区间外，被夹回边界"), T("only a notice; investigate if the count is large", "알림일 뿐. 개수가 많을 때만 조사", "只是提示；个数多才需要查")),
    ("ValidSamples_validPercent identical on every row", T("whole-recording value by design", "설계상 기록 전체 값", "按设计就是整段记录的值"), T("use `SmoothSig_missingDataPercent` for per-segment missingness", "구간별 결측은 `SmoothSig_missingDataPercent`", "看每段缺失率用 `SmoothSig_missingDataPercent`")),
    ("SmoothSig_meanDiam looks fine but the data is poor", T("gaps shorter than 250 ms were interpolated over", "250 ms 미만 공백이 보간으로 메워짐", "小于 250 ms 的缺口被插值填平了"), T("read `missingDataPercent` and `ValidSamples_sampleCount` too", "`missingDataPercent`와 `ValidSamples_sampleCount`도 함께 본다", "同时看 `missingDataPercent` 和 `ValidSamples_sampleCount`")),
    ("a whole result row is NaN", T("segment start/end is `NaN` (missing event), or no samples fall inside", "구간 시작/끝이 `NaN`(이벤트 없음) 또는 구간 안에 샘플이 없음", "分段起 / 止是 `NaN`（缺事件），或段内没有样本"), T("check the event table for the missing marker; nothing is imputed", "이벤트 표에서 빠진 마커 확인. 대체값은 넣지 않는다", "去事件表里找缺的 marker；不会补值")),
    ("plotData does nothing / is skipped", T("`-batch` has no desktop", "`-batch`에는 데스크톱이 없음", "`-batch` 没有桌面"), T("run in desktop MATLAB", "데스크톱 MATLAB에서 실행", "在桌面 MATLAB 里运行")),
    ("plotData shows one file only", T("`plotMultipleFiles = false` in the source (heavy)", "소스에 `plotMultipleFiles = false`(무거움)", "源码里 `plotMultipleFiles = false`（很吃资源）"), T("change that switch in `PupilDataModel.m`", "`PupilDataModel.m`에서 그 스위치 변경", "改 `PupilDataModel.m` 里的这个开关")),
    ("addpath fails in Examples", T("paths written with Windows backslashes `..\\..\\helperFunctions\\`", "경로가 Windows 역슬래시로 적혀 있음", "路径写成 Windows 反斜杠"), T("use `../../helperFunctions/` on macOS / Linux", "macOS / Linux에서는 `../../helperFunctions/`", "macOS / Linux 改成 `../../helperFunctions/`")),
    ("`MATLAB -batch` fails with several lines", T("`-batch` takes ONE line of command", "`-batch`는 한 줄 명령만 받음", "`-batch` 后面只能写一行命令"), T("put the code in a script file and `run('x.m')`", "코드를 스크립트 파일에 넣고 `run('x.m')`", "把代码放进脚本文件，再 `run('x.m')`")),
]


def trouble_table(lang):
    i = IDX[lang]
    head = {"en": "| symptom | cause | fix |", "ko": "| 증상 | 원인 | 해결 |", "zh": "| 症状 | 原因 | 修法 |"}[lang]
    return head + "\n|---|---|---|\n" + "\n".join("| %s | %s | %s |" % (s if s.startswith("`") else "`%s`" % s if " " not in s or s[0].islower() is False else s, c[i], f[i]) for s, c, f in TROUBLE) + "\n"


# ---------------------------------------------------------------------------
# prose
# ---------------------------------------------------------------------------
FLOW = {
    "en": """```
01 raw trk    (01_raw_trk/*.trk)      the recording date lives in these names; never renamed
      │  trk2csv_batch
      ▼
02 samples    (02_samples/subNNN_*.csv, 21 cols) + 02_all_qc_summary.csv + 02_all_issues.csv
      │
      ├──▶ 03 events      (03_events/subNNN_events.csv)
      │        │  ymtcEventTable (+ TrialOrder-HK/*.xlsx)
      │        ▼
      │   05 markers     (05_markers/05_all_markers.csv, 18 cols) · 05_all_markers_5step.csv
      │        ├ ymtcTrialWide    → 05_all_trials_wide.csv (14)
      │        └ ymtcTimingCheck  → 05_all_timing_check.csv (7)
      │
      └──▶ 04 pupil       (04_pupil/) csv2kretmat → .mat → PupilDataModel
               │  04_all_segments.csv (16) · 04_all_trials_qc.csv (19) · 04_all_subjects_qc.csv (5)
               │  segments/subNNN_leftpupil_segments.csv
               ▼
         06 merged      (06_merged/06_all_merged.csv, 69 cols) = 05 markers + 4 segments x 12 stats + 3 QC flags

side check, feeds nothing downstream:
     03 events ──ymtcRunCheck──▶ 07 checks  (07_checks/07_all_run_check.csv, 9)
```

Two branches leave 02 — 03 (events) and 04 (pupil metrics) — and neither depends on the other.
03 feeds 05; 04 and 05 are merged into 06. 07 only inspects 03.""",
    "ko": """```
01 원본 trk      01_원본trk/*.trk              녹화 날짜가 파일명에 있음; 이름 변경 금지
      │  trk2csv_batch
      ▼
02 샘플          02_샘플/subNNN_*.csv (21열) + 02_all_qc_summary.csv + 02_all_issues.csv
      │
      ├──▶ 03 이벤트    03_이벤트/subNNN_events.csv
      │        │  ymtcEventTable (+ TrialOrder-HK/*.xlsx)
      │        ▼
      │   05 marker 표  05_all_markers.csv (18열) · 05_all_markers_5step.csv
      │        ├ ymtcTrialWide    → 05_all_trials_wide.csv (14)
      │        └ ymtcTimingCheck  → 05_all_timing_check.csv (7)
      │
      └──▶ 04 눈동자 지표  csv2kretmat → .mat → PupilDataModel
               │  04_all_segments.csv (16) · 04_all_trials_qc.csv (19) · 04_all_subjects_qc.csv (5)
               │  segments/subNNN_leftpupil_segments.csv
               ▼
         06 병합표      06_all_merged.csv (69열) = 05 marker + 4구간 × 12통계 + 3 QC 플래그

별도 점검(다운스트림 없음):
     03 이벤트 ──ymtcRunCheck──▶ 07 점검  07_all_run_check.csv (9)
```

02에서 두 갈래(03 이벤트 / 04 눈동자 지표)로 나뉘고, 03이 05를 만들며,
04와 05가 06에서 합쳐진다. 07은 03만 검사한다.""",
    "zh": """```
01 原始 trk      01_raw_trk/*.trk              录制日期在文件名里，永不改名
      │  trk2csv_batch
      ▼
02 样本          02_samples/subNNN_*.csv（21 列）+ 02_all_qc_summary.csv + 02_all_issues.csv
      │
      ├──▶ 03 事件      03_events/subNNN_events.csv
      │        │  ymtcEventTable（+ TrialOrder-HK/*.xlsx）
      │        ▼
      │   05 marker 表  05_all_markers.csv（18 列）· 05_all_markers_5step.csv
      │        ├ ymtcTrialWide    → 05_all_trials_wide.csv（14）
      │        └ ymtcTimingCheck  → 05_all_timing_check.csv（7）
      │
      └──▶ 04 瞳孔指标  csv2kretmat → .mat → PupilDataModel
               │  04_all_segments.csv（16）· 04_all_trials_qc.csv（19）· 04_all_subjects_qc.csv（5）
               │  segments/subNNN_leftpupil_segments.csv
               ▼
         06 合并表     06_all_merged.csv（69 列）= 05 marker + 4 段 × 12 统计 + 3 个质控列

旁路检查（不喂给下游）：
     03 事件 ──ymtcRunCheck──▶ 07 检查  07_all_run_check.csv（9）
```

02 之后分成两路：03 事件、04 瞳孔指标，互不依赖；03 喂给 05，04 和 05 在 06 合并；07 只检查 03。""",
}



REVIEW = {
 "en": """## 9. Review map: what to read, and in what order

If you have to check this code yourself, this is the shortest route. Every path below is real; the line counts are taken from the files.

```
code/ymtc/                        in this repository
  ymtcEventTable.m                184   the marker table itself
  trk2csv.m                        87   one .trk -> one csv
  private/readTrk.m                79   the text parser
  private/labelSamples.m           46   events -> samples
  private/checkTrk.m              134   what is recorded as an anomaly
  ymtcEventTableBatch / RunCheck / TimingCheck / TrialWide   wrappers, skim

代码_matlab/                      with the study data, not in this repository
  csv2kretmat.m                   259   the four segment definitions
  example_kret_pipeline.m         140   filter -> interpolate -> segment -> stats
  ymtcTrialQC.m                   110   the three rejection rules
  ymtcMergeResults.m              ~110  how the 69 columns are assembled
```

| read | what to confirm while reading | why it matters | time |
|---|---|---|---|
| 1. `ymtcEventTable.m` | the five marker/event pairs; how the trial order is chosen; where `condition` / `timing` / `certainty` / `outcome` come from; what `diff_s` is; why `run = ceil(trial/21)` | every claim about task conditions rests on this file | 40 min |
| 2. `trk2csv.m` -> `private/readTrk.m` -> `labelSamples.m` -> `checkTrk.m` | how one csv row is built; what is recorded instead of repaired | the input of everything else | 60 min |
| 3. `csv2kretmat.m` | the four segments and their windows; the time-zero convention | decides what "countdown" means in every pupil column | 30 min |
| 4. `example_kret_pipeline.m` + `docs/03` | which filter runs when; what is a paper default and what we changed | the only place a number is produced | 40 min |
| 5. `ymtcTrialQC.m` + `docs/05` | the three rules and their thresholds | decides which trials survive | 20 min |
| 6. `ymtcMergeResults.m` | the join key (`participant` + `run` + `trial`) and the column order | explains the 69-column table | 20 min |

Three routes, depending on how much time you have:

- **30 minutes**: file 1 only, with the dictionary open on `docs/02` - enough to defend every column of the marker table.
- **2 hours**: files 1-2, plus `checkDocs` - enough to defend the whole preparation layer.
- **half a day**: all six - enough to defend every number in the final table.""",
 "ko": """## 9. 검토 지도: 무엇을 어떤 순서로 읽을까

이 코드를 직접 확인해야 한다면, 가장 짧은 경로는 이것이다. 아래 경로는 모두 실제 파일이고 줄 수는 파일에서 센 값이다.

```
code/ymtc/                        이 저장소
  ymtcEventTable.m                184   마커 표 자체
  trk2csv.m                        87   .trk 하나 -> csv 하나
  private/readTrk.m                79   텍스트 파서
  private/labelSamples.m           46   이벤트 -> 샘플
  private/checkTrk.m              134   무엇을 이상치로 기록하는가
  ymtcEventTableBatch / RunCheck / TimingCheck / TrialWide   래퍼, 훑어보기

代码_matlab/                      연구 데이터와 함께, 저장소에는 없음
  csv2kretmat.m                   259   네 구간 정의
  example_kret_pipeline.m         140   필터 -> 보간 -> 구간 -> 통계
  ymtcTrialQC.m                   110   세 가지 제외 규칙
  ymtcMergeResults.m              ~110  69개 열이 만들어지는 방식
```

| 읽기 | 읽으면서 확인할 것 | 왜 중요한가 | 시간 |
|---|---|---|---|
| 1. `ymtcEventTable.m` | 다섯 마커/이벤트 쌍; trial order 선택 방식; `condition`/`timing`/`certainty`/`outcome`의 출처; `diff_s`의 의미; `run = ceil(trial/21)`인 이유 | 조건에 관한 모든 주장이 이 파일에 달려 있다 | 40분 |
| 2. `trk2csv.m` -> `readTrk.m` -> `labelSamples.m` -> `checkTrk.m` | csv 한 행이 만들어지는 과정; 고치지 않고 기록하는 것 | 나머지 전부의 입력 | 60분 |
| 3. `csv2kretmat.m` | 네 구간과 창; 시간 0 기준 | 모든 눈동자 열에서 "countdown"의 의미를 결정 | 30분 |
| 4. `example_kret_pipeline.m` + `docs/03` | 어느 필터가 언제; 무엇이 논문 기본값이고 무엇을 바꿨는지 | 숫자가 생기는 유일한 곳 | 40분 |
| 5. `ymtcTrialQC.m` + `docs/05` | 세 규칙과 임계값 | 어떤 trial이 살아남는지 결정 | 20분 |
| 6. `ymtcMergeResults.m` | 조인 키(`participant`+`run`+`trial`)와 열 순서 | 69열 표를 설명 | 20분 |

시간에 따른 세 가지 경로:

- **30분**: 1번 파일만, `docs/02` 사전을 옆에 두고 - 마커 표의 모든 열을 방어할 수 있다.
- **2시간**: 1-2번 + `checkDocs` - 준비 계층 전체를 방어할 수 있다.
- **반나절**: 여섯 개 전부 - 최종 표의 모든 숫자를 방어할 수 있다.""",
 "zh": """## 9. 审阅地图：读哪些文件、按什么顺序

如果要自己核一遍代码，这是最短路线。下面的路径都是真实的，行数是从文件里数出来的。

```
code/ymtc/                        在本仓库里
  ymtcEventTable.m                184   marker 表本身
  trk2csv.m                        87   .trk → csv
  private/readTrk.m                79   文本解析
  private/labelSamples.m           46   事件 → 样本
  private/checkTrk.m              134   什么会被记成异常
  ymtcEventTableBatch / RunCheck / TimingCheck / TrialWide   外围，扫一眼

代码_matlab/                      和研究数据放在一起，不在仓库里
  csv2kretmat.m                   259   四个段的定义
  example_kret_pipeline.m         140   滤波 → 插值 → 分段 → 统计
  ymtcTrialQC.m                   110   三条剔除规则
  ymtcMergeResults.m              ~110  69 列是怎么拼出来的
```

| 读 | 读的时候确认什么 | 为什么重要 | 时间 |
|---|---|---|---|
| 1. `ymtcEventTable.m` | 五组 marker↔事件；order 怎么选；`condition`/`timing`/`certainty`/`outcome` 从哪来；`diff_s` 是什么；为什么 `run = ceil(trial/21)` | 所有关于条件的说法都压在这个文件上 | 40 分钟 |
| 2. `trk2csv.m` → `readTrk.m` → `labelSamples.m` → `checkTrk.m` | 一行 csv 怎么产生；什么只记录不修补 | 后面全部环节的输入 | 60 分钟 |
| 3. `csv2kretmat.m` | 四个段和它们的窗口；时间零点约定 | 决定每个瞳孔列里“countdown”指什么 | 30 分钟 |
| 4. `example_kret_pipeline.m` + `docs/03` | 哪个滤波在哪一步；哪些是论文默认、哪些是我们改的 | 唯一产生数字的地方 | 40 分钟 |
| 5. `ymtcTrialQC.m` + `docs/05` | 三条规则和阈值 | 决定哪些 trial 能留下 | 20 分钟 |
| 6. `ymtcMergeResults.m` | 合并键（`participant`+`run`+`trial`）和列顺序 | 解释那张 69 列的表 | 20 分钟 |

按你能投入的时间，三条路线：

- **30 分钟**：只读第 1 个，旁边开着 `docs/02` 列字典——足够守住 marker 表的每一列。
- **2 小时**：第 1–2 项，外加跑一次 `checkDocs`——足够守住整个数据准备层。
- **半天**：六项全读——足够守住最终表里的每一个数字。""",
}

KRET_DETAIL = {
 "en": """#### What each stage actually does

| stage | function (file:line) | decision | key settings |
|---|---|---|---|
| 1 range | `removeOutOfBounds` (`rawDataFilter.m:197`) | diameter outside the plausible range becomes invalid | `PupilDiameter_Min/_Max` (defaults 1.5 / 9, **millimetres**) |
| 2 blink | `madSpeedFilter` (`229`) + `expandGaps` (`511`) | sample-to-sample speed above `median + 16 MAD`; plus 50 ms around every gap wider than 75 ms | `dilationSpeedFilter_MadMultiplier=16`, `maxGap_ms=200` |
| 3 trend | `madDeviationFilter` (`284`) | distance from a 16 Hz low-passed trend line above `median + 16 MAD`; 4 passes let wrongly rejected samples come back | `residualsFilter_passes=4`, `MadMultiplier=16` |
| 4 islands | `removeLoners` (`440`) | islands narrower than 50 ms, separated by more than 40 ms | `islandFilter_minIslandWidth_ms=50`, `_islandSeperation_ms=40` |
| 5 smooth | `interpAndSmooth` (`ValidSamplesModel.m:107`) | linear interpolation to 1000 Hz, then a 4th-order Butterworth at 4 Hz, zero phase (`filtfilt`) | `interp_upsamplingFreq=1000`, `LpFilt_cutoffFreq=4` |
| 6 segments | `analyze` (`203`) | per-segment mean / min / max / missing% from the smooth signal **and** from the valid samples | — |

Every threshold is `median + n*MAD`, never mean +/- SD, because a handful of large artifacts would inflate an SD enough to hide themselves. All values above are paper defaults; our pipeline changes only the range filter, since the paper's numbers are millimetres and our data are camera pixels.

The code never edits the diameter. `rawDataFilter` returns one logical vector (`isValid`) and the raw samples stay as recorded; everything downstream works from that mask, which is why a rejected sample can never be recovered later.""",
 "ko": """#### 각 단계가 실제로 하는 일

| 단계 | 함수 (파일:행) | 판단 | 주요 설정 |
|---|---|---|---|
| 1 범위 | `removeOutOfBounds` (`rawDataFilter.m:197`) | 그럴듯한 범위를 벗어난 직경은 무효 | `PupilDiameter_Min/_Max` (기본 1.5 / 9, **밀리미터**) |
| 2 깜박임 | `madSpeedFilter` (`229`) + `expandGaps` (`511`) | `median + 16 MAD`를 넘는 샘플 간 속도, 그리고 75 ms보다 넓은 간격 주변 50 ms | `dilationSpeedFilter_MadMultiplier=16`, `maxGap_ms=200` |
| 3 추세 | `madDeviationFilter` (`284`) | 16 Hz 저역 통과 추세선에서 `median + 16 MAD` 이상 벗어난 점. 4회 반복으로 잘못 제거된 샘플이 돌아온다 | `residualsFilter_passes=4` |
| 4 고립 | `removeLoners` (`440`) | 50 ms보다 좁고 40 ms 이상 떨어진 섬 | `minIslandWidth_ms=50`, `islandSeperation_ms=40` |
| 5 평활 | `interpAndSmooth` (`ValidSamplesModel.m:107`) | 1000 Hz 선형 보간 후 4차 Butterworth 4 Hz, 영위상(`filtfilt`) | `interp_upsamplingFreq=1000`, `LpFilt_cutoffFreq=4` |
| 6 구간 | `analyze` (`203`) | 구간별 평균/최소/최대/결측%를 평활 신호와 유효 샘플 양쪽에서 | — |

모든 임계값은 `median + n*MAD`이며 평균 ± SD가 아니다. 큰 아티팩트 몇 개가 SD를 부풀려 스스로를 숨기기 때문이다. 위 값은 모두 논문 기본값이고, 우리 파이프라인은 범위 필터만 바꾼다(논문 값은 밀리미터, 우리 데이터는 픽셀).

코드는 직경을 절대 고치지 않는다. `rawDataFilter`는 논리 벡터(`isValid`) 하나를 돌려주고 원시 샘플은 그대로 남는다.""",
 "zh": """#### 每一阶段到底做了什么

| 阶段 | 函数（文件:行） | 判断什么 | 关键设置 |
|---|---|---|---|
| 1 范围 | `removeOutOfBounds`（`rawDataFilter.m:197`） | 直径超出合理范围即无效 | `PupilDiameter_Min/_Max`（默认 1.5 / 9，**毫米**） |
| 2 眨眼 | `madSpeedFilter`（`229`）+ `expandGaps`（`511`） | 相邻样本速度超过 `median + 16 MAD`；再把宽于 75 ms 的缺口前后各 50 ms 去掉 | `dilationSpeedFilter_MadMultiplier=16`、`maxGap_ms=200` |
| 3 趋势 | `madDeviationFilter`（`284`） | 离 16 Hz 低通趋势线超过 `median + 16 MAD` 的点；**回扫 4 趟**让被误删的好样本复活 | `residualsFilter_passes=4` |
| 4 孤立 | `removeLoners`（`440`） | 窄于 50 ms、且与邻段隔开 40 ms 以上的孤岛 | `minIslandWidth_ms=50`、`islandSeperation_ms=40` |
| 5 平滑 | `interpAndSmooth`（`ValidSamplesModel.m:107`） | 线性插值到 1000 Hz，再走 4 阶 Butterworth 4 Hz、零相位（`filtfilt`） | `interp_upsamplingFreq=1000`、`LpFilt_cutoffFreq=4` |
| 6 分段 | `analyze`（`203`） | 每段的均值/最小/最大/缺失%，平滑信号和有效样本各算一套 | — |

所有阈值都是 `median + n*MAD`，不是均值 ± SD——少数巨大伪影会把 SD 撑大，反而把自己藏起来。上面全是论文默认值；我们的管线只改了范围滤波，因为论文的数字是毫米、我们的数据是相机像素。

**代码从不修改直径**：`rawDataFilter` 只返回一个逻辑向量（`isValid`），原始样本原样保留；下游全部基于这个掩码，所以被否掉的样本后面救不回来。""",
}

KRET_FLOW = {
    "en": """```
RawFileModel ──saveMatFile──▶ <name>.mat
        │
        ▼  PupilDataModel.batchConstructor(...)        one object per file
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter     gives isValid per raw sample
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth              gives the 1000 Hz smooth signal
 (3) analyzeSegments()       ValidSamplesModel.analyze                      gives 10 statistics per segment per eye
 (4) exportSegments(folder)  continuous time course of every segment → CSV
 (5) plotData()              visual check (needs desktop MATLAB)
```""",
    "ko": """```
RawFileModel ──saveMatFile──▶ <name>.mat
        │
        ▼  PupilDataModel.batchConstructor(...)        파일마다 객체 하나
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter     원시 샘플마다 isValid
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth              1000 Hz 평활 신호
 (3) analyzeSegments()       ValidSamplesModel.analyze                      구간·눈마다 통계량 10개
 (4) exportSegments(folder)  구간별 연속 시간 곡선 → CSV
 (5) plotData()              육안 점검 (데스크톱 MATLAB 필요)
```""",
    "zh": """```
RawFileModel ──saveMatFile──▶ <name>.mat
        │
        ▼  PupilDataModel.batchConstructor(...)        每个文件一个对象
 (1) filterRawData()         RawSamplesModel.filterData → rawDataFilter     产出每个原始样本的 isValid
 (2) processValidSamples()   ValidSamplesModel.interpAndSmooth              产出 1000 Hz 平滑信号
 (3) analyzeSegments()       ValidSamplesModel.analyze                      产出每段每只眼 10 个统计量
 (4) exportSegments(folder)  每段的连续时间曲线 → CSV
 (5) plotData()              目视检查（需要桌面 MATLAB）
```""",
}

PROSE = {
    "en": {
        "h_map": "1. Map: every table and where it comes from",
        "map_intro": "Folder numbers (`00`–`06`) are the data folders next to this repository. `[ymtc]` = our code in `code/ymtc/`, `[Kret code]` = the original classes in `code/dataModels/`, `[Kret adapter]` = our glue between them.",
        "tbl_list_head": "| table | file | rows | columns | produced by |",
        "h_kret": "2. The Kret & Sjak-Shie pipeline (original code)",
        "kret_design": "Design points: the pipeline only flags (`isValid`), it never overwrites the raw diameter; valid samples and the smooth signal are different objects; every threshold lives in `getDefaultSettings()`; each object carries its own settings; left, right and mean are analysed separately. Time units: `t_ms` is in milliseconds, `segmentStart`, `segmentEnd` and `signal.t` are in seconds.",
        "h_in": "2.1 What goes in: the .mat file (`RawFileModel`)",
        "in_text": "`RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename)` checks its input and writes a `.mat` with four variables. Unfold each field:",
        "h_obj": "2.2 The objects and their fields",
        "pdm": "`PupilDataModel` — properties", "raws": "`RawSamplesModel` — properties", "vals": "`ValidSamplesModel` — properties",
        "h_methods": "2.3 Methods: input → output",
        "methods_head": "| method | input | output | console message |",
        "h_out": "3. Output tables, column by column",
        "out_intro": "Each table lists every column. A triangle in the last column unfolds how it is computed, traps and known caveats.",
        "h_set": "4. Settings",
        "h_fn": "5. Files and functions",
        "h_ex": "6. The two official examples",
        "h_tr": "7. Troubleshooting: symptom → cause → fix",
        "h_lim": "8. Limitations",
        "lim": "- The original README requires the Signal Processing and Statistics toolboxes and was tested on MATLAB 2012b / 2016a / 2017a on Windows 7. This fork patches it for macOS (path separator in `PupilDataModel`, `FALLBACK/`); see `git log`.\n- The filter parameters are the paper's defaults and have NOT been tuned for YMTC data. Tuning needs desktop MATLAB and `plotData()` on the raw traces.\n- Pupil size is in camera pixels, from one eye; gaze is not recorded; the unit of `pupil_angle` and the meaning of the `sp_` prefix are unconfirmed.\n- This page describes what the code does, not whether the results are good. Data quality: [`../docs/05_data_quality.md`](../docs/05_data_quality.md).",
        "h_more": "10. Further reading",
        "more": "[`../docs/01_pipeline_overview.md`](../docs/01_pipeline_overview.md) · [`../docs/02_column_dictionary.md`](../docs/02_column_dictionary.md) · [`../docs/03_pupil_size_internals.md`](../docs/03_pupil_size_internals.md) · [`ymtc/README.md`](ymtc/README.md) · [`../docs/04_our_code.md`](../docs/04_our_code.md) · [`../docs/06_faq.md`](../docs/06_faq.md)",
        "a_sample": "02 · per-sample CSV — `<name>.csv` from `trk2csv` (21 columns, one row per eye-tracker sample)",
        "a_qc": "02 · `trk2csv_qc_summary.csv` (25 columns, one row per .trk file)",
        "a_issues": "02 · `trk2csv_issues.csv` (5 columns, one row per anomaly)",
        "a_ev03": "03 · `<sub>_events.csv` (3 columns, one row per software event)",
        "a_event": "05 · event table — `<sub>_event_table.csv`, `<sub>_event_table_5step.csv`, `all_subjects_event_table*.csv` (18 columns)",
        "a_evsum": "05 · `event_table_summary.csv` (6 columns, one row per subject)",
        "a_wide": "05 · `all_subjects_trials_wide.csv` (14 columns, one row per trial)",
        "a_timing": "05 · `timing_check.csv` (7 columns, one row per subject and marker)",
        "a_run": "00 · `run_check.csv` (9 columns, one row per subject)",
        "a_seg": "Statistics per segment — 12 concepts that appear in `kret_results.csv`, `trials_qc.csv` and (with a segment prefix) in the final table",
        "a_kret": "04 · `kret_results.csv` (16 columns, one row per subject × trial × segment = 4 per trial)",
        "a_tqc": "04 · `trials_qc.csv` (19 columns = the 16 above + 3 QC flags, repeated on the 4 segment rows of a trial)",
        "a_sqc": "04 · `subjects_qc.csv` (5 columns, one row per subject)",
        "a_segcsv": "04 · `segments/<name>_leftpupil_segments.csv` (6–7 columns, one row per 1000 Hz sample, from `exportSegments`)",
        "a_final": "06 · `<sub>_final.csv` and `all_subjects_final.csv` — 69 columns, one row per marker",
        "a_final_note": "Built by `ymtcMergeResults` from the 5-step event table. Each segment's statistics sit on the marker row it belongs to: baseline → Onset, countdown and preOutcome → countdown row, postOutcome → Outcome row. WhiteNoise and Rating rows have `NaN` there. Full column list:",
        "a_analyze": "The upstream table: what `analyzeSegments` returns",
        "analyze_text": "One table per object: all columns of your `segmentsTable`, then 10 columns per eye appended on the right, prefixed `leftPupil_`, `rightPupil_`, `meanPupil_`. Our data has one pupil, so only `leftPupil_*` appears. In MATLAB the table header also carries `VariableUnits` and `VariableDescriptions`; they are lost when saved as CSV, which is why this page exists.",
        "a_codes": "Issue codes (column `code`)",
        "a_mat": "Contents of the .mat written by `csv2kretmat`",
        "mat_text": "`diameterUnit = 'px'`; `diameter.t_ms` (ms, starting at 0), `diameter.L` (pupil size, `NaN` = missing), `diameter.R` empty; `zeroTime_ms` = original MRC timestamp of the first sample; `segmentsTable` with `segmentStart`, `segmentEnd`, `segmentName` plus `segmentType`, `participant`, `trial`. Four segment types per trial: `baseline` `[CueStart − 0.5 s, CueStart)`, `countdown` `[CueStart, StimuliStart)`, `preOutcome` `[StimuliStart − 2 s, StimuliStart)`, `postOutcome` `[StimuliStart, StimuliStart + 2 s)`. The i-th `CueStart` is paired with the i-th `StimuliStart`. The boundaries come from MEASURED markers, not design values.",
        "set_raw": "`settings.raw` (from `rawDataFilter()`)", "set_valid": "`settings.valid` (from `ValidSamplesModel.getDefaultSettings()`)",
        "set_trk": "`trk2csv` options", "set_kret": "`csv2kretmat` options",
        "fn_up": "Original code (`helperFunctions/`)", "fn_our": "Our layer (`ymtc/` and the adapter)",
        "ex_text": "`main_Dataset1.m` is the shortest demonstration of steps (1)–(5). Our YMTC data follows the same one-pupil route with `trk2csv` as converter.",
    },
    "ko": {
        "h_map": "1. 지도: 모든 표와 그 출처",
        "map_intro": "폴더 번호(`00`–`06`)는 이 저장소 옆의 데이터 폴더이다. `[ymtc]` = `code/ymtc/`의 우리 코드, `[Kret code]` = `code/dataModels/`의 원본 클래스, `[Kret 어댑터]` = 둘을 잇는 우리 코드.",
        "tbl_list_head": "| 표 | 파일 | 행 | 열 | 생성 |",
        "h_kret": "2. Kret & Sjak-Shie 파이프라인 (원본 코드)",
        "kret_design": "설계 요점: 파이프라인은 표시(`isValid`)만 하고 원시 직경을 덮어쓰지 않는다. valid 샘플과 평활 신호는 별개의 객체이다. 모든 임계값은 `getDefaultSettings()`에 있고 객체마다 자기 설정을 가진다. 왼쪽·오른쪽·평균을 따로 분석한다. 시간 단위: `t_ms`는 밀리초, `segmentStart`·`segmentEnd`·`signal.t`는 초.",
        "h_in": "2.1 입력: .mat 파일 (`RawFileModel`)",
        "in_text": "`RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename)`은 입력을 검사하고 변수 네 개가 든 `.mat`을 쓴다. 필드별로 펼쳐 보라:",
        "h_obj": "2.2 객체와 필드",
        "pdm": "`PupilDataModel` — 속성", "raws": "`RawSamplesModel` — 속성", "vals": "`ValidSamplesModel` — 속성",
        "h_methods": "2.3 메서드: 입력 → 출력",
        "methods_head": "| 메서드 | 입력 | 출력 | 콘솔 메시지 |",
        "h_out": "3. 출력 표, 열 단위",
        "out_intro": "각 표는 모든 열을 나열한다. 마지막 열의 삼각형을 누르면 계산 방법, 함정, 알려진 주의점이 펼쳐진다.",
        "h_set": "4. 설정",
        "h_fn": "5. 파일과 함수",
        "h_ex": "6. 공식 예제 두 개",
        "h_tr": "7. 문제 해결: 증상 → 원인 → 해결",
        "h_lim": "8. 한계",
        "lim": "- 원본 README는 Signal Processing과 Statistics 툴박스를 요구하며 Windows 7의 MATLAB 2012b / 2016a / 2017a에서 테스트했다. 이 포크는 macOS용으로 패치했다(`PupilDataModel`의 경로 구분자, `FALLBACK/`). `git log` 참조.\n- 필터 매개변수는 논문 기본값이며 YMTC 데이터에 맞춰 조정하지 않았다. 조정하려면 데스크톱 MATLAB에서 `plotData()`로 원시 궤적을 봐야 한다.\n- 동공 크기는 카메라 픽셀 단위, 한쪽 눈 기준이다. 시선은 기록되지 않았다. `pupil_angle`의 단위와 `sp_` 접두사의 뜻은 확인되지 않았다.\n- 이 문서는 코드가 무엇을 하는지만 설명하며 결과가 좋은지는 판단하지 않는다. 데이터 품질: [`../docs/05_data_quality.md`](../docs/05_data_quality.md).",
        "h_more": "10. 더 읽을 거리",
        "more": "[`../docs/01_pipeline_overview.md`](../docs/01_pipeline_overview.md) · [`../docs/02_column_dictionary.md`](../docs/02_column_dictionary.md) · [`../docs/03_pupil_size_internals.md`](../docs/03_pupil_size_internals.md) · [`ymtc/README.md`](ymtc/README.md) · [`../docs/04_our_code.md`](../docs/04_our_code.md) · [`../docs/06_faq.md`](../docs/06_faq.md)",
        "a_sample": "02 · 샘플 단위 CSV — `trk2csv`가 쓰는 `<name>.csv` (21열, 시선추적기 샘플마다 한 행)",
        "a_qc": "02 · `trk2csv_qc_summary.csv` (25열, .trk 파일마다 한 행)",
        "a_issues": "02 · `trk2csv_issues.csv` (5열, 이상치마다 한 행)",
        "a_ev03": "03 · `<sub>_events.csv` (3열, 소프트웨어 이벤트마다 한 행)",
        "a_event": "05 · 이벤트 표 — `<sub>_event_table.csv`, `<sub>_event_table_5step.csv`, `all_subjects_event_table*.csv` (18열)",
        "a_evsum": "05 · `event_table_summary.csv` (6열, 피험자마다 한 행)",
        "a_wide": "05 · `all_subjects_trials_wide.csv` (14열, trial마다 한 행)",
        "a_timing": "05 · `timing_check.csv` (7열, 피험자 × 마커마다 한 행)",
        "a_run": "00 · `run_check.csv` (9열, 피험자마다 한 행)",
        "a_seg": "구간별 통계 — `kret_results.csv`, `trials_qc.csv`에 나오고 최종 표에는 구간 접두사를 붙여 나오는 12개 개념",
        "a_kret": "04 · `kret_results.csv` (16열, 피험자 × trial × 구간마다 한 행 = trial당 4행)",
        "a_tqc": "04 · `trials_qc.csv` (19열 = 위 16열 + QC 표시 3개, trial의 4개 구간 행에 반복)",
        "a_sqc": "04 · `subjects_qc.csv` (5열, 피험자마다 한 행)",
        "a_segcsv": "04 · `segments/<name>_leftpupil_segments.csv` (6–7열, `exportSegments`가 쓰는 1000 Hz 샘플마다 한 행)",
        "a_final": "06 · `<sub>_final.csv`와 `all_subjects_final.csv` — 69열, 마커마다 한 행",
        "a_final_note": "`ymtcMergeResults`가 5단계 이벤트 표로 만든다. 각 구간의 통계는 그 구간이 속한 마커 행에 놓인다: baseline → Onset, countdown·preOutcome → 카운트다운 행, postOutcome → Outcome 행. WhiteNoise와 Rating 행은 거기가 `NaN`. 전체 열 목록:",
        "a_analyze": "원본 표: `analyzeSegments`가 반환하는 것",
        "analyze_text": "객체마다 표 하나: `segmentsTable`의 모든 열 뒤에 눈마다 10개 열이 오른쪽으로 붙는다. 접두사는 `leftPupil_`, `rightPupil_`, `meanPupil_`. 우리 데이터는 동공이 하나라 `leftPupil_*`만 나온다. MATLAB에서는 표 머리에 `VariableUnits`와 `VariableDescriptions`도 있지만 CSV로 저장하면 사라진다. 이 문서가 필요한 이유이다.",
        "a_codes": "이상치 코드(열 `code`)",
        "a_mat": "`csv2kretmat`이 쓰는 .mat의 내용",
        "mat_text": "`diameterUnit = 'px'`; `diameter.t_ms`(ms, 0에서 시작), `diameter.L`(동공 크기, `NaN` = 결측), `diameter.R` 비어 있음; `zeroTime_ms` = 첫 샘플의 원래 MRC 타임스탬프; `segmentsTable`은 `segmentStart`, `segmentEnd`, `segmentName`과 `segmentType`, `participant`, `trial`. trial마다 구간 네 종류: `baseline` `[CueStart − 0.5 s, CueStart)`, `countdown` `[CueStart, StimuliStart)`, `preOutcome` `[StimuliStart − 2 s, StimuliStart)`, `postOutcome` `[StimuliStart, StimuliStart + 2 s)`. i번째 `CueStart`와 i번째 `StimuliStart`를 짝지운다. 경계는 설계값이 아니라 **실측** 마커에서 온다.",
        "set_raw": "`settings.raw` (`rawDataFilter()`에서)", "set_valid": "`settings.valid` (`ValidSamplesModel.getDefaultSettings()`에서)",
        "set_trk": "`trk2csv` 옵션", "set_kret": "`csv2kretmat` 옵션",
        "fn_up": "원본 코드(`helperFunctions/`)", "fn_our": "우리 계층(`ymtc/`와 어댑터)",
        "ex_text": "`main_Dataset1.m`은 (1)~(5)단계의 가장 짧은 시연이다. 우리 YMTC 데이터는 `trk2csv`를 변환기로 하여 같은 한 동공 경로를 따른다.",
    },
    "zh": {
        "h_map": "1. 总图：每张表和它的来源",
        "map_intro": "文件夹编号（`00`–`06`）是本仓库旁边的数据文件夹。`[ymtc]` = `code/ymtc/` 里我们的代码，`[Kret code]` = `code/dataModels/` 里的原版类，`[Kret 适配器]` = 我们在两者之间的衔接代码。",
        "tbl_list_head": "| 表 | 文件 | 行 | 列 | 由谁生成 |",
        "h_kret": "2. Kret & Sjak-Shie 流水线（原版代码）",
        "kret_design": "设计要点：流水线只做标记（`isValid`），从不覆盖原始直径；valid 样本和平滑信号是两个不同的对象；所有阈值都在 `getDefaultSettings()` 里，每个对象带自己的设置；左、右、均值分开分析。时间单位：`t_ms` 是毫秒，`segmentStart`、`segmentEnd`、`signal.t` 是秒。",
        "h_in": "2.1 输入：.mat 文件（`RawFileModel`）",
        "in_text": "`RawFileModel(diameterUnit, diameter, segmentsTable, zeroTime_ms, filename)` 会检查输入，写出一个含四个变量的 `.mat`。逐个字段展开看：",
        "h_obj": "2.2 对象与字段",
        "pdm": "`PupilDataModel` —— 属性", "raws": "`RawSamplesModel` —— 属性", "vals": "`ValidSamplesModel` —— 属性",
        "h_methods": "2.3 方法：输入 → 输出",
        "methods_head": "| 方法 | 输入 | 输出 | 终端打印 |",
        "h_out": "3. 输出表，逐列说明",
        "out_intro": "每张表列出每一列。最后一列的三角形展开后是计算方法、陷阱和已知注意事项。",
        "h_set": "4. 设置项",
        "h_fn": "5. 文件与函数",
        "h_ex": "6. 两个官方例子",
        "h_tr": "7. 排错：症状 → 原因 → 修法",
        "h_lim": "8. 局限",
        "lim": "- 原版 README 要求 Signal Processing 和 Statistics 两个工具箱，测试环境是 Windows 7 上的 MATLAB 2012b / 2016a / 2017a。本 fork 为 macOS 做了补丁（`PupilDataModel` 的路径分隔符、`FALLBACK/`），见 `git log`。\n- 滤波参数是论文默认值，**没有针对 YMTC 数据调过**。要调需要桌面 MATLAB，用 `plotData()` 看原始轨迹。\n- 瞳孔大小是相机像素、单眼；没有记录注视；`pupil_angle` 的单位和 `sp_` 前缀的含义未确认。\n- 本页只描述代码做了什么，不判断结果好坏。数据质量见 [`../docs/05_data_quality.md`](../docs/05_data_quality.md)。",
        "h_more": "10. 延伸阅读",
        "more": "[`../docs/01_pipeline_overview.md`](../docs/01_pipeline_overview.md) · [`../docs/02_column_dictionary.md`](../docs/02_column_dictionary.md) · [`../docs/03_pupil_size_internals.md`](../docs/03_pupil_size_internals.md) · [`ymtc/README.md`](ymtc/README.md) · [`../docs/04_our_code.md`](../docs/04_our_code.md) · [`../docs/06_faq.md`](../docs/06_faq.md)",
        "a_sample": "02 · 逐样本 CSV —— `trk2csv` 写出的 `<name>.csv`（21 列，每个眼动仪样本一行）",
        "a_qc": "02 · `trk2csv_qc_summary.csv`（25 列，每个 .trk 文件一行）",
        "a_issues": "02 · `trk2csv_issues.csv`（5 列，每条异常一行）",
        "a_ev03": "03 · `<sub>_events.csv`（3 列，每个软件事件一行）",
        "a_event": "05 · 事件表 —— `<sub>_event_table.csv`、`<sub>_event_table_5step.csv`、`all_subjects_event_table*.csv`（18 列）",
        "a_evsum": "05 · `event_table_summary.csv`（6 列，每个被试一行）",
        "a_wide": "05 · `all_subjects_trials_wide.csv`（14 列，每个 trial 一行）",
        "a_timing": "05 · `timing_check.csv`（7 列，每个被试 × marker 一行）",
        "a_run": "00 · `run_check.csv`（9 列，每个被试一行）",
        "a_seg": "每段的统计量 —— 12 个概念，出现在 `kret_results.csv`、`trials_qc.csv`，在最终表里则带上分段前缀",
        "a_kret": "04 · `kret_results.csv`（16 列，每个被试 × trial × 分段一行 = 每 trial 4 行）",
        "a_tqc": "04 · `trials_qc.csv`（19 列 = 上面 16 列 + 3 个质控标记，在 trial 的 4 个分段行上重复）",
        "a_sqc": "04 · `subjects_qc.csv`（5 列，每个被试一行）",
        "a_segcsv": "04 · `segments/<name>_leftpupil_segments.csv`（6–7 列，每个 1000 Hz 样本一行，由 `exportSegments` 写出）",
        "a_final": "06 · `<sub>_final.csv` 与 `all_subjects_final.csv` —— 69 列，每个 marker 一行",
        "a_final_note": "由 `ymtcMergeResults` 基于 5 步事件表合并而成。每个分段的统计量放在它所属的 marker 行上：baseline → Onset，countdown 和 preOutcome → 倒计时行，postOutcome → Outcome 行；WhiteNoise 和 Rating 行在这些列上是 `NaN`。完整列表：",
        "a_analyze": "原版的表：`analyzeSegments` 返回什么",
        "analyze_text": "每个对象一张表：先是你的 `segmentsTable` 全部列，再向右接上每只眼的 10 列，前缀为 `leftPupil_`、`rightPupil_`、`meanPupil_`。我们的数据只有一只瞳孔，所以只有 `leftPupil_*`。在 MATLAB 里表头还带 `VariableUnits` 和 `VariableDescriptions`，存成 CSV 时会丢，这就是本页存在的原因。",
        "a_codes": "异常代码（列 `code`）",
        "a_mat": "`csv2kretmat` 写出的 .mat 的内容",
        "mat_text": "`diameterUnit = 'px'`；`diameter.t_ms`（毫秒，从 0 开始）、`diameter.L`（瞳孔大小，`NaN` = 缺失）、`diameter.R` 为空；`zeroTime_ms` = 第一个样本的原始 MRC 时间戳；`segmentsTable` 含 `segmentStart`、`segmentEnd`、`segmentName`，以及 `segmentType`、`participant`、`trial`。每个 trial 四种分段：`baseline` `[CueStart − 0.5 s, CueStart)`、`countdown` `[CueStart, StimuliStart)`、`preOutcome` `[StimuliStart − 2 s, StimuliStart)`、`postOutcome` `[StimuliStart, StimuliStart + 2 s)`。第 i 个 `CueStart` 与第 i 个 `StimuliStart` 配对。边界来自**实测** marker，不是设计值。",
        "set_raw": "`settings.raw`（来自 `rawDataFilter()`）", "set_valid": "`settings.valid`（来自 `ValidSamplesModel.getDefaultSettings()`）",
        "set_trk": "`trk2csv` 选项", "set_kret": "`csv2kretmat` 选项",
        "fn_up": "原版代码（`helperFunctions/`）", "fn_our": "我们的层（`ymtc/` 与适配器）",
        "ex_text": "`main_Dataset1.m` 是 (1)–(5) 步的最短演示。我们的 YMTC 数据走同样的单瞳孔路线，转换器是 `trk2csv`。",
    },
}

TABLE_LIST = [
    ("per-sample CSV", "02_samples/<name>.csv", "1 / sample", 21, "trk2csv [ymtc]"),
    ("QC summary", "02_samples/02_all_qc_summary.csv", "1 / file", 25, "trk2csv_batch [ymtc]"),
    ("issues", "02_samples/02_all_issues.csv", "1 / anomaly", 5, "trk2csv_batch [ymtc]"),
    ("events", "03_events/<sub>_events.csv", "1 / event", 3, "event extraction"),
    ("event table", "05_markers/05_<sub>_markers[_5step].csv", "1 / marker (624 · 372)", 18, "ymtcEventTable [ymtc]"),
    ("event summary", "05_markers/05_all_markers_summary.csv", "1 / subject", 6, "ymtcEventTableBatch [ymtc]"),
    ("trials wide", "05_markers/05_all_trials_wide.csv", "1 / trial", 14, "ymtcTrialWide [ymtc]"),
    ("timing check", "05_markers/05_all_timing_check.csv", "1 / subject × marker", 7, "ymtcTimingCheck [ymtc]"),
    ("run check", "07_checks/07_all_run_check.csv", "1 / subject", 9, "ymtcRunCheck [ymtc]"),
    ("Kret results", "04_pupil/04_all_segments.csv", "1 / trial × segment", 16, "analyzeSegments [Kret code]"),
    ("trial QC", "04_pupil/04_all_trials_qc.csv", "1 / trial × segment", 19, "Kret pipeline script"),
    ("subject QC", "04_pupil/04_all_subjects_qc.csv", "1 / subject", 5, "Kret pipeline script"),
    ("segment curves", "04_pupil/segments/<name>_leftpupil_segments.csv", "1 / 1000 Hz sample", 7, "exportSegments [Kret code]"),
    ("final", "06_merged/06_<sub>_merged.csv, 06_all_merged.csv", "1 / marker", 69, "ymtcMergeResults [ymtc]"),
]

METHODS = [
    ("PupilDataModel.batchConstructor(folder, dirStruct, settings)", T("folder, `dir('*.mat')` result, settings", "폴더, `dir('*.mat')` 결과, 설정", "文件夹、`dir('*.mat')` 的结果、设置"), T("array of objects", "객체 배열", "对象数组"), "Constructing N Data Objects..."),
    ("filterRawData()", T("—", "—", "—"), T("`isValid` stored on each eye", "각 눈에 `isValid` 저장", "每只眼的 `isValid` 写进对象"), "Filtering the raw data in N files..."),
    ("processValidSamples()", T("— (needs `isValid`)", "— (`isValid` 필요)", "—（需要 `isValid`）"), T("`*_ValidSamples` objects with the smooth signal; plus `mean` for two eyes", "평활 신호를 가진 `*_ValidSamples` 객체; 두 눈이면 `mean`도", "带平滑信号的 `*_ValidSamples` 对象；双眼时再加 `mean`"), "Interpolating and smooting the valid raw data subsets of N files..."),
    ("analyzeSegments()", T("— (needs the smooth signal)", "— (평활 신호 필요)", "—（需要平滑信号）"), T("cell array, one result table per object; join with `vertcat(results{:})`", "cell 배열, 객체마다 결과 표 하나. `vertcat(results{:})`로 합침", "cell 数组，每个对象一张结果表；用 `vertcat(results{:})` 合并"), "File i (name): analyzing K segments."),
    ("exportSegments(folder, options)", T("output folder; options `Eyes`, `SegmentTypes`, `NaNString`, `ZScore`", "출력 폴더; 옵션 `Eyes`, `SegmentTypes`, `NaNString`, `ZScore`", "输出文件夹；选项 `Eyes`、`SegmentTypes`、`NaNString`、`ZScore`"), T("one CSV per object per eye", "객체·눈마다 CSV 하나", "每个对象每只眼一个 CSV"), "File i (name) left pupil: wrote N samples to <file>"),
    ("plotData()", T("—", "—", "—"), T("figure window", "그림 창", "图形窗口"), "—"),
]


def methods_table(lang):
    i = IDX[lang]
    P = PROSE[lang]
    return P["methods_head"] + "\n|---|---|---|---|\n" + "\n".join(
        "| `%s` | %s | %s | `%s` |" % (m, a[i], o[i], c) for m, a, o, c in METHODS) + "\n"


def trouble_tbl(lang):
    i = IDX[lang]
    head = {"en": "| symptom | cause | fix |", "ko": "| 증상 | 원인 | 해결 |", "zh": "| 症状 | 原因 | 修法 |"}[lang]
    rows = []
    for s, c, f in TROUBLE:
        rows.append("| %s | %s | %s |" % ("`%s`" % s.strip("`") if "`" not in s else s, c[i], f[i]))
    return head + "\n|---|---|---|\n" + "\n".join(rows) + "\n"


def sectionlang(lang):
    P = PROSE[lang]
    i = IDX[lang]
    o = []
    o.append("# %s" % u("title", lang))
    o.append("")
    o.append(u("intro", lang))
    o.append("")
    # 1 map
    o.append("## %s" % P["h_map"])
    o.append("")
    o.append(P["map_intro"])
    o.append("")
    o.append(FLOW[lang])
    o.append("")
    o.append(P["tbl_list_head"])
    o.append("|---|---|---|---|---|")
    for a, b, c, d, e in TABLE_LIST:
        o.append("| %s | `%s` | %s | %d | %s |" % (a, b, c, d, e))
    o.append("")
    # 2 kret
    o.append("## %s" % P["h_kret"])
    o.append("")
    o.append(P["kret_design"])
    o.append("")
    o.append(KRET_FLOW[lang])
    o.append("")
    o.append(KRET_DETAIL[lang])
    o.append("")
    o.append("### %s" % P["h_in"])
    o.append("")
    o.append(P["in_text"])
    o.append("")
    o.append("\n".join(det("<code>%s</code>" % n, d[i]) for n, d in RAWFILE_FIELDS))
    o.append(det(P["a_mat"], P["mat_text"]))
    o.append("### %s" % P["h_obj"])
    o.append("")
    o.append(det("<b>%s</b>" % P["pdm"], props(PDM_PROPS, lang)))
    o.append(det("<b>%s</b>" % P["raws"], props(RAWSAMP_PROPS, lang)))
    o.append(det("<b>%s</b>" % P["vals"], props(VALID_PROPS, lang)))
    o.append("### %s" % P["h_methods"])
    o.append("")
    o.append(methods_table(lang))
    # 3 outputs
    o.append("## %s" % P["h_out"])
    o.append("")
    o.append(P["out_intro"])
    o.append("")
    blocks = [
        ("a_sample", table(SAMPLE_COLS, lang)),
        ("a_qc", table(QC_COLS, lang)),
        ("a_issues", table(ISSUE_COLS, lang)),
        ("a_ev03", table(EVENT03_COLS, lang)),
        ("a_event", table(EVENT_COLS, lang)),
        ("a_evsum", table(EVSUM_COLS, lang)),
        ("a_wide", table(WIDE_COLS, lang)),
        ("a_timing", table(TIMING_COLS, lang)),
        ("a_run", table(RUNCHK_COLS, lang)),
    ]
    for key, body in blocks:
        o.append(det("<b>%s</b>" % P[key], body))
        if key == "a_issues":
            codes_head = {"en": "| code | severity | meaning |", "ko": "| 코드 | 심각도 | 의미 |", "zh": "| 代码 | 严重度 | 含义 |"}[lang]
            cb = codes_head + "\n|---|---|---|\n" + "\n".join("| `%s` | %s | %s |" % (c, s, m[i]) for c, s, m in ISSUE_CODES)
            o.append(det("<b>%s</b>" % P["a_codes"], cb))
    o.append(det("<b>%s</b>" % P["a_analyze"], P["analyze_text"] + "\n\n" + table(SEG_UP, lang)))
    o.append(det("<b>%s</b>" % P["a_kret"], table(KRET_ID, lang) + "\n" + {"en": "plus the 10 `leftPupil_*` statistic columns (same names as above, prefixed).", "ko": "그리고 `leftPupil_*` 통계 열 10개(위와 같은 이름, 접두사 포함).", "zh": "再加 10 个 `leftPupil_*` 统计列（名字同上，加前缀）。"}[lang] + "\n"))
    o.append(det("<b>%s</b>" % P["a_tqc"], table(TRIALS_QC, lang) + "\n" + {"en": "The first 16 columns are exactly `kret_results.csv`.", "ko": "앞 16열은 `kret_results.csv`와 완전히 같다.", "zh": "前 16 列与 `kret_results.csv` 完全一致。"}[lang] + "\n"))
    o.append(det("<b>%s</b>" % P["a_sqc"], table(SUBJ_QC, lang)))
    o.append(det("<b>%s</b>" % P["a_segcsv"], table(SEGCSV, lang)))
    o.append(det("<b>%s</b>" % P["a_final"], P["a_final_note"] + "\n\n" + final_list(lang)))
    # 4 settings
    o.append("## %s" % P["h_set"])
    o.append("")
    o.append(det("<b>%s</b>" % P["set_raw"], set_table(RAW_SET, lang)))
    o.append(det("<b>%s</b>" % P["set_valid"], set_table(VALID_SET, lang)))
    o.append(det("<b>%s</b>" % P["set_trk"], set_table(TRK_OPT, lang)))
    o.append(det("<b>%s</b>" % P["set_kret"], set_table(KRET_OPT, lang)))
    # 5 functions
    o.append("## %s" % P["h_fn"])
    o.append("")
    o.append(YMTC_CHAIN[lang])
    o.append("")
    hdr = {"en": ("file", "lines", "what it does", "writes"),
           "ko": ("파일", "행", "하는 일", "출력"),
           "zh": ("文件", "行数", "做什么", "写出")}[lang]
    o.append("| %s | %s | %s | %s |" % hdr)
    o.append("|---|---|---|---|")
    for f, n, what, out in YMTC_TABLE:
        o.append("| `%s` | %s | %s | %s |" % (f, n, what[i], out[i]))
    o.append("")
    o.append(det("<b>%s</b>" % P["fn_up"], "\n".join(det("<code>%s</code>" % n, d[i]) for n, d in HELPERS)))
    o.append(det("<b>%s</b>" % P["fn_our"], "\n".join(det("<code>%s</code>" % n, d[i]) for n, d in YMTC_FILES)))
    # 6 examples
    o.append("## %s" % P["h_ex"])
    o.append("")
    o.append(P["ex_text"])
    o.append("")
    o.append("\n".join(det("<code>Examples/%s/</code>" % n, d[i]) for n, d in EXAMPLES))
    # 7 troubleshooting
    o.append("## %s" % P["h_tr"])
    o.append("")
    o.append(trouble_tbl(lang))
    # 8 limits, 9 more
    o.append("## %s" % P["h_lim"])
    o.append("")
    o.append(P["lim"])
    o.append("")
    o.append(REVIEW[lang])
    o.append("")
    o.append("## %s" % P["h_more"])
    o.append("")
    o.append(P["more"])
    o.append("")
    o.append("Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods, 51*(3), 1336–1342.")
    return "\n".join(o) + "\n"


def build():
    top = ['<a id="top"></a>', "",
           "**[English](#english) · [한국어](#한국어) · [中文](#中文)**", ""]
    parts = list(top)
    for lang, anchor, name in (("en", "english", "English"), ("ko", "한국어", "한국어"), ("zh", "中文", "中文")):
        parts.append('<a id="%s"></a>' % anchor)
        parts.append("")
        parts.append(sectionlang(lang))
        parts.append("[↑ top](#top) · **[English](#english) · [한국어](#한국어) · [中文](#中文)**")
        parts.append("")
        parts.append("---")
        parts.append("")
    text = "\n".join(parts).rstrip("-\n ") + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(len(text.splitlines()), "lines", len(text) // 1024, "KB")


if __name__ == "__main__":
    build()
