function demoDir=run_natural_demo(naturalImagePath,courseRun)
% Current course demo: RGB main, gray comparison, four traditional controls.
% Offline fixed parameters. Legacy five-method demo: run_natural_demo_legacy.
root=fileparts(fileparts(mfilename('fullpath')));cfg=course_edge_config();
if nargin<2||isempty(courseRun)
    courseRun=fullfile(root,'results','course_natural','run_20261026_231522_733');
end
locked=load(fullfile(courseRun,'parameters_locked.mat'),'choices');choices=locked.choices;
referenceAvailable=nargin<1||isempty(naturalImagePath);referencePath='';imageId='custom';
if referenceAvailable
    m=jsondecode(fileread(fullfile(root,'results','course_rgb_phase_recall','run_20261027_01','manifest.json')));
    record=m.records(1);naturalImagePath=record.image;referencePath=record.reference;imageId=record.id;
end
source=imread(naturalImagePath);
if ndims(source)==3,I=im2double(rgb2gray(source));else,I=im2double(source);end
demoDir=fullfile(root,'results','natural_demo',['rgb_main_' char(datetime('now','Format','yyyyMMdd_HHmmss_SSS'))]);mkdir(demoDir);
imwrite(source,fullfile(demoDir,'input_source.png'));
[main,mainDetails]=course_fourier_edges(source);[gray,grayDetails]=course_fourier_edges(source,'gray');
allEdges=struct('rgb_main',main,'gray_phase',gray);
methodNames={'rgb_main','gray_phase'};displayNames={'RGB FFT + phase gate (main)','Gray FFT + phase (comparison)'};
for k=1:numel(choices)
    c=choices(k);if strcmp(c.method,'fft_gaussian'),continue;end
    allEdges.(c.method)=course_detect_edges(I,c,cfg.paddingPixels);
    methodNames{end+1}=c.method;displayNames{end+1}=strrep(c.method,'_',' '); %#ok<AGROW>
end
assert(numel(methodNames)==6);GT=[];rows=struct([]);
if referenceAvailable
    addpath(fullfile(root,'external','structured_edges'));
    for f={'matlab','images','channels'},addpath(fullfile(root,'external','pdollar_toolbox',f{1}));end
    z=load(referencePath,'groundTruth');GT=false(size(I));
    for k=1:numel(z.groundTruth),GT=GT|logical(z.groundTruth{k}.Boundaries);end
    imwrite(GT,fullfile(demoDir,'gt_union_display.png'));
end
for k=1:numel(methodNames)
    name=methodNames{k};BW=allEdges.(name);imwrite(BW,fullfile(demoDir,[name '_edges.png']));
    if referenceAvailable
        [~,cr,sr,cp,sp]=edgesEvalImg(double(BW),referencePath,'thrs',.5,'maxDist',.0075,'thin',1);
        P=cp/max(sp,1);R=cr/max(sr,1);
        r=struct('method',name,'precision',P,'recall',R,'f1',2*P*R/max(P+R,eps), ...
            'cntR',cr,'sumR',sr,'cntP',cp,'sumP',sp);
        if isempty(rows),rows=r;else,rows(end+1)=r;end %#ok<AGROW>
    end
end
fig=figure('Visible','off','Color','w','Position',[30 30 1450 800]);
layout=tiledlayout(fig,2,4,'TileSpacing','compact','Padding','compact');
ax=nexttile(layout);imshow(source,'Parent',ax);title(ax,'Original RGB input');
ax=nexttile(layout);
if referenceAvailable,imshow(GT,'Parent',ax);title(ax,'GT union (display only)');else,imshow(I,'Parent',ax);title(ax,'Grayscale input (comparison)');end
for k=1:6
    ax=nexttile(layout);imshow(allEdges.(methodNames{k}),'Parent',ax);title(ax,displayNames{k});
    if referenceAvailable
        r=rows(k);xlabel(ax,sprintf('P %.1f%% | R %.1f%% | F1 %.1f%%',100*r.precision,100*r.recall,100*r.f1));
    end
end
title(layout,'RGB Fourier edge detection: main method and fixed comparisons');
exportgraphics(fig,fullfile(demoDir,'six_methods.png'),'Resolution',200);
exportgraphics(fig,fullfile(demoDir,'six_methods.pdf'),'ContentType','vector');close(fig);
% Compatibility filename for previous quick-start commands. The current
% documentation uses six_methods.png to describe the actual six methods.
copyfile(fullfile(demoDir,'six_methods.png'),fullfile(demoDir,'five_methods.png'));
RGB=im2double(source);if ismatrix(RGB),RGB=repmat(RGB,1,1,3);end
spectra=zeros(size(I,1)+64,size(I,2)+64,3);channelNames={'R','G','B'};
for channel=1:3
    Ip=padarray(RGB(:,:,channel),[32 32],'symmetric','both');spectra(:,:,channel)=log1p(abs(fftshift(fft2(Ip))));
    imwrite(mat2gray(spectra(:,:,channel)),fullfile(demoDir,['spectrum_' channelNames{channel} '.png']));
end
fig=figure('Visible','off','Color','w','Position',[30 30 1200 850]);
layout=tiledlayout(fig,2,3,'TileSpacing','loose','Padding','loose');
for channel=1:3
    ax=nexttile(layout);imshow(spectra(:,:,channel),[],'Parent',ax);title(ax,[channelNames{channel} ': log FFT magnitude'],'FontSize',11);
end
ax=nexttile(layout);imshow(mainDetails.seedResponse,[],'Parent',ax);title(ax,'Strong-seed response','FontSize',11);
ax=nexttile(layout);imshow(mainDetails.linkResponse,[],'Parent',ax);title(ax,'Phase-gated weak links','FontSize',11);
ax=nexttile(layout);imshow(main,'Parent',ax);title(ax,'RGB main edges','FontSize',11);
exportgraphics(fig,fullfile(demoDir,'frequency_spectra.png'),'Resolution',200);
exportgraphics(fig,fullfile(demoDir,'frequency_spectra.pdf'),'ContentType','vector');close(fig);
if referenceAvailable,writetable(struct2table(rows),fullfile(demoDir,'metrics.csv'));end
mainConfig=jsondecode(fileread(fullfile(root,'matlab','course_main_method.json')));
save(fullfile(demoDir,'demo_arrays.mat'),'source','I','spectra','allEdges','mainDetails','grayDetails', ...
    'choices','naturalImagePath','referencePath','imageId','mainConfig');
status=struct('status','completed','mainMethod','rgb_phase_gate','candidateId',mainConfig.candidateId, ...
    'grayRole','comparison','methods',6,'referenceAvailable',referenceAvailable,'imageId',imageId, ...
    'evaluation','Official matcher maxDist=.0075, thin=1; single-image demonstration only.', ...
    'controlParameterNote','Four traditional controls retain historical course validation settings; no new selection.', ...
    'parameterSearch',false,'training',false,'gpuRequired',false,'anisotropicSupport',false);
stream=fopen(fullfile(demoDir,'completed.json'),'w','n','UTF-8');assert(stream>=0);
fprintf(stream,'%s\n',jsonencode(status,'PrettyPrint',true));fclose(stream);
fprintf('NATURAL_RGB_MAIN_DEMO_COMPLETED=%s\n',demoDir);
end
