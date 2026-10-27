function F=course_rgb_phase_features(image,grayFeatures)
% Image-only RGB FFT derivatives and energy-weighted phase support.
% This is a vector-gradient extension, NOT a quaternion Fourier transform.
validateattributes(image,{'uint8','uint16','double','single'},{'real','finite','nonempty'});
if ismatrix(image),image=repmat(image,1,1,3);end
assert(size(image,3)==3,'Expected RGB image.');
RGB=im2double(image);assert(min(RGB(:))>=0&&max(RGB(:))<=1);
if nargin<2||isempty(grayFeatures)
    grayFeatures=course_phase_features(im2double(rgb2gray(image)),32);
end
g=grayFeatures; p=g.phase([g.phase.k]==4);
F=struct('grayNMS',g.nms,'gx',g.gx,'gy',g.gy, ...
    'Qgray',min(p.moment/.15,1),'Jxx',zeros(size(g.gx)), ...
    'Jxy',zeros(size(g.gx)),'Jyy',zeros(size(g.gx)), ...
    'Qcolor',zeros(size(g.gx)),'replicatedGray',false);
F.replicatedGray=isequal(RGB(:,:,1),RGB(:,:,2))&&isequal(RGB(:,:,1),RGB(:,:,3));
weighted=zeros(size(g.gx));energy=weighted;
for c=1:3
    I=RGB(:,:,c);bank=course_fourier_scale_bank(I,1.8,32);b=bank(1);
    F.Jxx=F.Jxx+b.gx.^2/3;F.Jxy=F.Jxy+b.gx.*b.gy/3;F.Jyy=F.Jyy+b.gy.^2/3;
    if max(I(:))-min(I(:))<=1e-12
        moment=zeros(size(I));
    else
        Ip=padarray(I,[32 32],'symmetric','both');
        moment=phasecong3(Ip,4,6,3,2.1,.55,4,.5,10,-1);
        moment=max(real(moment(33:32+size(I,1),33:32+size(I,2))),0);
    end
    w=b.gx.^2+b.gy.^2;weighted=weighted+w.*min(moment/.15,1);energy=energy+w;
end
F.Qcolor=weighted./max(energy,eps);F.Qcolor(energy<=1e-20)=0;
assert(all(isfinite(F.Qcolor(:)))&&all(F.Qcolor(:)>=0&F.Qcolor(:)<=1+1e-12));
end
