#!/usr/bin/env python


import subprocess
import math
import os
import shutil


from datetime import datetime,timedelta,time


def get_video_length(filename):
    '''Get the size of the selected video and return it in seconds
    '''

    output = subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename)).strip()
    video_length = int(float(output))
    print("Video length in seconds: "+str(video_length))

    return video_length

def ceildiv(a, b):
    
    return int(math.ceil(a / float(b)))

def desaturate_video(file_dir, output, filename, overwrite=False):
    '''Function for desaturation of the selected video file
    If overwrite is True then the  clip will be processed even if it exists, else it is skipped
    
    For the desaturation the clip is recoded through ffmpeg using the command "-vf hue=s=0" which sets them to 0 leaving only value part of HSV
    The ffmpeg is run through a subprocess, which waits until the process is over and returns any output from ffmpeg to the python console
    '''
    output = os.path.normpath(output)
    file_dir = os.path.normpath(file_dir)
    
    set_overwrite = "-n"
    if overwrite:
        set_overwrite = "-y"
    
    try:
        filebase = ".".join(filename.split(".")[:-1])
        fileext = filename.split(".")[-1]
        
        print(filebase)
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))
        
        
    if not overwrite and os.path.exists(os.path.join(output,filebase + "." +  fileext)): 
        print (f"File {os.path.join(output,filebase)} exists and overwrite is not set to true ")
        return -1
        
    desaturate_cmd = ["ffmpeg", set_overwrite, "-i", file_dir, "-vf", "hue=s=0",os.path.join(output,filebase + "." +  fileext) ]
    
    print("About to run: "+" ".join(desaturate_cmd))
    
    subprocess.check_output(desaturate_cmd)
    
    
def fix_video(file_dir, output, filename, overwrite=False):
    '''Function for recoding the input videos, before any processing and sampling is done
    This is done, because if the video contains timeline skips, errors or repeated steps, it will result in errors in all subsequent steps
    If overwrite is True then the  clip will be processed even if it exists, else it is skipped
    
    The name of the input file is copied to the output, the recode is done using libx264, as it was seen as stable
    '''
    output = os.path.normpath(output)
    file_dir = os.path.normpath(file_dir)
    

    
    try:
        filebase = ".".join(filename.split(".")[:-1])
        fileext = filename.split(".")[-1]
        
        print(filebase)
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))
        # + "_fixed" 
        
    if not overwrite and os.path.exists(os.path.join(output,filebase + "." +  fileext)): 
        print (f"File {os.path.join(output,filebase)} exists and overwrite is not set to true ")
        return -1
        

    fix_cmd = ["ffmpeg", "-y", "-i", file_dir, "-c:v", "libx264",os.path.join(output,filebase + "." +  fileext) ]
    
    print("About to run: "+" ".join(fix_cmd))
    
    subprocess.check_output(fix_cmd)
    
    
def split_into_days(outputFileDir, path, name, clip_counter, day_time_regex = '%Y%m%d%H%M', day_regex = '%Y%m%d', overwrite=False ):
    '''Function for recoding and splitting the input files of varying sizes into 1 day long ones.
    If the file is larger than 1 day, then it is split into a number of files always at 0:00. 
    If the files is smaller than 1 day, then it is renamed accordingly
    
    If overwrite is True then the  clip will be processed even if it exists, else it is skipped
    The day_time_regex and day_regex are used to transform the datetime files into strings and vice/versa
    
    The files are also put into directories depending on the date. Split files are put in different directories
    The ffmpeg encoding uses the fast -ss property when using internal tracking as the size of the files is large
    '''
    fileext = name.split(".")[-1]
    

            
    curr_videoFilePath = os.path.join(path, name)
    curr_length = get_video_length(curr_videoFilePath)
    
    startTime_str = name.encode("ascii", errors="ignore").decode().split("_")[0]
    
    print(startTime_str)
    
    
    startTime_dt = datetime.strptime(startTime_str, day_time_regex)
    
    endTime_dt = startTime_dt + timedelta(seconds = curr_length)
    
    endTime_str = endTime_dt.strftime(day_time_regex)
    
    
    
    if startTime_dt.day != endTime_dt.day:
        print(f" {name} needs split")
        
        startTime_endOfDay = datetime.combine(startTime_dt, time(23,59,59))
        
        startTime_cutoff = (startTime_endOfDay - startTime_dt).total_seconds()
        
        startTime_endOfDay_str = startTime_endOfDay.strftime(day_time_regex)
        
        
        
        output = os.path.join(outputFileDir, startTime_dt.date().strftime(day_regex)) 
        
        if not os.path.exists(output):
            os.makedirs(output, exist_ok=True)
            
        strOut = output + "\\" + startTime_str + "_" + startTime_endOfDay_str + "." + fileext    
        if not overwrite and os.path.exists(strOut):
            
            
            print (f"File {strOut} exists and overwrite is not set to true ")
        else:
        
            split_args = ["ffmpeg","-y", "-ss", str(0), "-i", curr_videoFilePath, "-to", str(startTime_cutoff),"-c", "copy",
                            output + "\\" + startTime_str + "_" + startTime_endOfDay_str + "." + fileext]
            print("About to run: "+" ".join(split_args))
            subprocess.check_output(split_args)
        
        
        
        clip_counter = 0
        
        endTime_startOfDay = datetime.combine(endTime_dt, time()) 
        endTime_startOfDay_str = endTime_startOfDay.strftime(day_time_regex)
    
        output = os.path.join(outputFileDir, endTime_dt.date().strftime(day_regex)) 
        
        if not os.path.exists(output):
            os.makedirs(output, exist_ok=True)
            
            
        if not overwrite and os.path.exists(output + "\\" + endTime_startOfDay_str + "_" + endTime_str + "." + fileext):
            
            strOut = output + "\\" + endTime_startOfDay_str + "_" + endTime_str + "." + fileext
            print (f"File {strOut} exists and overwrite is not set to true ")
        else:
        
        
            split_args = ["ffmpeg","-y", "-ss", str(startTime_cutoff), "-i", curr_videoFilePath, "-to", str(curr_length),"-c", "copy",
                            output + "\\" + endTime_startOfDay_str + "_" + endTime_str + "." + fileext]
            print("About to run: "+" ".join(split_args))
            subprocess.check_output(split_args)
        
        
        
        
    else:
        
        
        output = os.path.join(outputFileDir, startTime_dt.date().strftime(day_regex)) 
        
        if not os.path.exists(output):
            os.makedirs(output, exist_ok=True)
            clip_counter = 0
        
        strOut = output + "\\" + startTime_str + "_" + endTime_str + "." + fileext
        if not overwrite and os.path.exists(strOut):
            print("No overwrite and file exists")
        else:
            
            newPath = shutil.copy(curr_videoFilePath, output + "\\" + startTime_str + "_" + endTime_str + "." + fileext)
        
        
        print(f"{name} just copy")
        
    
    clip_counter+=1
    
    return clip_counter
    
    

