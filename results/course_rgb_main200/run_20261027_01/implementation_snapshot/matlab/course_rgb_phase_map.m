function S=course_rgb_phase_map(F,choice,qfrdMap)
% Fixed image-only fusion. No labels or fitted models enter this function.
if nargin<3,qfrdMap=[];end
gray=F.grayNMS.*(.75+.25*F.Qgray);
switch choice.kind
    case 'gray_phase'
        S=gray;
    case {'rgb_fft','rgb_phase'}
        b=choice.beta;
        if b==0||F.replicatedGray
            S=F.grayNMS;Q=F.Qgray;
        else
            A=(1-b)*F.gx.^2+b*F.Jxx;B=(1-b)*F.gx.*F.gy+b*F.Jxy;
            C=(1-b)*F.gy.^2+b*F.Jyy;
            lambda=max((A+C+sqrt(max((A-C).^2+4*B.^2,0)))/2,0);
            theta=.5*atan2(2*B,A-C);nx=cos(theta);ny=sin(theta);
            % Choose a repeatable sign; suppressing a ridge is sign-sensitive
            % on exact equal-valued plateaus in the existing NMS convention.
            flip=nx.*F.gx+ny.*F.gy<0;nx(flip)=-nx(flip);ny(flip)=-ny(flip);
            S=gradient_nonmax_suppression(sqrt(lambda).*nx,sqrt(lambda).*ny,'peak');
            Q=(1-b)*F.Qgray+b*F.Qcolor;
        end
        if strcmp(choice.kind,'rgb_phase'),S=S.*(.75+.25*Q);end
    case 'qfrd_fusion'
        assert(isequal(size(qfrdMap),size(gray))&&all(isfinite(qfrdMap(:))));
        S=(1-choice.beta)*gray+choice.beta*qfrdMap.*(.75+.25*F.Qcolor);
    otherwise,error('Unknown RGB branch: %s',choice.kind);
end
assert(all(isfinite(S(:)))&&min(S(:))>=-1e-12&&max(S(:))<=1+1e-10);
end
