import matplotlib.pyplot as plt
import pandas as pd
import pygmt as gmt
import re
import matplotlib.ticker as ticker

eq_table=pd.read_excel("./20180206_Hualien Earthquake/FreeField/Index/20180206_Hualien Earthquake.xlsx")
eq_table["Lat_final"]=eq_table["Lat"]+(eq_table["Lat.min"]/60) #60進位轉10進位
eq_table["Lon_final"]=eq_table["Lon"]+(eq_table["Lon.min"]/60) 

intensity_table=pd.read_excel("./intensity_result.xlsx")
intensity_table.dropna(how="all",inplace=True) #drop index 423 (壞掉的資料)
intensity_table.reset_index(drop=True, inplace=True)

pattern=r"\w+"
for index in range(len(intensity_table)): 
    # print(index)
    sta_name=re.findall(pattern,intensity_table["Station Code"][index])[0]
    intensity_table.loc[index,["Station Code"]]=sta_name
    if intensity_table["intensity"][index]=="5弱":
        intensity_table.loc[index,["intensity"]]=5.0
    elif intensity_table["intensity"][index]=="5強":
        intensity_table.loc[index,["intensity"]]=5.5
    elif intensity_table["intensity"][index]=="6弱":
        intensity_table.loc[index,["intensity"]]=6.0
    elif intensity_table["intensity"][index]=="6強":
        intensity_table.loc[index,["intensity"]]=6.5

station_table=pd.read_csv("./20180206_Hualien Earthquake/FreeField/Index/Station.log",\
                    sep=r"\s+",usecols=[0,1,2],names=["Station Code","Lon","Lat"])

merge_table=pd.merge(intensity_table,station_table,on=["Station Code"],how="left")
merge_table["intensity"]=pd.to_numeric(merge_table["intensity"])

velocity_intensity_table=merge_table.dropna(subset=["PGV (cm/sec)"])
velocity_intensity_table.reset_index(drop=True, inplace=True)

velocity_intensity_table[velocity_intensity_table["intensity"]>=6.5]["Station Code"]
velocity_intensity_table[velocity_intensity_table["intensity"]==7]["Station Code"]

fig, ax = plt.subplots() 
ax.hist(merge_table["intensity"],bins=7)
ax.set_xlabel("intensity")
ax.set_ylabel("number of stations")
ax.set_title("intensity & station histogram")

tick_spacing=1
fig, ax = plt.subplots() 
ax.hist(velocity_intensity_table["intensity"],bins=10)
ax.set_xlabel("intensity")
ax.set_ylabel("number of stations")
ax.set_title("intensity & station histogram (calculate velocity)")
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

TWgrid = gmt.datasets.load_earth_relief(resolution="15s",\
    region=[119.5, 122.5, 21.5, 25.5])

df_list=[merge_table,velocity_intensity_table]
Title=["Intensity from station","Intensity from station (calculate velocity)"]
for df,title in zip(df_list,Title):
    fig = gmt.Figure()
    fig.grdimage(grid=TWgrid,projection="M15c",cmap="gray")
    fig.coast(shorelines="1p,black",water="white")

    fig.basemap(frame=["a",f'+t"{title}"'])
    gmt.makecpt(cmap="panoply", series=[min(df["intensity"]),max(df["intensity"])])
    fig.plot(x=eq_table["Lon_final"],y=eq_table["Lat_final"],style="a0.75c",pen="black",color="red")
    fig.plot(x=df["Lon"],y=df["Lat"],color=df["intensity"],cmap=True,style="c0.3c",)
    fig.colorbar(frame='af+l"intensity"')
    fig.show()


# fig.text(text="50km", x=120, y=21.9)



fig = gmt.Figure()
fig.grdimage(grid=TWgrid,projection="M15c",cmap="geo")
fig.coast(shorelines="1p,black")

fig.basemap(frame=["a",f'+t"2018 0206 Hualien Earthquake"'])
fig.plot(x=eq_table["Lon_final"],y=eq_table["Lat_final"],style="a0.75c",pen="black",color="red")
fig.plot(x=merge_table["Lon"],y=merge_table["Lat"],color="lightgray",pen="black",style="t0.4c",)
fig.colorbar(frame='af+l"elevation"')
fig.show()