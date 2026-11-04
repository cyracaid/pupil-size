function results = trk2csv_batch(inFolder, options)
%TRK2CSV_BATCH Convert every .trk in a folder (one csv per participant file) and collect all anomalies.
% EN: Convert every .trk in a folder, and write a QC summary plus an issues table.
% KO: 폴더 안의 모든 .trk 를 변환하고 QC 요약표와 이상치 표를 함께 쓴다.
% ZH: 转换整个文件夹的 .trk，并写出 QC 汇总表和异常表。
%
%   results = trk2csv_batch('D:\ymtc\raw');                         % csv go to D:\ymtc\raw\csv
%   results = trk2csv_batch(inFolder, 'OutFolder', outFolder, ...
%                           'Parameters', {'CueDurationSec', 1.0});  % options passed on to trk2csv
%
% Besides the per-participant csv files, two tables are written in OutFolder:
%   trk2csv_qc_summary.csv   one row per file: counts, valid fractions, cue/countdown durations, status
%   trk2csv_issues.csv       one row per recorded anomaly (participant, file, severity, code, message)
% A file that cannot be read is recorded as status "failed" with code READ_ERROR; the batch goes on.
%
% Name-value options
%   OutFolder   output folder (default: <inFolder>/csv)
%   Recursive   also search sub-folders (default false)
%   Parameters  cell array of name-value pairs forwarded to trk2csv, e.g. {'ExpectedRuns', 4}
%
% Output: struct with fields summary (table), issues (table), files (string array).

    arguments
        inFolder (1,:) char
        options.OutFolder (1,:) char = ''
        options.Recursive (1,1) logical = false
        options.Parameters (1,:) cell = {}
    end
    if isempty(options.OutFolder), options.OutFolder = fullfile(inFolder, 'csv'); end
    if ~isfolder(options.OutFolder), mkdir(options.OutFolder); end

    if options.Recursive
        files = dir(fullfile(inFolder, '**', '*.trk'));
    else
        files = dir(fullfile(inFolder, '*.trk'));
    end
    files = files(~[files.isdir]);
    [~, order] = sort({files.name}); files = files(order);
    if isempty(files)
        warning('trk2csv:noFiles', 'No .trk files found in %s', inFolder);
    end

    summaries = cell(numel(files), 1);
    issueList = cell(numel(files), 1);
    names = strings(numel(files), 1);
    for i = 1:numel(files)
        f = fullfile(files(i).folder, files(i).name);
        names(i) = string(f);
        try
            [~, rep] = trk2csv(f, 'OutFolder', options.OutFolder, options.Parameters{:});
            summaries{i} = rep.summary; issueList{i} = rep.issues;
        catch ME
            [~, base] = fileparts(files(i).name);
            tok = regexp(base, '^(sub\d+)', 'tokens', 'once');
            if isempty(tok), p = base; else, p = tok{1}; end
            sm = emptySummary(p, files(i).name); sm.n_issues = 1;
            summaries{i} = struct2table(sm);
            iss = emptyIssues();
            iss(end+1,:) = {string(p), string(files(i).name), "error", "READ_ERROR", string(ME.message)};
            issueList{i} = iss;
            fprintf('%s: FAILED: %s\n', files(i).name, ME.message);
        end
    end

    summary = vertcat(summaries{:});
    issues = vertcat(issueList{:});
    if isempty(summary), summary = struct2table(emptySummary('', '')); summary(1,:) = []; end
    if isempty(issues), issues = emptyIssues(); end
    writetable(summary, fullfile(options.OutFolder, 'trk2csv_qc_summary.csv'));
    writetable(issues, fullfile(options.OutFolder, 'trk2csv_issues.csv'));
    results = struct('summary', summary, 'issues', issues, 'files', names);

    fprintf('\n%d file(s): %d ok, %d with warnings, %d failed. Summary and issues written to %s\n', ...
        height(summary), sum(summary.status == "ok"), sum(summary.status == "warn"), ...
        sum(summary.status == "failed"), options.OutFolder);
end
