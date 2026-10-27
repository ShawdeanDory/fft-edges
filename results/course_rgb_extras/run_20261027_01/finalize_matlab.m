root=fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
addpath(fullfile(root,'matlab'));verify_course_rgb_extras;
v=struct('matlabVersion',version,'matlabRelease',version('-release'),'imageProcessingToolbox',ver('images'), ...
    'ablationImages',200,'noiseImages',10,'noiseSeeds',3,'training',false,'gpuRequired',false);
f=fopen(fullfile(root,'results','course_rgb_extras','run_20261027_01','runtime.json'),'w','n','UTF-8');
fprintf(f,'%s\n',jsonencode(v,'PrettyPrint',true));fclose(f);
