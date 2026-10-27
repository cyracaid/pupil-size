function m = nanmean(x)
%NANMEAN Fallback: mean with NaN omission (no Statistics and Machine
%Learning Toolbox). Vector/matrix behavior matches the toolbox nanmean.
m = mean(x, 'omitnan');
end
