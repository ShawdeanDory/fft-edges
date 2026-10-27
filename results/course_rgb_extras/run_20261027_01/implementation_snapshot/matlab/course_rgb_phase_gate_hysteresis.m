function [BW,details]=course_rgb_phase_gate_hysteresis(C,choice,high,ratio)
% Separate phase gating of strong seeds and weak continuation pixels.
seedQ=C.(choice.seedSupport);linkQ=C.(choice.linkSupport);
seedResponse=C.reference.*(1-choice.seedEta*(1-seedQ));
linkResponse=C.reference.*(1-choice.linkEta*(1-linkQ));
strong=seedResponse>=high;weak=linkResponse>=high*ratio;
assert(all(~strong(:)|weak(:)),'Strong seeds must be included in weak graph.');
if any(strong(:)),BW=imreconstruct(strong,weak,8)>0;else,BW=false(size(strong));end
BW=bwmorph(BW,'thin',Inf);BW([1 end],:)=false;BW(:,[1 end])=false;
if nargout>1
    details=struct('seedResponse',seedResponse,'linkResponse',linkResponse,'strong',strong,'weak',weak, ...
        'seedPixels',nnz(strong),'weakPixels',nnz(weak),'choice',choice,'high',high,'ratio',ratio);
end
end
