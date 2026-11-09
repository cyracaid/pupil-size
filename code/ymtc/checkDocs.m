function ok = checkDocs(root)
%CHECKDOCS Compare the column dictionary with the real header of every output table.
% EN: Fails loudly when a table gains or loses a column that docs/02 does not list.
% KO: 표에 열이 추가되거나 빠졌는데 docs/02 에 없으면 실패한다.
% ZH: 表里多一列少一列而 docs/02 没写，就报错。
%
%   ok = checkDocs();          % uses ymtcConfig's root
%   ok = checkDocs('/path/to/project');
%
% Run after every pipeline run. Nothing is written; the answer is the console
% output and the returned flag (true = every table matches the dictionary).

arguments
    root (1,1) string = ""
end

if root == ""
    C = ymtcConfig();
    root = C.root;
end

%% Expected columns, straight from docs/02_column_dictionary.md

ev = ["participant","order","run","trial","trial_in_run","ymtc_marker","trk_event", ...
      "time_ms","t_from_onset_s","expected_from_onset_s","diff_s","expected_duration_s", ...
      "condition","timing","certainty","outcome","actual_outcome","step"];

stat = ["segmentStart","segmentEnd","SmoothSig_meanDiam","SmoothSig_minDiam", ...
        "SmoothSig_maxDiam","SmoothSig_missingDataPercent","SmoothSig_sampleCount", ...
        "ValidSamples_meanDiam","ValidSamples_minDiam","ValidSamples_maxDiam", ...
        "ValidSamples_validPercent","ValidSamples_sampleCount"];

segCols = strings(1, 0);
for s = ["baseline","countdown","preOutcome","postOutcome"]
    segCols = [segCols, s + "_" + stat]; %#ok<AGROW>
end

qc    = ["RejectCountdown","PreOutcomeMostlyMissing","SubjectExcluded"];
kret  = [stat(1:2), "segmentName", "segmentType", "participant", "trial", ...
         "leftPupil_" + stat(3:end)];

spec = {
    "04_all_segments",  fullfile(root,'04_瞳孔指标','04_all_segments.csv'),  kret
    "04_all_trials_qc", fullfile(root,'04_瞳孔指标','04_all_trials_qc.csv'),     [kret, qc]
    "04_all_subjects_qc",fullfile(root,'04_瞳孔指标','04_all_subjects_qc.csv'),   ["participant","nTrials","nRejected","rejectPct","subjectExcluded"]
    "05_all_markers_5step",fullfile(root,'05_marker表','05_all_markers_5step.csv'), ev
    "05_all_markers",fullfile(root,'05_marker表','05_all_markers.csv'),       ev
    "05_all_trials_wide",fullfile(root,'05_marker表','05_all_trials_wide.csv'), ...
        ["participant","order","run","trial","condition","timing","certainty","outcome", ...
         "onset_s","countdown_s","outcome_s","whitenoise_s","rating_s","has_rating"]
    "05_timing_check",   fullfile(root,'05_marker表','05_all_timing_check.csv'), ...
        ["participant","phase","n","mean_s","sd_s","min_s","max_s"]
    "run_check",         fullfile(root,'07_检查','07_all_run_check.csv'), ...
        ["participant","status","nSTART","nBurnInStart","nBurnOutStart","nCueStart", ...
         "trialsPerRun","runAssignmentOK","note"]
    "06_all_merged",fullfile(root,'06_合并表','06_all_merged.csv'), ...
        [ev, segCols, qc]
};

%% Compare

ok = true;
for i = 1:size(spec, 1)
    name = spec{i, 1};
    file = spec{i, 2};
    want = string(spec{i, 3});

    if ~isfile(file)
        fprintf('[skip] %-16s %s not found\n', name, file);
        ok = false;
        continue
    end

    fid = fopen(file, 'r');
    line = fgetl(fid);
    fclose(fid);
    got = string(strsplit(line, ','));

    missingCols = setdiff(want, got, 'stable');
    extraCols   = setdiff(got, want, 'stable');

    if isempty(missingCols) && isempty(extraCols)
        if isequal(want, got)
            fprintf('[ok]   %-16s %d columns\n', name, numel(got));
        else
            fprintf('[ok]   %-16s %d columns (same set, different order)\n', name, numel(got));
        end
    else
        ok = false;
        fprintf('[FAIL] %-16s %d columns\n', name, numel(got));
        if ~isempty(missingCols), fprintf('         missing in file : %s\n', strjoin(missingCols, ', ')); end
        if ~isempty(extraCols),   fprintf('         not in dictionary: %s\n', strjoin(extraCols, ', ')); end
    end
end

if ok
    fprintf('\nAll tables match docs/02_column_dictionary.md.\n');
else
    fprintf('\nAt least one table differs - update docs/02 (and docs/zh/02) in the same commit.\n');
end
end
