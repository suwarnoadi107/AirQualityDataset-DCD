import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import statistics
import streamlit as st

from babel.numbers import format_currency
from shapely.geometry import Point
sns.set(style='dark')

# Upload Data
dire = "Air-quality-dataset"
files = os.listdir(dire)
all_data = []
for file in files:
    data = pd.read_csv(f'Air-quality-dataset/{file}')
    data2 = pd.DataFrame(data)
    all_data.append(data2)

# Joining All Data
i = 1
while i < len(all_data):
    if (i == 1):
        air_qi = pd.concat([all_data[0], all_data[1]], axis=0)
    else:
        air_qi = pd.concat([air_qi, all_data[i]], axis=0)
    i += 1

# Change Format of Datetime
air_qi['date'] = pd.to_datetime(air_qi[['year','month','day']])
air_qi['date_h'] = pd.to_datetime(air_qi[['year','month','day','hour']])
air_qi = air_qi.iloc[:,1:]

# Change the Position of Features
new_col = ['date_h', 'PM2.5', 'PM10', 'SO2', 
           'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM', 
           'station', 'date', 'year', 'month', 'day', 'hour']
air_qi = air_qi.reindex(columns=new_col)

# Change the name of columns
new_col = ['date_h', 'PM2.5', 'PM10', 'SO2', 
           'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM', 
           'station', 'date', 'year', 'month', 'day', 'hour']
air_qi.columns = new_col

# Upload Longitude and Latitude of Observation Stations
locsta = pd.read_excel('lonlat_sta.xlsx')
air_qi = pd.merge(
    left=air_qi,
    right=locsta,
    how='left',
    left_on='station',
    right_on='station'
)

# Upload Shape file of Beijing City, China
shp_beijing = gpd.read_file('gadm41_CHN_shp/gadm41_CHN_3_Beijing.shp')

# Data Imputation
stations = air_qi['station'].unique()
hours = air_qi['hour'].unique()

def imputation_mean(data, variables, stations, hours):
    ''' 
    A function of filling the values of missing values with its average.
    Imputation was did in some variabels or features depending on the station and recording time.
    
    Args:
        data (pd.DataFrame): The DataFrame containing missing values.
        variables (list): A list of variable names (column names) to impute.
        stations (list): A list of station observations.
        hours (list): A list of time measurements.

    Returns:
        pd.DataFrame: The DataFrame with missing values filled by mean for specified conditions.
    '''
    for variable in variables:
        for station in stations:
            for hour in hours:
                data[variable][(data['station'] == station) &
                                 (data['hour'] == hour)] = data[(data['station'] == station) &
                                                                    (data['hour'] == hour)][variable].fillna(
                                                                        value=data[(data['station'] == station) &
                                                                                     (data['hour'] == hour)][variable].mean())
    return data

variabel = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'WSPM']
imputation_mean(air_qi, variables=variabel, stations=stations, hours=hours)

def imputation_modus(data, variables, stations, hours):
    ''' 
    A function of filling the values of missing values with its mode.
    Imputation was did in some variabels or features depending on the station and recording time.
    
    Args:
        data (pd.DataFrame): The DataFrame containing missing values.
        variables (list): A list of variable names (column names) to impute.
        stations (list): A list of station observations.
        hours (list): A list of time measurements.

    Returns:
        pd.DataFrame: The DataFrame with missing values filled by mode for specified conditions.
    '''
    for variable in variables:
        for station in stations:
            for hour in hours:
                modus = statistics.mode(data[variable][(data['station'] == station) & (data['hour'] == hour)])
                data[variable][(data['station'] == station) &
                                 (data['hour'] == hour)] = data[(data['station'] == station) &
                                                                    (data['hour'] == hour)][variable].fillna(
                                                                        value=modus)
    return data

variabel = ['wd']
imputation_modus(air_qi, variables=variabel, stations=stations, hours=hours)

# Make a function to filter data by station
stations = air_qi['station'].unique()
def filter_sta(data, col, stations, listSta):
    '''
    A function to filter data by a station. Each data is saved to list.

    Args:
        data (pd.DataFrame): The DataFrame.
        col (chr): the name of station column in data.
        stations (list): A list of station observations.
        listSta (list): An empty list.

    Returns:
        list : list of filtered data (in pd.Dataframe) by station.
    '''

    for station in stations:
        filterData = data[data[col]==station]
        filteredData = pd.DataFrame(filterData)
        listSta.append(filteredData)
    return listSta

