
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, Conv1D, MaxPooling2D, Dropout
import numpy as np
from keras.models import load_model
from keras.losses import mean_squared_error
import os
import cv2
import mp3
from keras import metrics
from preprocessing import *

def non_zero_accuracy(y_true, y_pred):
    y_true = y_true * (y_true != 0) 
    y_pred = y_pred * (y_true != 0)

    error = metrics.mean_squared_error(y_true, y_pred)
    return error

def LossFunction(t, p):
    return mean_squared_error(t, p)

def InitializeModel():
  model = Sequential()

  model.add(Dense(1024, activation='tanh', input_shape=(88,)))
  model.add(Dense(88, activation='tanh'))

  model.compile(
    optimizer='adam',
    loss=LossFunction,
    metrics=["accuracy"],
  )
  
  return model

def FitSave(model, i, o):
  model.fit(
    i,
    o,
    epochs=48,
    batch_size=64)
  model.save('model.h5', True)

def TestModel(modelFile, i):
  model = load_model("model.h5", custom_objects={"LossFunction":LossFunction})
  return model.predict(i)

def FitData(model, mp3Dir, midDir, appendConverted=True):
  for f in os.listdir(midDir):
    if ".mid" in f:
      print(f)
      try:
        if appendConverted:
          i, o = GetData(midDir+"/"+f, mp3Dir+"/"+f.replace(".mid", "-converted.mp3"))
        else:
          i, o = GetData(midDir+"/"+f, mp3Dir+"/"+f.replace(".mid", ".mp3"))
        FitSave(model, i, o)
      except Exception as e:
        print(e)
        continue

model = InitializeModel()
FitData(model, "data/bach", "data/bach")


#i, o = main.GetData("data/invent1.mid", "data/invent1.mp3")
# i = main.GetSound("data/invent1.mp3")
# cv2.imwrite("predict_data.bmp", TestModel("model.h5", i)*255)
