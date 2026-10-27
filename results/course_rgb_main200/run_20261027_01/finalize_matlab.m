root=fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
addpath(fullfile(root,'matlab'));verify_course_rgb_main200;
runtime=struct('matlabVersion',version,'matlabRelease',version('-release'),'platform',computer, ...
    'imageProcessingToolbox',ver('images'),'evaluatedMethods',6,'images',200,'training',false,'gpuRequired',false);
f=fopen(fullfile(root,'results','course_rgb_main200','run_20261027_01','runtime.json'),'w','n','UTF-8');
fprintf(f,'%s\n',jsonencode(runtime,'PrettyPrint',true));fclose(f);
