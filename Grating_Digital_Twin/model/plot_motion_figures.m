function handle = plot_motion_figures(motion, figure_visible)
%PLOT_MOTION_FIGURES Plot displacement, velocity and phase for publication.
if nargin<2, figure_visible='on'; end
handle=figure('Name','Stage 2 motion model','Color','w','Visible',figure_visible);
tiledlayout(3,1,'TileSpacing','compact','Padding','compact');
nexttile; plot(motion.t*1e3,motion.x*1e6,'LineWidth',1.25); grid on;
xlabel('Time [ms]'); ylabel('Displacement x [\mum]'); title(sprintf('Relative displacement (%s)',strrep(motion.mode,'_',' ')));
nexttile; plot(motion.t*1e3,motion.velocity*1e3,'LineWidth',1.25); grid on;
xlabel('Time [ms]'); ylabel('Velocity [mm/s]'); title('Analytical velocity');
nexttile; plot(motion.t*1e3,motion.theta,'LineWidth',1.25); grid on;
xlabel('Time [ms]'); ylabel('Phase \theta [rad]'); title('\theta(t)=2\pi x(t)/P');
end
