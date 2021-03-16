from Zinthesia import Midi_Video
from mido import MidiFile
import numpy as np
import mido
import math
import cv2

def Midi2Array(midiFilePath, dtime):
    midifile = MidiFile(midiFilePath)
    midi = Midi_Video.ParseMidi(midifile)
    result = np.zeros((math.ceil(midifile.length*dtime), 88), dtype="uint8")

    for i in midi:
        if "notes" in i:
            for note in i["notes"]:
                s = slice(round(i["time"]*dtime), round(i["time"]*dtime)+round(note["duration"]*dtime))
                result[s, note["note"]-1] = note["velocity"]
                #result[s, note["note"]-1] = 128
    return result
