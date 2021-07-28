## Harbor-Dataset-Pre-Processing


Code for pre-processing raw video surveillance data used in the experiments presented here https://github.com/IvanNik17/Seasonal-Changes-in-Thermal-Surveillance-Imaging

## Requirements

- Python 3
- Pandas
- Numpy
- ffmpeg (http://ffmpeg.org/)
- DMI open weather API (https://confluence.govcloud.dk/display/FDAPI)
- Meteostat open weather API (https://dev.meteostat.net/)

## Usage

**Download and extract dataset**

Download from X and extract raw video directories in the suitable directory. Beware that raw dataset is >250 GB

```bash
wget ...
```

**Run through pre-processing pipeline**

Run the 'Dataset Preprocessing.ipynb' Jupyter notebook and follow the steps outlined there. Main processing steps are as follows:

- Recode the input raw video files to remove fragmentations and possible timeline errors. Slowest operation in the pipeline. It can take up to 15 hours, depending on CPU and GPU performance
- Segment the fixed input raw videos into days, as some files are less than a day and some are more than a day. Put the files in directories based on date
- Split the raw daily videos into clips of set size and save only certain clips. Default case is saving a 2-minute clip for every 30 minutes of video footage through the day. Save clips to the specific date folder and name them using the time they were taken
- Desaturate the clips to zero out redundant color dimensions
- Gather weather data either from DMI or Meteostat open weather API and save it as metadata, together with clip timestamps and folder structure

Files are not deleted after each processing step, but if space is a concern can be deleted after the next processing step has been done.
The pipeline can be set to overwrite already processed files or to skip the already done files in case the code has been stopped early.

**Helper functions**
The 'ffmpegSplit.py' is based on the work by https://github.com/ToastyMallows/ffmpegSplit and uses direct calls to ffmpeg through the subprocess library. It contains the functions:
- fix_video - for recoding the video 
- split_into_days - for splitting the raw fixed video into days. If the file is longer than a day, it is split at 0:00 hours
- split_by_seconds - for splitting the daily raw videos into clips of certain size and saving only certain clips
- desaturate_video - zeros the hue and saturation parts of the HSV video clips to make the size smaller and importing them for processing faster
- get_video_length - calculates the size of the input video file and returns it

The 'weatherGet.py' and 'weatherDenmarkGet.py' are helper scripts for gathering weather data from Meteostat and DMI's free weather API.
The 'weatherGet.py' contains only the function getWeather, which requires the start and end time, the required period - either hourly or daily and the coordinates where the weather should be gathered from. The function automatically gets the closest weather station to the given coordinates.
The 'weatherDenmarkGet.py' contains the getClosestStation function, which is used to find the closest weather station to given coordinates and returns the ID of that station. The getWeatherDK requires the start and end time and the station ID, as well as the free API key for connecting to DMI's weather service. It returns the gathered observations. A helper function distLatLong is also used for calculating the shortest distance between the desired coordinates and the weather stations.
