import cv2
import numpy as np
from cv2 import VideoWriter, VideoWriter_fourcc
from mido import MidiFile
import math
import random
from mido import tick2second
import copy
import time as clock
import subprocess
import os

def SaveList(l, file):
    with open(file, 'w') as f:
        for item in l:
            f.write("%s\n" % item)



class Midi_Video:
    def __init__(self, midi_path, video_path, framerate=60, width=1920, height=1080, colors = [(60,250,165),(235,180,135),(250,143,191),(60,164,60),(60,250,165),(235,180,135),(250,143,191),(60,164,60)]):
        self.midi_path = os.path.abspath(midi_path)
        self.video_path = video_path
        self.framerate = framerate
        self.width = width
        self.height = height
        self.white = int(width / 51)
        self.black = int(self.white*(13.7/23.5))
        self.keysX = []
        self.colors = colors
        self.scroll_speed = 0
        self.OrderedKeys = []
        
        for key in range(1, 89):
            self.keysX.append(self.KeyX(key))

        for key in range(1, 89):
            if (key-1)%12 not in [1,4,6,9,11]:
                self.OrderedKeys.insert(0, key)
            else:
                self.OrderedKeys.append(key)

        codec = VideoWriter_fourcc(*'mp4v')
        self.video = VideoWriter(video_path[:-3]+"avi", codec, float(framerate), (width, height))

    def KeyX(self, number): 
                positions = [0,
                            self.white*1.5-self.black,
                            self.white*1,
                            self.white*2,
                            self.white*3-self.black/2,
                            self.white*3,
                            self.white*4-self.black/2,
                            self.white*4,
                            self.white*5,
                            self.white*5.5,
                            self.white*6,
                            self.white*7-self.black/ 2]

                octave = math.floor((number-1)/12)
                keyAboveOctave = ((number-1)%12)
                return octave*7*self.white+positions[keyAboveOctave]
   
    def ParseMidi(mid):
        messages = [msg.dict() for msg in list(mid)]
        SaveList(messages, "orig.txt")

        time = 0
        parsed = []

        for msg in messages:
            time+= msg["time"]
            if msg["type"] is "note_on" or msg["type"] is "note_off":
                if (msg["type"] != "note_off") and (msg["velocity"] != 0):
                    keyType = "black"
                    if (msg["note"]-21)%12 not in [1,4,6,9,11]:
                        keyType = "white"
                        
                    if (len(parsed) != 0) and ("tempo" not in parsed[-1]) and ("pedal" not in parsed[-1]) and  (time == parsed[-1]["time"]):
                        parsed[-1]["notes"].append({"note":msg["note"]-20, "key":keyType, "duration":0, "channel":msg["channel"], "velocity":msg["velocity"]})
                    else:
                        parsed.append({"notes":[{"note":msg["note"]-20, "key":keyType,"duration":0, "channel":msg["channel"], "velocity":msg["velocity"]}],"time":time})
                else:
                    for m in reversed(parsed):
                        if "notes" in m:
                            for note in m["notes"]:
                                if (note["note"] == msg["note"]-20) and (note["duration"] == 0):                                  
                                    note["duration"] = round(time,3)-round(m["time"],3)

            #elif (msg["type"] == "control_change") and (msg["control"] == 64):
            #    if msg["value"] >= 64:
            #        parsed.append({"pedal":"on","time":time})
            #    elif msg["value"] <= 63:
            #        parsed.append({"pedal":"off","time":time})
                
        return parsed

    def DecodeSound(self):
         subprocess.call("""vlc -I dummy {0} "{1}{2}}},access=file}}" vlc://quit""".format(self.midi_path,":sout=#transcode{acodec=mp3,ab=256}:std{dst={", r"C:\Users\filip\Desktop\repos\Zinthesia\sound.mp3"), shell=True)  
        #subprocess.call("""vlc -I dummy -vvv {0} {1} --sout-keep --sout={2}{3}}} --sout-all vlc://quit""".format(self.midi_path, r"C:\Users\filip\Desktop\repos\Zinthesia\silence.mp3","#gather:transcode{acodec=mp3,ab=256}:standard{access=file, mux=dummy, dst={", dest), shell=True)
    
    def MergeVideo(self):
        dest = os.path.abspath(self.video_path[:-3]+"avi")
        delay = int(1000+(self.height-5.5*self.white)/(self.scroll_speed*self.framerate)*1000)
        subprocess.call("""vlc -I dummy -vvv {0} --input-slave {1} --audio-desync={4} --sout-keep --sout={2}{3}}} vlc://quit""".format(
        dest, r"C:\Users\filip\Desktop\repos\Zinthesia\sound.mp3", "#transcode{vcodec=h264,vb=1024,scale=1,acodec=mp4a,ab=256,channels=6}:standard{access=file,mux=mp4,dst=",dest[:-3]+"mp4",delay), shell=True)  
    
    def WriteKeyboard(self, frame, activeKeys):
                for i, key in enumerate(self.OrderedKeys):
                    if i<52:
                        color = (255,255,255)
                        for k in activeKeys:
                            if self.keysX[key-1] == k["pos"][0] and k["pos"][1] > (self.height-5.5*self.white):
                                color = k["color"]
                        #White key fill
                        cv2.rectangle(frame, (int(self.keysX[key-1]), self.height+2), 
                                            (int(self.keysX[key-1]+self.width / 52), int(self.height-(self.white*5.5))),
                                            color, -1)
                        
                        #White key border
                        cv2.rectangle(frame, (int(self.keysX[key-1]), self.height+2), 
                                            (int(self.keysX[key-1]+self.width / 52), int(self.height-(self.white*5.5))),
                                            (0,0,0), 3)
                    else:
                        color = (0,0,0)
                        for k in activeKeys:
                            if int(self.keysX[key-1]) == k["pos"][0] and k["pos"][1] > (self.height-5.5*self.white):
                                color = k["color"]
                        #Black key fill
                        cv2.rectangle(frame, (int(self.keysX[key-1]), int(self.height-2*self.white)+2),
                                            (int(self.keysX[key-1]+self.black), int(self.height-(2+self.white*5.5))),
                                            color, -1)
                        #Black key border
                        cv2.rectangle(frame, (int(self.keysX[key-1]), int(self.height-2*self.white)+2),
                                            (int(self.keysX[key-1]+self.black), int(self.height-(2+self.white*5.5))),
                                            (0,0,0), 2)

    def BackgroundFrame(self):
        image = np.zeros((self.height, self.width, 3), np.uint8)
        image[:] = (49, 47, 49)
        return image

    def WriteFrames(self):    
        mid = MidiFile(self.midi_path)
        self.scroll_speed = int(150/math.log2(mid.ticks_per_beat))
        scroll_speed = self.scroll_speed
        delay_start = 1
        delay_end = self.height/(scroll_speed*self.framerate)

        print("Parsing midi...")
        messages = Midi_Video.ParseMidi(mid)
        
        SaveList(messages, "messages.txt")

        activeNotes = []
        background = self.BackgroundFrame()

        start_time = clock.time()

        colors = []
        for color in self.colors:
            colors.append([color,(color[0]-50, color[1]-50, color[2]-50)])

        for frame_number in range(0, math.ceil(self.framerate*(mid.length+delay_start+delay_end))):
            frame = copy.copy(background)
            time = frame_number/self.framerate
            if time>delay_start:
                while (len(messages) != 0) and ((time-delay_start)-1/self.framerate) >= messages[0]["time"]:
                    msg = messages[0]
                    messages.pop(0)
                    if "notes" in msg:
                        for note in msg["notes"]:
                            if note["key"] == "white":
                                x = self.keysX[note["note"]-1]
                                y = note["duration"]*self.framerate*scroll_speed
                                activeNotes.insert(0, {"size":(self.white, int(y)), "pos":[int(x),0], "channel":note["channel"], "color":colors[note["channel"]][0]})
                            else:
                                x = self.keysX[note["note"]-1]
                                y = note["duration"]*self.framerate*scroll_speed
                                activeNotes.append({"size":(self.black-2,int(y)), "pos":[int(x),0], "channel":note["channel"], "color":colors[note["channel"]][1]})

                for note in activeNotes[:]:                        
                    pos = note["pos"]
                    cv2.rectangle(frame, (pos[0]+2,pos[1]),(pos[0]+note["size"][0], pos[1]-note["size"][1]), note["color"], -1)      
                    note["pos"][1]+=scroll_speed
                    if pos[1] > (self.height-5.5*self.white+note["size"][1]):
                        activeNotes.remove(note)

            if frame_number%self.framerate*10 == 0:
                print(frame_number)
            self.WriteKeyboard(frame, activeNotes)
            self.video.write(frame)

                
        print("Render time: %ss" % (clock.time() - start_time))
        self.video.release()


def CreateSong():
    from mido import Message, MidiFile, MidiTrack

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message('note_on', note=37, velocity=64, time=0))
    track.append(Message('note_on', note=47, velocity=64, time=0))
    track.append(Message('note_off', note=37, velocity=64, time=5000))
    track.append(Message('note_off', note=47, velocity=64, time=5000))

    mid.save('new_song.mid')
