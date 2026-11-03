% trk2csv  MRC eye-tracker .trk logs to csv (one csv per participant), with anomaly recording
%
% Main functions
%   trk2csv        - convert one .trk file; returns the table and a report (summary, issues)
%   trk2csv_batch  - convert a folder of .trk files; writes qc summary and issues tables
%
% Tests
%   runtests('tests')
