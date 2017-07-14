import cv2
import numpy as np
from src.MyUtils_ import MyUtils
from src.ImageCropper_ import ImageCropper
from src.Evaluator_ import Evaluator
from src.Pickler_ import Pickler
from src import Constants
from src.Transfer_Calculator_ import Transfer_Calculator as tc
import pickle
import os

# This class contains the logic displaying our predictions to the user
class Predictor:
 ### METHODS ################################################################
    @staticmethod
    def __test_setup(testset_path):
        pickles_path = os.path.join(testset_path, Constants.PICKLES)
        if not os.path.exists(pickles_path):
            os.makedirs(pickles_path)
            Pickler.pickle_wells(testset_path)

        results_path = os.path.join(testset_path, Constants.RESULTS_DIR)
        if not os.path.exists(results_path):
            os.makedirs(results_path)

        transfer_path = os.path.join(testset_path, Constants.TRANSFER)
        if not os.path.exists(transfer_path):
            os.makedirs(transfer_path)
            tc.get_all_transfer_values(testset_path)
        return
    
    @staticmethod
    def __pred_setup(predset_path):
        pickles_path = os.path.join(predset_path, Constants.PICKLES)
        if not os.path.exists(pickles_path):
            os.makedirs(pickles_path)
            Pickler.pickle_wells_no_category(predset_path)

        results_path = os.path.join(predset_path, Constants.RESULTS_DIR)
        if not os.path.exists(results_path):
            os.makedirs(results_path)

        transfer_path = os.path.join(predset_path, Constants.TRANSFER)
        if not os.path.exists(transfer_path):
            os.makedirs(transfer_path)
            tc.get_well_transfer_values(predset_path)
        return




    # Purpose - Takes in folder with all the images for a well (uncropped)
    #           It first crops all the images, then it predicts the number
    #           of eyes for each image. It prints these results to file. At 
    #           the top of this file is the prediction for the entire well
    #
    # Takes - folder_path: location of the well to predict
    #         encoding: used for converting from one-hot to text
    #         model: the neural network to use for prediction
    #         op_params: Contrast is an optional parameter.
    #                    if they pass contrast as a parameter increase
    #                    the contrast of the test images
    #
    # Returns - a string with the results for the well.
    #           Also creates a file and writes the results there
    @staticmethod
    def predict_well(imgs_path, results_path, encoding, model, well_name,
                        img_conf, count_conf, maybe_conf):
        images = pickle.load(open(imgs_path,"rb"))
        pred = model.predict(images)

        # Write the results file
        with  open(results_path,'w') as results:
            #Write the header
            results.write("Name\tPredicted Category")
            for cat in encoding:
                results.write("\t" + cat)
            results.write('\n')

            # Uses the confindencies of the predictions and the number of 
            # frames predicted normal to predict if a well is normal.
            pred_cat = Evaluator.is_it_normal(pred, img_conf, count_conf,
                                                maybe_conf)

            well_results = well_name + "\t" + pred_cat
            results.write(well_results)

            #Write the results for each individual image
            for i in range(0,len(pred)):
                results.write('\n')
                results.write(str(i+1)+"_img" + '\t'
                        + Evaluator.max_pred(pred[i], encoding))
                for confidence in pred[i]:
                    results.write('\t' + str(confidence))
            return well_results, pred_cat

    @staticmethod
    def predict_wells(predset_path, encoding, model, img_conf, count_conf,
                                                    maybe_conf):
        """This method takes a prediction set and predicts
        the label for each well"""
        all_well_results = list()
        predicted_labels = list()

        Predictor.__pred_setup(predset_path)
        wells = MyUtils.listdir_nohidden(os.path.join(
            predset_path, "Transfer_Values"))
        for well in wells:
            print ("   Predicting well " + well )
            #Get the well results from each well
            trans_value_path = (os.path.join(predset_path, "Transfer_Values"
                                     , well))
            results_path = (os.path.join(predset_path, "Results",
                                     well + ".txt"))
            well_results, pred_cat = Predictor.predict_well(
                                         trans_value_path,
                                         results_path,
                                         encoding,
                                         model,
                                         well,
                                         img_conf,
                                         count_conf,
                                         maybe_conf)

            #Add the well results to a list with all the well results
            #append at the end of the line what category the well actually
            #is
            all_well_results.append(well_results)
            predicted_labels.append(pred_cat)

        # Write the results for the test set in a new file
        with open(os.path.join(
            predset_path, "Results","Pred_Set.txt"),'w') as results:
             # Individual Well Results Header
            results.write("Well\tPredicted_Category\n")

            for well_results in all_well_results:
                split_results = well_results.split('\t')
                well = split_results[0]
                pred_cat = split_results[1]
                results.write(well + '\t'
                                + pred_cat + '\n')
        return
			


    # Purpose - Predict all the wells in test set
    #
    # Takes - testset_path: the absolute path of the test set
    #
    # Returns - nothing, creates a file and writes the results there
    @staticmethod
    def test_wells(testset_path, encoding, model, img_conf,
                    count_conf, maybe_conf):
        all_well_results = list()
        actual_labels = list()
        predicted_labels = list()
        
        Predictor.__test_setup(testset_path) 
        categories = MyUtils.listdir_nohidden(os.path.join(testset_path 
                                                ,"Transfer_Values"))

        for category in categories:
            print ("Predicting " + category)
            if not os.path.exists(
                    os.path.join(testset_path, "Results", category)):
                os.makedirs(os.path.join(testset_path, "Results", category))
            wells = MyUtils.listdir_nohidden(os.path.join(testset_path
                                            ,"Transfer_Values", category))

            for well in wells:
                print ("   Predicting well " + well )
                #Get the well results from each well
                trans_value_path = (os.path.join(
                                        testset_path, "Transfer_Values"
                                        , category, well))
                results_path = (os.path.join(testset_path, "Results" 
                                        ,category, well + ".txt"))
                well_results, pred_cat = Predictor.predict_well(
                                             trans_value_path,
                                             results_path,
                                             encoding,
                                             model,
                                             well,
                                             img_conf,
                                             count_conf,
                                             maybe_conf)
 
                #Add the well results to a list with all the well results
                #append at the end of the line what category the well actually
                #is
                all_well_results.append(well_results + '\t' + category)
                actual_labels.append(category)
                predicted_labels.append(pred_cat)

        # Calculate the Balanced Error Rate
        BER, TP, FP, TN, FN, NS = Evaluator.calc_balanced_accuracy(
                                                    actual_labels,
                                                    predicted_labels)
        
        # Write the results for the test set in a new file
        with open(os.path.join(
                testset_path, "Results", "Test_Set.txt"),'w') as results:
            results.write("All Well Results\n")
            results.write("Balanced Error Rate: " + str(BER) + '\n')
            results.write("True Positive Count "
                            + "(Worm predicted abnormal and actually was): "
                            + str(TP) + '\n')
            results.write("True Negative Count "
                            + "(Worm predicted normal and actually was): "
                            + str(TN) + '\n')
            results.write("False Positive Count "
                            + "(Worm predicted abnormal but it was normal): "
                            + str(FP) + '\n')
            results.write("False Negative Count "
                            + "(Worm predicted normal but it was abnormal): "
                            + str(FN) + '\n')
            results.write("Unsure Count "
                     + "(Model lacked the confidence to make a prediction): "
                     + str(NS) + '\n')

            # Empty line between overall results and individual well results
            results.write('\n')

            # Individual Well Results Header
            results.write("Well\tActual_Category\tPredicted_Category\n")
            
            for well_results in all_well_results:
                split_results = well_results.split('\t')
                well = split_results[0]
                pred_cat = split_results[1]
                act_cat = split_results[len(split_results)-1]
                results.write(well + '\t'
                        + act_cat + '\t' + pred_cat + '\n')








