function t = emptyIssues()
    t = table('Size', [0 5], 'VariableTypes', repmat({'string'}, 1, 5), ...
        'VariableNames', {'participant','file','severity','code','message'});
end
