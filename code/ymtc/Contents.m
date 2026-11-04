% trk2csv  MRC eye-tracker .trk logs to csv (one csv per participant), with anomaly recording
% EN: Package contents: trk2csv, trk2csv_batch and their private helpers.
% KO: 패키지 구성: trk2csv, trk2csv_batch 와 private 도우미 함수들.
% ZH: 包内容：trk2csv、trk2csv_batch 及其 private 辅助函数。
%
% Main functions
%   trk2csv        - convert one .trk file; returns the table and a report (summary, issues)
%   trk2csv_batch  - convert a folder of .trk files; writes qc summary and issues tables
%
% Tests
%   runtests('tests')
