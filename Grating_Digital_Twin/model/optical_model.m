function optical = optical_model(theta, optical_parameter)
%OPTICAL_MODEL Ideal photoelectric conversion model.
%   I(t)=I0+Im*cos(theta(t)); theta is supplied by stage 2.
validateattributes(theta,{'numeric'},{'vector','real','finite'});
assert(optical_parameter.I0>=abs(optical_parameter.Im),'optical_model:Range','I0 must be >= |Im| for non-negative intensity.');
theta=theta(:); I=optical_parameter.I0+optical_parameter.Im*cos(theta);
optical=struct('theta',theta,'phase',theta,'intensity',I,'I0',optical_parameter.I0, ...
    'Im',optical_parameter.Im,'amplitude',abs(optical_parameter.Im),'period_phase',2*pi);
end
