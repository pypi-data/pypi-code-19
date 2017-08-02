#-------------------------------------------------------------------------------
#Targeting:     Python 2 and 3
#Use:           Will implement functions for all commands to the controller
#-------------------------------------------------------------------------------

from mf_client.MF_socketIO import *

#-------------------------------------------------------------------------------

class MF_API_Client:

    def __init__(self,  controllerUrl, controllerPort, password, room):
        self.controller = MF_socketIO(controllerUrl, controllerPort, password)
        self.room = room

    def sendScenesAndThemes(self, scenes, themes=[]):
        if (len(scenes) > 0):
            score = {'play': {'scenes' : scenes, 'themes' : themes} }
            self.controller.send(self.room, 'showScenesAndThemes', score);
        else:
            raise ValueError('Scene list must not be empty!')

    def changeRoom(self, newRoom):
        self.room=newRoom
