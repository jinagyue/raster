function handles = plot_evaluation(report,figure_visible)
%PLOT_EVALUATION Generate compact paper figures for stage-6 experiments.
if nargin<2, figure_visible='on'; end
handles=struct(); handles.figure=figure('Color','w','Name','Stage 6 evaluation','Visible',figure_visible); tiledlayout(2,2,'TileSpacing','compact');
snr_t=[report.snr.traditional]; snr_i=[report.snr.improved]; phase_t=[report.phase.traditional]; phase_i=[report.phase.improved]; amp_t=[report.amplitude.traditional]; amp_i=[report.amplitude.improved];
nexttile; plot(report.t*1e3,report.recovery.estimate.x_true*1e3,'k--'); hold on; plot(report.t*1e3,report.recovery.estimate.x_direct*1e3); plot(report.t*1e3,report.recovery.estimate.x_est*1e3,'LineWidth',1.1); grid on; xlabel('Time [ms]'); ylabel('Displacement [mm]'); title('Displacement recovery'); legend('True','Direct atan2','Calibrated','Location','best');
nexttile; semilogy([report.snr.snr_db],[snr_t.rmse]./1e-6,'o-'); hold on; semilogy([report.snr.snr_db],[snr_i.rmse]./1e-6,'s-'); grid on; xlabel('SNR [dB]'); ylabel('RMSE [\mum]'); title('Noise robustness'); legend('Direct','Calibrated','Location','best');
nexttile; plot([report.phase.phase_error_deg],[phase_t.rmse]./1e-6,'o-'); hold on; plot([report.phase.phase_error_deg],[phase_i.rmse]./1e-6,'s-'); grid on; xlabel('Phase error magnitude [deg]'); ylabel('RMSE [\mum]'); title('Phase-error sensitivity'); legend('Direct','Calibrated','Location','best');
nexttile; plot([report.amplitude.amplitude_mismatch_pct],[amp_t.rmse]./1e-6,'o-'); hold on; plot([report.amplitude.amplitude_mismatch_pct],[amp_i.rmse]./1e-6,'s-'); grid on; xlabel('Amplitude mismatch [%]'); ylabel('RMSE [\mum]'); title('Amplitude-mismatch sensitivity'); legend('Direct','Calibrated','Location','best');
end
