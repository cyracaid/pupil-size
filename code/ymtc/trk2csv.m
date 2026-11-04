function [T, report] = trk2csv(trkFile, options)
%TRK2CSV Convert one MRC eye-tracker .trk log into ONE csv, and record every anomaly.
% EN: Convert one MRC .trk log into one csv, recording anomalies instead of repairing them.
% KO: MRC .trk 로그 하나를 csv 하나로 변환하고, 이상치는 고치지 않고 기록만 한다.
% ZH: 把单个 MRC .trk 日志转成一个 csv；异常只记录，不修补。
%
%   T = trk2csv('sub119_YMTC_..._0001.trk');
%   [T, report] = trk2csv(trkFile, 'OutFolder', 'D:\ymtc\csv', 'CueDurationSec', 1.0);
%
% One row per eye-tracker sample. Task events (SoftwareEvent lines) are not written as
% rows of their own: each event is attached to the first sample whose timestamp is >= the
% event time and appears in the `event` column (several events on one sample are joined
% with ';'). run / trial / trial_in_run / phase are filled forward from the events.
% NOTHING IS REPAIRED OR INFERRED: if the log deviates from the expected structure
% (missing START, no events, unexpected counts, cue duration not equal to the setting, ...)
% the deviation is recorded in report.issues and printed; the data are written as logged.
%
% Name-value options
%   OutFolder             where the csv goes (default: folder of the .trk)
%   Overwrite             overwrite an existing csv (default true)
%   WriteReport           also write <name>_issues.csv next to the csv (default false)
%   ExpectedRuns          4      expected number of runs (START events)
%   ExpectedTrialsPerRun  21     expected trials per run
%   CueDurationSec        1.0    cue duration in the task setting
%   CueToleranceSec       0.001  allowed difference from the setting
%   MinValidFraction      0.5    pupil-valid fraction below this is reported (nothing dropped)
%   MaxGapMs              200    time gap between samples above this is reported
%   Quiet                 false  suppress printing
%
% Outputs
%   T       table with one row per sample, columns:
%           participant, run, trial, trial_in_run, phase, time_ms, t_run_s, event,
%           sp_pup_x/y, sp_glint_x/y, vector_x/y, gaze_x/y, pupil_2a, pupil_2b, pupil_angle,
%           pupil_valid, gaze_valid
%   report  struct: summary (1-row table), issues (table), header (struct), csv (path)

    arguments
        trkFile (1,:) char
        options.OutFolder (1,:) char = ''
        options.Overwrite (1,1) logical = true
        options.WriteReport (1,1) logical = false
        options.ExpectedRuns (1,1) double = 4
        options.ExpectedTrialsPerRun (1,1) double = 21
        options.CueDurationSec (1,1) double = 1.0
        options.CueToleranceSec (1,1) double = 0.001
        options.MinValidFraction (1,1) double = 0.5
        options.MaxGapMs (1,1) double = 200
        options.Quiet (1,1) logical = false
    end

    [folder, base, ext] = fileparts(trkFile);
    if isempty(options.OutFolder), options.OutFolder = folder; end
    if isempty(options.OutFolder), options.OutFolder = '.'; end
    if ~isfolder(options.OutFolder), mkdir(options.OutFolder); end
    outCsv = fullfile(options.OutFolder, [base '.csv']);
    if isfile(outCsv) && ~options.Overwrite
        error('trk2csv:exists', 'Output exists and Overwrite is false: %s', outCsv);
    end
    tok = regexp(base, '^(sub\d+)', 'tokens', 'once');
    if isempty(tok), participant = base; else, participant = tok{1}; end
    fileName = [base ext];

    S = readTrk(trkFile);
    L = labelSamples(S.tm, S.evT, S.evN);
    [summary, issues] = checkTrk(participant, fileName, S, options);

    M = S.M; ns = numel(S.tm);
    T = table(repmat(string(participant), ns, 1), L.run, L.trial, L.trial_in_run, string(L.phase), ...
        S.tm, L.t_run_s, string(L.event), ...
        M(:,1), M(:,2), M(:,3), M(:,4), M(:,5), M(:,6), M(:,7), M(:,8), M(:,9), M(:,10), M(:,11), ...
        ~isnan(M(:,9)), ~isnan(M(:,7)), ...
        'VariableNames', {'participant','run','trial','trial_in_run','phase','time_ms','t_run_s','event', ...
        'sp_pup_x','sp_pup_y','sp_glint_x','sp_glint_y','vector_x','vector_y','gaze_x','gaze_y', ...
        'pupil_2a','pupil_2b','pupil_angle','pupil_valid','gaze_valid'});
    writetable(T, outCsv);

    report = struct('summary', summary, 'issues', issues, 'header', S.header, 'csv', outCsv);
    if options.WriteReport
        writetable(issues, fullfile(options.OutFolder, [base '_issues.csv']));
    end
    if ~options.Quiet
        fprintf('%s: %d samples, %d events, %d issue(s) -> %s\n', participant, ns, numel(S.evT), height(issues), outCsv);
        for i = 1:height(issues)
            fprintf('  [%s] %s: %s\n', issues.severity(i), issues.code(i), issues.message(i));
        end
    end
end
