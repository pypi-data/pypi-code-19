# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 17:48:19 2017

@author: julien
"""
import time
import logging

from pypot.robot.sensor import Sensor
import speech_recognition as sr

logger = logging.getLogger(__name__)

from ._nogit_credential import GOOGLE_CLOUD_SPEECH_CREDENTIALS

class VoiceRecognition(Sensor):
    """
    Define a voice recognition sensor
    """
    registers = Sensor.registers + ['phrase']

    def __init__(self, name):
        Sensor.__init__(self, name)

        self._last_phrase = None
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()
        self._timestamp = None
        self.running = False
        
    def __repr__(self):
        return ('<VoiceSensor name={self.name} ' 
                ' speech : {self._timestamp}  >').format(self=self)
    
    @property
    def phrase(self):
        return (self._timestamp, self._last_phrase)
    
    def listen_ones(self):
        with self._microphone as source:
            audio = self._recognizer.listen(source)
        self._last_phrase = self._recognizer.recognize_google_cloud(
                audio, language='fr-FR',
                credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        self._timestamp = time.time()
        
    def callback(self, recognizer, audio):
        try :
            self._last_phrase = self._recognizer.recognize_google_cloud(
                audio, language='fr-FR',
                credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
            self._timestamp = time.time()
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.warning("Could not request results from Google Speech Recognition service; {0}".format(e))
                
    def start(self):
        if not self.running :
            self.stop_listening = self._recognizer.listen_in_background(self._microphone, self.callback)
            self.running = True
        else :
            logger.warning('Backround VoiceRecognition already start')
        
    def close(self):
        if self.running :
            self.stop_listening()
            self.running = False
        else :
            logger.warning('Backround VoiceRecognition not started')
        
            
        