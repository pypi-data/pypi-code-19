# This file is for calculating the output of the inception
# model so we can we that as input to our neural netwroks. 
# This is used for transfer learning. For more information
# see (https://github.com/Hvass-Labs/TensorFlow-Tutorials
#                   /blob/master/08_Transfer_Learning.ipynb)
import os
from src.Constants import INCEPTION_DIR
from src.MyUtils_ import MyUtils
import pickle
# Functions and classes for loading and using the Inception model.
from src import inception
from src.inception import transfer_values_cache

class Transfer_Calculator:

    @staticmethod
    def getTransferValues(source_p, dest_p):
        inception.data_dir = INCEPTION_DIR
    
        inception.maybe_download()
    
        model = inception.Inception()
    
        file_path_cache_train = dest_p
    
        print("Processing Inception transfer-values ...")
    
        images = pickle.load( open(source_p, 'rb'))
    
        transfer_values_train = transfer_values_cache(
                                        cache_path=file_path_cache_train,
                                        images=images,
                                        model=model)
        return
    
    @staticmethod
    def get_all_transfer_values(test_set):
        categories = MyUtils.listdir_nohidden(os.path.join(test_set, "Images"))
        # The highest level directory will have a folder for each category
        for category in categories:
            os.mkdir(os.path.join(test_set, "Transfer_Values", category))
            wells = list(MyUtils.listdir_nohidden(os.path.join(
                test_set, "Pickles", category)))
    	
            for well in wells:
                Transfer_Calculator.getTransferValues(
                        os.path.join(test_set, "Pickles"
                                    ,category, well)
                        , os.path.join(test_set, "Transfer_Values"
                                       , category, well))
        return

    @staticmethod
    def get_well_transfer_values(pred_set):
        wells = MyUtils.listdir_nohidden(os.path.join(pred_set, "Images"))

        for well in wells:
            Transfer_Calculator.getTransferValues(
                    os.path.join(pred_set, "Pickles", well)
                    , os.path.join(pred_set, "Transfer_Values", well))

    

