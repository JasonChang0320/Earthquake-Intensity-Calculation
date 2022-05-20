import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from scipy import signal
import matplotlib
matplotlib.use('Agg') #不顯示圖
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta'] #導入中文字
#======function============================================
def PGA_intensity(pga):
    result="需算PGV"
    if pga<0.8:
        result=0
    elif 0.8<=pga<2.5:
        result=1
    elif 2.5<=pga<8.0:
        result=2
    elif 8.0<=pga<25:
        result=3
    elif 25<= pga <80:
        result=4
    # if pga>80:
    #     print(result)  
    # else:  
    #     print(f"震度:{result}級")
    return result

def acc2vel(data_info,acc_data):
    vel_df=pd.DataFrame(columns=["Time","Vertical","NS","EW"])
    dt=1/data_info["SampleRate(Hz)"][1] #一筆資料佔幾秒
    vel_df["Time"]=np.array(acc_data["Time"][1:])
    for component in ["Vertical","NS","EW"]:
        v1=np.array(acc_data[component][0:-1])
        v2=np.array(acc_data[component][1:])
        velocity=np.cumsum((v1+v2)*dt/2)
    # vel_list.append(velocity)
        vel_df[component]=velocity
    return vel_df
def PGV_intensity(pgv):
    if pgv<0.2:
        result=0
    elif 0.2<=pgv<0.7:
        result=1
    elif 0.7<=pgv<1.9:
        result=2 
    elif 1.9<=pgv<5.7:
        result=3
    elif 5.7<= pgv <15:
        result=4
    elif 15<= pgv <30:
        result="5弱"
    elif 30<= pgv <50:
        result="5強"
    elif 50<= pgv<80:
        result="6弱"
    elif 80<= pgv <140:
        result="6強"
    elif pgv>=140:
        result=7
    # print(f"震度:{result}")
    return result
#===========================================================
#read data
dir_path="./20180206_Hualien Earthquake/FreeField/Record/"
dir_data=os.listdir(dir_path)
waveform_data_list=[]

pattern=r".*\.txt"
for data in dir_data:
    target=re.findall(pattern,data)
    if target: # list 為空值判斷會回傳 False, 反之
        # print(target)
        waveform_data_list.append(target[0])
#=============read data
error_list=[]

