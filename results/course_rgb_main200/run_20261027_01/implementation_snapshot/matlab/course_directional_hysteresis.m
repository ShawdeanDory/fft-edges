function BW=course_directional_hysteresis(S,nx,ny,low,high,angleDegrees)
%COURSE_DIRECTIONAL_HYSTERESIS Seeded weak-edge graph with orientation gates.
weak=S>=low;strong=S>=high;BW=false(size(S));
if ~any(strong(:)),return;end
if angleDegrees==0
    BW=imreconstruct(strong,weak,8)>0;
else
    pixels=find(weak);ids=zeros(size(S));ids(pixels)=1:numel(pixels);
    [M,N]=size(S);a=[];b=[];
    for step=[0 1;1 -1;1 0;1 1]'
        dy=step(1);dx=step(2);r=max(1,1-dy):min(M,M-dy);c=max(1,1-dx):min(N,N-dx);
        id1=ids(r,c);id2=ids(r+dy,c+dx);
        align=abs(nx(r,c).*nx(r+dy,c+dx)+ny(r,c).*ny(r+dy,c+dx))>=cosd(angleDegrees);
        length=hypot(dx,dy);
        tangent1=abs(dx*nx(r,c)+dy*ny(r,c))/length<=cosd(30)+1e-12;
        tangent2=abs(dx*nx(r+dy,c+dx)+dy*ny(r+dy,c+dx))/length<=cosd(30)+1e-12;
        keep=id1>0&id2>0&align&tangent1&tangent2;
        a=[a;id1(keep)];b=[b;id2(keep)]; %#ok<AGROW>
    end
    G=graph(a,b,[],numel(pixels));components=conncomp(G);
    seeded=unique(components(strong(pixels)));
    BW(pixels)=ismember(components,seeded);
end
BW=bwmorph(BW,'thin',Inf);BW([1 end],:)=false;BW(:,[1 end])=false;
end
