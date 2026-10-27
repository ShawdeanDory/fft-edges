function [BW, nms] = thin_hysteresis_edges(gx, gy, thresholds, normalization)
%THIN_HYSTERESIS_EDGES Interpolated NMS and 8-connected hysteresis.
% thresholds=[low high] are fractions of this image's peak gradient.

if nargin < 4, normalization = 'peak'; end
validateattributes(thresholds, {'numeric'}, ...
    {'vector', 'numel', 2, 'real', 'finite', '>', 0, '<=', 1});
assert(thresholds(1) < thresholds(2), ...
    'fourierDemo:ThresholdOrder', 'Expected 0 < low < high <= 1.');

[nms, ~] = gradient_nonmax_suppression(gx,gy,normalization);

weak = nms >= thresholds(1);
strong = nms >= thresholds(2);
BW = imreconstruct(strong, weak, 8) > 0;
end
