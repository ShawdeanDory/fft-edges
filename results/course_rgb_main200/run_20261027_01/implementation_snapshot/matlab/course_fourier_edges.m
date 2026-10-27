function [BW,details]=course_fourier_edges(image,method)
% Unified project entry. RGB Fourier + phase gating is the chosen main method.
% Usage: course_fourier_edges(image) or course_fourier_edges(image,'gray').
root=fileparts(fileparts(mfilename('fullpath')));
config=jsondecode(fileread(fullfile(root,'matlab','course_main_method.json')));
if nargin<2||isempty(method),method=config.mainMethod;end
switch char(method)
    case {'rgb','rgb_phase_gate'}
        [BW,details]=course_fourier_rgb_phase_gate_edges(image,'selected');
        c=details.choice;
        assert(strcmp(c.candidateId,config.candidateId)&&c.seedEta==config.seedEta&&c.linkEta==config.linkEta);
        assert(details.high==config.high&&details.ratio==config.ratio);
        details.method='rgb_phase_gate';details.role='main';
        details.description='RGB ordinary 2D FFT derivatives + phase support; preserve strong seeds and gate weak links.';
    case {'gray','gray_phase'}
        [BW,details]=course_fourier_phase_edges(image);
        details.method='gray_phase';details.role='comparison';
    otherwise,error('Unknown course method: %s',method);
end
details.projectMainMethod=config.mainMethod;details.roleDecision='User-selected project main method; historical statistical judgments unchanged.';
end
