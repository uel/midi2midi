
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
import threading
import time

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
  history = model.fit(
    i,
    o,
    epochs=48,
    batch_size=64,
    verbose=0)
  model.save('model.h5', True)
  return history.history["acc"][-1]

def TestModel(modelFile, i):
  model = load_model("model.h5", custom_objects={"LossFunction":LossFunction})
  return model.predict(i)


data = []
def GenerateData(mp3Dir, midDir, appendConverted=True):
  for f in os.listdir(midDir):
    if ".mid" in f:
      try:
        if appendConverted:
          i, o = GetData(midDir+"/"+f, mp3Dir+"/"+f.replace(".mid", "-converted.mp3"))
        else:
          i, o = GetData(midDir+"/"+f, mp3Dir+"/"+f.replace(".mid", ".mp3"))
        data.append((i, o, f))
      except Exception as e:
        print(e)
        continue

def Train(model):
  while True:
    if data != []:
      try:
        i, o = data.pop(0)
        FitSave(model, i, o)
      except Exception as e:
        print(e)
        continue

def FitData(model, mp3Dir, midDir, appendConverted=True):
  dataThread = threading.Thread(target=GenerateData, args=(mp3Dir, midDir))
  dataThread.start()
  t = time.time()
  while True:
    if data != []:
      try:
        i, o, f = data.pop(0)
        acc = str(round(FitSave(model, i, o)*100, 2))
        print(acc+"% - "+str(round(time.time()-t, 1))+"s"+" - "+f)
        open("accuracy.json", "a").write('["'+f+'", '+acc+'],\n')
        t = time.time()
      except Exception as e:
        print(e)
        continue
    time.sleep(1)



model = InitializeModel()
FitData(model, r"C:\Users\Filip\Desktop\Programmerinig\repos\GA\wave2midi\data\midi_data", r"C:\Users\Filip\Desktop\Programmerinig\repos\GA\wave2midi\data\midi_data")


#i, o = main.GetData("data/invent1.mid", "data/invent1.mp3")
# i = main.GetSound("data/invent1.mp3")
# cv2.imwrite("predict_data.bmp", TestModel("model.h5", i)*255)
