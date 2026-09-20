function report = stage14_comparison(p,output_folder)
%STAGE14_COMPARISON Formal comparison without redesigning core algorithms.
% Methods: Patent 1/4, 1/16, 1/32; traditional atan2; existing improved.
% Every predefined case is retained. Failed/non-finite cases remain in the
% output table with status="failed" and an error message.
if nargin<1||isempty(p), p=parameter(); end
root=fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'), ...
    fullfile(root,'algorithm'),fullfile(root,'mechanics'),fullfile(root,'interface'));
if nargin<2||isempty(output_folder), output_folder=fullfile(root,'data','stage14'); end
if ~isfolder(output_folder), mkdir(output_folder); end

cfg=struct('sample_count',2001,'duration',1,'reference_torque',8, ...
    'torsion_length',0.012,'shear_modulus',79e9,'shaft_diameter',0.008, ...
    'grating_radius',0.007,'grating_period',p.grating.period, ...
    'parameter_source','simulation/default','seed_base',20260916);
cases=build_cases(p,cfg);
method_names=["Patent 1/4","Patent 1/16","Patent 1/32", ...
    "Traditional atan2","Existing improved"];
ncase=numel(cases); nmethod=numel(method_names); nrow=ncase*nmethod;
rows=table('Size',[nrow 14], ...
    'VariableTypes',{'string','string','double','string','string','double','double','double','double','double','double','double','double','string'}, ...
    'VariableNames',{'case_name','disturbance','torque_peak_Nm','method','status', ...
    'rmse_m','mae_m','maximum_error_m','resolution_m','nominal_step_m', ...
    'robustness_score','degradation_ratio','seed','error_message'});
case_data=repmat(struct('definition',[],'time',[],'torque',[],'x_true',[], ...
    'estimates',struct(),'errors',struct(),'zero_status',[]),ncase,1);
