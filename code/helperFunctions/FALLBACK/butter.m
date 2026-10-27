function [b,a] = butter(n, Wn)
%BUTTER Fallback Butterworth lowpass filter design (no Signal Processing Toolbox).
%
%   [b,a] = butter(n, Wn) — lowpass only. Wn is the cutoff normalized to
%   Nyquist (0 < Wn < 1), exactly as in the toolbox butter, using the fs=2
%   convention. Coefficients are computed with the bilinear transform of the
%   analog Butterworth prototype (poles on the left-half circle), with
%   cutoff prewarping and DC gain normalized to 1.
%
%   This folder (FALLBACK/) is only added to the path when the Signal
%   Processing Toolbox is NOT available; when the toolbox is installed the
%   built-in butter is used instead. Results match the toolbox version to
%   numerical precision for the lowpass case used by the pupil-size code.

if ~(isnumeric(n) && isscalar(n) && isfinite(n) && n == floor(n) && n > 0)
    error('butter:fallback','Only a positive integer order is supported.');
end
if ~(isnumeric(Wn) && isscalar(Wn) && Wn > 0 && Wn < 1)
    error(['butter:fallback' ...
        ' Fallback supports only lowpass with 0 < Wn < 1 (Nyquist = 1).']);
end

% Digital cutoff (rad/sample) and its prewarped analog counterpart.
% Bilinear prewarping: Omega = (2/T)*tan(omega/2) with T = 1/fs = 1/2, so
% (2/T) = 4. (An earlier version divided omega by 4 instead of 2, which
% shifted the realized cutoff; verified against scipy.signal.butter.)
omegaC = pi*Wn;
OmegaC = 4*tan(omegaC/2);   % fs = 2 convention (s = 4 (z-1)/(z+1))

% Analog Butterworth prototype poles (left half plane) and their digital
% images; an n-th order lowpass has all n zeros at z = -1:
k  = 0:n-1;
p  = OmegaC * exp(1i*pi*(2*k + n + 1)/(2*n));
zp = (4 + p) ./ (4 - p);

bz  = real(poly(-ones(1,n)));
az  = real(poly(zp));
g   = polyval(bz,1) / polyval(az,1);   % normalize DC gain to 1
b   = bz / g;
a   = az;

end
