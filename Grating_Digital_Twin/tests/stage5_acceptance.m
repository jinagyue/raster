function report = stage5_acceptance()
%STAGE5_ACCEPTANCE Compare direct atan2 with calibrated phase recovery.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'),fullfile(root,'algorithm'));
p=parameter(); p.motion.v=1e-2; p.motion.duration=20e-3; t=(0:1/p.motion.sample_rate:p.motion.duration).'; motion=motion_model(t,p.motion,p.grating.period); optical=optical_model(motion.theta,p.optical); optical.t=t; ideal=signal_generator(optical,p.signal); ideal.t=t;
e=p.errors; e.amplitude=p.optical.Im*[0.65 1.35 0.80 1.20]; e.phase_error=[0.15 -0.12 0.08 -0.10]; e.offset=[0.15 -0.10 0.08 -0.05]; e.noise_rms=[0.01 0.01 0.01 0.01]; e.hf_amplitude=0; e.hf_frequency=0; d=error_model(ideal,t,e);
z=phase_estimation(d,p.grating.period,t,motion.x); improvement=z.metrics.traditional.rmse-z.metrics.improved.rmse;
report=struct('traditional_rmse_m',z.metrics.traditional.rmse,'improved_rmse_m',z.metrics.improved.rmse,'traditional_max_error_m',z.metrics.traditional.max_error,'improved_max_error_m',z.metrics.improved.max_error,'improved_resolution_1sigma_m',z.metrics.improved.resolution_1sigma,'rmse_improvement_m',improvement,'pass_outputs',all([numel(z.theta_est)==numel(t),numel(z.x_est)==numel(t)]),'pass_improved',z.metrics.improved.rmse<z.metrics.traditional.rmse,'pass_finite',all(isfinite(z.x_est)));
report.pass=report.pass_outputs&&report.pass_improved&&report.pass_finite; assert(report.pass,'stage5_acceptance:Failed','Stage 5 phase-estimation acceptance failed.');
end
