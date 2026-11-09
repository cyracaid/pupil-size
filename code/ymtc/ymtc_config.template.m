function C = ymtc_config(C)
%YMTC_CONFIG TEMPLATE - copy to ymtc_config.m and edit. That file is git-ignored.
% EN: Optional override of ymtcConfig. Copy to ymtc_config.m, uncomment, edit.
% KO: ymtcConfig 덮어쓰기용 템플릿. ymtc_config.m 으로 복사한 뒤 주석을 풀고 수정한다.
% ZH: ymtcConfig 的可选覆盖模板。复制成 ymtc_config.m，去掉注释后改成自己的路径。
%
% Nothing here is necessary when the project folders sit next to 代码_matlab/.
% Use it when the raw data live somewhere else, e.g. an external drive:
%
%   C.root     = '/path/to/your/project';
%   C.eventDir = fullfile(C.root, 'events');
%   C.orderDir = fullfile(C.root, 'TrialOrder-HK');
%   C.outDir   = fullfile(C.root, 'event_tables');
%   C.qcDir    = fullfile(C.root, 'qc');
%
% ymtc_config.m itself is listed in .gitignore: keep machine paths out of the repo.

% C.root     = '/path/to/your/project';
% C.eventDir = fullfile(C.root, '03_events');
% C.outDir   = fullfile(C.root, '05_markers');
% C.orderDir = fullfile(C.root, 'TrialOrder-HK');
% C.qcDir    = fullfile(C.root, '00_检查');
end
