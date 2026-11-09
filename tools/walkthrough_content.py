# -*- coding: utf-8 -*-
"""Content for 构建_代码讲解.py: the map stages, the file order, and the notes.

Each entry in CONTENT[file]['blocks'] is (first_line, last_line) plus HTML for
the explanation. Line numbers are 1-based and must match the real file.
"""

FILES = [
    ("Contents.m", 11),
    ("ymtcConfig.m", 40),
    ("trk2csv.m", 87),
    ("trk2csv_batch.m", 76),
    ("private/readTrk.m", 79),
    ("private/labelSamples.m", 46),
    ("private/checkTrk.m", 134),
    ("private/emptySummary.m", 14),
    ("private/emptyIssues.m", 8),
    ("ymtcEventTable.m", 184),
    ("ymtcEventTableBatch.m", 122),
    ("csv2kretmat.m", 259),
    ("example_kret_pipeline.m", 140),
    ("ymtcTrialQC.m", 114),
    ("ymtcMergeResults.m", 109),
    ("ymtcTrialWide.m", 68),
    ("ymtcTimingCheck.m", 71),
    ("ymtcRunCheck.m", 117),
    ("checkDocs.m", 133),
    ("ymtcManipulationCheck.m", 113),
    ("ymtcFilterPlots.m", 85),
    ("ymtc_config.template.m", 23),
    ("tests/test_trk2csv.m", 201),
]

STAGES = [
    {"num": "01", "name": "原始数据", "desc": "眼动仪的 .trk，只读",
     "files": []},
    {"num": "02", "name": "解析", "desc": "一行一个样本的 csv",
     "files": [("trk2csv.m", 87), ("trk2csv_batch.m", 76),
               ("private/readTrk.m", 79), ("private/labelSamples.m", 46),
               ("private/checkTrk.m", 134)]},
    {"num": "03", "name": "事件", "desc": "每被试一个事件表",
     "files": [("ymtcEventTable.m", 184), ("ymtcEventTableBatch.m", 122)]},
    {"num": "04", "name": "瞳孔指标", "desc": "滤波、插值、分段、剔除",
     "files": [("csv2kretmat.m", 259), ("example_kret_pipeline.m", 140),
               ("ymtcTrialQC.m", 114)]},
    {"num": "05", "name": "marker 表", "desc": "宽表与时间检查",
     "files": [("ymtcTrialWide.m", 68), ("ymtcTimingCheck.m", 71)]},
    {"num": "06", "name": "合并", "desc": "69 列的主交付表",
     "files": [("ymtcMergeResults.m", 109)]},
    {"num": "07", "name": "检查", "desc": "运行结构与文档一致性",
     "files": [("ymtcRunCheck.m", 117), ("checkDocs.m", 133)]},
    {"num": "§", "name": "地图与工具", "desc": "路径、诊断、测试",
     "files": [("ymtcConfig.m", 40), ("ymtcManipulationCheck.m", 113),
               ("ymtcFilterPlots.m", 85), ("ymtc_config.template.m", 23),
               ("tests/test_trk2csv.m", 201), ("Contents.m", 11)]},
]

R = '<p class="rtip"><b>给 R 读者：</b>'


