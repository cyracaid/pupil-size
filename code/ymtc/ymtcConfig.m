function C = ymtcConfig()
%YMTCCONFIG Folder layout used by the ymtc* functions. No absolute paths in the repo.
% EN: Where the YMTC folders are. Defaults sit next to this file; override in ymtc_config.m.
% KO: YMTC 폴더 위치. 기본값은 이 파일 옆이고, ymtc_config.m 에서 덮어쓴다.
% ZH: YMTC 各文件夹的位置。默认就在本文件旁边，可在 ymtc_config.m 里覆盖。
%
%   C = ymtcConfig();          % defaults + your private overrides
%
% The repository ships no absolute path. The defaults below assume the project
% layout that trk2csv / ymtcEventTable use (see README); if your folders live
% somewhere else, copy ymtc_config.template.m to ymtc_config.m, edit it, and
% that file - which is git-ignored - is applied on top of these defaults.
%
% Fields
%   root      project folder that holds the numbered folders
%   eventDir  03_events/                one csv per subject with the trk events
%   outDir    05_markers/           ymtcEventTable output
%   orderDir  TrialOrder-HK/          the task's trial order workbooks
%   qcDir     07_checks/                ymtcRunCheck output
%   pupilDir  04_pupil/            Kret pipeline output
%   mergeDir  06_merged/              ymtcMergeResults output

here = fileparts(mfilename('fullpath'));   % 代码_matlab/
root = fileparts(here);                    % project folder

C = struct();
C.root     = root;
C.eventDir = fullfile(root, '03_events');
C.outDir   = fullfile(root, '05_markers');
C.orderDir = fullfile(root, 'TrialOrder-HK');
C.qcDir    = fullfile(root, '07_checks');
C.pupilDir = fullfile(root, '04_pupil');
C.mergeDir = fullfile(root, '06_merged');

% Optional private override: a file the user creates and keeps out of git.
overrideFile = fullfile(here, 'ymtc_config.m');
if isfile(overrideFile)
    C = ymtc_config(C);        % receives the defaults, returns the edited struct
end
end
