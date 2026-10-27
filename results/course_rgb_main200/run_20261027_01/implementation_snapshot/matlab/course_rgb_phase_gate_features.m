function C=course_rgb_phase_gate_features(F)
% Pure isotropic FFT/phase features. No anisotropic kernels or SVD bank.
b=.25;A=(1-b)*F.gx.^2+b*F.Jxx;B=(1-b)*F.gx.*F.gy+b*F.Jxy;
D=(1-b)*F.gy.^2+b*F.Jyy;theta=.5*atan2(2*B,A-D);
nx=cos(theta);ny=sin(theta);flip=nx.*F.gx+ny.*F.gy<0;nx(flip)=-nx(flip);ny(flip)=-ny(flip);
Q=(1-b)*F.Qgray+b*F.Qcolor;[X,Y]=meshgrid(1:size(Q,2),1:size(Q,1));
% Both sides must have support to protect a short phase valley along the
% original contour tangent. Sampling uses image-only reference directions.
tx=-ny;ty=nx;
q1=interp2(Q,X+2*tx,Y+2*ty,'linear',0);q2=interp2(Q,X-2*tx,Y-2*ty,'linear',0);
C=struct('reference',course_rgb_phase_map(F,struct('kind','rgb_phase','beta',.25)), ...
    'gray',course_rgb_phase_map(F,struct('kind','gray_phase')), ...
    'Q',Q,'Qbridge',max(Q,min(q1,q2)),'Qmax',max(F.Qgray,F.Qcolor));
assert(all(isfinite(C.Qbridge(:)))&&all(C.Qbridge(:)>=0&C.Qbridge(:)<=1+1e-12));
end