CONTENT = {
    # ------------------------------------------------------------------ 配置
    "ymtcConfig.m": {
        "summary": "所有函数共用的文件夹布局。仓库里不出现任何绝对路径，"
                   "路径从“这个文件在哪”推出来。",
        "blocks": [
            (1, 5, R + "相当于一个返回 list 的函数，里面有 7 个路径。<code>%YMTCCONFIG</code> "
                       "是 H1 行，<code>help ymtcConfig</code> 显示的就是它。三行 EN/KO/ZH 是给人和 agent 看的摘要。</p>"),
            (9, 21, "字段表：<code>root</code> 是项目根，其余六个各指一个编号文件夹。"
                    "注意注释里写的是**新名字**（<code>03_events</code>、<code>05_markers</code>），"
                    "和磁盘上的真实目录一致。</p>"),
            (23, 24, "<code>mfilename('fullpath')</code> 拿到**本文件自己的绝对路径**，"
                     "<code>fileparts</code> 取父目录，两次就得到项目根。"
                     "这样无论你把项目拷到哪里、谁 clone 到哪台机器，路径都对——"
                     "这是替代硬编码的关键一行。</p>"
                     "<p>对应 R 里的 <code>here::here()</code>。</p>"),
            (26, 33, "建一个 <code>struct</code>（类似 R 的 list），字段就是上面那张表。"
                     "<code>fullfile</code> 会按平台自动选 <code>/</code> 或 <code>\\</code>，"
                     "所以不要自己拼字符串。</p>"),
            (35, 40, "**私有覆盖**：如果用户建了 <code>ymtc_config.m</code>（被 .gitignore 排除），"
                     "就把默认结构体传给它，由它返回改过的版本。"
                     "于是同一个函数既能在仓库里跑，也能在用户自己的目录结构下跑，而不用改代码。</p>"
                     "<p>这是“配置与代码分离”的做法，等价于 R 里读一个 <code>config.yml</code>。</p>"),
        ],
    },

    # ------------------------------------------------------------- 剔除规则
    "ymtcTrialQC.m": {
        "summary": "分析计划里的三条 trial 剔除规则。它决定哪些 trial、哪些被试进入最终分析，"
                   "所以是整条链里最需要逐行确认的文件之一。",
        "blocks": [
            (1, 2, R + "函数有两个输出。<code>options</code> 不是普通参数——"
                       "它由下面的 <code>arguments</code> 块按名值对填充，"
                       "类似 R 里 <code>function(x, ..., max_missing = 50)</code> 的具名参数，但会做类型校验。</p>"),
            (3, 10, "两行调用示例：一个传路径，一个传内存表并覆盖默认值。"
                    "下面写明规则出处（分析计划第 6 步、Kret 2019 第 7 步），"
                    "科研代码里这一步很重要——读者要能追到规则是**谁定的**。</p>"),
            (11, 26, "<b>三条规则</b>，注意 <code>reject</code>（剔除）和 <code>flag</code>（只标记）是两回事："
                     "<ul><li><b>R1</b> countdown 段缺失 &gt; 50% → <b>剔除</b>该 trial</li>"
                     "<li><b>R2</b> preOutcome 段缺失太多 → <b>只标记</b>，因为这一段要当 GLM 的调节变量，"
                     "缺失多则不可信，但不该因此丢掉 trial</li>"
                     "<li><b>R3</b> 某被试被剔除的 trial 超过 20% → <b>整个被试排除</b>（Leuchs / Shechner）</li></ul>"
                     "还有一条（导数斜率 &gt;3.3 SD）明确声明<b>不在这里实现</b>，因为需要连续信号。</p>"),
            (27, 34, "标准三段：输入 / 选项 / 输出。<code>qcTable</code> 是原表加三列标记；"
                     "<code>summary</code> 是被试级汇总。</p>"),
            (35, 41, "<code>arguments</code> 块：<code>(1,1)</code> 是尺寸校验，<code>double</code> / "
                     "<code>logical</code> 是类型校验，<code>= 50</code> 是默认值。"
                     "传错类型（例如 <code>'50'</code> 字符串）会<b>立刻</b>报错，而不是跑到一半才崩。"
                     "R 里没有等价物，最接近的是 <code>stopifnot()</code>。</p>"),
            (43, 53, "读数据。如果已经是 table 就直接用（流水线走这条，零拷贝）；"
                     "否则读 CSV。</p>"
                     "<p><b>那个注释是一个真实的坑</b>：<code>readtable</code> 默认把文本列读成 cell 数组，"
                     "而后面拿它和 string 比 <code>== \"countdown\"</code> 会报 "
                     "<code>Invalid data type</code>。加 <code>'TextType','string'</code> 才安全。"
                     "R 里对应的是 <code>read.csv(..., stringsAsFactors = FALSE)</code> 之后还要注意 "
                     "character vs factor 的区别。</p>"),
            (54, 58, "列名检查：<code>setdiff</code> 找出“要求有、实际缺”的列，"
                     "<code>assert</code> 一旦非空就报错，并把缺的列名拼进错误信息。"
                     "比等到后面某个字段报“不存在”要清楚得多。</p>"),
            (60, 74, "<b>R1 / R2 的实现。</b>一条正经的 trial 表里 countdown 行和 preOutcome 行是混排的，"
                     "所以先用逻辑向量把它们分开（<code>isCountdown</code> 是<b>行掩码</b>，不是 trial 掩码）。</p>"
                     "<p>先整列建好全 false（<code>false(height(R),1)</code>），再只给对应段的行赋值："
                     "countdown 行管 <code>RejectCountdown</code>，preOutcome 行管 "
                     "<code>PreOutcomeMostlyMissing</code>，互不干扰。</p>"
                     "<p>右边 <code>R.leftPupil_...(isCountdown) &gt; 阈值</code> 是逐元素比较，"
                     "省略号只是续行。这就是 R 里的 <code>vec[mask] &gt; thr</code>。</p>"),
            (76, 84, "<b>R3 的实现。</b><code>cdFlags</code> 和 <code>subj</code> 都用同一个 "
                     "<code>isCountdown</code> 掩码取——一个 trial 恰好一个 countdown 行，"
                     "所以两者逐元素对齐，长度都等于 trial 数。</p>"
                     "<p><code>unique</code> 的第三个输出 <code>subjIdx</code> 把“被试名”变成"
                     "“分组编号”（A,A,B → 1,1,2）；<code>accumarray</code> 再按编号分组求和，"
                     "于是 <code>nTrials</code> 是每组计数、<code>nRejected</code> 是每组被剔数。"
                     "这在 R 里就是 <code>tapply(x, g, sum)</code> 或 <code>dplyr::count()</code>。</p>"
                     "<p><code>./</code> 是逐元素除法（不是矩阵除法），然后乘 100 比阈值。</p>"),
            (86, 95, "把被试级结论<b>展开回行级</b>：先建全 false 的列，再对每个被试把它所有行（两段都算）"
                     "赋成同一个值。这里用循环而不是向量化，因为“分组广播回行”没有一行等价函数，"
                     "而被试数很小，循环最易读。</p>"
                     "<p>最后 <code>table(...)</code> 造被试级汇总表，"
                     "<code>'VariableNames'</code> 按位置命名，顺序必须一一对应。</p>"),
            (97, 112, "打印。<code>~options.Quiet</code> 让流水线可以静默运行。"
                      "<code>%%</code> 是转义的字面百分号。</p>"
                      "<p>最后一行的 <code>char(string(subjectExcluded(i)))</code> 是防御式写法："
                      "<code>fprintf('%s', true)</code> 在不同 MATLAB 版本行为不一致，"
                      "转成 <code>'true'</code>/<code>'false'</code> 才稳。</p>"
                      "<p>注意 R2 的统计出现在报告里、却<b>不</b>进入 R3 —— 打印时也标了 "
                      "<code>(flag only)</code>，防止读者误以为它会剔除数据。</p>"),
            (114, 114, "结束函数。</p>"),
        ],
    },

    "Contents.m": {
        "summary": "只放一句话说明。MATLAB 用它给整个文件夹写摘要，"
                   "`help 代码_matlab` 会显示。",
        "blocks": [],
    },

    "trk2csv.m": {
        "summary": "把一个 `.trk` 文本日志解析成一行一个样本的 CSV。纯 MATLAB，不需要任何工具箱。"
                   "最重要的设计原则写在注释第 14 行：**只记录、不修补**。",
        "blocks": [
            (1, 16, R + "两个输出：数据表 <code>T</code> 和一份 report（结构体，含 summary / issues / header / csv）。</p>"
                       "<p>第 10–13 行说明了这张表的样子：<b>一行一个样本</b>，事件不单独占行，"
                       "而是挂到“时间戳第一个大于等于事件时刻”的那个样本上；"
                       "一个样本上如果有多个事件，用 <code>;</code> 连起来。"
                       "run / trial / phase 这些列是从事件往<em>后</em>填的。</p>"
                       "<p><b>第 14–16 行是全文件最重要的约定</b>：日志缺 START、没有事件、"
                       "cue 时长和设定不符——一律记进 <code>report.issues</code> 并打印，"
                       "但<em>写出去的数据保持原样</em>。这样下游看到的永远是真实的采集结果，"
                       "而不是被脚本悄悄“修好”的样子。</p>"),
            (18, 29, "选项表。注意 <code>ExpectedRuns = 4</code>、<code>ExpectedTrialsPerRun = 21</code>："
                     "任务设计是 4 个 run × 21 个 trial，这两个数只用来<b>核对</b>，不用来生成数据。</p>"),
            (30, 35, "输出说明：21 列。<code>pupil_valid</code> / <code>gaze_valid</code> 是日志里本来就有的标志位，"
                     "不是我们算的。</p>"),
            (37, 49, "<code>arguments</code> 块，和 <code>ymtcTrialQC</code> 一样：类型 + 尺寸 + 默认值。"
                     "区别是这里第一个参数限定了 <code>(1,:) char</code>（必须是字符行向量，不能是 string），"
                     "因为后面要用 <code>fileparts</code> 和 <code>regexp</code>。</p>"),
            (51, 58, "输出路径。<code>fileparts</code> 拆成目录/文件名/扩展名；"
                     "没给 <code>OutFolder</code> 就写到 <code>.trk</code> 旁边。"
                     "<code>isfile &amp;&amp; ~Overwrite</code> 时直接报错，避免覆盖别人正在用的结果。</p>"),
            (59, 61, "从文件名里抠出被试编号：正则 <code>^(sub\\d+)</code> 抓开头的 sub+数字。"
                     "抓不到就整段文件名当 ID。<code>tok{{1}}</code> 是提取到的字符串。</p>"),
            (63, 65, "<b>三步核心工作</b>，都放在 <code>private/</code> 里："
                     "<ul><li><code>readTrk</code>：把文本解析成表头 / 样本矩阵 / 事件</li>"
                     "<li><code>labelSamples</code>：把事件挂到样本、向后填 run/trial/phase</li>"
                     "<li><code>checkTrk</code>：和“任务应该产生什么”对比，生成 issues</li></ul>"
                     "三个函数各管一件事，这个文件只做编排。</p>"),
            (67, 75, "拼表。<code>repmat(string(participant), ns, 1)</code> 把被试 ID 复制成 ns 行，"
                     "这样表里每一行都自带被试名（R 里相当于 <code>rep()</code>）。</p>"
                     "<p><code>M</code> 是样本矩阵，<code>M(:,1..11)</code> 按位置摊进 11 列——"
                     "这种写法可读性差，但表格列顺序由 <code>'VariableNames'</code> 兜底，"
                     "两边的顺序必须一一对应，改一处就要改两处。</p>"
                     "<p>最后两列值得注意：<code>~isnan(M(:,9))</code> 和 <code>~isnan(M(:,7))</code> —— "
                     "有效性是<b>从数值本身推出来</b>的（NaN 即无效），不是另读一列标志。</p>"),
            (77, 80, "把三样东西打包进 report 返回；只有显式要求时才把 issues 写成 CSV。</p>"),
            (81, 86, "打印。每个 issue 一行，带 severity 和 code，方便 grep。"
                     "<code>%%</code> 这里没有，用的是普通 <code>%d</code> / <code>%s</code>。</p>"),
        ],
    },
    "trk2csv_batch.m": {
        "summary": "对一整个文件夹调用 `trk2csv`，另外产出两张质量表（`02_all_qc_summary.csv`、`02_all_issues.csv`）。",
        "blocks": [],
    },
    "private/readTrk.m": {
        "summary": "真正的解析器：把文本切成表头、样本、事件三段。被 `trk2csv` 调用，所以在 `private/` 里。",
        "blocks": [],
    },
    "private/labelSamples.m": {
        "summary": "把事件挂到样本上，并向后填充 run / trial / phase —— 每个样本因此知道自己属于哪个 trial。",
        "blocks": [],
    },
    "private/checkTrk.m": {
        "summary": "拿日志和“任务本来应该产生什么”对比，只**记录**异常，从不修补数据。",
        "blocks": [],
    },
    "private/emptySummary.m": {
        "summary": "空的 QC 汇总表骨架（列名齐全、零行），用于一个文件都没有的情况。",
        "blocks": [],
    },
    "private/emptyIssues.m": {
        "summary": "空的异常表骨架，同上。",
        "blocks": [],
    },
    "ymtcEventTable.m": {
        "summary": "一个被试 → 一行一个 marker 的表。条件、时序、确定性都从 marker 名字里解码，"
                   "order 则由倒计时长度反推。",
        "blocks": [],
    },
    "ymtcEventTableBatch.m": {
        "summary": "循环所有被试，加上汇总表和合并表。单个被试失败不会中断整批。",
        "blocks": [],
    },
    "csv2kretmat.m": {
        "summary": "把逐样本 CSV 转成 Kret 的 `.mat` 格式：时间归零、去重复时间戳、无效样本设 NaN、单位标成像素。",
        "blocks": [],
    },
    "example_kret_pipeline.m": {
        "summary": "跑 Kret 的整条算法：滤波 → 插值 → 平滑 → 分段 → 统计，产出 `04_all_segments.csv` 等。",
        "blocks": [],
    },
    "ymtcMergeResults.m": {
        "summary": "把事件表和瞳孔统计拼成 69 列的主交付表。**段统计挂在各自起始 marker 那一行**。",
        "blocks": [],
    },
    "ymtcTrialWide.m": {
        "summary": "长表转宽表：一个 trial 一行，每个 marker 一列。",
        "blocks": [],
    },
    "ymtcTimingCheck.m": {
        "summary": "按被试 × 阶段汇总实测与设计的时差（`diff_s`）。",
        "blocks": [],
    },
    "ymtcRunCheck.m": {
        "summary": "每个 run 真的是 21 个 trial 吗？用 `BurnInStart` 当分界来数。",
        "blocks": [],
    },
    "checkDocs.m": {
        "summary": "拿手写的列清单和真实 CSV 表头逐张比对，文档过期就报错。",
        "blocks": [],
    },
    "ymtcManipulationCheck.m": {
        "summary": "威胁 vs 安全的瞳孔对比：把两段的行合起来，逐被试做 Welch t。",
        "blocks": [],
    },
    "ymtcFilterPlots.m": {
        "summary": "不给桌面也要能看滤波效果：原始样本、被剔样本、平滑信号，导成 PNG。",
        "blocks": [],
    },
    "ymtc_config.template.m": {
        "summary": "私有配置模板。复制成 `ymtc_config.m`（被 git 忽略）就能覆盖默认路径。",
        "blocks": [],
    },
    "tests/test_trk2csv.m": {
        "summary": "解析层的自测：构造小日志、跑 trk2csv、逐项断言。",
        "blocks": [],
    },
}
