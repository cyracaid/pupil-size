function S = ymtcEventTableBatch(options)
%YMTCEVENTTABLEBATCH All subjects -> one event table each, plus a summary.
%
%   S = ymtcEventTableBatch;                        % the 9 participants we have
%   S = ymtcEventTableBatch('Subjects', "sub149");  % just one
%   S = ymtcEventTableBatch('Order', 4);            % force one trial order for all
%   S = ymtcEventTableBatch('NoiseParts', false);   % 5 rows per trial, own file names
%
% This is only a loop around ymtcEventTable.m; the per-subject rules are there.
% For every subject the single input is 03_事件时间线/<sub>_events.csv:
%   file missing      -> status "skipped_no_file",   nothing is attempted
%   no CueStart rows  -> status "skipped_no_events", the trk has no trial markers
%   function fails    -> status "error",             the batch keeps going
%   otherwise         -> status "ok" and 05_事件对照表/<sub>_event_table.csv
%
% Output (in 05_事件对照表/):
%   <sub>_event_table.csv           from ymtcEventTable.m, one per subject that ran
%   all_subjects_event_table.csv    the same rows stacked, all subjects
%   event_table_summary.csv         one row per subject: status, chosen order,
%                                   rows, trials, note
%   With 'NoiseParts', false the two tables are named *_5step.csv instead,
%   and the summary is the same (the subjects and orders do not change).
% Nothing is repaired, imputed, or dropped silently: every subject ends up as
% one row of the summary, so a skipped participant is visible, not forgotten.

arguments
    options.Subjects (1,:) string = ["sub119" "sub124" "sub128" "sub134" ...
                                     "sub137" "sub139" "sub140" "sub141" "sub149"]
    options.Order (1,1) double = 0        % 0 = each subject picks its best order
    options.NoiseParts (1,1) logical = true   % false = 5-step tables, *_5step.csv
    options.WriteCombined (1,1) logical = true
end

here   = fileparts(mfilename('fullpath'));   % 代码_matlab/
root   = fileparts(here);                    % pupil folder
evDir  = fullfile(root, '03_事件时间线');
outDir = fullfile(root, '05_事件对照表');
if ~isfolder(outDir), mkdir(outDir); end

summary = {};      % one row per subject, written as event_table_summary.csv
parts   = {};      % event tables of the subjects that ran, for the combined csv

for s = options.Subjects

    %% 1. Skip a subject whose event timeline was never written
    evFile = fullfile(evDir, s + "_events.csv");
    if ~isfile(evFile)
        fprintf('[skip] %s: %s not found\n', s, evFile);
        summary(end+1, :) = {s, "skipped_no_file", NaN, 0, 0, ...
                             "no 03_事件时间线 csv"}; %#ok<AGROW>
        continue
    end

    %% 2. Read the markers and run the per-subject function.
    % One try/catch around both: whatever goes wrong for one subject becomes
    % one "error" row in the summary, and the batch keeps going.
    try
        % The event column must be forced to string. On a header-only csv
        % (no data rows) 'TextType' does not apply and 'event' comes back as
        % a double column, so comparing it with "CueStart" would error out.
        opt = detectImportOptions(evFile);
        opt = setvartype(opt, {'participant', 'event'}, 'string');
        E   = readtable(evFile, opt);

        nCue = 0;                                % no rows -> no trials, no error
        if height(E) > 0
            nCue = sum(E.event == "CueStart");
        end
        if nCue == 0
            fprintf('[skip] %s: no CueStart in the trk markers\n', s);
            summary(end+1, :) = {s, "skipped_no_events", NaN, 0, 0, ...
                                 "trk 里没有 CueStart"}; %#ok<AGROW>
            continue
        end

        T = ymtcEventTable(s, 'Order', options.Order, 'NoiseParts', options.NoiseParts);

        if nCue < 21                             % order match had nothing to compare
            fprintf('[warn] %s: only %d CueStart, order matching needs >= 21\n', s, nCue);
        end
        summary(end+1, :) = {s, "ok", T.order(1), height(T), max(T.trial), ...
                             ""}; %#ok<AGROW>
        parts{end+1} = T; %#ok<AGROW>
    catch err
        fprintf('[error] %s: %s\n', s, err.message);
        summary(end+1, :) = {s, "error", NaN, 0, 0, ...
                             string(err.message)}; %#ok<AGROW>
    end
end

%% 5. Summary table: one row per subject, ok or not
S = cell2table(summary, 'VariableNames', ...
    {'participant', 'status', 'order', 'nRows', 'nTrials', 'note'});
% cell2table leaves text columns as cell arrays; make them string so that
% the comparisons in step 7 and writetable behave predictably.
S.participant = string(S.participant);
S.status      = string(S.status);
S.note        = string(S.note);
writetable(S, fullfile(outDir, 'event_table_summary.csv'));

%% 6. All rows in one table (optional but handy for the next step)
if options.WriteCombined && ~isempty(parts)
    allT = vertcat(parts{:});
    % the 5-step version goes to its own file, so the two never overwrite
    if options.NoiseParts
        name = "all_subjects_event_table.csv";
    else
        name = "all_subjects_event_table_5step.csv";
    end
    writetable(allT, fullfile(outDir, name));
    fprintf('\ncombined: %d rows from %d subject(s) -> %s\n', ...
        height(allT), numel(parts), name);
end

%% 7. Tally
fprintf('\n%d subjects: %d ok, %d skipped, %d error\n', numel(options.Subjects), ...
    sum(S.status == "ok"), sum(startsWith(S.status, "skipped")), ...
    sum(S.status == "error"));
disp(S)
end
