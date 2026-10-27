function [nn,bin] = histc(x, edges)
%HISTC Fallback for the removed histc function (two-output form).
%
%   [n,bin] = histc(x,edges) with ascending edges. Bin k counts
%   edges(k) <= x < edges(k+1); the LAST bin also includes its right
%   edge (x == edges(end)); elements outside the edge range get bin = 0
%   and are not counted in n. Semantics match the original histc.

x     = x(:);
edges = edges(:);
nb    = numel(edges);

if nb == 0
    nn  = zeros(0,1);
    bin = zeros(numel(x),1);
    return;
end

% O(n log m) via sorted-edge lookup; materializing x >= edges would need
% ~100 GB for typical pupil recordings (10^6 samples x 10^5 edges).
% 'previous' returns the index of the greatest edge <= x, i.e. exactly the
% histc bin; 0 below the first edge and for x beyond the last edge.
M   = numel(edges);
bin = interp1(edges, 1:M, x, 'previous', 0);
bin(x > edges(end)) = 0;      % strictly beyond last edge -> unbinned

nn = histcounts(x, edges).';

end
