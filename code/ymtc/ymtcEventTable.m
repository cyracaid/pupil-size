function T = ymtcEventTable(subId, options)
%YMTCEVENTTABLE One subject -> one CSV of event markers in YMTC order.
% EN: Build one subject's YMTC marker table: Onset > countdown > Outcome > WhiteNoise > Rating.
% KO: 한 피험자의 YMTC 마커 표를 만든다: Onset > 카운트다운 > Outcome > WhiteNoise > Rating.
% ZH: 生成单个被试的 YMTC marker 表：Onset → 倒计时 → Outcome → WhiteNoise → Rating。
%
%   T = ymtcEventTable('sub149');
%   T = ymtcEventTable('sub149', 'Order', 4);   % force the trial order
%   T = ymtcEventTable('sub149', 'NoiseParts', false);   % 4-5 rows per trial
%
% Input : 03_events/<subId>_events.csv   (trk markers: participant,time_ms,event)
%         TrialOrder-HK/TrialOrder<o>Run<r>.xlsx   (the task's marker names/onsets/durations)
% Output: 05_markers/05_<subId>_markers.csv, one row per marker, in time order:
%         Onset<cond> > PredictableTime...(countdown) > Outcome<cond> > WhiteNoise > Rating
%         With 'NoiseParts', false the file is 05_<subId>_markers_5step.csv instead
%         (no WhiteNoise_part2-4 rows, 4-5 rows per trial).
%         Columns: participant, order, run, trial, trial_in_run, ymtc_marker, trk_event,
%         time_ms, t_from_onset_s, expected_from_onset_s, diff_s, expected_duration_s,
%         condition, timing, certainty, outcome, actual_outcome, step
%           condition  PTCT / PTCS / PTUO / UTCT / UTCS / UTUO   (read off Onset<cond>)
%           timing     P / U        certainty  C / U
%           outcome    T / S / O    (O = the order's name does not say, the Outcome does)
%           actual_outcome  T / S, what the trial really ended in. Equal to `outcome` for
%                      certain trials; for the uncertain ones (UO) it is the last letter of
%                      the Outcome marker name (OutcomeUTUOT -> T, OutcomeUTUOS -> S).
%           step       1 Onset, 2 countdown, 3 Outcome, 4 WhiteNoise, 5 Rating
%
% How the trk markers line up with the task markers (one trial):
%   trk CueStart          = Onset<cond>        (cue, 1 s)
%   trk CueFinish         = countdown start    (PredictableTime... / UnpredictableTime...)
%   trk StimuliStart      = Outcome<cond>      (2.7 s)
%   trk WhitenoiseStart1  = WhiteNoise         (2.3 s; parts 2-4 are kept as extra rows)
%   trk RatingStart       = Rating             (6 s, only some trials)
% The condition name is NOT in the trk file. It comes from the trial order, and the
% order is chosen by comparing each trial's countdown length with the order files.
% Nothing is repaired: a marker that is absent in the trk gets an empty time.

arguments
    subId (1,1) string
    options.Order (1,1) double = 0        % 0 = pick the best-matching order
    options.NoiseParts (1,1) logical = true   % false = drop WhiteNoise_part2-4 rows
end

%% 1. Paths (no absolute path here; see ymtcConfig.m / ymtc_config.m)
C        = ymtcConfig();
evFile   = fullfile(C.eventDir, subId + "_events.csv");
orderDir = C.orderDir;
outDir   = C.outDir;
if ~isfolder(outDir), mkdir(outDir); end

%% 2. Read the trk markers (already time ordered in the file)
E = readtable(evFile, 'TextType', 'string');
assert(height(E) > 0, '%s has no event markers in the trk file.', subId);

cueIdx  = find(E.event == "CueStart");
stimIdx = find(E.event == "StimuliStart");
nTrial  = min(numel(cueIdx), numel(stimIdx));

%% 3. Load the 5 x 4 trial orders
orders = cell(5, 4);
for o = 1:5
    for r = 1:4
        orders{o, r} = readOrder(fullfile(orderDir, sprintf('TrialOrder%dRun%d.xlsx', o, r)));
    end
end

%% 4. Choose the order: compare countdown length (StimuliStart - CueStart - 1 s cue)
dur = (E.time_ms(stimIdx(1:nTrial)) - E.time_ms(cueIdx(1:nTrial))) / 1000 - 1;
err = zeros(5, 1);
for o = 1:5
    for r = 1:floor(nTrial / 21)
        d = dur((r-1)*21 + (1:21));
        expected = cellfun(@(x) x.dur(2), orders{o, r}.trials(:));   % countdown row duration
        err(o) = err(o) + mean(abs(d - expected));
    end
end
[errSorted, rank] = sort(err);
if options.Order == 0
    order = rank(1);
else
    order = options.Order;
end
fprintf('%s: order %d (mean error summed over runs %.2f s; next best %.2f s)\n', ...
    subId, order, err(order), errSorted(2));

%% 5. Walk through the markers in time order and write rows
trkNames = ["CueStart" "CueFinish" "StimuliStart" "WhitenoiseStart1" "RatingStart"];
rows = {};
trial = 0;
nMismatch = 0;
for i = 1:height(E)
    ev = E.event(i);

    if any(ev == ["START" "BurnInStart" "BurnOutStart"])
        % run-level markers: no trial, no condition
        rows(end+1, :) = {subId, order, NaN, NaN, NaN, ev, ev, E.time_ms(i), ...
                          NaN, NaN, NaN, NaN, "", "", "", "", "", NaN}; %#ok<AGROW>
        continue
    end

    if ev ~= "CueStart", continue, end          % trial blocks are written at CueStart
    trial = trial + 1;
    if trial > nTrial, break, end
    run = ceil(trial / 21);  k = trial - (run-1)*21;
    tr  = orders{order, run}.trials{k};          % names/onsets/durations of this trial
    cueTime = E.time_ms(i);

    % Condition code, read straight off the trial's first marker name:
    %   OnsetPTCTO -> PTCT   OnsetPTCSO -> PTCS   OnsetPTUO -> PTUO
    %   OnsetUTCTO -> UTCT   OnsetUTCSO -> UTCS   OnsetUTUO -> UTUO
    cond = extractBefore(extractAfter(tr.names(1), "Onset"), 5);
    cl   = char(cond);          % string "PTCT" -> char row 'PTCT', so letters can be picked
    timing    = string(cl(1));  % P / U  (predictable vs unpredictable time)
    certainty = string(cl(3));  % C / U  (certain vs uncertain outcome)
    outcome   = string(cl(4));  % T / S / O  (O = threat or safe is decided at the outcome)
    % what the trial really ended in: for UO trials read the last letter of the Outcome marker name
    actual = outcome;
    if outcome == "O"
        outName = char(tr.names(3));          % e.g. 'OutcomeUTUOT'
        actual  = string(outName(end));       % T or S
    end

    % trk markers that belong to this trial: from this CueStart to the next one
    if trial < numel(cueIdx), lastRow = cueIdx(trial+1) - 1; else, lastRow = height(E); end
    block = E(i:lastRow, :);
    % a RatingStart after the trial's last marker belongs to this trial too

    for m = 1:numel(tr.names)                    % m = 1 Onset, 2 countdown, 3 Outcome, 4 WhiteNoise, 5 Rating
        j = find(block.event == trkNames(m), 1); % first matching trk marker
        if isempty(j), tms = NaN; else, tms = block.time_ms(j); end
        rows(end+1, :) = {subId, order, run, trial, k, tr.names(m), trkNames(m), tms, ...
            (tms - cueTime)/1000, tr.onset(m) - tr.onset(1), ...
            (tms - cueTime)/1000 - (tr.onset(m) - tr.onset(1)), tr.dur(m), ...
            cond, timing, certainty, outcome, actual, m}; %#ok<AGROW>
        if m == 4 && options.NoiseParts            % extra white-noise parts 2-4
            for p = 2:4
                j = find(block.event == "WhitenoiseStart" + p, 1);
                if isempty(j), tms = NaN; else, tms = block.time_ms(j); end
                rows(end+1, :) = {subId, order, run, trial, k, "WhiteNoise_part" + p, ...
                    "WhitenoiseStart" + p, tms, (tms - cueTime)/1000, NaN, NaN, NaN, ...
                    cond, timing, certainty, outcome, actual, 4}; %#ok<AGROW>
            end
        end
    end

    % consistency: trk has RatingStart iff the order has a Rating row
    hasRatingTrk   = any(block.event == "RatingStart");
    hasRatingOrder = numel(tr.names) >= 5;
    if hasRatingTrk ~= hasRatingOrder
        nMismatch = nMismatch + 1;
        fprintf('  trial %d (run %d): Rating in trk = %d, in order = %d\n', ...
            trial, run, hasRatingTrk, hasRatingOrder);
    end
end

%% 6. Table + CSV
T = cell2table(rows, 'VariableNames', {'participant', 'order', 'run', 'trial', 'trial_in_run', ...
    'ymtc_marker', 'trk_event', 'time_ms', 't_from_onset_s', 'expected_from_onset_s', ...
    'diff_s', 'expected_duration_s', 'condition', 'timing', 'certainty', 'outcome', 'actual_outcome', 'step'});
% The noise-free version gets its own name, so the two never overwrite
% each other: <sub>_event_table.csv vs <sub>_event_table_5step.csv.
if options.NoiseParts
    outFile = fullfile(outDir, "05_" + subId + "_markers.csv");
else
    outFile = fullfile(outDir, "05_" + subId + "_markers_5step.csv");
end
writetable(T, outFile);
fprintf('%d rows written to %s\n', height(T), outFile);
fprintf('trials in trk: %d; Rating mismatches vs order: %d\n', nTrial, nMismatch);
end

%% ---- helper: one TrialOrder xlsx -> trials, each with marker names/onsets/durations ----
function R = readOrder(xlsx)
T  = readtable(xlsx);
nm = string(T.names);
starts = find(startsWith(nm, "Onset"));       % each trial starts at an Onset row
R.trials = cell(numel(starts), 1);
for t = 1:numel(starts)
    first = starts(t);
    if t < numel(starts), last = starts(t+1) - 1; else, last = numel(nm); end
    names = nm(first:last);
    R.trials{t} = struct('names', names, 'onset', T.onsets(first:last), 'dur', T.durations(first:last));
end
end
