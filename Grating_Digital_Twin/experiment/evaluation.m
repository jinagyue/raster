function report = evaluation(p)
%EVALUATION Run reproducible stage-6 robustness experiments.
% Experiments: displacement recovery, SNR sweep, phase-error sweep and
% amplitude-mismatch sweep. Both direct atan2 and calibrated estimates are
% retained for paper tables.
if nargin<1||isempty(p), p=parameter(); end
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'),fullfile(root,'algorithm'));
p.motion.duration=max(p.motion.duration,20e-3); t=(0:1/p.motion.sample_rate:p.motion.duration).'; motion=motion_model(t,p.motion,p.grating.period); optical=optical_model(motion.theta,p.optical); optical.t=t;
s=p.signal; s.amplitudes=[1 1 1 1]; s.phi_error=[0 0 0 0]; s.offset=optical.I0*[1 1 1 1]; s.noise_rms=[0 0 0 0]; ideal=signal_generator(optical,s); ideal.t=t;
base=p.errors; base.amplitude=p.optical.Im*[0.90 1.10 0.95 1.05]; base.phase_error=[0.02 -0.02 0.01 -0.015]; base.offset=[0.03 -0.02 0.02 -0.01]; base.hf_amplitude=0; base.hf_frequency=0;
% Experiment 1: nominal recovery with representative non-idealities.
e1=base; e1.noise_rms=[0.005 0.005 0.005 0.005]; d=error_model(ideal,t,e1); r1=phase_estimation(d,p.grating.period,t,motion.x); report.recovery=pack_result('recovery',r1);
% Experiment 2: SNR sweep (noise sigma derived from signal RMS).
snr_db=[30 20 10]; report.snr=struct([]); signal_rms=p.optical.Im/sqrt(2);
for k=1:numel(snr_db)
    e=base; e.noise_rms=(signal_rms/10^(snr_db(k)/20))*ones(1,4); d=error_model(ideal,t,e); z=phase_estimation(d,p.grating.period,t,motion.x); item=pack_result(sprintf('SNR_%ddB',snr_db(k)),z); item.snr_db=snr_db(k); if isempty(report.snr), report.snr=item; else, report.snr(k)=item; end
end
% Experiment 3: common phase-error magnitude sweep.
phase_deg=[0 1 3 5 10]; report.phase=struct([]);
for k=1:numel(phase_deg)
    e=base; q=phase_deg(k)*pi/180; e.phase_error=[q -q q -q]; e.noise_rms=zeros(1,4); d=error_model(ideal,t,e); z=phase_estimation(d,p.grating.period,t,motion.x); item=pack_result(sprintf('phase_%gdeg',phase_deg(k)),z); item.phase_error_deg=phase_deg(k); if isempty(report.phase), report.phase=item; else, report.phase(k)=item; end
end
% Experiment 4: amplitude mismatch sweep.
amp_pct=[0 5 10 20 30]; report.amplitude=struct([]);
for k=1:numel(amp_pct)
    e=base; q=amp_pct(k)/100; e.amplitude=p.optical.Im*[1+q 1-q 1+q 1-q]; e.phase_error=zeros(1,4); e.noise_rms=zeros(1,4); d=error_model(ideal,t,e); z=phase_estimation(d,p.grating.period,t,motion.x); item=pack_result(sprintf('amplitude_%gpercent',amp_pct(k)),z); item.amplitude_mismatch_pct=amp_pct(k); if isempty(report.amplitude), report.amplitude=item; else, report.amplitude(k)=item; end
end
report.t=t; report.motion=motion; report.parameter=p; report.summary=summary_table(report);
end

function q=pack_result(name,z)
q=struct('name',name,'traditional',z.metrics.traditional,'improved',z.metrics.improved,'estimate',z);
end
function T=summary_table(r)
groups={r.recovery,r.snr,r.phase,r.amplitude}; n=0; for g=1:numel(groups), n=n+numel(groups{g}); end
T=table('Size',[n,7],'VariableTypes',{'string','double','double','double','double','double','double'},'VariableNames',{'case_name','traditional_rmse','improved_rmse','traditional_max','improved_max','improved_resolution','improvement_ratio'}); row=0;
for g=1:numel(groups)
    rows=groups{g};
    for i=1:numel(rows)
        row=row+1; T.case_name(row)=string(rows(i).name); T.traditional_rmse(row)=rows(i).traditional.rmse; T.improved_rmse(row)=rows(i).improved.rmse; T.traditional_max(row)=rows(i).traditional.max_error; T.improved_max(row)=rows(i).improved.max_error; T.improved_resolution(row)=rows(i).improved.resolution_1sigma; T.improvement_ratio(row)=rows(i).improved.rmse/max(rows(i).traditional.rmse,eps);
    end
end
end
