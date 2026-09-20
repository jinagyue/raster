function report = stage4_acceptance()
%STAGE4_ACCEPTANCE Verify deterministic injection and stochastic components.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'));
p=parameter(); t=(0:1/p.motion.sample_rate:20e-3).'; motion=motion_model(t,p.motion,p.grating.period); optical=optical_model(motion.theta,p.optical); optical.t=t; ideal=signal_generator(optical,p.signal); ideal.t=t;
e=p.errors; e.amplitude=[0.7 0.8 0.9 1.0]; e.phase_error=[0.03 -0.02 0.01 -0.04]; e.offset=[0.1 -0.05 0.02 0.08]; e.noise_rms=[0 0 0 0]; e.hf_amplitude=0; e.hf_frequency=0;
d=error_model(ideal,t,e); expected=zeros(size(d.channels));
for k=1:4, expected(:,k)=e.amplitude(k)*cos(ideal.theta+ideal.phase_offsets(k)+e.phase_error(k))+ideal.offset(k)+e.offset(k); end
formula_error=max(abs(d.channels(:)-expected(:))); parameter_error=max(abs(d.amplitude-e.amplitude))+max(abs(d.phase_error-e.phase_error))+max(abs(d.offset-e.offset));
e.hf_amplitude=0.2; e.hf_frequency=250; e.noise_rms=[0 0 0 0]; d_hf=error_model(ideal,t,e); hf_error=max(abs(d_hf.high_frequency_interference(:,1)-0.2*sin(2*pi*250*t)));
e.noise_rms=[0.02 0.02 0.02 0.02]; d_noise=error_model(ideal,t,e); measured_std=std(d_noise.noise,0,1); noise_error=max(abs(measured_std-0.02));
tol=1e-12; report=struct('formula_error_max',formula_error,'parameter_error_max',parameter_error,'hf_formula_error_max',hf_error,'noise_std_error_max',noise_error,'tolerance',tol,'pass_formula',formula_error<tol,'pass_parameters',parameter_error<tol,'pass_hf',hf_error<tol,'pass_noise',noise_error<0.01);
report.pass=report.pass_formula&&report.pass_parameters&&report.pass_hf&&report.pass_noise; assert(report.pass,'stage4_acceptance:Failed','Stage 4 error-model acceptance failed.');
end
