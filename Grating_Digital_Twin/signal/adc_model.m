function adc = adc_model(voltage,t,a)
%ADC_MODEL Sample, clip and quantize an analog sensor voltage.
%   Voltage range is [a.vmin,a.vmax] (default 0..3.3 V), with a.bits ADC.
%   If a.sample_rate is provided, linear interpolation creates uniform ADC
%   sample instants, making sampling-frequency studies reproducible.
if nargin<2||isempty(t), t=(0:size(voltage,1)-1).'; end
if nargin<3||isempty(a), a=struct('sample_rate',1/mean(diff(t)),'bits',12,'vmin',0,'vmax',3.3); end
t=t(:); x=double(voltage); assert(size(x,1)==numel(t),'adc_model:Length','Voltage and time lengths differ.');
assert(all(diff(t)>0),'adc_model:Time','Time vector must be strictly increasing.');
fs_in=1/median(diff(t)); fs=a.sample_rate; assert(fs>0,'adc_model:Rate','sample_rate must be positive.');
if abs(fs-fs_in)/fs_in<1e-10
    ts=t; xs=x;
else
    ts=(t(1):1/fs:t(end)).';
    xs=interp1(t,x,ts,'linear','extrap');
end
levels=2^a.bits-1; clipped=min(max(xs,a.vmin),a.vmax); code=round((clipped-a.vmin)/(a.vmax-a.vmin)*levels); code=min(max(code,0),levels);
reconstructed=a.vmin+code/levels*(a.vmax-a.vmin); qerr=reconstructed-xs;
adc=struct('t_input',t,'analog_input',x,'t',ts,'sampled_voltage',xs,'clipped_voltage',clipped, ...
    'code',uint16(code),'reconstructed_voltage',reconstructed,'quantization_error',qerr, ...
    'bits',a.bits,'levels',levels,'vmin',a.vmin,'vmax',a.vmax,'sample_rate',fs, ...
    'input_rate',fs_in,'lsb',(a.vmax-a.vmin)/levels,'clip_count',sum(any(xs~=clipped,2)));
end
