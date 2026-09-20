function state = torque_model(torque,mechanical)
%TORQUE_MODEL Circular-shaft torque-to-torsion physical model.
%   theta = T*L/(G*J), J = pi*d^4/32.
%   All inputs use SI units. Default values are simulation assumptions and
%   must not be interpreted as patent dimensions or calibrated properties.
validateattributes(torque,{'numeric'},{'real','finite','vector'},mfilename,'torque');
required={'torsion_length','shear_modulus','shaft_diameter','grating_radius','grating_period'};
for k=1:numel(required)
    name=required{k};
    if ~isfield(mechanical,name)
        error('torque_model:MissingParameter','Missing mechanical parameter: %s.',name);
    end
    validateattributes(mechanical.(name),{'numeric'},{'scalar','real','finite','positive'},mfilename,name);
end
if ~isfield(mechanical,'phase_zero')||isempty(mechanical.phase_zero), mechanical.phase_zero=0; end
validateattributes(mechanical.phase_zero,{'numeric'},{'scalar','real','finite'},mfilename,'phase_zero');
if ~isfield(mechanical,'parameter_source')||isempty(mechanical.parameter_source)
    mechanical.parameter_source='simulation/default';
end
J=pi*mechanical.shaft_diameter^4/32;
theta_torsion=double(torque)*mechanical.torsion_length/(mechanical.shear_modulus*J);
relative_displacement=mechanical.grating_radius*theta_torsion;
optical_phase=2*pi*relative_displacement/mechanical.grating_period+mechanical.phase_zero;
state=struct('torque',double(torque),'polar_moment',J, ...
    'torsion_angle',theta_torsion,'relative_displacement',relative_displacement, ...
    'optical_phase',optical_phase,'parameter',mechanical, ...
    'parameter_source',char(mechanical.parameter_source), ...
    'equation','theta=T*L/(G*J), J=pi*d^4/32, dx=r*theta, phase=2*pi*dx/P');
end
