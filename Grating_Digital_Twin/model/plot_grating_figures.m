function handles = plot_grating_figures(main_model, reference_model, g, visualization)
%PLOT_GRATING_FIGURES Generate stage-1 paper figures.
if nargin < 4, visualization=struct('figure_visible','on','local_periods',5,'export',false,'export_folder',''); end
vis=visualization.figure_visible;
handles=struct();
handles.overview=figure('Name','Grating 3-D structure','Color','w','Visible',vis);
surf(main_model.X*1e3,main_model.Y*1e3,main_model.Z*1e6,'EdgeColor','none'); axis tight; axis vis3d; grid on;
xlabel('x [mm]'); ylabel('y [mm]'); zlabel('Height [\mum]');
title(sprintf('3-D sinusoidal grating (P = %.3g \\mum, N = %d, L = %.3g mm)',g.period*1e6,g.number,g.length*1e3));
colormap(parula); colorbar; view(35,28); camlight headlight; lighting gouraud;
handles.local=figure('Name','Local grating detail','Color','w','Visible',vis);
span=min(visualization.local_periods*g.period,g.number*g.period); mask=main_model.X(1,:)<=span;
surf(main_model.X(:,mask)*1e6,main_model.Y(:,mask)*1e3,main_model.Z(:,mask)*1e6,'EdgeColor','none'); grid on;
xlabel('x [\mum]'); ylabel('y [mm]'); zlabel('Height [\mum]');
title(sprintf('Local detail (%d periods)',round(span/g.period))); view(35,28); camlight headlight; lighting gouraud;
handles.relative=figure('Name','Relative displacement','Color','w','Visible',vis); hold on;
plot(main_model.X(1,:)*1e3,zeros(1,size(main_model.X,2)),'k-','LineWidth',5);
plot(reference_model.X(1,:)*1e3,0.12*ones(1,size(reference_model.X,2)),'Color',[0.85 0.2 0.15],'LineWidth',5);
delta=reference_model.x_shift-main_model.x_shift;
plot([main_model.x_shift reference_model.x_shift]*1e3,[0.06 0.06],'b->','LineWidth',1.5,'MarkerFaceColor','b');
xlabel('x [mm]'); ylabel('Grating layer'); yticks([0 0.12]); yticklabels({'Main','Reference'});
title(sprintf('Relative displacement \\Delta x = %.3g \\mum',delta*1e6)); grid on; ylim([-0.04 0.18]);
if visualization.export
    if ~isfolder(visualization.export_folder), mkdir(visualization.export_folder); end
    exportgraphics(handles.overview,fullfile(visualization.export_folder,'stage1_overview.png'),'Resolution',300);
    exportgraphics(handles.local,fullfile(visualization.export_folder,'stage1_local.png'),'Resolution',300);
    exportgraphics(handles.relative,fullfile(visualization.export_folder,'stage1_relative.png'),'Resolution',300);
end
end
