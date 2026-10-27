function run_course_rgb_extras(indices)
root=fileparts(fileparts(mfilename('fullpath')));run=fullfile(root,'results','course_rgb_extras','run_20261027_01');
addpath(fullfile(root,'external','kovesi'),fullfile(root,'external','structured_edges'));
for f={'matlab','images','channels'},addpath(fullfile(root,'external','pdollar_toolbox',f{1}));end
p=jsondecode(fileread(fullfile(run,'parameters_locked.json')));m=jsondecode(fileread(fullfile(run,'manifest.json')));
t=jsondecode(fileread(fullfile(run,'tasks.json')));if nargin<1,indices=1:numel(t.tasks);end
folder=fullfile(run,'samples');if ~isfolder(folder),mkdir(folder);end
for index=indices
    task=t.tasks(index);output=fullfile(folder,[task.taskId '.mat']);if isfile(output),continue;end
    timer=tic;r=m.records(task.imageIndex);assert(strcmp(r.id,task.imageId));source=imread(r.image);RGB=im2double(source);
    input=source;inputStats=struct('rgbRMSE',0,'grayRMSE',0,'preclipRGBRMSE',0,'clippedFraction',0,'rngSeed',task.rngSeed);
    if task.noiseStd>0
        rng(task.rngSeed,'twister');raw=RGB+task.noiseStd*randn(size(RGB));input=im2uint8(min(max(raw,0),1));
        inputStats.preclipRGBRMSE=sqrt(mean((raw(:)-RGB(:)).^2));inputStats.clippedFraction=mean(raw(:)<0|raw(:)>1);
        difference=im2double(input)-RGB;inputStats.rgbRMSE=sqrt(mean(difference(:).^2));
        difference=im2double(rgb2gray(input))-im2double(rgb2gray(source));inputStats.grayRMSE=sqrt(mean(difference(:).^2));
    end
    if strcmp(task.stage,'ablation'),methods=p.ablationMethods;else,methods=p.noiseMethods;end
    F=course_rgb_phase_features(input);C=course_rgb_phase_gate_features(F);gray=im2double(rgb2gray(input));
    old=load(fullfile(root,'results','course_rgb_main200','run_20261027_01','samples',[r.id '.mat']),'masks');
    data=load(r.reference,'groundTruth');expectedR=sum(cellfun(@(x)nnz(x.Boundaries),data.groundTruth));
    rows=struct([]);masks=cell(1,numel(methods));regressions=struct('main',false,'gray',false,'allCleanControls',false);
    for j=1:numel(methods)
        name=methods{j};
        switch name
            case 'rgb_main',BW=course_rgb_phase_gate_hysteresis(C,p.selected,p.high,p.ratio);
            case 'gray_phase',BW=fromMap(C.gray,p);
            case 'gray_fft',BW=fromMap(F.grayNMS,p);
            case 'rgb_fft',BW=fromMap(course_rgb_phase_map(F,struct('kind','rgb_fft','beta',p.beta)),p);
            case 'rgb_phase',BW=fromMap(C.reference,p);
            otherwise
                choice=p.controls(strcmp({p.controls.method},name));assert(isscalar(choice));BW=course_detect_edges(gray,choice,p.padding);
        end
        if task.noiseStd==0
            if strcmp(name,'rgb_main'),regressions.main=isequal(BW,old.masks{1});assert(regressions.main);end
            if strcmp(name,'gray_phase'),regressions.gray=isequal(BW,old.masks{2});assert(regressions.gray);end
            if strcmp(task.stage,'noise'),assert(isequal(BW,old.masks{j}));end
        end
        [~,cr,sr,cp,sp]=edgesEvalImg(double(BW),r.reference,'thrs',.5,'maxDist',p.maxDist,'thin',p.thin);
        assert(sr==expectedR&&sp==nnz(bwmorph(BW,'thin',Inf)));P=cp/max(sp,1);R=cr/max(sr,1);
        row=struct('taskId',task.taskId,'imageId',r.id,'stage',task.stage,'method',name,'noiseStd',task.noiseStd, ...
            'seed',task.seed,'rngSeed',task.rngSeed,'precision',P,'recall',R,'f1',2*P*R/max(P+R,eps), ...
            'cntR',cr,'sumR',sr,'cntP',cp,'sumP',sp,'rgbRMSE',inputStats.rgbRMSE,'grayRMSE',inputStats.grayRMSE, ...
            'clippedFraction',inputStats.clippedFraction);
        if isempty(rows),rows=row;else,rows(end+1)=row;end %#ok<AGROW>
        masks{j}=BW;
    end
    if strcmp(task.stage,'noise')&&task.noiseStd==0,regressions.allCleanControls=true;end
    inputExample=[];
    if strcmp(task.stage,'noise')&&strcmp(r.id,p.noiseExampleId)&&(task.seed==p.noiseExampleSeed||task.seed==0),inputExample=input;end
    seconds=toc(timer);temporary=[output '.partial.mat'];
    save(temporary,'task','rows','masks','regressions','inputStats','inputExample','seconds');movefile(temporary,output,'f');
    fprintf('EXTRA_SAVED %d/300 %s rows=%d seconds=%.2f\n',index,task.taskId,numel(rows),seconds);
end
fprintf('RGB_EXTRAS_WORKER_COMPLETE\n');
end
function BW=fromMap(S,p)
BW=course_directional_hysteresis(S,zeros(size(S)),zeros(size(S)),p.high*p.ratio,p.high,0);
end
