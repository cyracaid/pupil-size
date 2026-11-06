function S = ymtcRunCheck(options)
%YMTCRUNCHECK Is each run really 21 trials? Run-level marker inventory.
% EN: Check that every run really has 21 trials, counted from BurnInStart.
% KO: 모든 run 이 정말 21 trial 인지 BurnInStart 기준으로 확인한다.
% ZH: 用 BurnInStart 做分界，核对每个 run 是否真的 21 个 trial。
%
%   S = ymtcRunCheck;                          % the 9 participants
%   S = ymtcRunCheck('Subjects', "sub134");    % one
%
% Why this exists: ymtcEventTable assigns trial k of run r by counting
% CueStart events (run = ceil(trial/21)). That silently assumes every run
% has exactly 21 trials. A missing START event does NOT break that, but a
% missing or extra trial would, and nothing would complain.
%
% Here the run boundaries come from BurnInStart (one per run, present in
% every subject so far), which is independent of START. So the trial count
% per run can be checked even when START is missing.
%
% Prints, per subject: how many START / BurnInStart / BurnOutStart / CueStart
% events there are, the trials per run, the START -> BurnInStart gaps, and a
% verdict. Writes 00_数据检查报告/run_check.csv. Nothing is repaired.

arguments
    options.Subjects (1,:) string = ["sub119" "sub124" "sub128" "sub134" ...
                                     "sub137" "sub139" "sub140" "sub141" "sub149"]
    options.TrialsPerRun (1,1) double = 21
end

C      = ymtcConfig();                       % paths; override in ymtc_config.m
evDir  = C.eventDir;
outDir = C.qcDir;
if ~isfolder(outDir), mkdir(outDir); end

rows = {};
for s = options.Subjects
    f = fullfile(evDir, s + "_events.csv");
    if ~isfile(f)
        fprintf('[skip] %s: no event timeline\n', s);
        rows(end+1, :) = {s, "no_file", 0, 0, 0, 0, "", false, "no 03_事件时间线 csv"}; %#ok<AGROW>
        continue
    end

    % the event column must be forced to string (see ymtcEventTableBatch)
    opt = detectImportOptions(f);
    opt = setvartype(opt, {'participant', 'event'}, 'string');
    E   = readtable(f, opt);
    if height(E) == 0
        fprintf('[skip] %s: no event rows in the trk\n', s);
        rows(end+1, :) = {s, "no_events", 0, 0, 0, 0, "", false, "trk 没有事件行"}; %#ok<AGROW>
        continue
    end

    ev   = E.event;
    t    = E.time_ms;
    nSTA = sum(ev == "START");
    nBI  = sum(ev == "BurnInStart");
    nBO  = sum(ev == "BurnOutStart");
    nCue = sum(ev == "CueStart");

    % 1. trials per run, using BurnInStart (not START) as the boundary
    runOf  = cumsum(ev == "BurnInStart");      % 0 before the first BurnInStart
    cueRun = runOf(ev == "CueStart");
    nRun   = max(runOf);
    counts = zeros(1, nRun);
    for r = 1:nRun
        counts(r) = sum(cueRun == r);
    end
    perRun = strjoin(string(counts), "/");

    % 2. START -> BurnInStart gaps (only pairs where both exist)
    gaps = [];
    lastStart = NaN;
    for i = 1:numel(ev)
        if ev(i) == "START", lastStart = t(i); end
        if ev(i) == "BurnInStart" && ~isnan(lastStart)
            gaps(end+1) = (t(i) - lastStart) / 1000; %#ok<AGROW>
            lastStart = NaN;
        end
    end

    % 3. verdict: run assignment in ymtcEventTable is only safe if every
    %    run has TrialsPerRun trials and there are as many runs as BurnIns
    runOK = nRun > 0 && nRun == nBI && all(counts == options.TrialsPerRun);
    note  = "";
    if nSTA < nBI
        note = sprintf("START 少 %d 个；run 从 START 数会错位，trial 划分不受影响", nBI - nSTA);
    end
    if ~runOK
        note = strtrim(note + " " + sprintf("每 run 的 trial 数不是 %d：条件可能对错 run", options.TrialsPerRun));
    end

    fprintf('%s: START %d, BurnInStart %d, BurnOutStart %d, CueStart %d -> 每 run %s\n', ...
        s, nSTA, nBI, nBO, nCue, perRun);
    if ~isempty(gaps)
        fprintf('   START->BurnInStart: %s s\n', strjoin(compose("%.1f", gaps), "  "));
    end
    if note ~= "", fprintf('   ! %s\n', note); end

    rows(end+1, :) = {s, "ok", nSTA, nBI, nBO, nCue, perRun, runOK, note}; %#ok<AGROW>
end

%% Summary table
S = cell2table(rows, 'VariableNames', {'participant', 'status', 'nSTART', ...
    'nBurnInStart', 'nBurnOutStart', 'nCueStart', 'trialsPerRun', 'runAssignmentOK', 'note'});
S.participant   = string(S.participant);
S.status        = string(S.status);
S.trialsPerRun  = string(S.trialsPerRun);
S.note          = string(S.note);
writetable(S, fullfile(outDir, 'run_check.csv'));

nOk   = sum(S.status == "ok" &  S.runAssignmentOK);
nBad  = sum(S.status == "ok" & ~S.runAssignmentOK);
nSkip = sum(S.status ~= "ok");
fprintf('\n%d subject(s): %d ok, %d run structure needs a look, %d skipped (no events)\n', ...
    height(S), nOk, nBad, nSkip);
disp(S)
end
