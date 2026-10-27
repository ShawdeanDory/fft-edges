function verify_course_rgb_main200()
root=fileparts(fileparts(mfilename('fullpath')));run=fullfile(root,'results','course_rgb_main200','run_20261027_01');
p=jsondecode(fileread(fullfile(run,'parameters_locked.json')));m=jsondecode(fileread(fullfile(run,'manifest.json')));rows=struct([]);
for r=reshape(m.records,1,[])
    z=load(fullfile(run,'samples',[r.id '.mat']));assert(numel(z.rows)==6&&numel(z.masks)==6&&z.grayAgreement);
    assert(isequaln(jsondecode(jsonencode(z.selected)),p.selected));
    assert(all(strcmp({z.rows.imageId},r.id))&&all([z.rows.sumR]==z.rows(1).sumR));
    for j=1:6
        assert(strcmp(z.rows(j).method,p.methods{j})&&z.rows(j).sumP==nnz(bwmorph(z.masks{j},'thin',Inf)));
    end
    if isempty(rows),rows=z.rows;else,rows=[rows z.rows];end %#ok<AGROW>
end
assert(numel(rows)==1200&&numel(unique({rows.imageId}))==200);summary=struct([]);
for name=reshape(p.methods,1,[])
    g=rows(strcmp({rows.method},name{1}));assert(numel(g)==200);P=sum([g.cntP])/sum([g.sumP]);R=sum([g.cntR])/sum([g.sumR]);
    row=struct('method',name{1},'images',200,'precision',P,'recall',R,'f1',2*P*R/(P+R), ...
        'macroPrecision',mean([g.precision]),'macroRecall',mean([g.recall]),'macroF1',mean([g.f1]));
    if isempty(summary),summary=row;else,summary(end+1)=row;end %#ok<AGROW>
end
writetable(struct2table(summary),fullfile(run,'matlab_summary.csv'));
r=m.records(1);[BW,~]=course_fourier_edges(r.image);z=load(fullfile(run,'samples',[r.id '.mat']));assert(isequal(BW,z.masks{1}));
v=struct('status','PASS','images',200,'rows',1200,'grayMaskRegression',200,'currentMainEntryAgreement',true,'methodsPerImage',6,'scoredThinningCountsMatch',true);
f=fopen(fullfile(run,'verification.json'),'w','n','UTF-8');assert(f>=0);cleanup=onCleanup(@()fclose(f));fprintf(f,'%s\n',jsonencode(v,'PrettyPrint',true));disp(struct2table(summary));fprintf('RGB200_VERIFICATION_PASS\n');
end
