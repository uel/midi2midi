
from keras.models import Sequential, Model
from keras.layers import Dense, Flatten, Conv1D, MaxPooling1D, Dropout, GlobalAveragePooling1D, Concatenate, Input, concatenate, Activation
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

def ParallelModel():
  inp = Input((88,1))
  l1 = Dense(88)(inp)
  l2 = Conv1D(88, 4)(inp)
  l2 = MaxPooling1D(3)(l2)
  l3 = Conv1D(88, 8)(inp)
  l3 = MaxPooling1D(3)(l2)
  l4 = Conv1D(88, 12)(inp)
  l4 = MaxPooling1D(3)(l4)

  merge = Concatenate(1)([l1, l2, l3, l4])
  merge2 = Activation("tanh")(merge)
  merge3 = Dropout(.3)(merge2)
  model = Model(inputs=inp, outputs=merge3)
  return model

def InitializeModel():
  model = Sequential()
  model.add(Conv1D(32, 3, activation='relu', input_shape=(88,1)))
  model.add(MaxPooling1D(2))
  model.add(Dropout(0.3))
  model.add(Conv1D(64, 3, activation='relu'))
  model.add(MaxPooling1D(2))
  model.add(Dropout(0.3))
  model.add(Conv1D(64, 3, activation='relu'))
  model.add(MaxPooling1D(2))
  model.add(Dropout(0.3))
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
    epochs=1,
    batch_size=1,
    verbose=1)
  model.save('model.h5', True)
  return history.history["accuracy"][-1]

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
        i = np.expand_dims(i, axis=2)
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

def Fit(model, mp3Dir, midDir, appendConverted=True):
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



#model = InitializeModel()
#Fit(model, r"data\music", r"data\music")
#TestModel()

i, o = GetData("data/music/01allema.mid", "data/music/01allema-converted.mp3")
#i = GetSound("data/bach/01allema-converted.mp3")
res = TestModel("model.h5", np.expand_dims(i, axis=2))[:,0,:]
cv2.imwrite("predict_data.bmp", res*255)
