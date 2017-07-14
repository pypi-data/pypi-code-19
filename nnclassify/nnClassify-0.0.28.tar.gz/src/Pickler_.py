# This file has all the methods for pickling and unpickling data

import cv2 
import random
import os
import math
import numpy as np
import shutil
import re
import pickle
from src import Constants

from src.Constants import BASE_DIR
from src.Constants import PRED_DIR
from src.Constants import TRAIN_DIR
from src.MyUtils_ import MyUtils

class Pickler:

    @staticmethod
    def pickle_wells(pred_set):
        """ This method pickles all the wells in a prediction set
        individually"""
        categories = MyUtils.listdir_nohidden(os.path.join(pred_set,"Images"))
    
        if not os.path.exists(os.path.join(pred_set, "Pickles")):
            os.makedirs(os.path.join(pred_set, "Pickles"))

        #The highest level directory will have a folder for each category
        # (0_Eyes, 1_Eye, 2_Eyes, etc.)
        for category in categories:
            if not os.path.exists(os.path.join(pred_set, "Pickles", category)):
                os.makedirs(os.path.join(pred_set, "Pickles", category))
    
            wells = MyUtils.listdir_nohidden(os.path.join(pred_set, "Images"
                                                                    ,category))
    
            # Inside each category will be a bunch of folders were each folder
            # is a singel well
            for well in wells:
                print ("Pickling well" + well)
                files = list(MyUtils.listdir_nohidden(
                    os.path.join(pred_set, "Images", category, well)))
    
                images = []
    
                for img in files:
                    images.append(img)
    
                images_np = np.zeros((len(images), 100, 100, 3))
    
                for i in range(0, len(images)):
                    images_np[i,:,:,:] = cv2.imread(os.path.join(
                            pred_set, 'Images', category, well,  images[i]))
    
                pickle.dump(images_np,
                            open(os.path.join(pred_set, 'Pickles'
                                , category, well),"wb"))
                print ("Done with well " + well)
                print (" ")
        return

    @staticmethod
    def pickle_wells_no_category(pred_set):
        """ This method pickles all the images for a prediction set.
        A prediction set has no categories"""
        if not os.path.exists(os.path.join(pred_set, "Pickles")):
            os.makedirs(os.path.join(pred_set, "Pickles"))
    
    
        wells = MyUtils.listdir_nohidden(os.path.join(pred_set, "Images"))
    
        # Inside each category will be a bunch of folders were each folder
        # is a singel well
        for well in wells:
            print ("Pickling well" + well)
            files = list(MyUtils.listdir_nohidden(os.path.join(
                pred_set, "Images", well)))
    
            images = []
    
            for img in files:
                images.append(img)
    
            images_np = np.zeros((len(images), 100, 100, 3)) 
    
            for i in range(0, len(images)):
                images_np[i,:,:,:] = cv2.imread(os.path.join(pred_set
                        ,'Images' 
                        , well, images[i]))
    
            pickle.dump(images_np,
                        open(os.path.join(pred_set, 'Pickles'
                             ,well),"wb"))
            print ("Done with well " + well)
            print (" ")
        return


    
    @staticmethod
    def pickleIndividualSet(set_path):
        """This method pickles a  set of individual images so
        that we don't have to read
        in all the images individaully each time"""
    
        labels = []
        all_images_np = np.empty((0,100,100,3))
        categories = MyUtils.listdir_nohidden(os.path.join(set_path
                                                ,'Images'))
    
        for category in categories:
    
            images = []
            files = list(MyUtils.listdir_nohidden(os.path.join(set_path  
                                        ,"Images", category)))
    
            for img in files:
                images.append(img)
    
            print (len(images))
    
            images_np = np.zeros((len(images), 100, 100, 3))
    
            for i in range(0, len(images)):
                images_np[i,:,:,:] = cv2.imread(os.path.join(set_path
                        ,'Images', category, images[i]))
                if category == Constants.WEIRD :
                    labels.append([0,0,1])
                elif category == Constants.NORMAL :
                    labels.append([0,1,0])
                else:
                    labels.append([1,0,0])
    
            all_images_np = np.concatenate((all_images_np, images_np),
                    axis = 0)
            labels_np = np.array(labels)
        pickle.dump( all_images_np, 
                open(os.path.join(set_path, 'images.p'),"wb"))
        pickle.dump( labels_np, 
                open(os.path.join(set_path, 'labels.p'),"wb"))
    
        return



