function report = stage8_acceptance()
%STAGE8_ACCEPTANCE Verify frame format, CRC, rate and round-trip recovery.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(fullfile(root,'config'),fullfile(root,'communication'));
n=20; adc=struct('code',uint16(repmat([0 1 2048 4095],n,1)),'t',(0:n-1).'/1000);
s=struct('mode','simulation','file',fullfile(root,'data','stage8_acceptance.bin'),'send_rate',1000,'baud_rate',115200,'realtime',false);
info=serial_output(s,adc,adc.t); fid=fopen(s.file,'r'); bytes=fread(fid,'*uint8'); fclose(fid); frame_count=floor(numel(bytes)/11); decoded=zeros(frame_count,4,'uint16'); valid=false(frame_count,1);
for k=1:frame_count, [decoded(k,:),valid(k)]=decode_frame(bytes((k-1)*11+(1:11))); end
rate_error=abs(info.sample_period-1/s.send_rate); data_ok=isequal(decoded,adc.code(1:frame_count,:));
report=struct('frame_length',11,'frame_count',frame_count,'bytes',numel(bytes),'sample_period_s',info.sample_period,'rate_error_s',rate_error,'valid_crc_fraction',mean(valid),'pass_format',all(mod(numel(bytes),11)==0)&&all(bytes(1:11:end)==hex2dec('AA')),'pass_crc',all(valid),'pass_rate',rate_error<1e-12,'pass_recovery',data_ok);
report.pass=report.pass_format&&report.pass_crc&&report.pass_rate&&report.pass_recovery; assert(report.pass,'stage8_acceptance:Failed','Stage 8 serial-output acceptance failed.');
end

function [codes,valid]=decode_frame(frame)
frame=uint8(frame(:)); codes=zeros(1,4,'uint16'); valid=false;
if numel(frame)~=11||frame(1)~=hex2dec('AA'), return; end
expected=uint16(frame(10))*256+uint16(frame(11)); if crc16_ccitt(frame(1:9))~=expected, return; end
for k=1:4, codes(k)=bitshift(uint16(frame(2*k)),8)+uint16(frame(2*k+1)); end
valid=true;
end

function crc=crc16_ccitt(bytes)
b=uint8(bytes(:)); crc=uint16(hex2dec('FFFF'));
for i=1:numel(b)
    crc=bitxor(crc,bitshift(uint16(b(i)),8));
    for j=1:8
        if bitand(crc,uint16(hex2dec('8000'))), crc=bitxor(bitshift(crc,1),uint16(hex2dec('1021'))); else, crc=bitshift(crc,1); end
    end
end
end
