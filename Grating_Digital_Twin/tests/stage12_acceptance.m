function report = stage12_acceptance()
%STAGE12_ACCEPTANCE Verify the torque-angle-displacement-phase chain.
root=fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root,'mechanics'),fullfile(root,'interface'),fullfile(root,'config'), ...
    fullfile(root,'model'),fullfile(root,'signal'),fullfile(root,'algorithm'), ...
    fullfile(root,'communication'));
p=struct('torsion_length',0.012,'shear_modulus',79e9,'shaft_diameter',0.008, ...
    'grating_radius',0.007,'grating_period',20e-6,'phase_zero',0, ...
    'parameter_source','simulation/default','serial_mode','none');
p0=p; p0.torque=0;
p1=p; p1.torque=0.25;
p2=p; p2.torque=0.50;
s0=torque_to_grating(p0); s1=torque_to_grating(p1); s2=torque_to_grating(p2);
J=pi*p.shaft_diameter^4/32;
theta_expected=p1.torque*p.torsion_length/(p.shear_modulus*J);
dx_expected=p.grating_radius*theta_expected;
phase_expected=2*pi*dx_expected/p.grating_period;
tol=1e-12;
report=struct();
report.pass_zero=abs(s0.torsion_angle)<tol&&abs(s0.relative_displacement)<tol&&abs(s0.optical_phase)<tol;
report.pass_double=abs(s2.torsion_angle-2*s1.torsion_angle)<tol;
report.pass_theta=abs(s1.torsion_angle-theta_expected)<tol;
report.pass_dx=abs(s1.relative_displacement-dx_expected)<tol;
report.pass_phase=abs(s1.optical_phase-phase_expected)<tol;
chain=python_control('run_torque',p1);
report.pass_existing_chain=strcmp(chain.status,'ok')&&chain.stage==12&& ...
    abs(chain.optical_phase-phase_expected)<tol&&size(chain.four_phase_signal,2)==4;
report.parameter_source=s1.parameter_source;
report.polar_moment=J;
report.torsion_angle=s1.torsion_angle;
report.relative_displacement=s1.relative_displacement;
report.optical_phase=s1.optical_phase;
report.pass=report.pass_zero&&report.pass_double&&report.pass_theta&& ...
    report.pass_dx&&report.pass_phase&&report.pass_existing_chain&& ...
    strcmp(report.parameter_source,'simulation/default');
assert(report.pass,'stage12_acceptance:Failed','Stage 12 physical-chain acceptance failed.');
end
