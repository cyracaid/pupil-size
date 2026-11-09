function W = ymtcTrialWide(inFile, outFile)
%YMTCTRIALWIDE Long event table -> one row per trial, one column per step.
%
%   W = ymtcTrialWide;                        % all_subjects_event_table_5step.csv
%   W = ymtcTrialWide('.../sub149_event_table.csv', '.../sub149_trials_wide.csv');
%
% Input : the long table written by ymtcEventTable / ymtcEventTableBatch
%         (one row per marker). The 5-step and the full version both work;
%         noise parts and run-level rows are dropped here.
% Output: 05_markers/05_all_trials_wide.csv, one row per trial:
%   participant, order, run, trial, condition, timing, certainty, outcome,
%   onset_s, countdown_s, outcome_s, whitenoise_s, rating_s, has_rating
%
% All times are seconds from that trial's Onset (so onset_s is always 0 and
% is only there to make the reference explicit). A step the trk did not log
% stays NaN - nothing is filled in. Trials without a Rating have NaN there
% and has_rating = false; that is 24 of the 84 trials per subject by design.

arguments
    inFile  (1,1) string = ""
    outFile (1,1) string = ""
end

C = ymtcConfig();                          % paths; override in ymtc_config.m
if inFile == ""
    inFile = fullfile(C.outDir, '05_all_markers_5step.csv');
end
if outFile == ""
    outFile = fullfile(C.outDir, '05_all_trials_wide.csv');
end
assert(isfile(inFile), 'Input table not found: %s', inFile);

T = readtable(inFile, 'TextType', 'string');

%% 1. Trial-level markers only
T = T(~isnan(T.trial), :);                               % drop run-level rows
T = T(~startsWith(T.ymtc_marker, "WhiteNoise_part"), :); % drop noise parts

%% 2. Group the rows into trials (one group = one trial)
key     = T.participant + "|" + string(T.run) + "|" + string(T.trial);
[u, ~, g] = unique(key, 'stable');

%% 3. One row per trial
rows = cell(numel(u), 14);
for i = 1:numel(u)
    b = T(g == i, :);
    t = nan(1, 5);                      % onset, countdown, outcome, whitenoise, rating
    t(b.step) = b.t_from_onset_s;       % b.step is 1..5 -> each time lands in its slot
    rows(i, :) = {b.participant(1), b.order(1), b.run(1), b.trial(1), ...
                  b.condition(1), b.timing(1), b.certainty(1), b.outcome(1), ...
                  t(1), t(2), t(3), t(4), t(5), ~isnan(t(5))};
end

%% 4. Table, sort, write
W = cell2table(rows, 'VariableNames', {'participant', 'order', 'run', 'trial', ...
    'condition', 'timing', 'certainty', 'outcome', ...
    'onset_s', 'countdown_s', 'outcome_s', 'whitenoise_s', 'rating_s', 'has_rating'});
% cell2table may leave text columns as cell arrays; make them plain strings
W.participant = string(W.participant);
W.condition   = string(W.condition);
W.timing      = string(W.timing);
W.certainty   = string(W.certainty);
W.outcome     = string(W.outcome);

W = sortrows(W, {'participant', 'trial'});
writetable(W, outFile);
fprintf('%d trials -> %s\n', height(W), outFile);
end
