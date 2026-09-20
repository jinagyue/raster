function handles = plot_cad_assembly(g,main_shift,reference_shift,figure_visible)
%PLOT_CAD_ASSEMBLY Display two closed grating solids and a mounting plate.
% The reference-grating slider provides interactive relative displacement.
if nargin<2, main_shift=0; end; if nargin<3, reference_shift=0; end; if nargin<4, figure_visible='on'; end
main=grating_cad_solid(g,main_shift); reference=grating_cad_solid(g,reference_shift);
handles=struct(); handles.figure=figure('Name','Interactive grating CAD assembly','Color','w','Visible',figure_visible);
ax=axes('Parent',handles.figure,'Position',[0.08 0.16 0.86 0.78]); hold(ax,'on');
handles.main=patch(ax,'Vertices',main.vertices*diag([1 1 1]),'Faces',main.faces,'FaceColor',[0.12 0.40 0.78],'EdgeColor','none','FaceAlpha',0.92);
handles.reference=patch(ax,'Vertices',reference.vertices,'Faces',reference.faces,'FaceColor',[0.90 0.28 0.16],'EdgeColor','none','FaceAlpha',0.72);
plot_mounting_plate(ax,g);
axis(ax,'equal'); axis(ax,'tight'); grid(ax,'on'); view(ax,35,25); rotate3d(handles.figure,'on'); camlight(ax,'headlight'); lighting(ax,'gouraud');
xlabel(ax,'x [mm]'); ylabel(ax,'y [mm]'); zlabel(ax,'z [\mum]'); title(ax,'Main/reference grating CAD-like solid assembly');
uicontrol(handles.figure,'Style','text','Units','normalized','Position',[0.08 0.075 0.18 0.035],'String','Reference shift [\mum]','BackgroundColor','w');
slider=uicontrol(handles.figure,'Style','slider','Units','normalized','Position',[0.27 0.08 0.48 0.03],'Min',-2*g.period*1e6,'Max',2*g.period*1e6,'Value',reference_shift*1e6,'Callback',@move_reference);
handles.slider=slider; handles.shift_text=uicontrol(handles.figure,'Style','text','Units','normalized','Position',[0.77 0.075 0.15 0.035],'String',sprintf('%.3g \mum',reference_shift*1e6),'BackgroundColor','w');
    function move_reference(src,~)
        shift=get(src,'Value')*1e-6; ref=grating_cad_solid(g,shift); set(handles.reference,'Vertices',ref.vertices); set(handles.shift_text,'String',sprintf('%.3g \\mum',shift*1e6)); drawnow;
    end
end

function plot_mounting_plate(ax,g)
% Transparent base plate gives the assembly a mechanical reference.
margin=max(0.15*g.length,5*g.period); x0=-margin; x1=g.number*g.period+margin; y0=-0.08*g.length; y1=1.08*g.length; z0=-0.12*g.height; z1=0;
V=[x0 y0 z0;x1 y0 z0;x1 y1 z0;x0 y1 z0;x0 y0 z1;x1 y0 z1;x1 y1 z1;x0 y1 z1]; F=[1 2 3 4;5 8 7 6;1 5 6 2;2 6 7 3;3 7 8 4;4 8 5 1];
patch(ax,'Vertices',V,'Faces',F,'FaceColor',[0.45 0.45 0.48],'FaceAlpha',0.25,'EdgeColor',[0.25 0.25 0.25]);
end
