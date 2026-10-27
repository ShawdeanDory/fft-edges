function [nms, scale] = gradient_nonmax_suppression(gx, gy, normalization)
%GRADIENT_NONMAX_SUPPRESSION Interpolated gradient-direction ridge selection.
% 'peak' preserves the original demo. 'p99' limits sensitivity to one extreme
% contrast transition; both use image values alone and never ground truth.
if nargin < 3, normalization = 'peak'; end
validateattributes(gx, {'double'}, {'2d','real','finite','nonempty'});
validateattributes(gy, {'double'}, {'size',size(gx),'real','finite'});
magnitude = hypot(gx,gy);
nms = zeros(size(magnitude));
scale = max(magnitude(:));
if scale <= 1e-12 || any(size(gx)<3), return; end
switch char(normalization)
    case 'peak'
    case 'p99'
        positive = sort(magnitude(magnitude>1e-12));
        position = 1+(numel(positive)-1)*.99;
        left = floor(position); right = ceil(position);
        scale = positive(left)+(position-left)*(positive(right)-positive(left));
    otherwise
        error('fourierCourse:Normalization','Unknown gradient normalization.');
end
[X,Y] = meshgrid(1:size(gx,2),1:size(gx,1));
denominator = max(magnitude,eps);
dx = gx./denominator; dy = gy./denominator;
forward = interp2(magnitude,X+dx,Y+dy,'linear',0);
backward = interp2(magnitude,X-dx,Y-dy,'linear',0);
keep = magnitude>=forward & magnitude>backward & magnitude>1e-12;
keep([1 end],:) = false; keep(:,[1 end]) = false;
nms(keep) = min(magnitude(keep)/max(scale,1e-12),1);
end
