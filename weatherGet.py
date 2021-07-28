# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 09:28:36 2021

@author: IvanTower
"""
from meteostat import Stations,Daily,Hourly
from datetime import datetime
import matplotlib.pyplot as plt


def getWeather(start, end, period = "hourly", coordinates = [57.0488, 9.9217]):
    """Get weather data between the selected start and end datetimes. Return the data in a pandas Series or DataFrame
    Inputs:
        start, end - datatimes, containing date, hour and minutes as a minimum
        period - it can either be "hourly" or "daily"
        coordinates - a tuple of latitude and longitude coordinates of a place to get the weather for
    Outputs:
        In case of hourly period the output data is returned as a DataFrame with a row representing each hour
        In case of daily period the output data is returned as a DataFrame/Series with a row representing each daily
        More information about structure of DataFrame - https://dev.meteostat.net/docs/
     
    """
    
    if period not in ["daily","hourly"]:
        raise Exception("Period must be either hourly or daily")
        
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        raise Exception("Start and End periods need to be of type datetime")
        
    
    stations = Stations()
    stations = stations.nearby(coordinates[0],coordinates[1])
    stations = stations.inventory(period, (start, end))
    station = stations.fetch(1)
    
    if period == "hourly": 
        data = Hourly(station, start, end)
    elif period == "daily":
        data = Daily(station, start, end)
    else:
        return -1
    
    data = data.fetch()
    
    
    return data



if __name__ == '__main__':
    
    
    # Set time period
    start = datetime(2020, 1, 17, 23,0)
    end = datetime(2020, 1, 18, 23, 0)
    
    # Get nearby weather stations
    stations = Stations()
    stations = stations.nearby(57.0488, 9.9217)
    stations = stations.inventory('hourly', (start, end))
    station = stations.fetch(1)
    
    print(station)
    
    # Get hourly data
    data = Hourly(station, start, end)
    
    data = data.fetch()
    
    # Print DataFrame
    print(data)