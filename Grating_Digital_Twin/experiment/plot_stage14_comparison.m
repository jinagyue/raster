function files = plot_stage14_comparison(report,output_folder)
%PLOT_STAGE14_COMPARISON Export paper-ready Stage-14 comparison figures.
methods=report.methods; cases=string(report.case_definitions.name);
colors=lines(numel(methods)); files=strings(0,1);

fig=figure('Visible','off','Color','w','Position',[100 100 1500 620]);
rmse=nan(numel(cases),numel(methods));
for i=1:numel(cases), for j=1:numel(methods)
    q=report.results.case_name==cases(i)&report.results.method==methods(j);
    rmse(i,j)=report.results.rmse_m(q)*1e6;
end, end
bar(max(rmse,1e-6),'grouped'); set(gca,'YScale','log','FontName','Times New Roman','FontSize',10);
grid on; ylabel('RMSE [um]'); xlabel('Predefined test case');
xticks(1:numel(cases)); xticklabels(cases); xtickangle(35); legend(methods,'Location','eastoutside');
set(gca,'TickLabelInterpreter','none');
files=[files;export_pair(fig,output_folder,'stage14_rmse_all_cases')]; close(fig);

selected=[find(cases=="ideal",1),find(cases=="snr_10dB",1),find(cases=="torque_neg8Nm",1)];
fig=figure('Visible','off','Color','w','Position',[100 100 1500 820]);
tiles=tiledlayout(3,1,'TileSpacing','compact','Padding','compact');
fields={'baseline_4','baseline_16','baseline_32','traditional','improved'};
for s=1:numel(selected)
    c=selected(s); nexttile; hold on;
    for m=1:numel(methods)
        err=report.cases(c).errors.(fields{m})*1e6;
        plot(report.cases(c).torque,err,'LineWidth',1,'Color',colors(m,:));
    end
    grid on; ylabel('Error [um]'); title(cases(c),'FontWeight','normal','Interpreter','none');
end
xlabel(tiles,'Torque [N*m]'); legend(methods,'Location','eastoutside');
files=[files;export_pair(fig,output_folder,'stage14_error_curves')]; close(fig);

score=nan(numel(methods),numel(cases));
for i=1:numel(cases), for j=1:numel(methods)
    q=report.results.case_name==cases(i)&report.results.method==methods(j);
    score(j,i)=report.results.robustness_score(q);
end, end
fig=figure('Visible','off','Color','w','Position',[100 100 1500 500]);
h=imagesc(score,[0 1]); h.AlphaData=~isnan(score); colormap(parula); colorbar; axis tight;
set(gca,'Color',[0.82 0.82 0.82]);
set(gca,'YTick',1:numel(methods),'YTickLabel',methods,'XTick',1:numel(cases), ...
    'XTickLabel',cases,'FontName','Times New Roman','FontSize',10);
set(gca,'TickLabelInterpreter','none');
xtickangle(35); xlabel('Predefined test case'); ylabel('Method');
files=[files;export_pair(fig,output_folder,'stage14_robustness_score')]; close(fig);
end

function paths=export_pair(fig,folder,name)
png_path=fullfile(folder,[name '.png']); pdf_path=fullfile(folder,[name '.pdf']);
exportgraphics(fig,png_path,'Resolution',300);
exportgraphics(fig,pdf_path,'ContentType','vector');
paths=string({png_path;pdf_path});
end
