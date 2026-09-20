function model = grating_3D_model(g, x_shift)
%GRATING_3D_MODEL Build a sinusoidal 3-D grating using meshgrid/surf data.
%   MODEL = GRATING_3D_MODEL(G, X_SHIFT) returns X/Y/Z matrices that can
%   be passed directly to surf. The surface is
%   z(x)=H/2*[1+cos(2*pi*(x-X_SHIFT)/P)].
if nargin < 2, x_shift = 0; end
validateattributes(g.period,{'numeric'},{'scalar','positive'});
validateattributes(g.number,{'numeric'},{'scalar','integer','positive'});
validateattributes(g.length,{'numeric'},{'scalar','positive'});
validateattributes(g.height,{'numeric'},{'scalar','nonnegative'});
validateattributes(g.grid_x,{'numeric'},{'scalar','integer','>=',2});
validateattributes(g.grid_y,{'numeric'},{'scalar','integer','>=',2});
x = linspace(0,g.number*g.period,g.grid_x) + x_shift;
y = linspace(0,g.length,g.grid_y);
[X,Y] = meshgrid(x,y);
Z = 0.5*g.height*(1+cos(2*pi*(X-x_shift)/g.period));
model = struct('X',X,'Y',Y,'Z',Z,'period',g.period,'number',g.number, ...
    'length',g.length,'height',g.height,'x_shift',x_shift, ...
    'bounds',[min(x) max(x) min(y) max(y) min(Z(:)) max(Z(:))]);
end
