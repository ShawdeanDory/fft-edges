function [BW, details] = course_detect_edges(I, choice, padding)
%COURSE_DETECT_EDGES All detector inputs are image and fixed parameters only.
if nargin < 3, padding = 32; end
validateattributes(I,{'double'},{'2d','real','finite','>=',0,'<=',1});
details = struct;
switch choice.method
    case 'fft_gaussian'
        response = fourier_edge_responses(I,choice.sigma,choice.cutoff,padding);
        [BW,nms] = thin_hysteresis_edges(response.gx,response.gy, ...
            [choice.low choice.high],choice.normalization);
        details = struct('response',response,'nms',nms);
    case 'canny'
        BW = edge(I,'Canny',[choice.low choice.high],choice.sigma);
    case 'sobel'
        [~,threshold] = edge(I,'Sobel');
        actual = min(max(threshold*choice.factor,0),1);
        BW = edge(I,'Sobel',actual);
        details.threshold = actual;
    case {'ideal_highpass','gaussian_highpass'}
        response = fourier_edge_responses(I,1.5,choice.cutoff,padding);
        if strcmp(choice.method,'ideal_highpass')
            strength = abs(response.idealHighpass);
        else
            strength = abs(response.gaussianHighpass);
        end
        peak = max(strength(:));
        if peak <= 1e-12
            BW = false(size(I)); details.threshold = 0;
        else
            strength = strength/peak;
            threshold = min(graythresh(strength)*choice.factor,1);
            BW = strength>threshold;
            details.threshold = threshold;
        end
    otherwise
        error('fourierCourse:Method','Unknown method: %s',choice.method);
end
BW = bwmorph(BW,'thin',Inf);
BW([1 end],:) = false; BW(:,[1 end]) = false;
end
