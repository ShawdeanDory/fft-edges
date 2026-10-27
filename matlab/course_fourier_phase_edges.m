function [BW,details]=course_fourier_phase_edges(image,runDir)
%COURSE_FOURIER_PHASE_EDGES Explicit optional course candidate; no model loading.
root=fileparts(fileparts(mfilename('fullpath')));
if nargin<2||isempty(runDir)
    runs=dir(fullfile(root,'results','course_phase','run_*'));runs=runs([runs.isdir]);
    [~,order]=sort(string({runs.name}),'descend');runDir='';
    for i=order
        path=fullfile(runs(i).folder,runs(i).name);
        if isfile(fullfile(path,'completed.json')),runDir=path;break;end
    end
    assert(~isempty(runDir),'Run the phase experiment first, or provide its locked run directory.');
end
lock=load(fullfile(runDir,'parameters_locked.mat'),'choices');
choice=lock.choices(strcmp({lock.choices.branch},'fft_phase'));assert(numel(choice)==1);
addpath(fullfile(root,'external','kovesi'));
if ischar(image)||isstring(image),image=imread(image);end
if ndims(image)==3,image=rgb2gray(image);end
I=im2double(image);features=course_phase_features(I,32);
[BW,strength]=course_phase_edges(features,choice);
details=struct('choice',choice,'strength',strength,'phaseMoment',features.phase([features.phase.k]==choice.k).moment, ...
    'description','Validation-locked FFT + phase candidate; original demo remains separate.');
end