row=0;
for c=1:ncase
    definition=cases(c); t=linspace(0,cfg.duration,cfg.sample_count).';
    torque=linspace(0,definition.torque_peak,cfg.sample_count).';
    mechanical=torque_model(torque,struct('torsion_length',cfg.torsion_length, ...
        'shear_modulus',cfg.shear_modulus,'shaft_diameter',cfg.shaft_diameter, ...
        'grating_radius',cfg.grating_radius,'grating_period',cfg.grating_period, ...
        'phase_zero',0,'parameter_source',cfg.parameter_source));
    x_true=mechanical.relative_displacement;
    optical=optical_model(mechanical.optical_phase,p.optical); optical.t=t;
    ideal=signal_generator(optical,p.signal); ideal.t=t;
    e=p.errors; e.amplitude=definition.amplitude; e.phase_error=definition.phase_error;
    e.offset=definition.offset; e.hf_amplitude=0; e.hf_frequency=0;
    e.random_seed=definition.seed;
    if isfinite(definition.snr_db)
        sigma=(p.optical.Im/sqrt(2))/10^(definition.snr_db/20);
        e.noise_rms=sigma*ones(1,4);
    else
        sigma=0; e.noise_rms=zeros(1,4);
    end
    degraded=error_model(ideal,t,e);
    bp=patent_baseline_parameter();
    five_ideal=patent_five_channel_signal(mechanical.optical_phase,bp);
    stream=RandStream('mt19937ar','Seed',definition.seed+100000);
    zero_channel=five_ideal.ZERO+sigma*randn(stream,cfg.sample_count,1);
    five_channels=[zero_channel degraded.channels];

    estimates=struct(); messages=strings(1,nmethod); valid=false(1,nmethod);
    try
        baseline=patent_baseline_decoder(five_channels,cfg.grating_period,bp);
        estimates.baseline_4=double(baseline.count_4)*(cfg.grating_period/4);
        estimates.baseline_16=double(baseline.count_16)*(cfg.grating_period/16);
        estimates.baseline_32=double(baseline.count_32)*(cfg.grating_period/32);
        valid(1:3)=true;
    catch ME
        estimates.baseline_4=nan(cfg.sample_count,1);
        estimates.baseline_16=nan(cfg.sample_count,1);
        estimates.baseline_32=nan(cfg.sample_count,1);
        messages(1:3)=string(ME.identifier)+": "+string(ME.message);
        baseline=struct('zero_status',zero_channel>=bp.zero.threshold);
    end
    try
        estimates.traditional=traditional_atan2(degraded.channels,cfg.grating_period,x_true(1));
        valid(4)=all(isfinite(estimates.traditional));
        if ~valid(4), messages(4)="non-finite traditional atan2 output"; end
    catch ME
        estimates.traditional=nan(cfg.sample_count,1);
        messages(4)=string(ME.identifier)+": "+string(ME.message);
    end
    try
        lastwarn('');
        improved=phase_estimation(degraded,cfg.grating_period,t,x_true);
        [warning_message,warning_id]=lastwarn;
        estimates.improved=improved.x_est;
        valid(5)=all(isfinite(estimates.improved));
        if ~valid(5)
            messages(5)="non-finite existing improved output";
        elseif ~isempty(warning_message)
            messages(5)=string(warning_id)+": "+string(warning_message);
        end
    catch ME
        estimates.improved=nan(cfg.sample_count,1);
        messages(5)=string(ME.identifier)+": "+string(ME.message);
    end
    estimate_list={estimates.baseline_4,estimates.baseline_16,estimates.baseline_32, ...
        estimates.traditional,estimates.improved};
    nominal_steps=[cfg.grating_period/4,cfg.grating_period/16,cfg.grating_period/32,NaN,NaN];
    error_set=struct(); field_names={'baseline_4','baseline_16','baseline_32','traditional','improved'};
    for m=1:nmethod
        row=row+1; estimate=estimate_list{m}; err=estimate-x_true;
        error_set.(field_names{m})=err;
        rows.case_name(row)=string(definition.name);
        rows.disturbance(row)=string(definition.disturbance);
        rows.torque_peak_Nm(row)=definition.torque_peak;
        rows.method(row)=method_names(m);
        rows.seed(row)=definition.seed;
        rows.nominal_step_m(row)=nominal_steps(m);
        if valid(m)&&numel(estimate)==numel(x_true)&&all(isfinite(err))
            if strlength(messages(m))>0, rows.status(row)="warning";
            else, rows.status(row)="ok"; end
            rows.rmse_m(row)=sqrt(mean(err.^2));
            rows.mae_m(row)=mean(abs(err));
            rows.maximum_error_m(row)=max(abs(err));
            rows.resolution_m(row)=std(err);
            if rows.status(row)=="warning"
                rows.robustness_score(row)=NaN;
            else
                rows.robustness_score(row)=1/(1+rows.rmse_m(row)/(cfg.grating_period/32));
            end
            rows.error_message(row)=messages(m);
        else
            rows.status(row)="failed";
            rows.rmse_m(row)=NaN; rows.mae_m(row)=NaN;
            rows.maximum_error_m(row)=NaN; rows.resolution_m(row)=NaN;
            rows.robustness_score(row)=0;
            rows.error_message(row)=messages(m);
        end
    end
    case_data(c)=struct('definition',definition,'time',t,'torque',torque, ...
        'x_true',x_true,'estimates',estimates,'errors',error_set, ...
        'zero_status',baseline.zero_status);
end

for m=1:nmethod
    ideal_row=rows.case_name=="ideal"&rows.method==method_names(m);
    ideal_rmse=rows.rmse_m(ideal_row);
    method_rows=rows.method==method_names(m);
    if isempty(ideal_rmse)||~isfinite(ideal_rmse)||ideal_rmse<=eps
        rows.degradation_ratio(method_rows)=NaN;
    else
        rows.degradation_ratio(method_rows)=rows.rmse_m(method_rows)/ideal_rmse;
    end
end
rows.degradation_ratio(rows.status~="ok")=NaN;
summary=build_summary(rows,method_names);
failure_rows=rows(rows.status=="failed",:);
anomaly_rows=rows(rows.status~="ok",:);
case_table=struct2table(cases);
report=struct('stage',14,'methods',method_names,'configuration',cfg, ...
    'case_definitions',case_table,'results',rows,'summary',summary, ...
    'failures',failure_rows,'anomalies',anomaly_rows,'cases',case_data, ...
    'figure_files',strings(0,1), ...
    'policy','All predefined cases retained; no result-based exclusion.');
