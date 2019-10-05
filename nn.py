
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, Conv1D, MaxPooling2D, Dropout
import numpy as np
from keras.models import load_model
import main
import os
import cv2
import spectogram
import mp3
from keras import metrics

def non_zero_accuracy(y_true, y_pred):

    y_true = y_true * (y_true != 0) 
    y_pred = y_pred * (y_true != 0)

    error = metrics.mean_squared_error(y_true, y_pred)
    return error

model = Sequential()

model.add(Dense(512, activation='relu', input_shape=(512,32,1)))
model.add(Dense(256, activation='relu'))
model.add(Dense(128, activation='relu'))
model.add(Flatten())
model.add(Dense(88, activation='tanh'))

model.compile(
  optimizer='adam',
  loss='categorical_crossentropy',
  metrics=["accuracy"],
)

def FitSave(i, o):
  model.fit(
    i,
    o,
    epochs=1,
    batch_size=32)
  model.save('model.h5', True)

for _ in range(0, 10):
  for f in os.listdir("midi_data"):
    print(f)
    try:
      i, o = main.GetData("midi_data/"+f, "sound_data/"+f.replace(".mid", "-converted.mp3"))
    except Exception as e:
      print(e)
      raise e
      continue
    FitSave(i, o)


# rate, data = mp3.read("part.mp3")
# data = data.sum(axis=1) / 2
# spec = spectogram.librosa_cqt(data, rate, 512) / 255
# for i in range(0, spec.shape[0]).__reversed__():
#   if i%32 == 0:
#     spec = np.split(spec[:i], 512/16, axis=0)
#     break

# spec = np.dstack(spec)[:,:,:,None]

# model = load_model("model.h5", custom_objects={'non_zero_accuracy': non_zero_accuracy})
# cv2.imwrite("part_test.png", (model.predict(spec)>0.5)*255)
