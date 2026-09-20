function p = patent_baseline_parameter()
%PATENT_BASELINE_PARAMETER Independent Stage-13 baseline configuration.
% This configuration does not alter the improved phase-estimation algorithm.
p.channel_order = {'ZERO','MAIN','PHASE_90','PHASE_180','PHASE_270'};
p.signal.amplitude = 1.0;
p.signal.offset = 1.0;
p.zero.phase = 0;
p.zero.width = pi/24;
p.zero.low = 0;
p.zero.high = 1;
p.zero.threshold = 0.5;
p.direction.phase_deadband = 1e-10;
p.direction.positive_label = 'clockwise';
p.direction.negative_label = 'counter_clockwise';
p.subdivision = [4 16 32];
end
