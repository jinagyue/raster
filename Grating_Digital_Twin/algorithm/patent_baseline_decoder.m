function result = patent_baseline_decoder(five_channel,period,p)
%PATENT_BASELINE_DECODER Traditional patent-reference counting baseline.
%   Positive recovered phase is defined as clockwise. Negative recovered
%   phase is counter-clockwise. The decoder is independent of
%   phase_estimation.m and is intended as a comparison baseline.
if nargin<3||isempty(p), p=patent_baseline_parameter(); end
validateattributes(period,{'numeric'},{'scalar','real','finite','positive'},mfilename,'period');
if isstruct(five_channel)
    channels=double(five_channel.channels);
else
    channels=double(five_channel);
end
assert(ismatrix(channels)&&size(channels,2)==5, ...
    'patent_baseline_decoder:Channels','Input must be an N-by-5 matrix.');
assert(all(isfinite(channels),'all'), ...
    'patent_baseline_decoder:Finite','All channel samples must be finite.');

ZERO=channels(:,1); MAIN=channels(:,2); PHASE_90=channels(:,3);
PHASE_180=channels(:,4); PHASE_270=channels(:,5);
zero_status=ZERO>=p.zero.threshold;
zero_index=find(zero_status,1,'first');
assert(~isempty(zero_index),'patent_baseline_decoder:NoZero', ...
    'No ZERO reference was detected.');

in_phase=MAIN-PHASE_180;
quadrature=PHASE_270-PHASE_90;
phase_wrapped=atan2(quadrature,in_phase);
phase_unwrapped=unwrap(phase_wrapped);
reference_phase=phase_unwrapped(zero_index);
relative_phase=phase_unwrapped-reference_phase;

delta=[0;diff(relative_phase)];
direction=zeros(size(delta),'int8');
direction(delta>p.direction.phase_deadband)=int8(1);
direction(delta<-p.direction.phase_deadband)=int8(-1);
direction_label=repmat({"stationary"},numel(direction),1);
direction_label(direction>0)={p.direction.positive_label};
direction_label(direction<0)={p.direction.negative_label};

turns=relative_phase/(2*pi);
coarse_count=signed_completed_count(turns);
count_4=signed_completed_count(4*turns);
count_16=signed_completed_count(16*turns);
count_32=signed_completed_count(32*turns);
estimated_displacement=double(count_32)*(period/32);

result=struct('direction',direction,'direction_label',{direction_label}, ...
    'zero_status',zero_status,'zero_index',zero_index, ...
    'coarse_count',coarse_count,'count_4',count_4, ...
    'count_16',count_16,'count_32',count_32, ...
    'estimated_displacement',estimated_displacement, ...
    'phase_wrapped',phase_wrapped,'phase_unwrapped',phase_unwrapped, ...
    'relative_phase',relative_phase,'reference_phase',reference_phase, ...
    'period',period,'resolution',period/32, ...
    'channel_order',{p.channel_order},'method','Patent Baseline');
end

function count=signed_completed_count(value)
% Count completed signed intervals while remaining stable near boundaries.
tolerance=64*eps(max(1,max(abs(value))));
count=int64(sign(value).*floor(abs(value)+tolerance));
end
