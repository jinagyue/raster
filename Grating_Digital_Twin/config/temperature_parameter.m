function p = temperature_parameter()
%TEMPERATURE_PARAMETER Central Stage-15 temperature configuration.
% Coefficients below are unverified simulation assumptions. They do not
% originate from patent dimensions, material certificates or real tests.
p.reference_temperature_C = 20;
p.temperature_C = [-20 0 20 40 60 80];
p.torque_Nm = [-8 -4 -1 0 1 4 8];
p.material.shear_modulus_ref_Pa = 79e9;
p.material.shear_modulus_temp_coefficient_per_C = -3.0e-4;
p.grating.period_ref_m = 20e-6;
p.grating.period_temp_coefficient_per_C = 1.2e-5;
p.mechanics.torsion_length_m = 0.012;
p.mechanics.shaft_diameter_m = 0.008;
p.mechanics.grating_radius_m = 0.007;
p.metadata.parameter_source = 'simulation/default';
p.metadata.coefficients_verified = false;
p.metadata.claim = 'Unverified simulation coefficients; not real material-test data.';
end