# Make daily dataframe
def daily_airqi(data):
    air_qi_daily = data.groupby(['station','date']).agg({
        'PM2.5' : 'mean',
        'PM10' : 'mean',
        'SO2' : 'mean',
        'NO2' : 'mean',
       'CO' : 'mean',
        'O3' : 'mean',
        'TEMP' : 'mean',
        'PRES' : 'mean',
        'DEWP' : 'mean',
        'RAIN' : 'sum',
        'WSPM' : 'mean',
        'wd' : statistics.mode,
        })
    air_qi_daily.reset_index(inplace=True)
    return air_qi_daily

column_name = 'station'

air_qi_daily = daily_airqi(air_qi)
list_aq_daily_sta = []
filter_sta(air_qi_daily, col=column_name, stations=stations, listSta=list_aq_daily_sta)

# Make monthly dataframe since 2013 until 2017
def monthly_ey_airqi(data):
    air_qi_monthly_ey = data.groupby(['station','year','month']).agg({
        'PM2.5' : 'mean',
        'PM10' : 'mean',
        'SO2' : 'mean',
        'NO2' : 'mean',
        'CO' : 'mean',
        'O3' : 'mean',
        'TEMP' : 'mean',
        'PRES' : 'mean',
        'DEWP' : 'mean',
        'RAIN' : 'sum',
        'WSPM' : 'mean',
        'wd' : statistics.mode,
        })
    air_qi_monthly_ey.reset_index(inplace=True)
    air_qi_monthly_ey['day'] = 1
    air_qi_monthly_ey['date'] = pd.to_datetime(air_qi_monthly_ey[['year','month','day']])
    return air_qi_monthly_ey

column_name = 'station'

air_qi_monthly_ey = monthly_ey_airqi(air_qi)
list_aq_mon_year_sta = []
filter_sta(air_qi_monthly_ey, col=column_name, stations=stations, listSta=list_aq_mon_year_sta)

# Make monthly dataframe
def monthly_airqi(data):
    air_qi_monthly = data.groupby(['station','month']).agg({
        'PM2.5' : 'mean',
        'PM10' : 'mean',
        'SO2' : 'mean',
        'NO2' : 'mean',
       'CO' : 'mean',
        'O3' : 'mean',
        'TEMP' : 'mean',
        'PRES' : 'mean',
        'DEWP' : 'mean',
        'RAIN' : 'sum',
        'WSPM' : 'mean',
        'wd' : statistics.mode,
        })
    air_qi_monthly.reset_index(inplace=True)
    return air_qi_monthly

column_name = 'station'

air_qi_monthly = monthly_airqi(air_qi)
list_aq_monthly_sta = []
filter_sta(air_qi_monthly, col=column_name, stations=stations, listSta=list_aq_monthly_sta)

# Make yearly dataframe
for i in range(0, len(list_aq_daily_sta)):
    df = list_aq_daily_sta[i]
    df['yearly'] = 4
    df['yearly'].iloc[0:365] = 1
    df['yearly'].iloc[365:730] = 2
    df['yearly'].iloc[730:1095] = 3

list_aq_yearly_sta = []
for i in range(0, len(list_aq_daily_sta)):
    df = list_aq_daily_sta[i]
    air_qi_yearly = df.groupby(['station','yearly']).agg({
    'PM2.5' : 'mean',
    'PM10' : 'mean',
    'SO2' : 'mean',
    'NO2' : 'mean',
    'CO' : 'mean',
    'O3' : 'mean',
    'TEMP' : 'mean',
    'PRES' : 'mean',
    'DEWP' : 'mean',
    'RAIN' : 'sum',
    'WSPM' : 'mean',
    'wd' : statistics.mode,
    })
    
    air_qi_yearly.reset_index(inplace=True)
    list_aq_yearly_sta.append(air_qi_yearly)

i = 1
while i < len(list_aq_yearly_sta):
    if (i == 1):
        air_qi_yearly = pd.concat([list_aq_yearly_sta[0], list_aq_yearly_sta[1]], axis=0)
    else:
        air_qi_yearly = pd.concat([air_qi_yearly, list_aq_yearly_sta[i]], axis=0)
    i += 1

