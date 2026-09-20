function estimate = phase_estimation(nonideal, period, t, x_true)
%PHASE_ESTIMATION Calibrated four-phase displacement estimator.
%   The improved path performs robust offset removal, per-channel RMS
%   normalization, ellipse whitening (joint gain/phase compensation),
%   atan2 recovery and phase unwrapping. A direct-atan2 baseline is returned
%   for a controlled comparison; no zero-crossing counter is used.
if nargin<3 || isempty(t), t=nonideal.t; end
if nargin<4, x_true=[]; end
t=t(:); y=double(nonideal.channels); assert(size(y,2)==4,'phase_estimation:Channels','Four channels are required.');
% Baseline: only complementary differences and atan2.
raw_u=0.5*(y(:,1)-y(:,3)); raw_v=0.5*(y(:,4)-y(:,2));
theta_direct=unwrap(atan2(raw_v-mean(raw_v),raw_u-mean(raw_u)));
x_direct=period/(2*pi)*theta_direct;
% Improved 1-2: robust bias and amplitude compensation per channel.
center=median(y,1); centered=y-center; scale=sqrt(mean(centered.^2,1)); scale=max(scale,eps); normalized=centered./scale;
u=0.5*(normalized(:,1)-normalized(:,3)); v=0.5*(normalized(:,4)-normalized(:,2)); uv=[u v]; uv=uv-mean(uv,1);
% Improved 3: estimate ellipse covariance and whiten it to a unit circle.
C=(uv.'*uv)/max(size(uv,1)-1,1); [V,D]=eig(C+1e-12*eye(2)); lambda=max(diag(D),1e-12); W=V*diag(1./sqrt(lambda))*V.'; corrected_xy=uv*W.';
if corr(corrected_xy(:,1),uv(:,1),'Rows','complete')<0, corrected_xy(:,1)=-corrected_xy(:,1); end
if corr(corrected_xy(:,2),uv(:,2),'Rows','complete')<0, corrected_xy(:,2)=-corrected_xy(:,2); end
theta_corrected=unwrap(atan2(corrected_xy(:,2),corrected_xy(:,1)));
% Estimate residual phase bias of each channel for traceability.
if isfield(nonideal,'phase_offsets'), phase_offsets=nonideal.phase_offsets; else, phase_offsets=[0 pi/2 pi 3*pi/2]; end
phase_error_est=zeros(1,4); amplitude_est=zeros(1,4);
for k=1:4
    H=[cos(theta_corrected+phase_offsets(k)),sin(theta_corrected+phase_offsets(k))]; beta=H\centered(:,k); amplitude_est(k)=hypot(beta(1),beta(2)); phase_error_est(k)=atan2(-beta(2),beta(1));
end
% Remove the common residual phase rotation; metrics may additionally use x_true(1).
theta_est=theta_corrected-mean(phase_error_est); x_est=period/(2*pi)*theta_est;
if ~isempty(x_true)
    x_true=x_true(:); assert(numel(x_true)==numel(x_est),'phase_estimation:Length','x_true length mismatch.');
    x_direct=x_direct+(x_true(1)-x_direct(1)); x_est=x_est+(x_true(1)-x_est(1));
    err_direct=x_direct-x_true; err=x_est-x_true;
    metrics=struct('traditional',metric_struct(err_direct),'improved',metric_struct(err));
else
    err_direct=[]; err=[]; metrics=struct('traditional',metric_struct([]),'improved',metric_struct([]));
end
estimate=struct('t',t,'theta_est',theta_est,'x_est',x_est,'x_true',x_true,'error',err, ...
    'theta_direct',theta_direct,'x_direct',x_direct,'error_direct',err_direct, ...
    'raw_xy',[raw_u raw_v],'corrected_xy',corrected_xy,'channel_center',center, ...
    'channel_scale',scale,'whitening_matrix',W,'phase_error_est',phase_error_est, ...
    'amplitude_est',amplitude_est,'metrics',metrics, ...
    'rmse',metrics.improved.rmse,'max_error',metrics.improved.max_error, ...
    'resolution_1sigma',metrics.improved.resolution_1sigma);
end

function m=metric_struct(err)
if isempty(err), m=struct('rmse',NaN,'max_error',NaN,'resolution_1sigma',NaN); return; end
m=struct('rmse',sqrt(mean(err.^2)),'max_error',max(abs(err)),'resolution_1sigma',std(err));
end
