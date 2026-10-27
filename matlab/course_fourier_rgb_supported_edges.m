function [BW,details]=course_fourier_rgb_supported_edges(image)
% Current RGB default: preserve strong seeds, phase-gate weak links only.
% Historical entry is preserved with the phase-recall experiment artifacts.
[BW,details]=course_fourier_rgb_phase_gate_edges(image);
details.response=details.seedResponse;details.fullPaperReproduction=false;
end
