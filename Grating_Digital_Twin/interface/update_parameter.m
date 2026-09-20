function [p, circular] = update_parameter(input_parameter)
%UPDATE_PARAMETER Map Python circular-grating controls to MATLAB parameters.
%   [P,CIRCULAR] = UPDATE_PARAMETER(S) validates the five Stage-10/11
%   controls and returns a complete MATLAB parameter structure plus a
%   canonical circular-parameter record. Existing Stage 1-8 files remain
%   unchanged; this function is an adapter layer only.
if nargin < 1 || isempty(input_parameter)
    input_parameter = struct();
end
base = parameter();
required = {'period','radius','ring_number','height','shift'};
for k = 1:numel(required)
    name = required{k};
    if ~isfield(input_parameter,name)
        error('update_parameter:MissingField','Missing field: %s.',name);
    end
end
period = scalar_positive(input_parameter.period,'period');
radius = scalar_positive(input_parameter.radius,'radius');
ring_number = scalar_integer(input_parameter.ring_number,'ring_number');
height = scalar_nonnegative(input_parameter.height,'height');
shift = scalar_finite(input_parameter.shift,'shift');

% The legacy MATLAB geometry uses a rectangular length. Its length is set to
% the circular diameter only for compatibility; the circular mesh remains a
% Python-side structural representation.
p = base;
p.project.stage = 11;
p.grating.period = period;
p.grating.number = ring_number;
p.grating.length = 2*radius;
p.grating.height = height;
p.grating.reference_shift = shift;

% Height controls modulation depth while preserving non-negative intensity.
height_scale = height / max(base.grating.height,eps);
p.optical.Im = min(base.optical.I0*0.95, base.optical.Im*height_scale);
p.errors.amplitude = p.optical.Im*[1 1 1 1];
p.motion.reference_shift = shift;

circular = struct('period',period,'radius',radius,'ring_number',ring_number, ...
    'height',height,'shift',shift);
end

function value = scalar_positive(value,name)
value = scalar_finite(value,name);
if value <= 0, error('update_parameter:Range','%s must be positive.',name); end
end

function value = scalar_nonnegative(value,name)
value = scalar_finite(value,name);
if value < 0, error('update_parameter:Range','%s must be non-negative.',name); end
end

function value = scalar_integer(value,name)
value = scalar_finite(value,name);
if value < 1 || value ~= round(value)
    error('update_parameter:Range','%s must be a positive integer.',name);
end
value = round(value);
end

function value = scalar_finite(value,name)
if ~(isnumeric(value) && isscalar(value) && isreal(value) && isfinite(value))
    error('update_parameter:Type','%s must be a finite real scalar.',name);
end
value = double(value);
end
