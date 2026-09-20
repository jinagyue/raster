%SHOW_CAD_ASSEMBLY Interactive solid-model visualization.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(genpath(root)); p=parameter();
p.grating.base_thickness=0.2e-6; p.grating.cad_grid_x=401; p.grating.cad_grid_y=81;
plot_cad_assembly(p.grating,p.grating.main_shift,p.grating.reference_shift,'on');
