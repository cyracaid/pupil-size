function t = emptyIssues()
%EMPTYISSUES An empty issues table with the five standard columns.
% EN: An empty issues table with the five standard columns.
% KO: 다섯 개 표준 열을 가진 빈 이상치 표.
% ZH: 五列标准结构的空异常表。
    t = table('Size', [0 5], 'VariableTypes', repmat({'string'}, 1, 5), ...
        'VariableNames', {'participant','file','severity','code','message'});
end
