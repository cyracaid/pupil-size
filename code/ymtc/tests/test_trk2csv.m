function tests = test_trk2csv
%TEST_TRK2CSV Run with: runtests('tests')   (from the toolbox folder)
    tests = functiontests(localfunctions);
end

function setupOnce(tc)
    here = fileparts(fileparts(mfilename('fullpath')));
    addpath(here);
    tc.TestData.dir = tempname; mkdir(tc.TestData.dir);
end

function teardownOnce(tc)
    rmdir(tc.TestData.dir, 's');
end

% ---------------------------------------------------------------------------------
function testNormalFileEventsAttachedToSamples(tc)
    f = makeTrk(tc, 'sub001_ok.trk', fullStructure(2, 2));   % 2 runs x 2 trials
    [T, rep] = trk2csv(f, 'ExpectedRuns', 2, 'ExpectedTrialsPerRun', 2, 'Quiet', true);
    verifyGreaterThan(tc, height(T), 100);
    verifyTrue(tc, isfile(rep.csv));
    verifyEqual(tc, height(readtable(rep.csv)), height(T));
    verifyEqual(tc, max(T.run), 2);
    verifyEqual(tc, max(T.trial), 4);
    verifyEqual(tc, max(T.trial_in_run), 2);
    ev = T.event(T.event ~= "");
    verifyEqual(tc, sum(ev == "CueStart"), 4);
    % an event sits on the first sample at or after its time
    i = find(T.event == "CueStart", 1);                % first CueStart is at 2500 ms in fullStructure
    verifyTrue(tc, T.time_ms(i) >= 2500 && T.time_ms(i-1) < 2500);
    verifyEqual(tc, string(T.phase(i)), "cue");
    verifyTrue(tc, isempty(rep.issues) || all(rep.issues.severity ~= "error"));
    verifyEqual(tc, rep.summary.status, "ok");
end

function testVariableSpacingAndMissingFields(tc)
    lines = [header(); ...
        "1000.0  396.1 149.1  377.3 145.6  12.3722   -6  no gaze  51.1 56.3 1.012153 "; ...
        "1016.7  no pupil  no glint  no vektor  no gaze  no pupil geometry "; ...
        "1033.4  no pupil  220.3 146.7  no vektor  no gaze  no pupil geometry "; ...
        "1050.1  395.0 148.0  376.0 144.0  17.0   4.0  300.5 200.5  80.0 88.0 0.5 "; ...
        "stop timecounter: 1100.0 time: 2026-06-20T13:49:19.170+0900"];
    f = writeLines(tc, 'sub002_spacing.trk', lines);
    [T, rep] = trk2csv(f, 'Quiet', true);
    verifyEqual(tc, height(T), 4);
    verifyEqual(tc, T.vector_y(1), -6);
    verifyTrue(tc, isnan(T.pupil_2a(2)) && ~T.pupil_valid(2));
    verifyEqual(tc, T.sp_glint_x(3), 220.3);
    verifyTrue(tc, ~T.pupil_valid(3));
    verifyEqual(tc, T.gaze_x(4), 300.5);
    verifyTrue(tc, T.gaze_valid(4));
    verifyFalse(tc, any(rep.issues.code == "MALFORMED_LINES"));
end

function testMissingStartIsRecordedNotRepaired(tc)
    s = fullStructure(2, 2);
    s(find(strcmp(s(:,2), 'START'), 1), :) = [];   % drop the first START
    f = makeTrk(tc, 'sub003_nostart.trk', s);
    [T, rep] = trk2csv(f, 'ExpectedRuns', 2, 'ExpectedTrialsPerRun', 2, 'Quiet', true);
    codes = rep.issues.code;
    verifyTrue(tc, any(codes == "START_COUNT"));
    verifyTrue(tc, any(codes == "START_BURNIN_MISMATCH"));
    verifyEqual(tc, rep.summary.status, "warn");
    % not repaired: the first run's samples keep run 0, only the real START opens run 1
    firstCue = find(T.event == "CueStart", 1);
    verifyEqual(tc, T.run(firstCue), 0);
    verifyEqual(tc, max(T.run), 1);
    verifyEqual(tc, max(T.trial), 4);