writetable(rows,fullfile(output_folder,'stage14_results.csv'));
writetable(case_table,fullfile(output_folder,'stage14_case_definitions.csv'));
writetable(summary,fullfile(output_folder,'stage14_method_summary.csv'));
write_stage14_report(report,output_folder);
save(fullfile(output_folder,'stage14_report.mat'),'report','-v7.3');
report.figure_files=plot_stage14_comparison(report,output_folder);
save(fullfile(output_folder,'stage14_report.mat'),'report','-v7.3');
end

function cases=build_cases(p,cfg)
base=struct('name','','disturbance','','torque_peak',cfg.reference_torque, ...
    'amplitude',p.optical.Im*ones(1,4),'phase_error',zeros(1,4), ...
    'offset',zeros(1,4),'snr_db',Inf,'seed',cfg.seed_base);
cases=repmat(base,14,1); k=0;
k=k+1; cases(k)=make_case(base,'ideal','ideal',8,k);
k=k+1; q=make_case(base,'amplitude_mismatch','amplitude mismatch',8,k); q.amplitude=p.optical.Im*[0.65 1.35 0.80 1.20]; cases(k)=q;
k=k+1; q=make_case(base,'phase_error','phase error',8,k); q.phase_error=[0.15 -0.12 0.08 -0.10]; cases(k)=q;
k=k+1; q=make_case(base,'dc_offset','DC offset',8,k); q.offset=[0.15 -0.10 0.08 -0.05]; cases(k)=q;
for snr=[30 20 10]
    k=k+1; q=make_case(base,sprintf('snr_%ddB',snr),'Gaussian noise',8,k); q.snr_db=snr; cases(k)=q;
end
for torque=[-8 -4 -1 0 1 4 8]
    k=k+1;
    if torque<0, name=sprintf('torque_neg%gNm',abs(torque));
    elseif torque>0, name=sprintf('torque_pos%gNm',torque);
    else, name='torque_0Nm'; end
    cases(k)=make_case(base,name,'torque sweep',torque,k);
end
end

function q=make_case(base,name,disturbance,torque,index)
q=base; q.name=name; q.disturbance=disturbance; q.torque_peak=torque;
q.seed=base.seed+index-1;
end

function x=traditional_atan2(channels,period,x0)
y=double(channels); u=0.5*(y(:,1)-y(:,3)); v=0.5*(y(:,4)-y(:,2));
theta=unwrap(atan2(v-mean(v),u-mean(u)));
x=period/(2*pi)*theta; x=x+(x0-x(1));
end

function summary=build_summary(rows,methods)
n=numel(methods);
summary=table('Size',[n 8], ...
    'VariableTypes',{'string','double','double','double','double','double','double','string'}, ...
    'VariableNames',{'method','valid_cases','failed_cases','mean_rmse_m','median_rmse_m', ...
    'worst_rmse_m','mean_robustness','worst_case'});
for k=1:n
    q=rows(rows.method==methods(k),:); ok=q.status=="ok"|q.status=="warning";
    summary.method(k)=methods(k); summary.valid_cases(k)=sum(ok);
    summary.failed_cases(k)=sum(~ok);
    if any(ok)
        summary.mean_rmse_m(k)=mean(q.rmse_m(ok));
        summary.median_rmse_m(k)=median(q.rmse_m(ok));
        [summary.worst_rmse_m(k),idx]=max(q.rmse_m(ok));
        names=q.case_name(ok); summary.worst_case(k)=names(idx);
        summary.mean_robustness(k)=mean(q.robustness_score(ok),'omitnan');
    else
        summary.mean_rmse_m(k)=NaN; summary.median_rmse_m(k)=NaN;
        summary.worst_rmse_m(k)=NaN; summary.mean_robustness(k)=0;
        summary.worst_case(k)="all failed";
    end
end
end