for index in range(len(waveform_data_list)):
    print(index,"/",len(waveform_data_list))
    acc_data=pd.read_csv(dir_path+waveform_data_list[index],engine='python',sep=r"\s+",header=None,skiprows=11)
    # print(waveform_data_list[index])
    acc_data.columns=["Time","Vertical","NS","EW"]
    try:
        acc_data["Time"]=pd.to_numeric(acc_data["Time"])
        acc_data["Vertical"]=pd.to_numeric(acc_data["Vertical"])
        acc_data["NS"]=pd.to_numeric(acc_data["NS"])
        acc_data["EW"]=pd.to_numeric(acc_data["EW"])
        data_info=pd.read_csv(dir_path+waveform_data_list[index],engine="python",sep=r"#\D+:",header=None,nrows=11)
        info_columns=["StationCode","InstrumentKind","StartTime","RecordLength(sec)","SampleRate(Hz)",\
                        "AmplitudeUnit","AmplitudeMAX. U","AmplitudeMAX. N","AmplitudeMAX. E",'DataSequence',"Data"]
        data_info.dropna(axis=1,inplace=True)
        data_info=data_info.T
        data_info.columns=info_columns
        data_info["SampleRate(Hz)"]=pd.to_numeric(data_info["SampleRate(Hz)"]) #type int64
        data_info["RecordLength(sec)"]=pd.to_numeric(data_info["RecordLength(sec)"]) #type float64
    except:
        error_list.append([index,waveform_data_list[index],data_info['StationCode'][1]])
        continue

    #=============plot waveform, check data is ok
    # fig,ax=plt.subplots(3,1,figsize=(10,7))
    # ax[0].plot(acc_data["Time"],acc_data["Vertical"])
    # ax[1].plot(acc_data["Time"],acc_data["NS"])
    # ax[2].plot(acc_data["Time"],acc_data["EW"])
    # ax[0].axes.xaxis.set_ticklabels([])
    # ax[1].axes.xaxis.set_ticklabels([])
    # station_code=data_info['StationCode'][1]
    # start_time=data_info["StartTime"][1]
    # record_len=data_info["RecordLength(sec)"][1]
    # ax[0].set_title(f"Station Code:{station_code}, Start Time:{start_time}, Record_length (sec):{record_len}")
    # fig.show()

    #=======filter
    sample_rate=200 #取樣頻率
    order=4 #4階
    cutoff_freq=10  #(Hz)截至頻率
    Wn=2*cutoff_freq/sample_rate #Wn 是正規化的截止頻率，介於 0 和 1 之間
    #
    b, a = signal.butter(order, Wn, 'lowpass')  #scipy 的 butterworth 低通濾波器 
    acc_data["Vertical_filtered"] = signal.filtfilt(b, a, acc_data["Vertical"])
    acc_data["NS_filtered"] = signal.filtfilt(b, a, acc_data["NS"])
    acc_data["EW_filtered"] = signal.filtfilt(b, a, acc_data["EW"])

    #====== 3向量合成震波 計算PGA

    acc_data["Composition"]=np.sqrt(acc_data["Vertical_filtered"]**2+acc_data["NS_filtered"]**2+acc_data["EW_filtered"]**2)
    pga=np.max(acc_data["Composition"])
    #計算震度
    intensity=PGA_intensity(pga)
    #=============plot filtered waveform compare
    fig,ax=plt.subplots(3,2,figsize=(10,7))
    ax[0,0].plot(acc_data["Time"],acc_data["Vertical"])
    ax[1,0].plot(acc_data["Time"],acc_data["NS"])
    ax[2,0].plot(acc_data["Time"],acc_data["EW"])
    ax[0,0].axes.xaxis.set_ticklabels([])
    ax[1,0].axes.xaxis.set_ticklabels([])
    station_code=data_info['StationCode'][1]
    ax[0,0].set_title(f"Before filtered, Station Code:{station_code}")
    ax[1,0].set_ylabel("Acceleration (gal)")
    ax[2,0].set_xlabel("time (sec)")

    ax[0,1].plot(acc_data["Time"],acc_data["Vertical_filtered"])
    ax[1,1].plot(acc_data["Time"],acc_data["NS_filtered"])
    ax[2,1].plot(acc_data["Time"],acc_data["EW_filtered"])
    ax[0,1].axes.xaxis.set_ticklabels([])
    ax[1,1].axes.xaxis.set_ticklabels([])
    station_code=data_info['StationCode'][1]
    start_time=data_info["StartTime"][1]
    record_len=data_info["RecordLength(sec)"][1]
    ax[0,1].set_title(f"After filter: order={order}, cut off={cutoff_freq} (Hz)")
    ax[2,1].set_xlabel("time (sec)")
    ax[0,1].text(np.max(acc_data["Time"])-0.2*np.max(acc_data["Time"]),\
                np.max(acc_data["Vertical_filtered"])-0.2*np.max(acc_data["Vertical_filtered"]),\
                f"震度:{intensity}")
    #====make dir
    path_save = f"./Result/{data_info['StationCode'][1]}"
    if not os.path.isdir(path_save):
        os.makedirs(path_save)

    #========save data
    acc_data.to_csv(path_save+f"/{data_info['StationCode'][1]}_acc.csv",index = False)
    fig.savefig(path_save+f"/{data_info['StationCode'][1]}_acc.png")

    if index==0:
        result_table=pd.DataFrame(columns=["Station Code","file_name","intensity","PGA (gal)","PGV (cm/sec)"],index=range(len(waveform_data_list)))
    #acc to velocity
    if type(intensity)==str: #intensity="需算PGV"
        velocity_data=acc2vel(data_info,acc_data)
        #filter
        sample_rate=data_info["SampleRate(Hz)"] #取樣頻率
        order=4 #4階
        cutoff_freq=0.075  #(Hz)截至頻率
        Wn=2*cutoff_freq/sample_rate #Wn 是正規化的截止頻率，介於 0 和 1 之間
        b, a = signal.butter(order, Wn, 'highpass')  #scipy 的 butterworth 高通濾波器 
        velocity_data["Vertical_filtered"] = signal.filtfilt(b, a, velocity_data["Vertical"])
        velocity_data["NS_filtered"] = signal.filtfilt(b, a, velocity_data["NS"])
        velocity_data["EW_filtered"] = signal.filtfilt(b, a, velocity_data["EW"])

        #3向量合成震波 計算PGV 震度
        velocity_data["Composition"]=np.sqrt(velocity_data["Vertical_filtered"]**2+velocity_data["NS_filtered"]**2+velocity_data["EW_filtered"]**2)
        pgv=np.max(velocity_data["Composition"])
        # print("PGV:",pgv)
        intensity=PGV_intensity(pgv)
        #plot filtered waveform compare
        fig,ax=plt.subplots(3,2,figsize=(10,7))
        ax[0,0].plot(velocity_data["Time"],velocity_data["Vertical"])
        ax[1,0].plot(velocity_data["Time"],velocity_data["NS"])
        ax[2,0].plot(velocity_data["Time"],velocity_data["EW"])
        ax[0,0].axes.xaxis.set_ticklabels([])
        ax[1,0].axes.xaxis.set_ticklabels([])
        station_code=data_info['StationCode'][1]
        ax[0,0].set_title(f"Before filtered, Station Code:{station_code}")
        ax[1,0].set_ylabel("Velocity (cm/s)")
        ax[2,0].set_xlabel("time (sec)")

        ax[0,1].plot(velocity_data["Time"],velocity_data["Vertical_filtered"])
        ax[1,1].plot(velocity_data["Time"],velocity_data["NS_filtered"])
        ax[2,1].plot(velocity_data["Time"],velocity_data["EW_filtered"])
        ax[0,1].axes.xaxis.set_ticklabels([])
        ax[1,1].axes.xaxis.set_ticklabels([])
        station_code=data_info['StationCode'][1]
        start_time=data_info["StartTime"][1]
        record_len=data_info["RecordLength(sec)"][1]
        ax[0,1].set_title(f"After filter: order={order}, cut off={cutoff_freq} (Hz)")
        ax[2,1].set_xlabel("time (sec)")
        ax[0,1].text(np.max(velocity_data["Time"])-0.2*np.max(velocity_data["Time"]),\
                    np.max(velocity_data["Vertical_filtered"])-0.2*np.max(velocity_data["Vertical_filtered"]),\
                    f"震度:{intensity}")
        #save data
        velocity_data.to_csv(path_save+f"/{data_info['StationCode'][1]}_vel.csv",index = False)
        fig.savefig(path_save+f"/{data_info['StationCode'][1]}_vel.png")

        result_table["PGV (cm/sec)"][index]=pgv

    result_table["PGA (gal)"][index]=pga
    result_table["Station Code"][index]=data_info['StationCode'][1]
    result_table["file_name"][index]=waveform_data_list[index]
    result_table["intensity"][index]=intensity
    plt.cla()
    plt.close("all")
    # print("====================")
result_table.to_excel("./intensity_result.xlsx",index=False)

error_table=pd.DataFrame(error_list,columns=["index","file_name","Station Code"])

error_table.to_excel("./error_filename.xlsx",index=False)


        

