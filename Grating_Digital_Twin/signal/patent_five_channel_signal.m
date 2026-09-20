function signal = patent_five_channel_signal(theta,p)
%PATENT_FIVE_CHANNEL_SIGNAL Generate the patent baseline five-channel set.
% Channel order: ZERO, MAIN, PHASE_90, PHASE_180, PHASE_270.
% ZERO is a reference window centred on zero phase and repeated every 2*pi.
if nargin<2||isempty(p), p=patent_baseline_parameter(); end
validateattributes(theta,{'numeric'},{'vector','real','finite'},mfilename,'theta');
theta=double(theta(:));
A=p.signal.amplitude; B=p.signal.offset;
wrapped_zero=mod(theta-p.zero.phase+pi,2*pi)-pi;
zero_active=abs(wrapped_zero)<=p.zero.width/2;
ZERO=p.zero.low+(p.zero.high-p.zero.low)*double(zero_active);
MAIN=B+A*cos(theta);
PHASE_90=B+A*cos(theta+pi/2);
PHASE_180=B+A*cos(theta+pi);
PHASE_270=B+A*cos(theta+3*pi/2);
channels=[ZERO MAIN PHASE_90 PHASE_180 PHASE_270];
signal=struct('channels',channels,'channel_order',{p.channel_order}, ...
    'ZERO',ZERO,'MAIN',MAIN,'PHASE_90',PHASE_90, ...
    'PHASE_180',PHASE_180,'PHASE_270',PHASE_270, ...
    'theta',theta,'zero_active',zero_active,'parameter',p);
end
