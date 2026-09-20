function path = write_stage15_report(report,output_folder)
%WRITE_STAGE15_REPORT Human-readable temperature compensation report.
path=fullfile(output_folder,'stage15_report.md');
fid=fopen(path,'w'); assert(fid>0,'write_stage15_report:File','Cannot create report.');
cleanup=onCleanup(@()fclose(fid)); p=report.parameter;
fprintf(fid,'# Stage 15 Temperature Model and Compensation\n\n');
fprintf(fid,'## Evidence boundary\n\n');
fprintf(fid,'All coefficients in this report are `simulation/default` and unverified. ');
fprintf(fid,'They are not derived from patent dimensions, material certificates or real material tests.\n\n');
fprintf(fid,'## Central parameters\n\n');
fprintf(fid,'| Parameter | Value | Source |\n|---|---:|---|\n');
fprintf(fid,'| Reference temperature | %.6g degC | simulation/default |\n',p.reference_temperature_C);
fprintf(fid,'| Reference shear modulus | %.9g Pa | simulation/default |\n',p.material.shear_modulus_ref_Pa);
fprintf(fid,'| Shear-modulus temperature coefficient | %.9g /degC | simulation/default, unverified |\n',p.material.shear_modulus_temp_coefficient_per_C);
fprintf(fid,'| Reference grating period | %.9g m | simulation/default |\n',p.grating.period_ref_m);
fprintf(fid,'| Grating-period temperature coefficient | %.9g /degC | simulation/default, unverified |\n',p.grating.period_temp_coefficient_per_C);
fprintf(fid,'\n## Model\n\n');
fprintf(fid,'`G(T)=G0*(1+alpha_G*(T-T0))` and `P(T)=P0*(1+alpha_P*(T-T0))`.\n\n');
fprintf(fid,'Compensation OFF uses `G0` and `P0`. Compensation ON uses `G(T)` and `P(T)`.\n\n');
fprintf(fid,'## Temperature summary\n\n');
fprintf(fid,'| Temperature [degC] | Sensitivity change [%%] | Torque RMSE OFF [N*m] | Torque RMSE ON [N*m] | Displacement RMSE OFF [m] | Displacement RMSE ON [m] |\n');
fprintf(fid,'|---:|---:|---:|---:|---:|---:|\n');
for k=1:size(report.summary,1)
    q=report.summary(k,:);
    fprintf(fid,'| %.6g | %.9g | %.9g | %.9g | %.9g | %.9g |\n', ...
        q.temperature_C,100*q.sensitivity_variation,q.torque_rmse_off_Nm, ...
        q.torque_rmse_on_Nm,q.displacement_rmse_off_m,q.displacement_rmse_on_m);
end
fprintf(fid,'\nComplete sample-level results are retained in `stage15_temperature_results.csv` and `stage15_report.mat`.\n');
end
