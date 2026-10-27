function m = nanmax(x)
%NANMAX Fallback: maximum with NaN omission (no Statistics and Machine
%Learning Toolbox). Column-wise for matrices, as the toolbox nanmax.
m = max(x, [], 'omitnan');
end
