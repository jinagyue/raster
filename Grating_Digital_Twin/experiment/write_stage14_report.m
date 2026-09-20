function path = write_stage14_report(report,output_folder)
%WRITE_STAGE14_REPORT Create a human-readable, non-selective report index.
path=fullfile(output_folder,'stage14_report.md');
fid=fopen(path,'w'); assert(fid>0,'write_stage14_report:File','Cannot create report.');
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'# Stage 14 Patent Baseline vs Existing Algorithms\n\n');
fprintf(fid,'## Evidence boundary\n\n');
fprintf(fid,'- All mechanical values are `simulation/default`; results are simulation evidence, not patent or hardware performance.\n');
fprintf(fid,'- The predefined matrix contains %d cases and %d methods (%d rows). No result-based exclusion was applied.\n', ...
    height(report.case_definitions),numel(report.methods),height(report.results));
fprintf(fid,'- Warning and failed rows remain in `stage14_results.csv` and `stage14_report.mat`.\n\n');
fprintf(fid,'## Metric definitions\n\n');
fprintf(fid,'- RMSE, MAE and maximum error use displacement error in metres.\n');
fprintf(fid,'- Resolution is the sample standard deviation of displacement error.\n');
fprintf(fid,'- Nominal step is reported only for Patent 1/4, 1/16 and 1/32 counters.\n');
fprintf(fid,'- Robustness score is `1/(1+RMSE/(P/32))`; it is NaN when the algorithm reports an identifiability warning.\n');
fprintf(fid,'- Degradation ratio is case RMSE divided by the same method''s ideal-case RMSE; warnings/failures are NaN.\n\n');
fprintf(fid,'## Method summary\n\n');
fprintf(fid,'| Method | Valid cases | Failed cases | Mean RMSE [m] | Median RMSE [m] | Worst RMSE [m] | Worst case |\n');
fprintf(fid,'|---|---:|---:|---:|---:|---:|---|\n');
for k=1:height(report.summary)
    q=report.summary(k,:);
    fprintf(fid,'| %s | %d | %d | %.9g | %.9g | %.9g | %s |\n', ...
        q.method,q.valid_cases,q.failed_cases,q.mean_rmse_m,q.median_rmse_m, ...
        q.worst_rmse_m,q.worst_case);
end
fprintf(fid,'\n## Preserved anomalies\n\n');
if isempty(report.anomalies)
    fprintf(fid,'No warning or failed rows were produced.\n');
else
    fprintf(fid,'| Case | Method | Status | RMSE [m] | Message |\n');
    fprintf(fid,'|---|---|---|---:|---|\n');
    for k=1:height(report.anomalies)
        q=report.anomalies(k,:);
        message=replace(q.error_message,"|","/");
        fprintf(fid,'| %s | %s | %s | %.9g | %s |\n', ...
            q.case_name,q.method,q.status,q.rmse_m,message);
    end
end
fprintf(fid,'\n## Complete artifacts\n\n');
fprintf(fid,'- `stage14_results.csv`: all case-method metrics.\n');
fprintf(fid,'- `stage14_case_definitions.csv`: complete predefined inputs and seeds.\n');
fprintf(fid,'- `stage14_method_summary.csv`: aggregate method statistics.\n');
fprintf(fid,'- `stage14_report.mat`: complete trajectories, estimates, errors and metadata.\n');
end
