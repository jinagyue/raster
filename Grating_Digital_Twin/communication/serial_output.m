function info = serial_output(s,adc,t)
%SERIAL_OUTPUT Send four-channel ADC frames at a fixed sampling period.
% Frame: AA | A_H A_L | B_H B_L | C_H C_L | D_H D_L | CRC_H CRC_L.
if nargin<3||isempty(t), t=adc.t; end
if ~isfield(s,'send_rate'), s.send_rate=1/median(diff(t)); end
if ~isfield(s,'realtime'), s.realtime=true; end
if ~isfield(s,'baud_rate'), s.baud_rate=115200; end
if ~isfield(s,'mode'), s.mode='none'; end
if ~isfield(s,'file'), s.file='data/serial_stream.bin'; end
info=struct('mode',s.mode,'frames',0,'bytes',0,'file',s.file,'baud_rate',s.baud_rate,'sample_period',1/s.send_rate);
if strcmpi(s.mode,'none'), return; end
t=t(:); fs_in=1/median(diff(t)); step=max(1,round(fs_in/s.send_rate)); idx=1:step:size(adc.code,1); fid=-1; port=[];
if strcmpi(s.mode,'simulation')
    folder=fileparts(s.file); if ~isempty(folder)&&~isfolder(folder), mkdir(folder); end
    fid=fopen(s.file,'w'); assert(fid>0,'serial_output:File','Cannot open output file.');
elseif strcmpi(s.mode,'hardware')
    assert(exist('serialport','file')==2,'serial_output:API','serialport is unavailable in this MATLAB installation.');
    port=serialport(s.port,s.baud_rate,'Timeout',1);
else
    error('serial_output:Mode','mode must be none, simulation or hardware.');
end
wall=tic;
for k=1:numel(idx)
    i=idx(k); frame=encode_frame(adc.code(i,1:4));
    if fid>0, fwrite(fid,frame,'uint8'); else, write(port,frame,'uint8'); end
    info.frames=info.frames+1; info.bytes=info.bytes+numel(frame);
    if s.realtime, target=(k-1)/s.send_rate; pause(max(0,target-toc(wall))); end
end
if fid>0, fclose(fid); end
end

function frame=encode_frame(codes)
codes=uint16(reshape(codes,1,[])); assert(numel(codes)==4,'serial_output:Channels','Exactly four ADC channels are required.');
payload=zeros(1,8,'uint8');
for k=1:4
    payload(2*k-1)=uint8(bitshift(codes(k),-8)); payload(2*k)=uint8(bitand(codes(k),uint16(255)));
end
body=uint8([hex2dec('AA'),payload]); crc=crc16_ccitt(body);
frame=uint8([body,uint8(bitshift(crc,-8)),uint8(bitand(crc,uint16(255))) ]).';
end

function crc=crc16_ccitt(bytes)
b=uint8(bytes(:)); crc=uint16(hex2dec('FFFF'));
for i=1:numel(b)
    crc=bitxor(crc,bitshift(uint16(b(i)),8));
    for j=1:8
        if bitand(crc,uint16(hex2dec('8000')))
            crc=bitxor(bitshift(crc,1),uint16(hex2dec('1021')));
        else
            crc=bitshift(crc,1);
        end
    end
end
end
