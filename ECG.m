FS=500 %sample rate
D=127 %filter delay


ECG_data=load("ECG.txt");%import ECG data
ECG_data=ECG_data';%covert 
ECG_data=ECG_data(:);

T_length=length(ECG_data);%ECG time 
T=(1:T_length)/FS;
T=T';



%%%%%%%%%IIR filter %%%%%%%%%%%%%%%%%%%%%%%%%%%%
Fnorm=2/(FS/2);
df = designfilt('highpassiir',...
               'PassbandFrequency',Fnorm,...
               'FilterOrder',7,...
               'PassbandRipple',1,...
               'StopbandAttenuation',60);

ECG_Filter=filtfilt(df,ECG_data);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


subplot(5,2,1);                             %ECG original data
plot(T,ECG_data,'x-')
% hold on
xlabel('TIME/S')
ylabel('Amplitude')
title('ECG original data')
legend('ECG_data')

subplot(5,2,3);                             %ECG filter data
plot(T,ECG_Filter,'x-')
% hold on
xlabel('TIME/S')
ylabel('Amplitude')
title('ECG-peak -IIR filter-0 delay')
% hold off
legend('ECG_data')
% legend('ECG_data','R')
% axis([-inf,inf,2,3.5])


ECG_Filter=diff(ECG_Filter); %
ECG_Filter=ECG_Filter.^2 ;   %square


cycle=int16(T_length/50);%
i=int16(i);
ECG_Filter1=zeros;
ECG_Filter1(1)=ECG_Filter(1);
for i=0:(cycle-2)
    for j=1:50
        if j==1
        ECG_Filter1(50*i+j)=ECG_Filter(50*i+j);
        else
        ECG_Filter1(50*i+j)=ECG_Filter(50*i+j)+ECG_Filter1(50*i+j-1);
        end
    end

end

T_length=length(ECG_Filter1); 
T=(1:T_length)/FS;
T=T';


subplot(5,2,5); %PAN-TOMPKINS program
plot(T,ECG_Filter1,'x-')
xlabel('TIME/S')
ylabel('Amplitude')
title('PAN-TOMPKINS marks')
legend('ECG_Filter')


T_length=length(ECG_data);%ECG time 
T=(1:T_length)/FS;
T=T';


subplot(5,2,7);%make R wave 
plot(T,ECG_data,'x-')
xlabel('TIME/S')
ylabel('Amplitude')
hold on


ECG_Filter1=diff(ECG_Filter1);%
% ECG_Filter1=ECG_Filter1^2

T_length=length(ECG_Filter1); 
T=(1:T_length)/FS;
T=T';

ECG_Filter1(ECG_Filter1<0)=0;
% subplot(5,2,7);%make R wave 
% plot(T,ECG_Filter,'x-')
% xlabel('TIME/S')
% ylabel('Amplitude')
% hold on



cycle=int16(T_length/500);
i=int16(i);


THR0=max(ECG_Filter1(1:50));
THR1=0.5*THR0;
peaks_resume=0;
location_resume=0;

%%%%%%%%%%%%%%%%%%%%%%%
%%%THR0 for high ，THR1 for low 
%%%%%%%%%%%%%%%%%%%%%%
for i=0:(cycle-2)
    hold on
    if(THR0>max(ECG_Filter1(500*i+1:500*(i+1))))
        THR0=(max(ECG_Filter1(500*i+1:500*(i+1)))*1.25);
        THR1=0.4*max(ECG_Filter1(500*i+1:500*(i+1)));
    else
        THR0=0.7*max(ECG_Filter1(500*i+1:500*(i+1)));
        THR1=0.25*max(ECG_Filter1(500*i+1:500*(i+1)));
    end
    [peaks1,location1]=findpeaks(ECG_Filter1(500*i+1:500*(i+1)),T(500*i+1:500*(i+1)),'Annotate','extents');%find all peaks
    peaks1(peaks1<THR1)=0;
    peaks_length1=length(peaks1);
    for k=1:peaks_length1
        if(peaks1(k)~=0)
            if((location1(k)-location_resume(end))>0.05)%IF R-R time longer than 0.05s ，then it's non-repeat peaks
                peaks_resume(end+1)=peaks1(k);
                location_resume(end+1)=location1(k);
            end
        end
    end
    

    location_index1=int32(location_resume/0.002);
    location_index1(1)=1;
    plot(location_resume,ECG_data(location_index1),'rv','MarkerFaceColor','b')
    hold off
end

location_10s=location_resume(location_resume<10);
heart_beat=length(location_10s)*6;
text(0,0, 'heart beat is：'+string(heart_beat))

title('PAN-TOMPKINS')
hold off
legend('ECG_data','R')




%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%Resp%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%



Resp_data=load("Resp.txt");%import Resp data
Resp_data=Resp_data';%
Resp_data=Resp_data(:);

T1_length=length(Resp_data);
T1=(1:T1_length)/FS;
T1=T1';

subplot(5,2,2);%resp original data 
plot(T1,Resp_data,'x-')
% hold on
xlabel('TIME/S')
ylabel('Amplitude')
title('Resp original data')
legend('Resp_data')



Fnorm1=0.5/(FS/2);
Fnorm2=4/(FS/2);
df1 = designfilt('bandpassiir',...
               'PassbandFrequency1',Fnorm1,...
               'PassbandFrequency2',Fnorm2,...
               'FilterOrder',6,...
               'PassbandRipple',1);

Resp_Filter=filtfilt(df1,Resp_data);

subplot(5,2,4);%filter data
% plot(T1,Resp_Filter,'x-')
plot(T1,Resp_Filter,'x-')
xlabel('TIME/S')
ylabel('Amplitude')
title('Resp filter data(0.5hz-4hz)')
legend('Resp_Filter')



R_FFT=fft(Resp_Filter);
f=(0:T1_length-1)*FS/T1_length;
power = abs(R_FFT).^2/T1_length;


[Res_amp,Res_hz]=(max(power(T1_length/FS*0.75:T1_length/FS*4)))
Res_hz=Res_hz+T1_length/FS*0.75;
Res_hz=int16(Res_hz);
Res_hz=f(Res_hz);
Res_beat=Res_hz*60


subplot(5,2,6);%filter data 
% stem(f,abs(R_FFT).^2/T1_length);
plot(f,power,'x-')
text(Res_hz,Res_amp, 'resp is ：'+string(Res_beat))
% plot(f0,power0,'x-')
xlabel('hz')
ylabel('Amplitude')
title('RESP(H(jw))')
xlim([0.75 4]);
legend('Resp_H(jw)')



subplot(5,2,8);%resp peaks
plot(T1,Resp_Filter,'x-')
hold on
xlabel('TIME/S')
ylabel('Amplitude')
[peaks1,location1]=findpeaks(Resp_Filter,T1,'MinPeakProminence',0.02,'Annotate','extents');
location1_index=int32(location1/0.002);
plot(location1,Resp_Filter(location1_index),'gv','MarkerFaceColor','g')
title('Resp peaks')
hold off
legend('Resp_Filter','R')




