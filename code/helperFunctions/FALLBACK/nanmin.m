function m = nanmin(x)
%NANMIN Fallback: minimum with NaN omission (no Statistics and Machine
%Learning Toolbox). Column-wise for matrices, as the toolbox nanmin.
m = min(x, [], 'omitnan');
end
