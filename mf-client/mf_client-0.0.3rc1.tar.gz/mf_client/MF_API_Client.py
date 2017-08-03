#-------------------------------------------------------------------------------
#Targeting:     Python 2 and 3
#Use:           Will implement functions for all commands to the controller
#-------------------------------------------------------------------------------

from mf_client.MF_socketIO import *
import json



#-------------------------------------------------------------------------------

class MF_API_Client:

    def __init__(self, controllerUrl, controllerPort, password):
        self.controller = MF_socketIO(controllerUrl, controllerPort, password)

    def sendScenesAndThemes(self, room, scenes, themes=[]):

        #test if scene list is empty as not supported by hub
        if (len(scenes) > 0):
            score = {'play': {'scenes' : scenes, 'themes' : themes} }
            self.controller.send(room, 'showScenesAndThemes', score);
        else:
            raise ValueError('Scene list must not be empty!')

    def sendScene(self, room, scene):
        self.sendScenesAndThemes(room, [scene])

    #get all scenes
    def getSceneList(self, callback):

        def on_recive_scenes(*args):
            scenes = args[1]
            #add any pre processing here
            callback(scenes)

        self.controller.get('listScenes', on_recive_scenes)

    #get a single scene by ID
    def getSceneByID(self, ID, callback):

        def on_scene_loaded(*args):
            scene = args[1]
            #add any pre processing here
            callback(scene)

        self.controller.getWithParam('loadScene', ID, on_scene_loaded)