# Make a series correlation between rain and pollutant gases
dataa = pd.DataFrame(air_qi_monthly)
cormat = dataa.corr(method='pearson', numeric_only=True)
correlRainQI = pd.DataFrame(cormat)
correlRainQI = correlRainQI['RAIN'][1:7]

st.header('Proyek Analisis Data: Air Quality Dataset')
st.subheader('Location of Weather Observation Stations')

air_qi['geometry'] = air_qi.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
fig, ax = plt.subplots(figsize=(10, 10))
shp_beijing.plot(ax=ax, color='lightgray')

ax.scatter(air_qi['lon'], air_qi['lat'])
sns.scatterplot(x='lon', y='lat', hue='station', data=air_qi, palette='husl')
plt.xlabel('')
plt.ylabel('')
plt.legend()
st.pyplot(fig)

st.subheader('Climate Characteristic of Beijing City')

col1, col2, col3 = st.columns(3)
 
with col1:
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.lineplot(x=air_qi_monthly['month'], y=air_qi_monthly['TEMP'], legend=True)
    plt.title('Air Temperature', fontsize=100)
    st.pyplot(fig)
 
with col2:
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.barplot(x='month', y='RAIN', data=air_qi_monthly)
    plt.title('Rainfall', fontsize=100)
    st.pyplot(fig)
 
with col3:
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.lineplot(x='month', y='PRES', data=air_qi_monthly)
    plt.title('Air Pressure', fontsize=100)
    st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(16, 16))
    sns.lineplot(x='month', y='WSPM', data=air_qi_monthly, hue='station', legend='auto')
    plt.tight_layout()  # Menyesuaikan tata letak agar rapi

    st.caption('Wind Speed (m/s)')
    st.pyplot(fig)

with col2:
    wd_beijing = air_qi_monthly[['station','wd']].groupby(['station']).agg(statistics.mode)
    wd_beijing.reset_index(inplace=True)
    wd_beijing2 = pd.merge(
        left=wd_beijing,
        right=locsta,
        how='left',
        left_on='station',
        right_on='station'
    )
    wd_beijing2['geometry'] = wd_beijing2.apply(lambda row: Point(row['lon'], row['lat']), axis=1)

    fig, ax = plt.subplots(figsize=(16, 16))
    shp_beijing.plot(ax=ax, color='lightgray')

    ax.scatter(wd_beijing2['lon'], wd_beijing2['lat'])
    sns.scatterplot(x='lon', y='lat', hue='wd', data=wd_beijing2, palette='husl')
    plt.xlabel('')
    plt.ylabel('')
    plt.legend()

    st.caption('Variations of Wind Direction')
    st.pyplot(fig)

st.subheader("Seasonal Pattern of Pollutant Levels in Beijing")
st.caption('Choose the pollutant gas or materi particulate')

filtered_data = air_qi_monthly.copy()
st.dataframe(filtered_data, height=500, width=1000)

# PM2.5 
st.caption('Seasonal Pattern of PM2.5')
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(25, 10))  # Sesuaikan nrows dan ncols dengan jumlah plot
sns.lineplot(x='date', y='PM2.5', data=air_qi_monthly_ey, ax=axes[0,0])
axes[0,0].set_title('PM2.5 monthly average in Beijing for 4 years ', size=20)
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel("PM2.5", size=20)

sns.lineplot(x='date', y='PM2.5', data=air_qi_monthly_ey, hue='station', legend='auto', ax=axes[0,1])
axes[0,1].set_title('PM2.5 monthly average in each stations in Beijing for 4 years', size=20)
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')

sns.lineplot(x='yearly', y='PM2.5', data=air_qi_yearly, ax=axes[1,0])
axes[1,0].set_title('PM2.5 trends average in Beijing ', size=20)
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel("PM2.5", size=20)

sns.lineplot(x='yearly', y='PM2.5', data=air_qi_yearly, hue='station', legend='auto', ax=axes[1,1])
axes[1,1].set_title('PM2.5 trends in each stations in Beijing for 4 years', size=20)
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')

plt.legend(loc='lower right')
plt.tight_layout() 
st.pyplot(fig)  

# PM10
st.caption('Seasonal Pattern of PM10')
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(25, 10))  # Sesuaikan nrows dan ncols dengan jumlah plot
sns.lineplot(x='date', y='PM10', data=air_qi_monthly_ey, ax=axes[0,0])
axes[0,0].set_title('PM10 monthly average in Beijing for 4 years ', size=20)
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel("PM10", size=20)

