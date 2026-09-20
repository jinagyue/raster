function signal = signal_generator(optical, signal_parameter)
%SIGNAL_GENERATOR Generate ideal four-phase sensor signals.
%   S_k=I0+Im*cos(theta+offset_k), offsets=[0,pi/2,pi,3*pi/2].
theta=optical.theta(:); offsets=reshape(signal_parameter.phase_offsets,1,[]);
assert(numel(offsets)==4,'signal_generator:Channels','Four phase offsets are required.');
n=numel(theta); channels=zeros(n,4); phases=zeros(n,4);
for k=1:4
    phases(:,k)=theta+offsets(k);
    channels(:,k)=optical.I0+optical.Im*cos(phases(:,k));
end
signal=struct('t',[],'channels',channels,'phase',phases,'phase_offsets',offsets, ...
    'amplitude',optical.amplitude*ones(1,4),'offset',optical.I0*ones(1,4), ...
    'period_phase',2*pi,'theta',theta);
end