end

function testNoEventsIsRecorded(tc)
    lines = [header(); sampleLines(1000, 20); "stop timecounter: 1400.0 time: 2026-06-20T13:49:19.170+0900"];
    f = writeLines(tc, 'sub004_noevents.trk', lines);
    [T, rep] = trk2csv(f, 'Quiet', true);
    verifyTrue(tc, any(rep.issues.code == "NO_EVENTS"));
    verifyTrue(tc, all(T.run == 0) && all(string(T.phase) == "pre") && all(T.event == ""));
end

function testMalformedLinesCountedAndSkipped(tc)
    lines = [header(); sampleLines(1000, 5); "this is not a sample"; "1100.0 garbage 12"; sampleLines(1200, 5)];
    f = writeLines(tc, 'sub005_bad.trk', lines);
    [T, rep] = trk2csv(f, 'Quiet', true);
    verifyEqual(tc, height(T), 10);
    verifyTrue(tc, any(rep.issues.code == "MALFORMED_LINES"));
    verifyEqual(tc, rep.summary.n_malformed_lines, 2);
    verifyTrue(tc, any(rep.issues.code == "NO_STOP_LINE"));
end

function testCueDurationDiffersFromSetting(tc)
    s = {0,'START'; 500,'BurnInStart'; 1000,'CueStart'; 1900,'CueFinish'; 5000,'StimuliStart'; ...
         6000,'CueStart'; 7000,'CueFinish'; 9000,'StimuliStart'};
    f = makeTrk(tc, 'sub006_cue.trk', s);
    [~, rep] = trk2csv(f, 'ExpectedRuns', 1, 'ExpectedTrialsPerRun', 2, 'Quiet', true);
    i = find(rep.issues.code == "CUE_DURATION");
    verifyEqual(tc, numel(i), 1);
    verifyEqual(tc, rep.summary.n_cue_off_setting, 1);
    verifyEqual(tc, rep.summary.cue_dur_min_s, 0.9, 'AbsTol', 1e-9);
    verifyEqual(tc, rep.summary.cue_dur_max_s, 1.0, 'AbsTol', 1e-9);
    verifyEqual(tc, rep.summary.countdown_max_s, 4.0, 'AbsTol', 1e-9);
end

function testOverwriteFlag(tc)
    f = makeTrk(tc, 'sub007_over.trk', fullStructure(1, 1));
    trk2csv(f, 'Quiet', true);
    verifyError(tc, @() trk2csv(f, 'Overwrite', false, 'Quiet', true), 'trk2csv:exists');
end

function testBatchWritesSummaryIssuesAndSurvivesBadFile(tc)
    inDir = fullfile(tc.TestData.dir, 'batch_in'); mkdir(inDir);
    outDir = fullfile(tc.TestData.dir, 'batch_out');
    copyfile(makeTrk(tc, 'sub010_a.trk', fullStructure(1, 2)), inDir);
    copyfile(makeTrk(tc, 'sub011_b.trk', fullStructure(1, 3)), inDir);   % trial count differs
    fid = fopen(fullfile(inDir, 'sub012_broken.trk'), 'w'); fprintf(fid, 'not a trk file\r\n'); fclose(fid);
    res = trk2csv_batch(inDir, 'OutFolder', outDir, 'Parameters', {'ExpectedRuns', 1, 'ExpectedTrialsPerRun', 2});
    verifyEqual(tc, height(res.summary), 3);
    st = containers.Map(cellstr(res.summary.participant), cellstr(res.summary.status));
    verifyEqual(tc, st('sub010'), 'ok');
    verifyEqual(tc, st('sub011'), 'warn');
    verifyEqual(tc, st('sub012'), 'failed');
    verifyTrue(tc, any(res.issues.code == "READ_ERROR"));
    verifyTrue(tc, any(res.issues.code == "TRIAL_COUNT" & res.issues.participant == "sub011"));
    verifyTrue(tc, isfile(fullfile(outDir, 'trk2csv_qc_summary.csv')));
    verifyTrue(tc, isfile(fullfile(outDir, 'trk2csv_issues.csv')));
    verifyTrue(tc, isfile(fullfile(outDir, 'sub010_a.csv')));
    verifyFalse(tc, isfile(fullfile(outDir, 'sub012_broken.csv')));
