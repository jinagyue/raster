function files = plot_stage15_temperature(report,output_folder)
%PLOT_STAGE15_TEMPERATURE Export paper-ready temperature figures.
files=strings(0,1); p=report.parameter; summary=report.summary; rows=report.results;

fig=figure('Visible','off','Color','w','Position',[100 100 1200 520]);
tiledlayout(1,2,'TileSpacing','compact','Padding','compact');
nexttile; plot(summary.temperature_C,summary.shear_modulus_Pa/1e9,'o-','LineWidth',1.5);
grid on; xlabel('Temperature [degC]'); ylabel('Shear modulus [GPa]');
nexttile; plot(summary.temperature_C,100*summary.sensitivity_variation,'s-','LineWidth',1.5);
grid on; xlabel('Temperature [degC]'); ylabel('Sensitivity variation [%]');
files=[files;export_pair(fig,output_folder,'stage15_material_sensitivity')]; close(fig);

fig=figure('Visible','off','Color','w','Position',[100 100 1200 780]);
tiles=tiledlayout(2,1,'TileSpacing','compact','Padding','compact');
nexttile; semilogy(summary.temperature_C,max(summary.torque_rmse_off_Nm,eps),'o-','LineWidth',1.5); hold on;
semilogy(summary.temperature_C,max(summary.torque_rmse_on_Nm,eps),'s--','LineWidth',1.5);
grid on; ylabel('Torque RMSE [N*m]'); legend('Compensation OFF','Compensation ON','Location','best');
nexttile; semilogy(summary.temperature_C,max(summary.displacement_rmse_off_m*1e6,eps),'o-','LineWidth',1.5); hold on;
semilogy(summary.temperature_C,max(summary.displacement_rmse_on_m*1e6,eps),'s--','LineWidth',1.5);
grid on; ylabel('Displacement RMSE [um]'); legend('Compensation OFF','Compensation ON','Location','best');
xlabel(tiles,'Temperature [degC]');
files=[files;export_pair(fig,output_folder,'stage15_compensation_rmse')]; close(fig);

fig=figure('Visible','off','Color','w','Position',[100 100 1200 620]); hold on;
torques=unique(rows.torque_true_Nm,'stable'); colors=lines(numel(torques));
for k=1:numel(torques)
    q=rows(rows.torque_true_Nm==torques(k),:);
    plot(q.temperature_C,q.phase_error_rad,'o-','LineWidth',1.2,'Color',colors(k,:));
end
grid on; xlabel('Temperature [degC]'); ylabel('Temperature-induced phase error [rad]');
legend(compose('%g N*m',torques),'Location','eastoutside');
files=[files;export_pair(fig,output_folder,'stage15_phase_error')]; close(fig);
end

function paths=export_pair(fig,folder,name)
png_path=fullfile(folder,[name '.png']); pdf_path=fullfile(folder,[name '.pdf']);
exportgraphics(fig,png_path,'Resolution',300);
exportgraphics(fig,pdf_path,'ContentType','vector');
paths=string({png_path;pdf_path});
end
