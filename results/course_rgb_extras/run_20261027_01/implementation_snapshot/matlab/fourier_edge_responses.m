function out = fourier_edge_responses(I, sigma, cutoff, padding)
%FOURIER_EDGE_RESPONSES Gaussian derivatives and high-pass residuals by FFT.
% Frequencies use cycles/pixel. Padding=0 uses a periodic image model.
% cutoff is the ideal HP cutoff and the Gaussian HP characteristic scale.

validateattributes(I, {'double'}, {'2d', 'real', 'finite', 'nonempty'});
validateattributes(sigma, {'numeric'}, {'scalar', 'real', 'finite', 'positive'});
validateattributes(cutoff, {'numeric'}, ...
    {'scalar', 'real', 'finite', '>', 0, '<', 0.5});
if nargin < 4
    padding = max(32, ceil(6 * sigma));
end
validateattributes(padding, {'numeric'}, ...
    {'scalar', 'real', 'finite', 'integer', 'nonnegative'});

if padding > 0
    Ip = padarray(I, [padding padding], 'symmetric', 'both');
else
    Ip = I;
end
[M, N] = size(Ip);
fx = (-floor(N/2):ceil(N/2)-1) / N;
fy = (-floor(M/2):ceil(M/2)-1) / M;
[U, V] = meshgrid(fx, fy);
R2 = U.^2 + V.^2;
F = fftshift(fft2(Ip));

Hsmooth = exp(-2 * pi^2 * sigma^2 * R2);
Hx = 1i * 2 * pi * U .* Hsmooth;
Hy = 1i * 2 * pi * V .* Hsmooth;
% A real derivative must have zero response at the self-conjugate Nyquist
% frequency along its differentiated axis (for even image dimensions).
if mod(N, 2) == 0
    Hx(:, 1) = 0;
end
if mod(M, 2) == 0
    Hy(1, :) = 0;
end
Hideal = double(R2 >= cutoff^2);
Hgaussian = 1 - exp(-R2 / (2 * cutoff^2));

gxComplex = ifft2(ifftshift(F .* Hx));
gyComplex = ifft2(ifftshift(F .* Hy));
idealComplex = ifft2(ifftshift(F .* Hideal));
gaussianComplex = ifft2(ifftshift(F .* Hgaussian));
out.maxImaginaryResidual = max([max(abs(imag(gxComplex(:)))), ...
    max(abs(imag(gyComplex(:)))), max(abs(imag(idealComplex(:)))), ...
    max(abs(imag(gaussianComplex(:))))]);

rows = padding + (1:size(I, 1));
cols = padding + (1:size(I, 2));
out.gx = real(gxComplex(rows, cols));
out.gy = real(gyComplex(rows, cols));
out.magnitude = hypot(out.gx, out.gy);
% Retain signed high-pass residuals; abs() is used only for edge strength.
out.idealHighpass = real(idealComplex(rows, cols));
out.gaussianHighpass = real(gaussianComplex(rows, cols));
out.spectrum = F;
out.fx = fx;
out.fy = fy;
out.filters = struct('smoothing', Hsmooth, 'derivativeX', Hx, ...
    'derivativeY', Hy, 'idealHighpass', Hideal, ...
    'gaussianHighpass', Hgaussian);
out.padding = padding;
end