end

function testBatchDefaultOutFolderAndEmptyFolder(tc)
    inDir = fullfile(tc.TestData.dir, 'default_out'); mkdir(inDir);
    copyfile(makeTrk(tc, 'sub020_x.trk', fullStructure(1, 1)), inDir);
    trk2csv_batch(inDir, 'Parameters', {'ExpectedRuns', 1, 'ExpectedTrialsPerRun', 1});
    verifyTrue(tc, isfile(fullfile(inDir, 'csv', 'sub020_x.csv')));
    emptyDir = fullfile(tc.TestData.dir, 'empty'); mkdir(emptyDir);
    verifyWarning(tc, @() trk2csv_batch(emptyDir), 'trk2csv:noFiles');
end

% ---------------------------------------------------------------------------------
% helpers: synthetic .trk files (events are {time_ms, name}; samples every 16.7 ms)
function lines = header()
    lines = ["start timecounter: 0.0 time: 2026-06-20T13:10:56.228+0900"; "presentation_size: 1200 900"; ...
        "distance 1500"; "time(ms) sp_pup:x y sp_glint:x y vector:x y gaze:x y pupilsize: 2a 2b angle"; ""];
end

function out = sampleLines(t0, n)
    out = strings(n, 1);
    for k = 1:n
        out(k) = sprintf('%.1f  396.1 149.1  377.3 145.6  18.8241 3.44697  no gaze  81.2 88.6 0.712388 ', t0 + (k-1) * 16.7);
    end
end

function s = fullStructure(nRuns, nTrials)
% Per run: START, BurnInStart, then per trial CueStart, CueFinish (1 s), 3 s countdown, StimuliStart, 4 whitenoise.
    s = cell(0, 2); t = 0;
    for r = 1:nRuns
        s(end+1,:) = {t, 'START'}; t = t + 1000; %#ok<AGROW>
        s(end+1,:) = {t, 'BurnInStart'}; t = t + 500; %#ok<AGROW>
        for k = 1:nTrials
            s(end+1,:) = {t, 'CueStart'}; t = t + 1000; %#ok<AGROW>
            s(end+1,:) = {t, 'CueFinish'}; t = t + 3000; %#ok<AGROW>
            s(end+1,:) = {t, 'StimuliStart'}; t = t + 500; %#ok<AGROW>
            for w = 1:4, s(end+1,:) = {t, sprintf('WhitenoiseStart%d', w)}; t = t + 500; end %#ok<AGROW>
        end
        s(end+1,:) = {t, 'BurnOutStart'}; t = t + 1000; %#ok<AGROW>
    end
    s(:,1) = num2cell(cellfun(@(x) x + 1000, s(:,1)));   % shift so every event is after the first sample
end

function f = makeTrk(tc, name, events)
    events = events(:, 1:2);
    tEnd = max(cell2mat(events(:,1))) + 1000;
    lines = [header(); sampleLines(1000 - 16.7 * 3, ceil((tEnd - 1000) / 16.7) + 4)];
    ev = strings(size(events, 1), 1);
    for k = 1:size(events, 1)
        ev(k) = sprintf('%.1f SoftwareEvent  %s', events{k,1}, events{k,2});
    end
    sm = lines(5:end); sm = sm(sm ~= "");
    hd = lines(1:4);
    tSample = cellfun(@(x) sscanf(x, '%f', 1), cellstr(sm));
    tEvent = cell2mat(events(:,1));
    all = [sm; ev]; tAll = [tSample; tEvent];
    [~, o] = sort(tAll); body = all(o);
    stopLine = sprintf('stop timecounter: %.1f time: 2026-06-20T13:49:19.170+0900', tEnd);
    f = writeLines(tc, name, [hd; ""; body; stopLine]);
end

function f = writeLines(tc, name, lines)
    f = fullfile(tc.TestData.dir, name);
    fid = fopen(f, 'w'); fprintf(fid, '%s\r\n', lines{:}); fclose(fid);
end
