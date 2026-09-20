function solid = grating_cad_solid(g,x_shift)
%GRATING_CAD_SOLID Build a closed CAD-like sinusoidal grating solid.
% The mesh contains top surface, bottom face and four side walls, so it can
% be exported or used in patch/triangulation workflows. Units are metres.
if nargin<2, x_shift=0; end
if ~isfield(g,'base_thickness'), g.base_thickness=0.20*g.height; end
if ~isfield(g,'cad_grid_x'), g.cad_grid_x=min(g.grid_x,401); end
if ~isfield(g,'cad_grid_y'), g.cad_grid_y=min(g.grid_y,81); end
nx=max(2,round(g.cad_grid_x)); ny=max(2,round(g.cad_grid_y));
x=linspace(0,g.number*g.period,nx)+x_shift; y=linspace(0,g.length,ny); [X,Y]=meshgrid(x,y);
Ztop=g.base_thickness+0.5*g.height*(1+cos(2*pi*(X-x_shift)/g.period)); Zbot=zeros(size(Ztop));
nv=numel(X); V=[X(:),Y(:),Ztop(:);X(:),Y(:),Zbot(:)]; F=zeros(2*(nx-1)*(ny-1)+2*(nx-1)+2*(ny-1),4); f=0;
id=@(r,c) (r-1)*nx+c;
for r=1:ny-1
    for c=1:nx-1
        a=id(r,c); b=id(r,c+1); d=id(r+1,c); e=id(r+1,c+1); f=f+1; F(f,:)=[a b e d]; f=f+1; F(f,:)=[nv+d nv+e nv+b nv+a];
    end
end
for c=1:nx-1, f=f+1; F(f,:)=[id(1,c) id(1,c+1) nv+id(1,c+1) nv+id(1,c)]; f=f+1; F(f,:)=[id(ny,c+1) id(ny,c) nv+id(ny,c) nv+id(ny,c+1)]; end
for r=1:ny-1, f=f+1; F(f,:)=[id(r+1,1) id(r,1) nv+id(r,1) nv+id(r+1,1)]; f=f+1; F(f,:)=[id(r,nx) id(r+1,nx) nv+id(r+1,nx) nv+id(r,nx)]; end
solid=struct('vertices',V,'faces',F,'top_surface',struct('X',X,'Y',Y,'Z',Ztop), ...
    'bottom_surface',struct('X',X,'Y',Y,'Z',Zbot),'period',g.period,'number',g.number, ...
    'length',g.length,'height',g.height,'base_thickness',g.base_thickness,'x_shift',x_shift, ...
    'bounds',[min(x) max(x) min(y) max(y) 0 max(Ztop(:))]);
solid.approx_volume=trapz(y,trapz(x,Ztop-Zbot,2));
end
