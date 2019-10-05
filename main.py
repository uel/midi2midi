import mp3
import numpy as np
import midi
import math
import spectogram
import os
import cv2
import pylab

def ParseMp3ToMidi(soundDir, midiDir):
    #sound accuracy data/s
    sacc = 512
    #midi accuracy 
    macc = 16

    for f in os.listdir(midiDir):
        rate, data = mp3.read(soundDir+"/"+f.replace(".mid", "-converted.mp3"))
        data = data.sum(axis=1) / 2
        spec = spectogram.librosa_cqt(data, rate, sacc) / 255

        for i in range(0, spec.shape[0]).__reversed__():
            if i%32 == 0:
                spec = np.split(spec[:i], sacc/macc, axis=0)
                break

        spec = np.dstack(spec)[:,:,:,None]

        midiArray = midi.Midi2Array(midiDir+"/"+f, macc)[:spec.shape[0]] / 128

        if os.path.isfile("in.npy"):
            np.save("in.npy", np.concatenate((np.load("in.npy"), spec)))
        else:
            np.save("in.npy", spec)

        if os.path.isfile("out.npy"):
            np.save("out.npy", np.concatenate((np.load("out.npy"), midiArray)))
        else:
            np.save("out.npy", midiArray)

#ParseMp3ToMidi("sound_data", "midi_data")

#sound accuracy data/s
sacc = 512
#midi accuracy 
macc = 1

def GetData_0(midiFile, soundFile):
    rate, data = mp3.read(soundFile)
    data = data.sum(axis=1) / 2
    spec = spectogram.librosa_cqt(data, rate, sacc) / 255

    midiArray = midi.Midi2Array(midiFile, macc)

    s = spec*255
    m = midiArray.repeat(sacc/macc, axis=0).repeat(8, axis=1)[:spec.shape[0]]
    r = np.concatenate((s, m), axis=1)

    cv2.imwrite("current_data.bmp", r)

    for i in range(0, spec.shape[0]).__reversed__():
        if i%32 == 0:
            spec = np.split(spec[:i], sacc/macc, axis=0)
            break

    spec = np.dstack(spec)[:,:,:,None]

    midiArray = midiArray[:spec.shape[0]] / 128
    spec = spec[:midiArray.shape[0]]

    return spec, midiArray

limits = []
noteFrequencies = []
for x in range(1, 90):
    x = x-0.5
    limits.append(math.pow(2, (x-49)/12)*440)
    noteFrequencies.append(math.pow(2, (x+0.5-49)/12)*440)

def FrequencyDistribution(signal, rate=44100):
    fft = np.fft.fft(signal)
    freq = np.fft.fftfreq(len(fft), 1/rate)

    notes = []
    for x in range(0, 88):
        r = np.where((freq>limits[x])*(freq<=limits[x+1]))
        r = abs(fft[r])
        val = (max(r, default=0))
        notes.append(np.array([val*255]))

    pylab.plot(range(0, 88), notes)
    pylab.show()

    return np.array(notes)

def GetData(midiFile, soundFile):
    rate, data = mp3.read(soundFile)
    data = data.sum(axis=1) / 2

    freqDist = np.zeros((88, 0))

    for x in range(0, math.ceil(len(data)*macc/rate)):
        dist = FrequencyDistribution(data[int(rate/macc*x):int(rate/macc*(x+1))])
        freqDist = np.concatenate((freqDist, dist), axis=1)

    midiArray = midi.Midi2Array(midiFile, macc)

    m = midiArray[:freqDist.shape[1]]*2
    freqDist = freqDist.swapaxes(0, 1)
    r = np.concatenate((freqDist, m), axis=1)

    cv2.imwrite("current_data.bmp", r)

    return freqDist, midiArray

