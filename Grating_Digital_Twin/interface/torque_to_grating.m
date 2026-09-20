function state = torque_to_grating(input_parameter)
%TORQUE_TO_GRATING Validated Stage-12 mechanical interface.
%   STATE = TORQUE_TO_GRATING(S) maps scalar Torque to torsion angle,
%   grating tangential displacement and optical phase. Missing mechanical
%   values use explicit simulation/default assumptions.
if nargin<1||isempty(input_parameter), input_parameter=struct(); end
if ~isstruct(input_parameter)
    error('torque_to_grating:Type','input_parameter must be a structure.');
end
torque=get_scalar(input_parameter,'torque',0,false);
mechanical=struct( ...
    'torsion_length',get_scalar(input_parameter,'torsion_length',0.012,true), ...
    'shear_modulus',get_scalar(input_parameter,'shear_modulus',79e9,true), ...
    'shaft_diameter',get_scalar(input_parameter,'shaft_diameter',0.008,true), ...
    'grating_radius',get_scalar(input_parameter,'grating_radius',0.007,true), ...
    'grating_period',get_scalar(input_parameter,'grating_period',20e-6,true), ...
    'phase_zero',get_scalar(input_parameter,'phase_zero',0,false), ...
    'parameter_source','simulation/default');
if isfield(input_parameter,'parameter_source')&&~isempty(input_parameter.parameter_source)
    mechanical.parameter_source=char(input_parameter.parameter_source);
end
if ~strcmp(mechanical.parameter_source,'simulation/default')
    error('torque_to_grating:UnverifiedSource', ...
        'Stage-12 mechanical parameters are unverified and must remain marked simulation/default.');
end
state=torque_model(torque,mechanical);
end

function value=get_scalar(s,name,default_value,must_be_positive)
if ~isfield(s,name)||isempty(s.(name)), value=default_value; else, value=s.(name); end
if ~(isnumeric(value)&&isscalar(value)&&isfinite(value)&&isreal(value))
    error('torque_to_grating:Parameter','%s must be a finite real scalar.',name);
end
value=double(value);
if must_be_positive&&value<=0
    error('torque_to_grating:Range','%s must be positive.',name);
end
end
