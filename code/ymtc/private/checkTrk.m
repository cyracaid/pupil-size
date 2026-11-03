function [summary, issues] = checkTrk(participant, file, S, opts)
%CHECKTRK Record, never repair: compare a parsed log with what the task should have produced.
%   Severity "warn" = the file deviates from expectation; "info" = a fact worth knowing.
    issues = emptyIssues();
    function add(sev, code, msg)
        issues = [issues; table(string(participant), string(file), string(sev), string(code), string(msg), ...
            'VariableNames', issues.Properties.VariableNames)]; %#ok<AGROW>
    end

    tm = S.tm; M = S.M; evT = S.evT; evN = S.evN; ns = numel(tm);
    sm = emptySummary(participant, file);
    sm.n_samples = ns; sm.n_events = numel(evT);
    sm.duration_min = (tm(end) - tm(1)) / 60000;
    sm.sampling_hz = 1000 / median(diff(tm));
    sm.pupil_valid_fraction = mean(~isnan(M(:,9)));
    sm.gaze_valid_fraction = mean(~isnan(M(:,7)));
    sm.n_malformed_lines = S.malformed.n;

    cnt = @(name) sum(strcmp(evN, name));
    sm.n_START = cnt('START'); sm.n_BurnInStart = cnt('BurnInStart');
    sm.n_CueStart = cnt('CueStart'); sm.n_CueFinish = cnt('CueFinish');
    sm.n_StimuliStart = cnt('StimuliStart'); sm.n_RatingStart = cnt('RatingStart');
    sm.n_BurnOutStart = cnt('BurnOutStart');

    % --- file level -----------------------------------------------------------------
    if S.malformed.n > 0
        add('warn', 'MALFORMED_LINES', sprintf('%d line(s) could not be parsed and were skipped (first line numbers: %s). Example: "%s"', ...
            S.malformed.n, mat2str(S.malformed.lineNumbers'), S.malformed.examples{1}));
    end
    if ~S.header.has_stop_line
        add('warn', 'NO_STOP_LINE', 'The log has no "stop timecounter" line; it may be truncated.');
    end
    dt = diff(tm);
    if any(dt <= 0)
        j = find(dt <= 0, 1, 'first') + 1;
        add('warn', 'NONMONOTONIC_TIME', sprintf(['%d sample(s) have a timestamp not later than the previous one ' ...
            '(first: sample row %d, t=%.1f ms after %.1f ms). Rows are kept in log order; events are attached by time, so check the rows around it.'], ...
            sum(dt <= 0), j, tm(j), tm(j-1)));
    end
    gaps = find(dt > opts.MaxGapMs);
    if ~isempty(gaps)
        add('warn', 'TIME_GAP', sprintf('%d gap(s) longer than %g ms between samples (longest %.0f ms, first at t=%.1f s).', ...
            numel(gaps), opts.MaxGapMs, max(dt), (tm(gaps(1)) - tm(1)) / 1000));
    end
    if sm.pupil_valid_fraction < opts.MinValidFraction
        add('warn', 'LOW_PUPIL_VALID', sprintf('Only %.1f%% of samples have pupil data (reporting threshold %.0f%%; nothing was dropped).', ...
            100 * sm.pupil_valid_fraction, 100 * opts.MinValidFraction));
    end
    if sm.gaze_valid_fraction == 0
        add('info', 'NO_GAZE', 'No sample has gaze data.');
    end

    % --- events ---------------------------------------------------------------------
    if isempty(evT)
        add('warn', 'NO_EVENTS', 'The log has no SoftwareEvent lines; run, trial, phase and event cannot be filled.');
    else
        if sm.n_START ~= opts.ExpectedRuns
            add('warn', 'START_COUNT', sprintf('%d START event(s), expected %d (one per run).', sm.n_START, opts.ExpectedRuns));
        end
        if sm.n_BurnInStart ~= sm.n_START
            % name the BurnInStart that has no START since the previous BurnInStart
            tS = evT(strcmp(evN, 'START')); tB = evT(strcmp(evN, 'BurnInStart'));
            prev = -inf; miss = [];
            for k = 1:numel(tB)
                if ~any(tS > prev & tS < tB(k)), miss(end+1) = k; end %#ok<AGROW>
                prev = tB(k);
            end
            add('warn', 'START_BURNIN_MISMATCH', sprintf(['%d START but %d BurnInStart events. BurnInStart #%s has no START before it. ' ...
                'Run numbers are counted from START only, so samples before the first START are labelled run 0 and the later ' ...
                'runs are numbered one lower than their BurnInStart order.'], sm.n_START, sm.n_BurnInStart, mat2str(miss)));
        end
        expTrials = opts.ExpectedRuns * opts.ExpectedTrialsPerRun;
        if sm.n_CueStart ~= expTrials
            add('warn', 'TRIAL_COUNT', sprintf('%d CueStart event(s), expected %d (%d runs x %d trials).', ...
                sm.n_CueStart, expTrials, opts.ExpectedRuns, opts.ExpectedTrialsPerRun));
        end
        if sm.n_CueFinish ~= sm.n_CueStart || sm.n_StimuliStart ~= sm.n_CueStart
            add('warn', 'EVENT_COUNT_MISMATCH', sprintf('CueStart=%d, CueFinish=%d, StimuliStart=%d should be equal.', ...
                sm.n_CueStart, sm.n_CueFinish, sm.n_StimuliStart));
        end
        known = {'START','BurnInStart','CueStart','CueFinish','CountdownFinish','StimuliStart', ...
            'WhitenoiseStart1','WhitenoiseStart2','WhitenoiseStart3','WhitenoiseStart4','RatingStart','BurnOutStart'};
        unk = setdiff(unique(evN), known);
        if ~isempty(unk)
            add('info', 'UNKNOWN_EVENTS', ['Event name(s) not in the known list: ' strjoin(unk', ', ')]);
        end
        cue = pairDur(evT(strcmp(evN, 'CueStart')), evT(strcmp(evN, 'CueFinish')));
        cd  = pairDur(evT(strcmp(evN, 'CueStart')), evT(strcmp(evN, 'StimuliStart')));
        if any(~isnan(cue))
            sm.cue_dur_min_s = min(cue); sm.cue_dur_mean_s = mean(cue, 'omitnan'); sm.cue_dur_max_s = max(cue);
            off = abs(cue - opts.CueDurationSec) > opts.CueToleranceSec;
            sm.n_cue_off_setting = sum(off);
            if any(off)
                add('warn', 'CUE_DURATION', sprintf(['%d of %d cue(s) differ from the %.3f s setting by more than %.3f s: ' ...
                    'min %.3f, mean %.3f, max %.3f s (%d shorter, %d longer).'], sum(off), sum(~isnan(cue)), ...
                    opts.CueDurationSec, opts.CueToleranceSec, sm.cue_dur_min_s, sm.cue_dur_mean_s, sm.cue_dur_max_s, ...
                    sum(cue < opts.CueDurationSec - opts.CueToleranceSec), sum(cue > opts.CueDurationSec + opts.CueToleranceSec)));
            end
        end
        if any(~isnan(cd))
            sm.countdown_min_s = min(cd); sm.countdown_mean_s = mean(cd, 'omitnan'); sm.countdown_max_s = max(cd);
        end
    end

    sm.n_issues = height(issues);
    if any(issues.severity == "warn"), sm.status = "warn"; else, sm.status = "ok"; end
    summary = struct2table(sm);
end

function d = pairDur(tS, tE)
% Seconds from each start to the first end after it, NaN if the next start comes first or no end exists.
    d = nan(numel(tS), 1);
    for k = 1:numel(tS)
        j = find(tE > tS(k), 1, 'first');
        if isempty(j), continue; end
        if k < numel(tS) && tE(j) >= tS(k+1), continue; end
        d(k) = (tE(j) - tS(k)) / 1000;
    end
end
