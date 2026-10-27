function run_course_rgb_main200(indices)
% Six unchanged frozen pipelines on the complete official200 test images.
root=fileparts(fileparts(mfilename('fullpath')));run=fullfile(root,'results','course_rgb_main200','run_20261027_01');
addpath(fullfile(root,'external','kovesi'),fullfile(root,'external','structured_edges'));
for f={'matlab','images','channels'},addpath(fullfile(root,'external','pdollar_toolbox',f{1}));end
p=jsondecode(fileread(fullfile(run,'parameters_locked.json')));m=jsondecode(fileread(fullfile(run,'manifest.json')));
assert(m.count==200&&numel(p.methods)==6&&~p.parameterSearch&&~p.thresholdScan);
if nargin<1,indices=1:200;end
folder=fullfile(run,'samples');if ~isfolder(folder),mkdir(folder);end
for i=indices
    r=m.records(i);output=fullfile(folder,[r.id '.mat']);if isfile(output),fprintf('RGB200_CACHED %d/200 %s\n',i,r.id);continue;end
    totalTimer=tic;image=imread(r.image);I=im2double(rgb2gray(image));
    data=load(r.reference,'groundTruth');expectedR=sum(cellfun(@(t)nnz(t.Boundaries),data.groundTruth));
    rows=struct([]);masks=cell(1,6);detectionSeconds=zeros(1,6);scoringSeconds=zeros(1,6);scoredPixelCounts=zeros(1,6);
    mainDetails=struct;grayAgreement=false;
    for j=1:6
        method=p.methods{j};timer=tic;
        if j==1
            [BW,mainDetails]=course_fourier_edges(image);assert(strcmp(mainDetails.role,'main')&&~mainDetails.anisotropicSupport);
            assert(isequaln(jsondecode(jsonencode(mainDetails.choice)),p.selected));
        elseif j==2
            [BW,~]=course_fourier_edges(image,'gray');
            % Independent previous completed200 output, no regenerated labels.
            old=load(fullfile(root,'results','course_full200','run_20261027_01','samples','fft_phase',[r.id '.mat']),'fixed');
            grayAgreement=isequal(BW,old.fixed);assert(grayAgreement,'Frozen gray output changed: %s',r.id);
        else
            c=p.controls(strcmp({p.controls.method},method));assert(isscalar(c));BW=course_detect_edges(I,c,p.padding);
        end
        detectionSeconds(j)=toc(timer);assert(isequal(size(BW),size(I))&&islogical(BW));
        timer=tic;[~,cr,sr,cp,sp]=edgesEvalImg(double(BW),r.reference,'thrs',.5,'maxDist',p.maxDist,'thin',p.thin);
        scoringSeconds(j)=toc(timer);assert(sr==expectedR);
        scoredPixelCounts(j)=nnz(bwmorph(BW,'thin',Inf));assert(sp==scoredPixelCounts(j));
        P=cp/max(sp,1);R=cr/max(sr,1);
        row=struct('imageId',r.id,'method',method,'precision',P,'recall',R,'f1',2*P*R/max(P+R,eps), ...
            'cntR',cr,'sumR',sr,'cntP',cp,'sumP',sp,'detectionSeconds',detectionSeconds(j),'scoringSeconds',scoringSeconds(j));
        if isempty(rows),rows=row;else,rows(end+1)=row;end %#ok<AGROW>
        masks{j}=BW;
    end
    % Save responses for fixed first-three visual examples, not every image.
    example=struct;
    if any(strcmp(p.figures.exampleIds,r.id))
        example.seedResponse=mainDetails.seedResponse;example.linkResponse=mainDetails.linkResponse;
        RGB=im2double(image);spectrum=zeros(size(I,1)+64,size(I,2)+64,3);
        for c=1:3,spectrum(:,:,c)=log1p(abs(fftshift(fft2(padarray(RGB(:,:,c),[32 32],'symmetric','both')))));end
        example.logSpectra=spectrum;
    end
    seconds=toc(totalTimer);selected=p.selected;temporary=[output '.partial.mat'];
    save(temporary,'rows','masks','grayAgreement','selected','detectionSeconds','scoringSeconds','scoredPixelCounts','seconds','example');movefile(temporary,output,'f');
    fprintf('RGB200_SAVED %d/200 %s rows=6 seconds=%.2f\n',i,r.id,seconds);
end
fprintf('RGB200_WORKER_COMPLETE\n');
end
