function bank = course_fourier_scale_bank(I, sigmas, padding)
%COURSE_FOURIER_SCALE_BANK Reuse one image FFT for several Gaussian derivatives.
if nargin<3, padding=32; end
validateattributes(I,{'double'},{'2d','real','finite','nonempty','>=',0,'<=',1});
validateattributes(sigmas,{'numeric'},{'vector','real','finite','positive'});
validateattributes(padding,{'numeric'},{'scalar','integer','nonnegative'});
Ip=padarray(I,[padding padding],'symmetric','both');
[M,N]=size(Ip); fx=(-floor(N/2):ceil(N/2)-1)/N; fy=(-floor(M/2):ceil(M/2)-1)/M;
[U,V]=meshgrid(fx,fy); R2=U.^2+V.^2; F=fftshift(fft2(Ip));
rows=padding+(1:size(I,1)); cols=padding+(1:size(I,2)); bank=struct([]);
for sigma=reshape(sigmas,1,[])
    H=exp(-2*pi^2*sigma^2*R2); Hx=1i*2*pi*U.*H; Hy=1i*2*pi*V.*H;
    if mod(N,2)==0, Hx(:,1)=0; end
    if mod(M,2)==0, Hy(1,:)=0; end
    x=ifft2(ifftshift(F.*Hx)); y=ifft2(ifftshift(F.*Hy));
    gx=real(x(rows,cols)); gy=real(y(rows,cols));
    nms=gradient_nonmax_suppression(gx,gy,'peak');
    item=struct('sigma',sigma,'gx',gx,'gy',gy,'nms',nms);
    if isempty(bank),bank=item;else,bank(end+1)=item;end %#ok<AGROW>
end
end
