function L = labelSamples(tm, evT, evN)
%LABELSAMPLES Attach events to samples and fill run / trial / phase forward from the events.
% EN: Attach events to samples, and carry run / trial / phase forward from them.
% KO: 이벤트를 샘플에 붙이고 run / trial / phase 를 앞으로 이어 간다.
% ZH: 把事件挂到样本上，并据此向后填充 run / trial / phase。
%   Each event goes on the first sample with time >= event time. Several events on the same
%   sample are joined with ';'. Nothing is inferred: run counts START events only, so samples
%   before the first START (or in a run whose START is missing) keep the previous run number
%   (0 at the start). Missing events are reported by checkTrk, not repaired here.
    ns = numel(tm);
    [evT, order] = sort(evT); evN = evN(order);
    nEv = numel(evT);
    eventStr = repmat({''}, ns, 1);
    marker = zeros(ns,1); runAt = zeros(ns,1); trialAt = zeros(ns,1); tirAt = zeros(ns,1);
    phaseAt = repmat({''}, ns, 1); runStartAt = nan(ns,1);
    run = 0; trial = 0; tir = 0; phase = 'pre'; runStart = NaN;
    for k = 1:nEv
        idx = find(tm >= evT(k), 1, 'first');
        if isempty(idx), idx = ns; end
        if isempty(eventStr{idx}), eventStr{idx} = evN{k}; else, eventStr{idx} = [eventStr{idx} ';' evN{k}]; end
        name = evN{k};
        switch true
            case strcmp(name, 'START')
                run = run + 1; tir = 0; phase = 'start'; runStart = tm(idx);
            case strcmp(name, 'CueStart')
                trial = trial + 1; tir = tir + 1; phase = 'cue';
            case strcmp(name, 'BurnInStart'),         phase = 'burn_in';
            case strcmp(name, 'CueFinish'),           phase = 'countdown';
            case strcmp(name, 'StimuliStart'),        phase = 'stimulus';
            case startsWith(name, 'WhitenoiseStart'), phase = ['whitenoise' name(end)];
            case strcmp(name, 'RatingStart'),         phase = 'rating';
            case strcmp(name, 'BurnOutStart'),        phase = 'burn_out';
            otherwise  % e.g. CountdownFinish and unknown events keep the current phase
        end
        marker(idx) = idx; runAt(idx) = run; trialAt(idx) = trial; tirAt(idx) = tir;
        phaseAt{idx} = phase; runStartAt(idx) = runStart;
    end
    src = cummax(marker);
    has = src > 0;
    L.event = eventStr;
    L.run = zeros(ns,1); L.trial = zeros(ns,1); L.trial_in_run = zeros(ns,1);
    L.phase = repmat({'pre'}, ns, 1); runStartV = nan(ns,1);
    L.run(has) = runAt(src(has)); L.trial(has) = trialAt(src(has)); L.trial_in_run(has) = tirAt(src(has));
    L.phase(has) = phaseAt(src(has)); runStartV(has) = runStartAt(src(has));
    L.t_run_s = (tm - runStartV) / 1000;
end
