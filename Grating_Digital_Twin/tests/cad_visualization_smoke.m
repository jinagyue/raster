function report = cad_visualization_smoke()
%CAD_VISUALIZATION_SMOKE Check closed mesh and relative-shift geometry.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'model')); p=parameter();
g=p.grating; g.base_thickness=0.2e-6; g.cad_grid_x=101; g.cad_grid_y=21; a=grating_cad_solid(g,0); b=grating_cad_solid(g,3e-6);
report=struct('vertices_main',size(a.vertices,1),'faces_main',size(a.faces,1),'closed_mesh',all(a.faces(:)>=1)&&all(a.faces(:)<=size(a.vertices,1)),'shift_error_m',abs((b.x_shift-a.x_shift)-3e-6)); report.pass=report.closed_mesh&&report.shift_error_m<1e-15; assert(report.pass,'cad_visualization_smoke:Failed','CAD mesh smoke test failed.');
end
