function m = nanmedian(x)
%NANMEDIAN Fallback: median with NaN omission (no Statistics and Machine
%Learning Toolbox).
m = median(x, 'omitnan');
end
