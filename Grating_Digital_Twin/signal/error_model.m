function degraded = error_model(ideal, t, e)
%ERROR_MODEL Apply configurable non-idealities to four ideal grating signals.
%   S_i=A_i*cos(theta+phase_offset_i+phi_i)+I0+B_i+n_i+h(t).
%   A_i, phi_i and B_i are four-element vectors; noise is Gaussian.
if nargin<2 || isempty(t), t=ideal.t; end
t=t(:); theta=ideal.theta(:); assert(numel(theta)==numel(t),'error_model:Length','Time and theta lengths differ.');
A=reshape(e.amplitude,1,[]); phi=reshape(e.phase_error,1,[]); B=reshape(e.offset,1,[]); sigma=reshape(e.noise_rms,1,[]);
assert(numel(A)==4&&numel(phi)==4&&numel(B)==4&&numel(sigma)==4,'error_model:Channels','Four parameters are required for each channel.');
offsets=reshape(ideal.phase_offsets,1,[]); n=numel(t); ideal_channels=zeros(n,4); deterministic=zeros(n,4);
for k=1:4
    ideal_channels(:,k)=ideal.amplitude(k)*cos(theta+offsets(k))+ideal.offset(k);
    deterministic(:,k)=A(k)*cos(theta+offsets(k)+phi(k))+ideal.offset(k)+B(k);
end
rng(e.random_seed,'twister'); noise=randn(n,4).*sigma;
hf=e.hf_amplitude*sin(2*pi*e.hf_frequency*t+e.hf_phase); interference=hf*ones(1,4);
channels=deterministic+noise+interference;
degraded=struct('t',t,'theta',theta,'channels',channels,'ideal_channels',ideal_channels, ...
    'amplitude',A,'phase_error',phi,'offset',B,'noise_rms',sigma, ...
    'noise',noise,'high_frequency_interference',interference, ...
    'deterministic',deterministic,'error',channels-ideal_channels,'parameter',e);
end
