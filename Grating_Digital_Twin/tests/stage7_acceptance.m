function report = stage7_acceptance()
%STAGE7_ACCEPTANCE Verify ADC mapping, quantization and sampling behavior.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'signal'));
p=parameter(); a=p.adc; t=(0:1e-5:10e-3).'; v=[zeros(1,1);0.5;1.65;3.3]; test_t=(0:3).';
cfg=a; cfg.sample_rate=1; endpoints=adc_model(v,test_t,cfg); endpoint_codes=double(endpoints.code(:,1)); map_error=max(abs(endpoint_codes-[0;620;2048;4095]));
tt=(0:1/100e3:10e-3).'; analog=1.65+1.2*sin(2*pi*1000*tt); cfg.sample_rate=100e3; q=adc_model(analog,tt,cfg);
levels=2^a.bits-1; range_ok=all(double(q.code(:))>=0)&&all(double(q.code(:))<=levels); bound_ok=max(abs(q.quantization_error))<=q.lsb/2+1e-12;
cfg.sample_rate=2e3; low=adc_model(analog,tt,cfg); cfg.sample_rate=20e3; high=adc_model(analog,tt,cfg); sampling_ok=numel(low.t)<numel(high.t)&&low.sample_rate==2e3&&high.sample_rate==20e3;
report=struct('endpoint_mapping_error_codes',map_error,'max_quantization_error_v',max(abs(q.quantization_error)),'half_lsb_v',q.lsb/2,'low_rate_samples',numel(low.t),'high_rate_samples',numel(high.t),'pass_mapping',map_error==0,'pass_range',range_ok,'pass_quantization_bound',bound_ok,'pass_sampling_rate',sampling_ok);
report.pass=report.pass_mapping&&report.pass_range&&report.pass_quantization_bound&&report.pass_sampling_rate; assert(report.pass,'stage7_acceptance:Failed','Stage 7 ADC acceptance failed.');
end
