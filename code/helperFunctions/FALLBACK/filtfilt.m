function y = filtfilt(b,a,x)
%FILTFILT Fallback zero-phase filtering (no Signal Processing Toolbox).
%
%   y = filtfilt(b,a,x) filters x in the forward direction and then again
%   after time reversal, giving zero phase distortion.
%
%   DEVIATION from the toolbox filtfilt: the initial-condition refinement
%   (Gustafsson's method) that suppresses start-up transients is NOT applied
%   here. Residual transients last ~2*order samples at the signal edges.
%   For the long pupil-size recordings this pipeline processes (minutes at
%   1000 Hz), the effect on any analyzed segment is negligible; verify with
%   plotData() before trusting edge-adjacent segments.

x = x(:);
y = filter(b,a,x);
y = filter(b,a,y(end:-1:1));
y = y(end:-1:1);

end
