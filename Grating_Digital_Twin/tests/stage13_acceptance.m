function report = stage13_acceptance()
%STAGE13_ACCEPTANCE Verify zero, direction and reversible subdivisions.
root=fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root,'config'),fullfile(root,'signal'),fullfile(root,'algorithm'));
p=patent_baseline_parameter();
period=20e-6;
step=2*pi/64;
forward=(0:step:4*pi).';
reverse=(4*pi-step:-step:0).';
theta=[forward;reverse];
five=patent_five_channel_signal(theta,p);
decoded=patent_baseline_decoder(five,period,p);

forward_index=2:numel(forward);
reverse_index=numel(forward)+1:numel(theta);
one_turn_index=1+round(2*pi/step);
two_turn_index=numel(forward);

report=struct();
report.pass_five_channels=size(five.channels,2)==5&& ...
    isequal(five.channel_order,{'ZERO','MAIN','PHASE_90','PHASE_180','PHASE_270'});
report.pass_zero=decoded.zero_status(1)&&decoded.zero_index==1&& ...
    ~decoded.zero_status(1+round((pi/2)/step));
report.pass_clockwise=all(decoded.direction(forward_index)==1);
report.pass_counter_clockwise=all(decoded.direction(reverse_index)==-1);
report.pass_reversible=decoded.coarse_count(two_turn_index)==2&& ...
    decoded.count_32(two_turn_index)==64&&decoded.coarse_count(end)==0&& ...
    decoded.count_32(end)==0;
report.pass_ratio_4=decoded.count_4(one_turn_index)==4*decoded.coarse_count(one_turn_index);
report.pass_ratio_16=decoded.count_16(one_turn_index)==16*decoded.coarse_count(one_turn_index);
report.pass_ratio_32=decoded.count_32(one_turn_index)==32*decoded.coarse_count(one_turn_index);
report.pass_displacement=abs(decoded.estimated_displacement(one_turn_index)-period)<1e-15&& ...
    abs(decoded.estimated_displacement(end))<1e-15;
report.zero_samples=sum(decoded.zero_status);
report.final_coarse_count=double(decoded.coarse_count(end));
report.final_count_32=double(decoded.count_32(end));
report.resolution=decoded.resolution;
report.pass=report.pass_five_channels&&report.pass_zero&&report.pass_clockwise&& ...
    report.pass_counter_clockwise&&report.pass_reversible&&report.pass_ratio_4&& ...
    report.pass_ratio_16&&report.pass_ratio_32&&report.pass_displacement;
assert(report.pass,'stage13_acceptance:Failed','Stage 13 patent-baseline acceptance failed.');
end
