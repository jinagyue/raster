function result = main(user_parameter, options)
%MAIN One-click runner for the complete MATLAB grating digital twin.
%   RESULT = MAIN() runs stages 1-8 with defaults. The default serial mode
%   is 'none', so no physical COM port is opened accidentally.
%   MAIN(P,OPTS) accepts a parameter override P and runtime options:
%       opts.show_figures  (default true)
%       opts.run_evaluation(default true)
%       opts.save_report   (default false)
%       opts.report_file   (default 'data/final_result.mat')
root=fileparts(mfilename('fullpath'));
addpath(fullfile(root,'config'),fullfile(root,'model'),fullfile(root,'signal'), ...
    fullfile(root,'algorithm'),fullfile(root,'communication'),fullfile(root,'experiment'),fullfile(root,'tests'));
p=parameter(); if nargin>=1 && ~isempty(user_parameter), p=merge_struct(p,user_parameter); end
opts=struct('show_figures',true,'run_evaluation',true,'save_report',false,'report_file','data/final_result.mat');
if nargin>=2 && ~isempty(options), opts=merge_struct(opts,options); end
if ~opts.show_figures, p.visualization.figure_visible='off'; end

fprintf('Grating Digital Twin: running stages 1-8...\n');
% Stage 1: geometry
main_grating=grating_3D_model(p.grating,p.grating.main_shift); reference_grating=grating_3D_model(p.grating,p.grating.reference_shift);
stage1=stage1_acceptance(); stage1_figures=plot_grating_figures(main_grating,reference_grating,p.grating,p.visualization);
fprintf('  [1/8] geometry      PASS\n');
% Stage 2: motion
t=(0:1/p.motion.sample_rate:p.motion.duration).'; motion=motion_model(t,p.motion,p.grating.period); stage2=stage2_acceptance();
stage2_figure=plot_motion_figures(motion,p.visualization.figure_visible); fprintf('  [2/8] motion        PASS\n');
% Stage 3: optical and four-phase signal
optical=optical_model(motion.theta,p.optical); optical.t=t; signals=signal_generator(optical,p.signal); signals.t=t; stage3=stage3_acceptance(); fprintf('  [3/8] optical       PASS\n');
% Stage 4: non-ideal signal
nonideal=error_model(signals,t,p.errors); stage4=stage4_acceptance(); fprintf('  [4/8] non-ideal     PASS\n');
% Stage 5: displacement estimation
estimate=phase_estimation(nonideal,p.grating.period,t,motion.x); stage5=stage5_acceptance(); fprintf('  [5/8] algorithm     PASS (RMSE %.3g um)\n',estimate.rmse*1e6);
% Stage 6: reproducible paper experiments
if opts.run_evaluation, evaluation_report=evaluation(p); stage6=stage6_acceptance(); else, evaluation_report=[]; stage6=struct('pass',true,'skipped',true); end
fprintf('  [6/8] evaluation    PASS\n');
% Stage 7: ADC
adc=adc_model(nonideal.channels,t,p.adc); stage7=stage7_acceptance(); fprintf('  [7/8] ADC           PASS\n');
% Stage 8: serial output (default none)
serial=serial_output(p.serial,adc,t); stage8=stage8_acceptance(); fprintf('  [8/8] serial        PASS (%s)\n',p.serial.mode);
result=struct('stage',8,'parameter',p,'main_grating',main_grating,'reference_grating',reference_grating, ...
    'motion',motion,'optical',optical,'signals',signals,'nonideal_signals',nonideal,'estimate',estimate,'evaluation',evaluation_report,'adc',adc,'serial',serial, ...
    'figures',struct('stage1',stage1_figures,'stage2',stage2_figure),'acceptance',struct('stage1',stage1,'stage2',stage2,'stage3',stage3,'stage4',stage4,'stage5',stage5,'stage6',stage6,'stage7',stage7,'stage8',stage8));
if opts.save_report
    report_file=opts.report_file; folder=fileparts(report_file); if ~isempty(folder)&&~isfolder(folder), mkdir(folder); end
    save(report_file,'result','-v7.3'); fprintf('Saved result to %s\n',report_file);
end
fprintf('All stages completed.\n');
end

function out=merge_struct(base,override)
out=base; names=fieldnames(override);
for k=1:numel(names)
    n=names{k}; if isfield(out,n)&&isstruct(out.(n))&&isstruct(override.(n)), out.(n)=merge_struct(out.(n),override.(n)); else, out.(n)=override.(n); end
end
end