sns.lineplot(x='date', y='PM10', data=air_qi_monthly_ey, hue='station', legend='auto', ax=axes[0,1])
axes[0,1].set_title('PM10 monthly average in each stations in Beijing for 4 years', size=20)
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')

sns.lineplot(x='yearly', y='PM10', data=air_qi_yearly, ax=axes[1,0])
axes[1,0].set_title('PM10 trends average in Beijing ', size=20)
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel("PM10", size=20)

sns.lineplot(x='yearly', y='PM10', data=air_qi_yearly, hue='station', legend='auto', ax=axes[1,1])
axes[1,1].set_title('PM10 trends in each stations in Beijing for 4 years', size=20)
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')

plt.legend(loc='lower right')
plt.tight_layout() 
st.pyplot(fig)  

# CO
st.caption('Seasonal Pattern of CO')
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(25, 10))  # Sesuaikan nrows dan ncols dengan jumlah plot
sns.lineplot(x='date', y='CO', data=air_qi_monthly_ey, ax=axes[0,0])
axes[0,0].set_title('CO monthly average in Beijing for 4 years ', size=20)
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel("CO", size=20)

sns.lineplot(x='date', y='CO', data=air_qi_monthly_ey, hue='station', legend='auto', ax=axes[0,1])
axes[0,1].set_title('CO monthly average in each stations in Beijing for 4 years', size=20)
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')

sns.lineplot(x='yearly', y='CO', data=air_qi_yearly, ax=axes[1,0])
axes[1,0].set_title('CO trends average in Beijing ', size=20)
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel("CO", size=20)

sns.lineplot(x='yearly', y='CO', data=air_qi_yearly, hue='station', legend='auto', ax=axes[1,1])
axes[1,1].set_title('CO trends in each stations in Beijing for 4 years', size=20)
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')

plt.legend(loc='lower right')
plt.tight_layout() 
st.pyplot(fig)

# SO2
st.caption('Seasonal Pattern of SO2')
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(25, 10))  # Sesuaikan nrows dan ncols dengan jumlah plot
sns.lineplot(x='date', y='SO2', data=air_qi_monthly_ey, ax=axes[0,0])
axes[0,0].set_title('SO2 monthly average in Beijing for 4 years ', size=20)
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel("SO2", size=20)

sns.lineplot(x='date', y='SO2', data=air_qi_monthly_ey, hue='station', legend='auto', ax=axes[0,1])
axes[0,1].set_title('SO2 monthly average in each stations in Beijing for 4 years', size=20)
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')

sns.lineplot(x='yearly', y='SO2', data=air_qi_yearly, ax=axes[1,0])
axes[1,0].set_title('SO2 trends average in Beijing ', size=20)
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel("SO2", size=20)

sns.lineplot(x='yearly', y='SO2', data=air_qi_yearly, hue='station', legend='auto', ax=axes[1,1])
axes[1,1].set_title('SO2 trends in each stations in Beijing for 4 years', size=20)
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')

plt.legend(loc='lower right')
plt.tight_layout() 
st.pyplot(fig)

# NO2
st.caption('Seasonal Pattern of NO2')
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(25, 10))  # Sesuaikan nrows dan ncols dengan jumlah plot
sns.lineplot(x='date', y='NO2', data=air_qi_monthly_ey, ax=axes[0,0])
axes[0,0].set_title('NO2 monthly average in Beijing for 4 years ', size=20)
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel("NO2", size=20)

sns.lineplot(x='date', y='NO2', data=air_qi_monthly_ey, hue='station', legend='auto', ax=axes[0,1])
axes[0,1].set_title('NO2 monthly average in each stations in Beijing for 4 years', size=20)
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')

sns.lineplot(x='yearly', y='NO2', data=air_qi_yearly, ax=axes[1,0])
axes[1,0].set_title('NO2 trends average in Beijing ', size=20)
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel("NO2", size=20)

sns.lineplot(x='yearly', y='NO2', data=air_qi_yearly, hue='station', legend='auto', ax=axes[1,1])
axes[1,1].set_title('NO2 trends in each stations in Beijing for 4 years', size=20)
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')

plt.legend(loc='lower right')
plt.tight_layout() 
st.pyplot(fig)

