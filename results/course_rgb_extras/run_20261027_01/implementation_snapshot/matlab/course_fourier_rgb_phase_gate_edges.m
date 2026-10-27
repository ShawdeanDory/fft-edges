function [BW,details]=course_fourier_rgb_phase_gate_edges(image,mode)
% Pure-phase RGB entry. 'selected' default; 'phase_only' previous gate.
% No anisotropic Gaussian bank or anisotropic support is computed.
if nargin<2,mode='selected';end
root=fileparts(fileparts(mfilename('fullpath')));addpath(fullfile(root,'external','kovesi'));
if ischar(image)||isstring(image),image=imread(image);end
if ismatrix(image),image=repmat(image,1,1,3);end
F=course_rgb_phase_features(image);C=course_rgb_phase_gate_features(F);high=.32;ratio=.3;
choice=struct('candidateId','phase_only_previous','seedEta',.125,'linkEta',.125,'seedSupport','Q','linkSupport','Q');
switch char(mode)
    case 'phase_only'
    case 'reference',choice.seedEta=0;choice.linkEta=0;choice.candidateId='reference';
    case 'selected'
        run=fullfile(root,'results','course_rgb_phase_recall','run_20261027_01');
        lock=jsondecode(fileread(fullfile(run,'parameters_locked.json')));choice=lock.selected;
    otherwise,error('Unknown pure-phase RGB mode: %s',mode);
end
[BW,details]=course_rgb_phase_gate_hysteresis(C,choice,high,ratio);
details.anisotropicSupport=false;details.grayMainChanged=false;details.ordinaryFFT=true;details.mode=char(mode);
end
