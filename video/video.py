import numpy as np
import cv2
import os
import time
import math

def ValidateVideo(video):
    l = math.inf
    loc = (0,0)
    f = 0
    keys = cv2.imread("keys.png")

    try:
        cap = cv2.VideoCapture(video)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(3))
        m = width/640
        dim = (int(605*m), int(65*m))
        k = cv2.resize(keys, dim, interpolation = cv2.INTER_AREA)
    except Exception as e:
        print(e)

    while(cap.isOpened()):
        try:
            f +=1
            cap.set(cv2.CAP_PROP_POS_FRAMES, f*(frame_count/10))
            ret, frame = cap.read()
            res = cv2.matchTemplate(frame, k, cv2.TM_SQDIFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if min_val<l:
                loc=min_loc
                l=min_val
            if f == 9:
                break
        except Exception as e:
            print(e)
            break
    
    cap.release()
    
    if l < 0.15:
        return True, l, loc

def FirstLastFrame(video):
    l = math.inf
    loc = (0,0)
    f = 0
    keys = cv2.imread("keys.png")

    try:
        cap = cv2.VideoCapture(video)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(3))
        m = width/640
        dim = (int(605*m), int(65*m))
        k = cv2.resize(keys, dim, interpolation = cv2.INTER_AREA)
    except Exception as e:
        print(e)

    while(cap.isOpened()):
        try:
            f +=1
            ret, frame = cap.read()
            res = cv2.matchTemplate(frame, k, cv2.TM_SQDIFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            print(min_val)
            if min_val < 0.1:
                return f

        except Exception as e:
            print(e)
            break
    
    cap.release()

def FindValidVideos():
    videoCount = 0
    for x in os.listdir("data"):
        videoCount+=1
        if "valid_" in x:
            continue
        valid, value, loc = ValidateVideo()
        if valid:
            try:
                os.rename("data/"+x, "data/valid_"+x)
            except Exception as e:
                print(e) 

        print("Videos Processed: ", videoCount) 
       
def CropVideo(video):
    valid, value, pos = ValidateVideo(video)
    os.system('ffmpeg -i "{}" -filter:v "crop=640:100:{}:{}" "{}"'.format(video,0,pos[1]-25, video.replace("video", "cropped2")))
    
def TrimVideo(video):



def AddAudio(video):
    os.system('ffmpeg -i "{}" -i "{}"  -shortest "{}"'.format(video, video.replace("cropped", "sound").replace("mp4", "mp3"), video.replace("cropped", "cropped_audio")))