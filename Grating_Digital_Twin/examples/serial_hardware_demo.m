function info = serial_hardware_demo(port_name)
%SERIAL_HARDWARE_DEMO Send a known four-channel ADC pattern over a real COM port.
% Close any serial assistant using the same port before running.  For a
% virtual null-modem pair, MATLAB may open COM5 while the assistant opens
% its paired COM6 endpoint.
if nargin < 1 || isempty(port_name), port_name = 'COM5'; end
root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root,'config'),fullfile(root,'communication'));
p = parameter();
p.serial.mode = 'hardware';
p.serial.port = char(port_name);
p.serial.baud_rate = 115200;
p.serial.send_rate = 500;
p.serial.realtime = true;

duration = 1.0;
fs = p.adc.sample_rate;
t = (0:1/fs:duration-1/fs).';
phase = 2*pi*5*t;
code = round(2047.5*(1+[cos(phase),cos(phase+pi/2), ...
    cos(phase+pi),cos(phase+3*pi/2)]));
adc = struct('code',uint16(min(max(code,0),4095)),'t',t);
info = serial_output(p.serial,adc,t);
fprintf('Sent %d frames (%d bytes) to %s at %d baud.\n', ...
    info.frames,info.bytes,p.serial.port,p.serial.baud_rate);
end
