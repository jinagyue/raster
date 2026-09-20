function p = parameter()
%PARAMETER Central parameter registry for the digital-twin project.
% SI units are used internally: metre, second, radian.
p.project.name = 'Grating Digital Twin';
p.project.stage = 8;
p.grating.period = 20e-6;          % P [m]
p.grating.number = 50;             % N [-]
p.grating.length = 2e-3;           % L [m]
p.grating.height = 1e-6;           % surface height [m]
p.grating.grid_x = 2001;           % points along x
p.grating.grid_y = 120;            % points along y
p.grating.main_shift = 0;          % main grating translation [m]
p.grating.reference_shift = 5e-6;  % reference grating translation [m]
p.motion.mode = 'constant_velocity'; % constant_velocity/acceleration/periodic_disturbance
p.motion.sample_rate = 20e3;        % motion simulation sample rate [Hz]
p.motion.duration = 20e-3;          % motion simulation duration [s]
p.motion.v = 2e-3;                  % constant velocity [m/s]
p.motion.v0 = 1e-3;                 % initial velocity [m/s]
p.motion.a = 0.2;                   % acceleration [m/s^2]
p.motion.A = 2e-6;                  % periodic disturbance amplitude [m]
p.motion.f = 100;                   % periodic disturbance frequency [Hz]
p.optical.I0 = 1.0;                 % optical DC intensity [a.u.]
p.optical.Im = 0.8;                 % optical modulation amplitude [a.u.]
p.signal.phase_offsets = [0 pi/2 pi 3*pi/2];
p.errors.amplitude = p.optical.Im*[1 1 1 1]; % A_i [a.u.]
p.errors.phase_error = [0 0 0 0];           % phi_i [rad]
p.errors.offset = [0 0 0 0];                % B_i [a.u.]
p.errors.noise_rms = [0 0 0 0];             % Gaussian sigma [a.u.]
p.errors.hf_amplitude = 0;                  % interference amplitude [a.u.]
p.errors.hf_frequency = 0;                  % interference frequency [Hz]
p.errors.hf_phase = 0;                      % interference phase [rad]
p.errors.random_seed = 20260904;
p.adc.sample_rate = p.motion.sample_rate; % ADC sampling rate [Hz]
p.adc.bits = 12;
p.adc.vmin = 0;
p.adc.vmax = 3.3;
p.serial.mode = 'none';
p.serial.port = 'COM5';
p.serial.file = 'data/serial_stream.bin';
p.serial.baud_rate = 115200;
% 11 bytes/frame and 8N1 require 110 line bits/frame.  At 115200 baud the
% theoretical ceiling is about 1047 frame/s; 500 frame/s leaves margin.
p.serial.send_rate = 500;
p.serial.realtime = true;
p.visualization.figure_visible = 'on';
p.visualization.local_periods = 5;
p.visualization.export = false;
p.visualization.export_folder = 'data/stage1_figures';
end
