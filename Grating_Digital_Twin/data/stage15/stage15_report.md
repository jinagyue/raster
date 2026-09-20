# Stage 15 Temperature Model and Compensation

## Evidence boundary

All coefficients in this report are `simulation/default` and unverified. They are not derived from patent dimensions, material certificates or real material tests.

## Central parameters

| Parameter | Value | Source |
|---|---:|---|
| Reference temperature | 20 degC | simulation/default |
| Reference shear modulus | 7.9e+10 Pa | simulation/default |
| Shear-modulus temperature coefficient | -0.0003 /degC | simulation/default, unverified |
| Reference grating period | 2e-05 m | simulation/default |
| Grating-period temperature coefficient | 1.2e-05 /degC | simulation/default, unverified |

## Model

`G(T)=G0*(1+alpha_G*(T-T0))` and `P(T)=P0*(1+alpha_P*(T-T0))`.

Compensation OFF uses `G0` and `P0`. Compensation ON uses `G(T)` and `P(T)`.

## Temperature summary

| Temperature [degC] | Sensitivity change [%] | Torque RMSE OFF [N*m] | Torque RMSE ON [N*m] | Displacement RMSE OFF [m] | Displacement RMSE ON [m] |
|---:|---:|---:|---:|---:|---:|
| -20 | -1.18577075 | 0.0547610496 | 0 | 6.03628972e-09 | 0 |
| 0 | -0.596421471 | 0.0275441038 | 0 | 3.03541687e-09 | 0 |
| 20 | 0 | 0 | 0 | 0 | 0 |
| 40 | 0.60362173 | 0.0278771857 | 0 | 3.07058751e-09 | 0 |
| 60 | 1.2145749 | 0.0560935212 | 0 | 6.17698748e-09 | 2.0374117e-21 |
| 80 | 1.83299389 | 0.0846552228 | 0 | 9.31985743e-09 | 0 |

Complete sample-level results are retained in `stage15_temperature_results.csv` and `stage15_report.mat`.
