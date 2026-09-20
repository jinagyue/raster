# Stage 14 Patent Baseline vs Existing Algorithms

## Evidence boundary

- All mechanical values are `simulation/default`; results are simulation evidence, not patent or hardware performance.
- The predefined matrix contains 14 cases and 5 methods (70 rows). No result-based exclusion was applied.
- Warning and failed rows remain in `stage14_results.csv` and `stage14_report.mat`.

## Metric definitions

- RMSE, MAE and maximum error use displacement error in metres.
- Resolution is the sample standard deviation of displacement error.
- Nominal step is reported only for Patent 1/4, 1/16 and 1/32 counters.
- Robustness score is `1/(1+RMSE/(P/32))`; it is NaN when the algorithm reports an identifiability warning.
- Degradation ratio is case RMSE divided by the same method's ideal-case RMSE; warnings/failures are NaN.

## Method summary

| Method | Valid cases | Failed cases | Mean RMSE [m] | Median RMSE [m] | Worst RMSE [m] | Worst case |
|---|---:|---:|---:|---:|---:|---|
| Patent 1/4 | 14 | 0 | 2.41938981e-06 | 2.80812294e-06 | 3.00935486e-06 | snr_10dB |
| Patent 1/16 | 14 | 0 | 6.85906449e-07 | 7.12303629e-07 | 1.00723669e-06 | snr_10dB |
| Patent 1/32 | 14 | 0 | 3.84128656e-07 | 3.59618789e-07 | 7.28462486e-07 | snr_10dB |
| Traditional atan2 | 14 | 0 | 1.33430073e-06 | 3.64712328e-07 | 5.69832816e-06 | torque_neg1Nm |
| Existing improved | 14 | 0 | 1.73048257e-06 | 1.47850809e-07 | 7.74794555e-06 | torque_neg1Nm |

## Preserved anomalies

| Case | Method | Status | RMSE [m] | Message |
|---|---|---|---:|---|
| torque_0Nm | Existing improved | warning | 0 | MATLAB:rankDeficientMatrix: 秩亏，秩 = 1，tol =  1.987517e-11。 |

## Complete artifacts

- `stage14_results.csv`: all case-method metrics.
- `stage14_case_definitions.csv`: complete predefined inputs and seeds.
- `stage14_method_summary.csv`: aggregate method statistics.
- `stage14_report.mat`: complete trajectories, estimates, errors and metadata.
