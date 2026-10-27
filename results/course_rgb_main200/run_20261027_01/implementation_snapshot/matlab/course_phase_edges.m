function [BW,S,nx,ny]=course_phase_edges(features,choice,high)
%COURSE_PHASE_EDGES No reference labels enter any detector computation.
if nargin<3,high=choice.high;end
S=features.nms;nx=features.normalX;ny=features.normalY;
if strcmp(choice.kind,'canny')
    % S remains an FFT reference; it is not Canny's internal gradient map.
    BW=edge(features.I,'Canny',[high*choice.ratio high],1.8);
    BW=bwmorph(BW,'thin',Inf);BW([1 end],:)=false;BW(:,[1 end])=false;return;
end
if choice.k>0
    phase=features.phase(find([features.phase.k]==choice.k,1));
    if strcmp(choice.kind,'phase')
        S=phase.nms;nx=phase.normalX;ny=phase.normalY;
    else
        Q=min(phase.moment/.15,1);
        S=S.*((1-choice.alpha)+choice.alpha*Q);
    end
end
BW=course_directional_hysteresis(S,nx,ny,high*choice.ratio,high,choice.angle);
end
