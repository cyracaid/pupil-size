function S = readTrk(trkFile)
%READTRK Parse an MRC eye-tracker .trk text log. Nothing is repaired or dropped silently.
% EN: Parse the .trk text log into header, samples and events. Nothing is repaired.
% KO: .trk 텍스트 로그를 헤더, 샘플, 이벤트로 파싱한다. 아무것도 고치지 않는다.
% ZH: 把 .trk 文本日志解析成表头、样本和事件；不做任何修补。
%   S.header    struct: start_timecounter, start_time_iso, stop_timecounter, stop_time_iso,
%               presentation_size, distance, column_line, has_stop_line
%   S.tm        n x 1 sample timestamps (ms)
%   S.M         n x 11 [sp_pup xy, sp_glint xy, vector xy, gaze xy, pupil 2a 2b angle]; NaN where the log says "no ..."
%   S.evT/evN   event times (ms) and names, in log order
%   S.malformed struct: n (count), lineNumbers (first 20), examples (first 3 texts)

    raw = fileread(trkFile);
    lines = splitlines(raw);

    h = struct('start_timecounter', NaN, 'start_time_iso', '', 'stop_timecounter', NaN, ...
        'stop_time_iso', '', 'presentation_size', [NaN NaN], 'distance', NaN, ...
        'column_line', '', 'has_stop_line', false);
    first = 0;
    for i = 1:numel(lines)
        s = strtrim(lines{i});
        if isempty(s), continue; end
        if startsWith(s, 'time(ms)'), h.column_line = s; first = i; break; end
        t = regexp(s, '^start timecounter:\s*([\d.]+)\s+time:\s*(\S+)', 'tokens', 'once');
        if ~isempty(t), h.start_timecounter = str2double(t{1}); h.start_time_iso = t{2}; end
        t = regexp(s, '^presentation_size:\s*(\d+)\s+(\d+)', 'tokens', 'once');
        if ~isempty(t), h.presentation_size = str2double(t); end
        t = regexp(s, '^distance\s+([\d.]+)', 'tokens', 'once');
        if ~isempty(t), h.distance = str2double(t{1}); end
    end
    if first == 0
        error('trk2csv:format', 'No column line ("time(ms) ...") found; is this an MRC .trk file?');
    end

    n = numel(lines);
    tm = nan(n,1); M = nan(n,11); isSample = false(n,1);
    evT = nan(n,1); evN = cell(n,1); nEv = 0;
    badLines = zeros(0,1); badText = cell(0,1);
    for i = first+1:n
        s = strtrim(lines{i});
        if isempty(s), continue; end
        if startsWith(s, 'stop timecounter')
            t = regexp(s, '^stop timecounter:\s*([\d.]+)\s+time:\s*(\S+)', 'tokens', 'once');
            if ~isempty(t)
                h.stop_timecounter = str2double(t{1}); h.stop_time_iso = t{2}; h.has_stop_line = true;
            end
        elseif contains(s, 'SoftwareEvent')
            t = regexp(s, '^([\d.]+)\s+SoftwareEvent\s+(\S+)', 'tokens', 'once');
            if isempty(t)
                badLines(end+1,1) = i; badText{end+1,1} = s; %#ok<AGROW>
            else
                nEv = nEv + 1; evT(nEv) = str2double(t{1}); evN{nEv} = t{2};
            end
        else
            % Field widths vary (e.g. "12.3  -6"), so do not split on spacing: replace every
            % "no ..." phrase by NaNs, then read 12 numbers:
            % time | pupil xy | glint xy | vector xy | gaze xy | pupil 2a 2b angle
            q = regexprep(s, 'no pupil geometry', 'nan nan nan');
            q = regexprep(q, 'no (pupil|glint|vektor|gaze)', 'nan nan');
            x = sscanf(q, '%f')';
            if numel(x) ~= 12 || isnan(x(1))
                badLines(end+1,1) = i; badText{end+1,1} = s; %#ok<AGROW>
            else
                tm(i) = x(1); M(i,:) = x(2:12); isSample(i) = true;
            end
        end
    end

    S.header = h;
    S.tm = tm(isSample);
    S.M = M(isSample,:);
    S.evT = evT(1:nEv);
    S.evN = evN(1:nEv);
    S.malformed = struct('n', numel(badLines), 'lineNumbers', badLines(1:min(20,end)), ...
        'examples', {badText(1:min(3,end))});
    if isempty(S.tm)
        error('trk2csv:empty', 'No samples found in %s', trkFile);
    end
end
