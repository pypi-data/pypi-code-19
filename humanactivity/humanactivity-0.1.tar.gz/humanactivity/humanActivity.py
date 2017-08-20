# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 20:25:40 2017

@author: Xeobo
"""
from enum import Enum
import threading
import time
from sklearn.preprocessing import StandardScaler
import pandas as pd

from keras.models import Sequential
from keras.models import model_from_json
import numpy as np


# Bean to format accelerometer data
class AccelerometerData:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getZ(self):
        return self.z

# Interface to accelerometer data source
# Be avare that interface function will be called every 50 ms,
# and should as soon as posible for algorithm to run correcly

class IAccelerometerDataSource:
    # Returns AccelerometerData object with current values of data
    def getCurrentReading(self):
        raise TypeError("Do not use interface itself! Implement your own class by deriving this interace!")


# Posible states that could be detected. IDLE is init state, before any state
# is recognized
class HumanActivityState(Enum):
    DOWNSTAIRS = 0
    JOGGING = 1
    SITTING = 2
    STANDING = 3
    UPSTAIRS = 4
    WALKING = 5
    IDLE = 6

SAMPLE_PERIOD = 0.05 #20Hz = 50 ms
# Time to wait until next state is provided
WAIT_TO_UPDATE = 0.5
# Window used for amount of data to be sent to Keras CNN
WINDOW_SIZE = 90


#Recognizer implementation
class HumanActivityRecognizer():
    # callback - function that will be called when new state is recognized
    #           and it receives HumanActivityState as argument
    # feedData - instance of class witch implements IAccelerometerDataSource 
    #            interface.
    def __init__(self, callback, feedData):
        self.x_array_ = []
        self.y_array_ = []
        self.z_array_ = []
        
        self.callback = callback
        self.feedData = feedData
        
        self.state = HumanActivityState.IDLE
        self.lock = threading.Lock()
        
        self.inputThread_running = True
        self.inputThreadObject = InputThread(self)
        self.inputThreadObject.start()
        
        self.outputThread_running = True
        self.outputThreadObject = OutputThread(self)
        
        self.outputThreadObject.start()
        
        #init mean normalisation
        dataset = pd.read_csv('har_scale_parameters.csv', names = ['mean','scale'], header = None)
        
        self.scX = StandardScaler()
        self.scX.mean_ = dataset['mean'][0]
        self.scX.scale_ = dataset['scale'][0]
        
        self.scY = StandardScaler()
        self.scY.mean_ = dataset['mean'][1]
        self.scY.scale_ = dataset['scale'][1]
        
        self.scZ = StandardScaler()
        self.scZ.mean_ = dataset['mean'][2]
        self.scZ.scale_ = dataset['scale'][2]
        

    # function that returns current recognizer state. Can be used for pooling
    # current state from Recognizer
    def getCurrentState(self):
        return self.state
    
    #stop algorithm from running
    def stopAlgorithm(self):
        self.inputThread_running = False
        self.outputThread_running = False
    
    # private function that should not be caled.
    def _normalize(self, currentReading):
        normalizedReading = AccelerometerData(
                self.scX.transform([currentReading.getX()][0].reshape(-1,1)),
                self.scY.transform([currentReading.getY()][0].reshape(-1,1)),
                self.scZ.transform([currentReading.getZ()][0].reshape(-1,1))
                )
        return normalizedReading


#input thread, Reads current accelerometer readings.#input thread, Reads current data from the model
class InputThread(threading.Thread):
    def __init__(self, model):
        threading.Thread.__init__(self)
        self.model = model
        
    def run(self):
        while(self.model.inputThread_running):
            currentReading = self.model.feedData.getCurrentReading()
            
            currentReading = self.model._normalize(currentReading)
            
            self.model.lock.acquire()
            
            if len(self.model.x_array_) == WINDOW_SIZE:
                del self.model.x_array_[0]
                del self.model.y_array_[0]
                del self.model.z_array_[0]
            
            self.model.x_array_.extend(currentReading.getX())
            self.model.y_array_.extend(currentReading.getY())
            self.model.z_array_.extend(currentReading.getZ())
            
                
            self.model.lock.release()
            
            time.sleep(SAMPLE_PERIOD)

# Output Thread, calculates new state.
class OutputThread(threading.Thread):
    def __init__(self, model):
        threading.Thread.__init__(self)
        self.model = model
        
    def run(self):
        #init keras model
        json_file = open('har_model_json', 'r')
        model_json =  json_file.read()
        json_file.close()
        predictor = model_from_json(model_json)
        # load weights into new model
        predictor.load_weights("har_model_save")
        while(self.model.outputThread_running):
            
            if len(self.model.x_array_) == WINDOW_SIZE:
                
                self.model.lock.acquire()
                
                matrix = np.hstack((np.array(self.model.x_array_).reshape(-1,1),
                          np.array(self.model.y_array_).reshape(-1,1),
                          np.array(self.model.z_array_).reshape(-1,1)))
                
                
                self.model.lock.release()
                parameter = np.empty((1, 90, 3))
                parameter [0,:,:] = matrix
                newState = np.argmax(predictor.predict(parameter))
                
                if self.model.state != newState:
                    self.model.callback(newState)
                
                self.model.state = newState
                
            time.sleep(WAIT_TO_UPDATE)

