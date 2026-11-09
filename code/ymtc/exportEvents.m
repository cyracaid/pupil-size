function T = exportEvents(src, options)
%EXPORTEVENTS Write 03_事件/<sub>_events.csv: one row per SoftwareEvent, with its exact time.
% EN: Extract the event timeline of a .trk (or a folder of them) into the table ymtcEventTable reads.
% KO: .trk(또는 폴더)의 이벤트 타임라인을 ymtcEventTable 이 읽는 표로 뽑아낸다.
% ZH: 把 .trk（或整个文件夹）里的事件时间线导出成 ymtcEventTable 读的那张表。
%
%   T = exportEvents('01_原始trk');                    % every .trk -> 03_事件/<sub>_events.csv
%   T = exportEvents('01_原始trk/sub119_x.trk');       % one file
%   T = exportEvents('01_原始trk', 'OutFolder', 'tmp');% somewhere else
%
% Why this function exists: ymtcEventTable takes 03_事件/<sub>_events.csv as its
% only input, and nothing in this repository produced that file. The event times
% are read straight from the SoftwareEvent lines, so they are the event's own
% timestamp - not the timestamp of the first sample at or after it. This matters:
% trk2csv attaches events to samples (up to one sample interval, ~17 ms late) for
% the per-sample table, and that ~17 ms would show up as a bias in ymtcTimingCheck.
%
% Output table, 3 columns (one row per event, in log order):
%   participant  subject id, same rule as trk2csv (leading "sub<digits>", else the base name)
%   time_ms      the event's own timestamp from the log, ms
%   event        the event name as logged (CueStart, StimuliStart, ...)
%
% A file with no SoftwareEvent lines gets a header-only csv and a warning; nothing
% is invented to fill it. An existing csv is not replaced unless Overwrite is true.
%
% Name-value options
%   OutFolder    where the csv go (default: the project's 03_事件/, see ymtcConfig.m)
%   Subjects     only these subjects, e.g. ["sub119" "sub134"]
%   Overwrite    replace an existing <sub>_events.csv (default true)
%   Quiet        suppress the per-file line (default false)

arguments
    src (1,1) string
    options.OutFolder (1,1) string = ""
    options.Subjects (1,:) string = string.empty(1, 0)
    options.Overwrite (1,1) logical = true
    options.Quiet (1,1) logical = false
end

if options.OutFolder == ""
    C = ymtcConfig();
    outDir = C.eventDir;
else
    outDir = options.OutFolder;
end
if ~isfolder(outDir), mkdir(outDir); end

%% 1. Which .trk files
if isfolder(src)
    d = dir(fullfile(src, '*.trk'));
    files = strings(0, 1);
    for i = 1:numel(d), files(end+1, 1) = string(fullfile(d(i).folder, d(i).name)); end %#ok<AGROW>
elseif isfile(src)
    files = src;
else
    error('exportEvents:noInput', 'Not a .trk file and not a folder: %s', src);
end
if isempty(files)
    warning('exportEvents:noFiles', 'No .trk files found in %s', src);
end

%% 2. One csv per file
parts = cell(0, 1);
for i = 1:numel(files)
    [~, base] = fileparts(files(i));
    subId = participantOf(base);        % same rule as trk2csv.m, kept in step by hand

    if ~isempty(options.Subjects) && ~any(subId == options.Subjects)
        continue
    end

    S = readTrk(files(i));              % private/readTrk.m: header, samples, events
    n = numel(S.evT);
    if n == 0
        warning('exportEvents:noEvents', '%s has no SoftwareEvent lines; writing a header-only csv', base);
        T1 = table(strings(0, 1), zeros(0, 1), strings(0, 1), ...
            'VariableNames', {'participant', 'time_ms', 'event'});
    else
        T1 = table(repmat(subId, n, 1), S.evT(:), string(S.evN(:)), ...
            'VariableNames', {'participant', 'time_ms', 'event'});
    end

    outCsv = fullfile(outDir, subId + "_events.csv");
    if isfile(outCsv) && ~options.Overwrite
        error('exportEvents:exists', 'Output exists and Overwrite is false: %s', outCsv);
    end
    writetable(T1, outCsv);
    if ~options.Quiet
        fprintf('%s: %d events -> %s\n', subId, n, outCsv);
    end
    parts{end+1} = T1; %#ok<AGROW>
end

%% 3. All rows, for the console and for whoever wants them
if isempty(parts)
    T = table(strings(0, 1), zeros(0, 1), strings(0, 1), ...
        'VariableNames', {'participant', 'time_ms', 'event'});
else
    T = vertcat(parts{:});
end
if ~options.Quiet
    fprintf('%d file(s), %d events total -> %s\n', numel(parts), height(T), outDir);
end
end

% ---------------------------------------------------------------------------------
function subId = participantOf(base)
% The same rule trk2csv.m applies: a leading "sub<digits>", otherwise the whole base name.
tok = regexp(base, '^(sub\d+)', 'tokens', 'once');
if isempty(tok), subId = string(base); else, subId = string(tok{1}); end
end
