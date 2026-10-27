function features=course_phase_features(I,padding)
%COURSE_PHASE_FEATURES Image-only FFT derivatives and author phase congruency.
if nargin<2,padding=32;end
bank=course_fourier_scale_bank(I,1.8,padding);features=bank(1);features.I=I;
features.normalX=features.gx./max(hypot(features.gx,features.gy),eps);
features.normalY=features.gy./max(hypot(features.gx,features.gy),eps);
Ip=padarray(I,[padding padding],'symmetric','both');
rr=padding+(1:size(I,1));cc=padding+(1:size(I,2));
features.phase=struct([]);
for k=[2 4]
    if max(I(:))-min(I(:))<=1e-12
        moment=zeros(size(I));orientation=moment;
    else
        [moment,~,orientation]=phasecong3(Ip,4,6,3,2.1,.55,k,.5,10,-1);
        moment=max(real(moment(rr,cc)),0);orientation=orientation(rr,cc);
        assert(all(isfinite(moment(:))),'Nonfinite author phase moment.');
    end
    % Author orientation is an anticlockwise normal in Cartesian coordinates.
    nx=cosd(orientation);ny=-sind(orientation);
    [nms,scale]=gradient_nonmax_suppression(moment.*nx,moment.*ny,'peak');
    item=struct('k',k,'moment',moment,'nms',nms*scale,'normalX',nx,'normalY',ny);
    if isempty(features.phase),features.phase=item;else,features.phase(end+1)=item;end %#ok<AGROW>
end
end
