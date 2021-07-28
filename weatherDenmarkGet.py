# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 11:55:14 2021

@author: IvanTower
"""
import requests
import pandas as pd
import numpy as np


from datetime import datetime,timedelta
from dmi_open_data import DMIOpenDataClient, Parameter

def distLatLong(lat1, long1, lat2, long2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, long1, lat2, long2 = map(np.radians, [lat1, long1, lat2, long2])
    # haversine formula 
    dlon = long2 - long1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km


def datetime_to_unixtime(dt):
    '''Function converting a datetime objects to a Unix microsecond string'''
    return str(int(pd.to_datetime(dt).value*10**-3))


def getClosestStation(coordinates = [57.049776, 9.926413],idsToSkip = ['20315']):
    
    api_key = 'a017c060-41ce-4516-85ba-086bc77bed0a'
    url_stations = 'https://dmigw.govcloud.dk/metObs/v1/station' # url for the current api version
    params = {'api-key' : api_key,
              'limit' : '10000',
              }
    
    r_s = requests.get(url_stations, params=params) # submit GET request based on url and headers
    print(r_s, r_s.url) # Print request status and url
    
    
    json_s = r_s.json() # Extract JSON object
    df_s = pd.DataFrame(json_s) # Convert JSON object to a DataFrame
    
    
    # coordinates = [57.049776, 9.926413]
    
    
    minDist = 1e10
    minDist_stationID = 0
    for index,station in df_s.iterrows():
        location = station['location']
        curr_latitude = location['latitude']
        curr_longitude = location['longitude']
        stationID = station['stationId']
        
        dist = distLatLong(coordinates[0],coordinates[1],curr_latitude,curr_longitude)
        if dist < minDist and stationID  not in idsToSkip:
            minDist = dist
            
            minDist_stationID = stationID
            
    return minDist_stationID


def getWeatherDK(start_time, end_time, stationId):
    
    api_key = 'a017c060-41ce-4516-85ba-086bc77bed0a'  # api key from DMI
    url = 'https://dmigw.govcloud.dk/metObs/v1/observation' # url for the current api version
    
    params = {'api-key' : api_key,
          'from' : datetime_to_unixtime(start_time),
          'to' : datetime_to_unixtime(end_time),
          'stationId' : stationId,
          'limit' : '10000',
          }
    
    
    r = requests.get(url, params=params) # submit GET request based on url and headers
    print(r, r.url) # Print request status and url
    
    
    json = r.json() # Extract JSON object
    df = pd.DataFrame(json) # Convert JSON object to a DataFrame
    
    df['time'] = pd.to_datetime(df['timeObserved'], unit='us') # Set the DataFrame index as the observation time
    
    df = df.drop(['_id', 'timeCreated', 'timeObserved'], axis=1) # Delete unused columns
    
    df.index = df['time'] # Set the time as the index
    
    mask = df['time'] == df['time'].dt.floor('10T')
    df_10minInterval = df[mask]
    
    df_10minInterval_removeDuplicates = df_10minInterval.drop_duplicates(['time','parameterId'])
    
    weatherObservations = df_10minInterval_removeDuplicates.pivot(index='time', columns='parameterId', values='value')
    
    return weatherObservations


if __name__ == '__main__':

    api_key = 'a017c060-41ce-4516-85ba-086bc77bed0a'
    
    coordinates = [57.049776, 9.926413]
    
    end_time = datetime(2021,1,15) # End time is defined as the current time
    start_time = datetime(2021,1,14) # Start time is defined as specific date
    
    minDist_id = getClosestStation(coordinates)

    
    # weatherData = getWeatherDK(start_time,end_time,minDist_id)
    
    
    
    url = 'https://dmigw.govcloud.dk/metObs/v1/observation' # url for the current api version
    

    

    
    
    # Specify query parameters
    params = {'api-key' : api_key,
              'from' : datetime_to_unixtime(start_time),
              'to' : datetime_to_unixtime(end_time),
              'stationId' : '06031',
              #'parameterId' : 'temp_mean_past1h',
              'limit' : '10000',
              }
    # 20315
    # 06031
    r = requests.get(url, params=params) # submit GET request based on url and headers
    print(r, r.url) # Print request status and url
    
    
    json = r.json() # Extract JSON object
    df = pd.DataFrame(json) # Convert JSON object to a DataFrame
    
    df['time'] = pd.to_datetime(df['timeObserved'], unit='us') # Set the DataFrame index as the observation time
    
    df = df.drop(['_id', 'timeCreated', 'timeObserved'], axis=1) # Delete unused columns
    
    df.index = df['time'] # Set the time as the index
    
    mask = df['time'] == df['time'].dt.floor('10T')
    df_10minInterval = df[mask]
    df_10minInterval_removeDuplicates = df_10minInterval.drop_duplicates(['time','parameterId'])
    
    # df2 = df_10minInterval.set_index(['time', 'parameterId']).unstack(level=-1)['value']
    df2 = df_10minInterval_removeDuplicates.pivot(index='time', columns='parameterId', values='value')
    
    # # params = ['wind_speed', 'humidity', 'temp_dry', "precip_past10min", "radia_glob", "sun_last10min_glob"]
    
    # client = DMIOpenDataClient(api_key=api_key)
    # stations = client.get_stations()
    
    # coordinates = [57.049776, 9.926413]
    
    
    # minDist = 1e10
    # minDist_stationID = 0
    # for station in stations:
    #     location = station['location']
    #     curr_latitude = location['latitude']
    #     curr_longitude = location['longitude']
    #     stationID = station['stationId']
        
    #     dist = distLatLong(coordinates[0],coordinates[1],curr_latitude,curr_longitude)
    #     if dist < minDist and stationID  not in ['20315']:
    #         minDist = dist
            
    #         minDist_stationID = stationID
            
    # # dmi_station = next(
    # #     station
    # #     for station in stations
    # #     if station['name'].lower() == 'dmi')
    
    
    # # Get temperature observations from DMI station in given time period
    # observations = client.get_observations(
    #     station_id = minDist_stationID,
    #     from_time=datetime(2021, 1, 20),
    #     to_time=datetime(2021, 1, 21),
    #     limit=10000)
