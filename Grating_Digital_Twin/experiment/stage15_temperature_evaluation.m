function report = stage15_temperature_evaluation(p,output_folder)
%STAGE15_TEMPERATURE_EVALUATION Compare compensation OFF and ON.
if nargin<1||isempty(p), p=temperature_parameter(); end
root=fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root,'config'),fullfile(root,'mechanics'));
if nargin<2||isempty(output_folder), output_folder=fullfile(root,'data','stage15'); end
if ~isfolder(output_folder), mkdir(output_folder); end
temperatures=p.temperature_C(:); torques=p.torque_Nm(:);
nT=numel(temperatures); nQ=numel(torques); n=nT*nQ;
rows=table('Size',[n 18], ...
    'VariableTypes',[repmat({'double'},1,17),{'string'}], ...
    'VariableNames',{'temperature_C','torque_true_Nm','shear_modulus_Pa', ...
    'torsional_sensitivity_rad_per_Nm','sensitivity_variation','grating_period_m', ...
    'phase_rad','phase_error_rad','torque_off_Nm','torque_off_error_Nm', ...
    'torque_on_Nm','torque_on_error_Nm','displacement_true_m', ...
    'displacement_off_m','displacement_off_error_m','displacement_on_m', ...
    'displacement_on_error_m','parameter_source'});
states=cell(nT,1); row=0;
for k=1:nT
    s=temperature_model(temperatures(k),torques,p); states{k}=s;
    idx=row+(1:nQ); row=row+nQ;
    rows.temperature_C(idx)=temperatures(k);
    rows.torque_true_Nm(idx)=torques;
    rows.shear_modulus_Pa(idx)=s.shear_modulus_Pa;
    rows.torsional_sensitivity_rad_per_Nm(idx)=s.torsional_sensitivity_rad_per_Nm;
    rows.sensitivity_variation(idx)=s.torsional_sensitivity_variation;
    rows.grating_period_m(idx)=s.grating_period_m;
    rows.phase_rad(idx)=s.measured_phase;
    rows.phase_error_rad(idx)=s.phase_error;
    rows.torque_off_Nm(idx)=s.compensation_off.torque_estimate;
    rows.torque_off_error_Nm(idx)=s.compensation_off.torque_error;
    rows.torque_on_Nm(idx)=s.compensation_on.torque_estimate;
    rows.torque_on_error_Nm(idx)=s.compensation_on.torque_error;
    rows.displacement_true_m(idx)=s.true_displacement;
    rows.displacement_off_m(idx)=s.compensation_off.displacement_estimate;
    rows.displacement_off_error_m(idx)=s.compensation_off.displacement_error;
    rows.displacement_on_m(idx)=s.compensation_on.displacement_estimate;
    rows.displacement_on_error_m(idx)=s.compensation_on.displacement_error;
    rows.parameter_source(idx)=string(s.parameter_source);
end
summary=temperature_summary(rows,temperatures);
report=struct();
report.stage=15;
report.parameter=p;
report.results=rows;
report.summary=summary;
report.states=states;
report.figure_files=strings(0,1);
report.evidence_boundary='All temperature coefficients are simulation/default and unverified.';
writetable(rows,fullfile(output_folder,'stage15_temperature_results.csv'));
writetable(summary,fullfile(output_folder,'stage15_temperature_summary.csv'));
write_stage15_report(report,output_folder);
save(fullfile(output_folder,'stage15_report.mat'),'report','-v7.3');
report.figure_files=plot_stage15_temperature(report,output_folder);
save(fullfile(output_folder,'stage15_report.mat'),'report','-v7.3');
end

function summary=temperature_summary(rows,temperatures)
n=numel(temperatures);
summary=table('Size',[n 11],'VariableTypes',repmat({'double'},1,11), ...
    'VariableNames',{'temperature_C','shear_modulus_Pa','sensitivity_variation', ...
    'torque_rmse_off_Nm','torque_rmse_on_Nm','torque_max_off_Nm','torque_max_on_Nm', ...
    'displacement_rmse_off_m','displacement_rmse_on_m', ...
    'displacement_max_off_m','displacement_max_on_m'});
for k=1:n
    q=rows(rows.temperature_C==temperatures(k),:);
    summary.temperature_C(k)=temperatures(k); summary.shear_modulus_Pa(k)=q.shear_modulus_Pa(1);
    summary.sensitivity_variation(k)=q.sensitivity_variation(1);
    summary.torque_rmse_off_Nm(k)=sqrt(mean(q.torque_off_error_Nm.^2));
    summary.torque_rmse_on_Nm(k)=sqrt(mean(q.torque_on_error_Nm.^2));
    summary.torque_max_off_Nm(k)=max(abs(q.torque_off_error_Nm));
    summary.torque_max_on_Nm(k)=max(abs(q.torque_on_error_Nm));
    summary.displacement_rmse_off_m(k)=sqrt(mean(q.displacement_off_error_m.^2));
    summary.displacement_rmse_on_m(k)=sqrt(mean(q.displacement_on_error_m.^2));
    summary.displacement_max_off_m(k)=max(abs(q.displacement_off_error_m));
    summary.displacement_max_on_m(k)=max(abs(q.displacement_on_error_m));
end
end
