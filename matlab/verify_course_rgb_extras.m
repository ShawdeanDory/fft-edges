function verify_course_rgb_extras()
root=fileparts(fileparts(mfilename('fullpath')));run=fullfile(root,'results','course_rgb_extras','run_20261027_01');
p=jsondecode(fileread(fullfile(run,'parameters_locked.json')));t=jsondecode(fileread(fullfile(run,'tasks.json')));rows=struct([]);
ab=0;no=0;clean=0;
for task=reshape(t.tasks,1,[])
    z=load(fullfile(run,'samples',[task.taskId '.mat']));assert(strcmp(z.task.taskId,task.taskId));
    if strcmp(task.stage,'ablation')
        assert(numel(z.rows)==5&&z.regressions.main&&z.regressions.gray);ab=ab+numel(z.rows);
    else
        assert(numel(z.rows)==6);no=no+numel(z.rows);
        if task.noiseStd==0,assert(z.regressions.allCleanControls);clean=clean+1;end
    end
    assert(all([z.rows.sumR]==z.rows(1).sumR));
    for j=1:numel(z.rows),assert(z.rows(j).sumP==nnz(bwmorph(z.masks{j},'thin',Inf)));end
    if isempty(rows),rows=z.rows;else,rows=[rows z.rows];end %#ok<AGROW>
end
assert(ab==1000&&no==600&&clean==10&&numel(rows)==1600);
summary=struct([]);
for stage={'ablation','noise'}
    if strcmp(stage{1},'ablation'),methods=p.ablationMethods;levels=0;else,methods=p.noiseMethods;levels=[0 .02 .05 .10];end
    for sigma=levels
        for j=1:numel(methods)
            g=rows(strcmp({rows.stage},stage{1})&strcmp({rows.method},methods{j})&abs([rows.noiseStd]-sigma)<1e-12);
            P=sum([g.cntP])/sum([g.sumP]);R=sum([g.cntR])/sum([g.sumR]);
            row=struct('stage',stage{1},'method',methods{j},'noiseStd',sigma,'rows',numel(g),'precision',P,'recall',R, ...
                'f1',2*P*R/(P+R),'macroF1',mean([g.f1]));
            if isempty(summary),summary=row;else,summary(end+1)=row;end %#ok<AGROW>
        end
    end
end
writetable(struct2table(summary),fullfile(run,'matlab_summary.csv'));
v=struct('status','PASS','tasks',300,'ablationRows',ab,'noiseRows',no,'allRows',1600, ...
    'cleanSixMethodMaskRegressions',60,'mainGrayAblationMaskRegressions',400,'frozenParameters',true);
f=fopen(fullfile(run,'verification.json'),'w','n','UTF-8');assert(f>=0);cleanup=onCleanup(@()fclose(f));fprintf(f,'%s\n',jsonencode(v,'PrettyPrint',true));disp(struct2table(summary));
end
