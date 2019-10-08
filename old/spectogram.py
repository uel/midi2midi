import librosa
import librosa.display
import numpy as np
import pylab
import cv2
import math
import mp3

def librosa_cqt(data, rate, sacc):
    length = len(data)/rate
    result = np.empty((sacc, 0), "uint8")

    for i in np.array_split(data, math.ceil(len(data)/(rate*65535/sacc))*10, axis=0):
        hop_length = 256
        C = librosa.cqt(i, sr=rate, fmin=26, n_bins=88, hop_length=hop_length)
        #logC = librosa.amplitude_to_db(np.abs(C))
        fig = pylab.figure(figsize=((i.shape[0]/rate)*sacc, sacc), frameon=False, dpi=1)
        ax = fig.add_axes([0,0,1,1])
        ax.axis("off")
        librosa.display.specshow(C, sr=rate, x_axis='time', y_axis='cqt_note', fmin=26, cmap='gray', bins_per_octave=12)
        pylab.axis('off')
        
        pylab.savefig('spectrogram.png', bbox_inches='tight')
        pylab.close()
        result = np.concatenate((result, cv2.imread("spectrogram.png", cv2.IMREAD_GRAYSCALE)), 1)

    print("Spectogram created")
    return result.swapaxes(0, 1)