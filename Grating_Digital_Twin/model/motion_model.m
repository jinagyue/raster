function motion = motion_model(t, m, period)
%MOTION_MODEL Parameterized relative-motion model for the grating pair.
%   motion = MOTION_MODEL(t,m,P) supports:
%   constant_velocity:     x=v*t
%   acceleration:          x=v0*t+0.5*a*t^2
%   periodic_disturbance:  x=v*t+A*sin(2*pi*f*t)
%   SI units are used internally.
validateattributes(t,{'numeric'},{'vector','real','finite','nonnegative'});
validateattributes(period,{'numeric'},{'scalar','positive','finite'});
t=t(:); mode=lower(string(m.mode));
switch mode
    case "constant_velocity"
        x=m.v*t;
        velocity=m.v+zeros(size(t));
    case "acceleration"
        x=m.v0*t+0.5*m.a*t.^2;
        velocity=m.v0+m.a*t;
    case "periodic_disturbance"
        omega=2*pi*m.f;
        x=m.v*t+m.A*sin(omega*t);
        velocity=m.v+m.A*omega*cos(omega*t);
    otherwise
        error('motion_model:UnknownMode','Unknown motion mode: %s.',mode);
end
theta=2*pi*x/period;
motion=struct('t',t,'mode',char(mode),'x',x,'velocity',velocity, ...
    'theta',theta,'period',period,'parameter',m);
end
