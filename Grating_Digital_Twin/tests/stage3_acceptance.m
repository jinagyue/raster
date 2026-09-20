function report = stage3_acceptance()
%STAGE3_ACCEPTANCE Check phase spacing, period consistency and formula error.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'));
p=parameter(); theta=linspace(0,16*pi,4001).'; optical=optical_model(theta,p.optical); signal=signal_generator(optical,p.signal);
expected=theta+p.signal.phase_offsets; phase_error=max(abs(signal.phase-expected),[],1);
formula_error=zeros(1,4); for k=1:4, formula_error(k)=max(abs(signal.channels(:,k)-(p.optical.I0+p.optical.Im*cos(expected(:,k))))); end
% A phase shift of 2*pi must reproduce every channel exactly.
optical2=optical_model(theta+2*pi,p.optical); signal2=signal_generator(optical2,p.signal); period_error=max(abs(signal2.channels(:)-signal.channels(:)));
phase_spacing=diff(p.signal.phase_offsets); phase_spacing=mod(phase_spacing+pi,2*pi)-pi; phase_spacing_error=max(abs(phase_spacing-pi/2));
tol=1e-12;
report=struct('phase_difference_error_rad',phase_spacing_error,'period_repeat_error',period_error, ...
    'formula_error_max',max(formula_error),'channel_formula_error',formula_error, ...
    'tolerance',tol,'pass_phase',phase_spacing_error<tol,'pass_period',period_error<tol, ...
    'pass_formula',max(formula_error)<tol);
report.pass=report.pass_phase&&report.pass_period&&report.pass_formula;
assert(report.pass,'stage3_acceptance:Failed','Stage 3 optical/signal acceptance failed.');
end
