function response = python_control(command, input_parameter)
%PYTHON_CONTROL MATLAB Engine endpoint for stages 9-12.
%   RESPONSE = PYTHON_CONTROL('ping') checks connectivity.
%   RESPONSE = PYTHON_CONTROL('set_parameter',S) validates and stores S.
%   RESPONSE = PYTHON_CONTROL('get_parameter') returns the stored controls.
%   RESPONSE = PYTHON_CONTROL('run_simulation',S) runs the adapter pipeline.
%   The previously accepted Stage 1-8 core model files are not modified.
 persistent current_parameter;
 root = fileparts(fileparts(mfilename('fullpath')));
 addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'), ...
     fullfile(root,'algorithm'),fullfile(root,'communication'),fullfile(root,'mechanics'));
if nargin < 1 || isempty(command)
    command = 'ping';
end
if ~(ischar(command) || (isstring(command) && isscalar(command)))
    error('python_control:InvalidCommand','command must be a character vector or scalar string.');
end
switch lower(char(command))
    case 'ping'
        response = struct('status','ok', ...
            'stage',9, ...
            'interface','python_control', ...
            'matlab_version',version);
    case 'set_parameter'
        if nargin < 2, error('python_control:MissingParameter','Parameter structure is required.'); end
        [~, current_parameter] = update_parameter(input_parameter);
        response = struct('status','ok','stage',10,'parameter',current_parameter);
    case 'get_parameter'
        if isempty(current_parameter)
            [~, current_parameter] = update_parameter(default_circular_parameter());
        end
        response = struct('status','ok','stage',10,'parameter',current_parameter);
    case 'run_simulation'
        if nargin < 2
            if isempty(current_parameter), input_parameter = default_circular_parameter();
            else, input_parameter = current_parameter; end
        end
        [p, current_parameter] = update_parameter(input_parameter);
        root = fileparts(fileparts(mfilename('fullpath')));
        addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'), ...
            fullfile(root,'algorithm'),fullfile(root,'communication'));
        t = (0:1/p.motion.sample_rate:p.motion.duration).';
        motion = motion_model(t,p.motion,p.grating.period);
        motion.x = motion.x + current_parameter.shift;
        motion.theta = 2*pi*motion.x/p.grating.period;
        optical = optical_model(motion.theta,p.optical); optical.t=t;
        signals = signal_generator(optical,p.signal); signals.t=t;
        nonideal = error_model(signals,t,p.errors);
        estimate = phase_estimation(nonideal,p.grating.period,t,motion.x);
        adc = adc_model(nonideal.channels,t,p.adc);
        p.serial.mode = 'none';
        serial = serial_output(p.serial,adc,adc.t);
        response = struct('status','ok','stage',11,'parameter',current_parameter, ...
            'adc_code',adc.code,'phase',estimate.theta_est,'signal',nonideal.channels, ...
            'time',adc.t,'serial',serial,'motion',motion);
    case 'run_torque'
        if nargin < 2, input_parameter = default_torque_parameter(); end
        response = run_torque_pipeline(input_parameter);
    otherwise
        error('python_control:UnknownCommand','Unsupported Stage-9 command: %s.',char(command));
end
end

function s = default_circular_parameter()
s = struct('period',20e-6,'radius',1e-3,'ring_number',50,'height',1e-6,'shift',5e-6);
end

function response = run_torque_pipeline(input_parameter)
%RUN_TORQUE_PIPELINE Torque-driven Stage-12 physical chain.
if ~isstruct(input_parameter), error('python_control:InvalidTorqueParameter','A parameter structure is required.'); end
base = parameter();
mechanical = torque_to_grating(input_parameter);
torque = mechanical.torque;
angle = mechanical.torsion_angle;
displacement = mechanical.relative_displacement;
base.grating.period = mechanical.parameter.grating_period;
base.grating.reference_shift = displacement;
% Stage-16 waveform preview: the slider value is the mean torque and a
% small sinusoidal excitation exposes the time-domain sensor response.
% This adapter change does not alter the accepted mechanics/signal models.
base.motion.duration = 8e-3;
base.motion.sample_rate = min(base.motion.sample_rate,20e3);
base.adc.sample_rate = base.motion.sample_rate;
if isfield(input_parameter,'serial_mode') && ~isempty(input_parameter.serial_mode)
    base.serial.mode = char(input_parameter.serial_mode);
else
    base.serial.mode = 'simulation';
end
base.serial.realtime = false;
base.serial.file = fullfile(fileparts(fileparts(mfilename('fullpath'))),'data','torque_serial_stream.bin');
root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'), ...
    fullfile(root,'algorithm'),fullfile(root,'communication'),fullfile(root,'mechanics'));
t = (0:1/base.motion.sample_rate:base.motion.duration).';
excitation_frequency = get_scalar(input_parameter,'excitation_frequency',250);
excitation_amplitude = get_scalar(input_parameter,'excitation_amplitude',max(0.20,0.15*abs(torque)));
torque_waveform = torque + excitation_amplitude*sin(2*pi*excitation_frequency*t);
dynamic_mechanical = torque_model(torque_waveform,mechanical.parameter);
phase = dynamic_mechanical.optical_phase;
optical = optical_model(phase,base.optical); optical.t=t;
signals = signal_generator(optical,base.signal); signals.t=t;
nonideal = error_model(signals,t,base.errors);
adc = adc_model(nonideal.channels,t,base.adc);
patent_signal = patent_five_channel_signal(phase);
five_channel_signal = [patent_signal.ZERO nonideal.channels];
serial = serial_output(base.serial,adc,adc.t);
response = struct('status','ok','stage',12,'torque',torque,'angle',angle, ...
    'torsion_angle',angle,'polar_moment',mechanical.polar_moment, ...
    'grating_displacement',displacement,'grating_relative_displacement',displacement, ...
    'optical_phase',mechanical.optical_phase,'phase',phase, ...
    'four_phase_signal',nonideal.channels,'adc_code',adc.code, ...
    'five_channel_signal',five_channel_signal, ...
    'torque_waveform',torque_waveform, ...
    'torsion_angle_waveform',dynamic_mechanical.torsion_angle, ...
    'displacement_waveform',dynamic_mechanical.relative_displacement, ...
    'time',adc.t,'serial_status',serial,'mechanical_parameter',mechanical.parameter, ...
    'parameter_source',mechanical.parameter_source);
end

function p = default_torque_parameter()
p = struct('torque',0,'torsion_length',0.012,'shear_modulus',79e9, ...
    'shaft_diameter',0.008,'grating_radius',0.007,'grating_period',20e-6, ...
    'phase_zero',0,'parameter_source','simulation/default');
end

function value = get_scalar(s,name,default_value)
if ~isfield(s,name) || isempty(s.(name)), value=default_value; return; end
value=s.(name);
if ~(isnumeric(value)&&isscalar(value)&&isfinite(value)&&isreal(value))
    error('python_control:InvalidTorqueParameter','%s must be a finite real scalar.',name);
end
value=double(value);
end