def split_by_seconds(filename, output, skip, split_length,startTime_str, clip_counter, overwrite = False, vcodec="copy", acodec="copy",
                     extra="", video_length=None, **kwargs):
    '''Function for splitting the large files into small clips of the same size
    The split_length specifies how large the clip will be
    If overwrite is True then the  clip will be processed even if it exists, else it is skipped
    
    The file is checked if the split length is 0 or bigger than the size of the file an error si given
    
    The clips are put in the proper folder depending on their date and named using the pattern clip_{number of clip in the day}_HHMM
    '''

    
    
    if split_length and split_length <= 0:
        print("Split length can't be 0")
        raise SystemExit

    if not video_length:
        video_length = get_video_length(filename)
    split_count = ceildiv(video_length, split_length)
    if(split_count == 1):
        print("Video length is less then the target split length.")
        raise SystemExit
        
    #filename = os.path.normpath(filename)
    output = os.path.normpath(output)
    
    # if desaturate == True:
    #     split_cmd = ["ffmpeg","-y", "-i", filename, "-vf", "hue=s=0", "-acodec", acodec] + shlex.split(extra)
        
    # else:
    #     split_cmd = ["ffmpeg","-y", "-i", filename, "-vcodec", vcodec, "-acodec", acodec] + shlex.split(extra)
    
    
    try:
        filebase = ".".join(filename.split(".")[:-1])
        fileext = filename.split(".")[-1]
        
        print(filebase)
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))
    
    startTime_str = startTime_str.encode("ascii", errors="ignore").decode()
    startTime_dt = datetime.strptime(startTime_str, '%Y%m%d%H%M')   
    
    for n in range(0, split_count):
        
        if n % skip == 0:
            split_args = []
            if n == 0:
                split_start = 0
            else:
                split_start = split_length * n


            clip_dt = startTime_dt + timedelta(seconds = split_start)
            clip_dt_str = clip_dt.time().strftime('%H%M')
            
            
            # ffmpeg -ss 00:01:00 -i input.mp4 -to 00:02:00 -c copy output.mp4
            
            # split_args += ["ffmpeg", "-ss", str(split_start), "-i", filename, "-to", str(split_length),"-c", "copy",
            #                 output + "\\" + str(n+1) + "-of-" + \
            #                 str(split_count) + "_" + str(split_start) + "." + fileext]
            
            strOut = output + "\\" + "clip_" + str(clip_counter) + "_" + clip_dt_str + "." + fileext
            if not overwrite and os.path.exists(strOut):
            
                
                print (f"File {strOut} exists and overwrite is not set to true ")
            else:
            
                split_args += ["ffmpeg","-y", "-ss", str(split_start), "-i", filename, "-to", str(split_length),"-c", "copy",
                                output + "\\" + "clip_" + str(clip_counter) + "_" + clip_dt_str + "." + fileext]
                print("About to run: "+" ".join(split_args))
            
                
                subprocess.check_output(split_args)
            
            
            # split_args += ["-ss", str(split_start), "-t", str(split_length),
            #                 output + "\\" + str(n+1) + "-of-" + \
            #                 str(split_count) + "_" + str(split_start) + "." + fileext]
            # print("About to run: "+" ".join(split_cmd+split_args))
        
            clip_counter+=1
            # subprocess.check_output(split_cmd+split_args)
    return clip_counter        
    print("<-------------- END FILE -------------->")