# O3
st.caption('Seasonal Pattern of O3')
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(25, 10))  # Sesuaikan nrows dan ncols dengan jumlah plot
sns.lineplot(x='date', y='O3', data=air_qi_monthly_ey, ax=axes[0,0])
axes[0,0].set_title('O3 monthly average in Beijing for 4 years ', size=20)
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel("O3", size=20)

sns.lineplot(x='date', y='O3', data=air_qi_monthly_ey, hue='station', legend='auto', ax=axes[0,1])
axes[0,1].set_title('O3 monthly average in each stations in Beijing for 4 years', size=20)
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')

sns.lineplot(x='yearly', y='O3', data=air_qi_yearly, ax=axes[1,0])
axes[1,0].set_title('O3 trends average in Beijing ', size=20)
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel("O3", size=20)

sns.lineplot(x='yearly', y='O3', data=air_qi_yearly, hue='station', legend='auto', ax=axes[1,1])
axes[1,1].set_title('O3 trends in each stations in Beijing for 4 years', size=20)
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')

plt.legend(loc='lower right')
plt.tight_layout() 
st.pyplot(fig)

st.subheader('Areas with the Highest and Lowest Levels of Air Pollution')

air_qi_sta = air_qi.groupby(['station']).agg({
    'PM2.5' : 'mean',
    'PM10' : 'mean',
    'SO2' : 'mean',
    'NO2' : 'mean',
    'CO' : 'mean',
    'O3' : 'mean',
    'TEMP' : 'mean',
    'PRES' : 'mean',
    'DEWP' : 'mean',
    'RAIN' : 'sum',
    'WSPM' : 'mean',
    'wd' : statistics.mode,
})
air_qi_sta.reset_index(inplace=True)

filtered_data = air_qi_sta.copy()
st.dataframe(filtered_data, height=500, width=1000)

categories = air_qi_sta['station']


# PM2.5
st.caption('Seasonal Pattern of O3')
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(25, 10)) 
data = air_qi_sta['PM2.5']

max_value = max(data)
min_value = min(data)
colors = []
for value in data:
    if value == max_value:
        colors.append('red')
    elif value == min_value:
        colors.append('green')
    else:
        colors.append('orange')
plt.barh(categories, data, color=colors)
plt.title('Concentration of PM2.5')
st.pyplot(fig)

# PM10
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(25, 10)) 
data = air_qi_sta['PM10']

max_value = max(data)
min_value = min(data)
colors = []
for value in data:
    if value == max_value:
        colors.append('red')
    elif value == min_value:
        colors.append('green')
    else:
        colors.append('orange')
plt.barh(categories, data, color=colors)
plt.title('Concentration of PM10')
st.pyplot(fig)

# CO
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(25, 10)) 
data = air_qi_sta['CO']

max_value = max(data)
min_value = min(data)
colors = []
for value in data:
    if value == max_value:
        colors.append('red')
    elif value == min_value:
        colors.append('green')
    else:
        colors.append('orange')
plt.barh(categories, data, color=colors)
plt.title('Concentration of CO')
st.pyplot(fig)

# SO2
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(25, 10)) 
data = air_qi_sta['SO2']

max_value = max(data)
min_value = min(data)
colors = []
for value in data:
    if value == max_value:
        colors.append('red')
    elif value == min_value:
        colors.append('green')
    else:
        colors.append('orange')
plt.barh(categories, data, color=colors)
plt.title('Concentration of SO2')
st.pyplot(fig)

# NO2
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(25, 10)) 
data = air_qi_sta['NO2']

max_value = max(data)
min_value = min(data)
colors = []
for value in data:
    if value == max_value:
        colors.append('red')
    elif value == min_value:
        colors.append('green')
    else:
        colors.append('orange')
plt.barh(categories, data, color=colors)
plt.title('Concentration of NO2')
st.pyplot(fig)

# O3
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(25, 10)) 
data = air_qi_sta['O3']

max_value = max(data)
min_value = min(data)
colors = []
for value in data:
    if value == max_value:
        colors.append('red')
    elif value == min_value:
        colors.append('green')
    else:
        colors.append('orange')
plt.barh(categories, data, color=colors)
plt.title('Concentration of O3')
st.pyplot(fig)


st.subheader('Correlation of Pollutant Gas/Materi Particulate to Rain')

fig, ax = plt.subplots(figsize=(25, 15))
sns.barplot(correlRainQI, color='red')
plt.ylabel('')
st.pyplot(fig)