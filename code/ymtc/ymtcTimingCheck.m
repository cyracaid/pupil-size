function S = ymtcTimingCheck(csvFile)
%YMTCTIMINGCHECK How far the trk markers drift from the task design.
%
%   S = ymtcTimingCheck;                               % all subjects together
%   S = ymtcTimingCheck('.../sub149_event_table.csv');  % one subject
%
% Descriptive only. For every subject and every trial-level marker it shows
% n, mean, SD, min and max of diff_s = measured - designed (seconds):
%   Countdown start  < 0  -> the cue ran shorter than the 1 s design
%   Outcome start    > 0  -> the outcome came later than designed
% Nothing is tested, nothing is corrected. A marker without a trk time
% (diff_s = NaN) is dropped and counted, not filled in.
%
% Writes 05_事件对照表/timing_check.csv, the same table that is printed.

arguments
    csvFile (1,1) string = ""
end

C = ymtcConfig();                          % paths; override in ymtc_config.m
if csvFile == ""
    csvFile = fullfile(C.outDir, 'all_subjects_event_table_5step.csv');
    if ~isfile(csvFile)                    % 5-step version not made yet -> full version
        csvFile = fullfile(C.outDir, 'all_subjects_event_table.csv');
    end
end
assert(isfile(csvFile), 'Input table not found: %s', csvFile);

A    = readtable(csvFile, 'TextType', 'string');
nAll = height(A);

%% 1. Keep the trial-level markers only
%    Noise parts carry no design value, and run-level rows have diff_s = NaN.
keep = ~startsWith(A.ymtc_marker, "WhiteNoise_part") & ~isnan(A.diff_s);
T    = A(keep, :);
fprintf('%d of %d rows kept (dropped: noise parts and markers with no trk time)\n', ...
    height(T), nAll);

%% 2. Collapse the long marker names into the five steps of one trial
m     = T.ymtc_marker;
phase = repmat("other", height(T), 1);
phase(startsWith(m, "Onset"))                                                = "1 Onset";
phase(startsWith(m, "PredictableTime") | startsWith(m, "UnpredictableTime")) = "2 Countdown start";
phase(startsWith(m, "Outcome"))                                              = "3 Outcome start";
phase(m == "WhiteNoise")                                                     = "4 WhiteNoise start";
phase(m == "Rating")                                                         = "5 Rating start";
T.phase = phase;

%% 3. n / mean / SD / min / max, per subject and per phase
[g, part, ph] = findgroups(T.participant, T.phase);
S = table(part, ph, ...
    splitapply(@numel, T.diff_s, g), ...
    splitapply(@mean,  T.diff_s, g), ...
    splitapply(@std,   T.diff_s, g), ...
    splitapply(@min,   T.diff_s, g), ...
    splitapply(@max,   T.diff_s, g), ...
    'VariableNames', {'participant', 'phase', 'n', 'mean_s', 'sd_s', 'min_s', 'max_s'});
S = sortrows(S, {'phase', 'participant'});

disp(S)
writetable(S, fullfile(C.outDir, 'timing_check.csv'));

%% 4. One line per phase: average of the subject means, so no subject
%    dominates the average (everyone has 84 trials here anyway).
[g2, ph2] = findgroups(S.phase);
fprintf('\nmean of the subject means (seconds):\n');
for i = 1:numel(ph2)
    fprintf('  %-20s %+7.3f   (subjects: %d)\n', ph2(i), ...
        mean(S.mean_s(g2 == i)), sum(g2 == i));
end
end
