function report = stage1_acceptance()
%STAGE1_ACCEPTANCE Physics-oriented acceptance checks for stage 1.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'model'));
p=parameter(); g=p.grating; main_model=grating_3D_model(g,g.main_shift); ref_model=grating_3D_model(g,g.reference_shift);
z_expected=0.5*g.height*(1+cos(2*pi*(main_model.X-g.main_shift)/g.period));
period_error=max(abs(z_expected(:)-main_model.Z(:)));
relative_shift=ref_model.x_shift-main_model.x_shift;
report=struct('period_m',g.period,'number',g.number,'length_m',g.length,'period_formula_max_error_m',period_error,'relative_shift_m',relative_shift,'pass_formula',period_error<1e-15,'pass_shift',abs(relative_shift-(g.reference_shift-g.main_shift))<1e-15);
report.pass=report.pass_formula && report.pass_shift;
assert(report.pass,'stage1_acceptance:Failed','Stage 1 geometry acceptance failed.');
end
