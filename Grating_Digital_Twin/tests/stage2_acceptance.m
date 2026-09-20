function report = stage2_acceptance()
%STAGE2_ACCEPTANCE Verify displacement, velocity and phase for all modes.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'model'));
p=parameter(); m=p.motion; P=p.grating.period; t=(0:1/m.sample_rate:m.duration).';
m.mode='constant_velocity'; r1=motion_model(t,m,P); x1=m.v*t; v1=m.v+zeros(size(t));
m.mode='acceleration'; r2=motion_model(t,m,P); x2=m.v0*t+0.5*m.a*t.^2; v2=m.v0+m.a*t;
m.mode='periodic_disturbance'; r3=motion_model(t,m,P); x3=m.v*t+m.A*sin(2*pi*m.f*t); v3=m.v+2*pi*m.f*m.A*cos(2*pi*m.f*t);
e_x=[max(abs(r1.x-x1)),max(abs(r2.x-x2)),max(abs(r3.x-x3))];
e_v=[max(abs(r1.velocity-v1)),max(abs(r2.velocity-v2)),max(abs(r3.velocity-v3))];
e_theta=[max(abs(r1.theta-2*pi*r1.x/P)),max(abs(r2.theta-2*pi*r2.x/P)),max(abs(r3.theta-2*pi*r3.x/P))];
tol=1e-14;
report=struct('modes',{{'constant_velocity','acceleration','periodic_disturbance'}}, ...
    'max_displacement_error_m',e_x,'max_velocity_error_mps',e_v, ...
    'max_phase_error_rad',e_theta,'tolerance',tol, ...
    'pass_displacement',all(e_x<tol),'pass_velocity',all(e_v<tol), ...
    'pass_phase',all(e_theta<tol));
report.pass=report.pass_displacement&&report.pass_velocity&&report.pass_phase;
assert(report.pass,'stage2_acceptance:Failed','Stage 2 motion-model acceptance failed.');
end
