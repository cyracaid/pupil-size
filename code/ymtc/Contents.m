% ymtc  MRC .trk logs -> sample csv -> event timeline -> marker table
% EN: Package contents: trk2csv (samples), exportEvents (event timeline), the ymtc* tables.
% KO: 패키지 구성: trk2csv(샘플), exportEvents(이벤트 타임라인), ymtc* 표들.
% ZH: 包内容：trk2csv（样本）、exportEvents（事件时间线）、ymtc* 各表。
%
% Main functions
%   trk2csv        - convert one .trk file; returns the table and a report (summary, issues)
%   trk2csv_batch  - convert a folder of .trk files; writes qc summary and issues tables
%   exportEvents   - one .trk or a folder -> 03_事件/<sub>_events.csv (one row per event)
%
% Marker tables
%   ymtcEventTable      - one subject -> 05_<sub>_markers.csv, one row per marker
%   ymtcEventTableBatch  - every subject, plus a summary and a combined table
%   ymtcRunCheck        - is every run really 21 trials (counted from BurnInStart)
%   ymtcTimingCheck     - diff_s per subject and marker
%   ymtcTrialWide       - long marker table -> one row per trial
%
% Housekeeping
%   ymtcConfig    - where the folders are (no path in the code)
%   checkDocs     - expected columns vs the header of every output table
%
% Tests
%   runtests('tests')
