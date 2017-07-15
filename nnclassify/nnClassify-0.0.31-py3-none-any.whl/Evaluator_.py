import numpy as np
from src import Constants
from src.MyUtils_ import MyUtils


### This class is for evaluating how the performance of our predictions
### It calculates things like the balanced error rate
class Evaluator:

    ### METHODS #################################################################
    # Purpose - A balnced error rate prevents the under represetation of 
    #           ceratin categories from causing false confidence. If we
    #           test on a data set that has 99,000 images of 2 eyed worms
    #           and only 1,000 images of 0 eyed worms, we could get 99% 
    #           accuracy just be always predicting 2 eyes.
    #
    # Takes - labels_test: the true label for each image
    #         labels_predicted: the labels that we predicted
    #         encoding: used to convert the one hot encoding of a category
    #                   into text
    #
    # Returns - Displays the balanced error rate
    @staticmethod
    def calc_balanced_accuracy(labels_test, labels_predicted):
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        ns = 0
        abnormal = [Constants.ABNORMAL]
        normal = [Constants.NORMAL]
        skip = [Constants.NOT_SURE, Constants.WEIRD]
        for idx in range(0,len(labels_test)):
            pred = labels_predicted[idx]
            true = labels_test[idx]

            # If the model isn't sure then don't factor
            # it into accuracy metric
            if pred in skip:
                ns += 1
            elif pred in abnormal and true in abnormal:
                tp += 1
            elif pred in abnormal and true not in abnormal:
                fp += 1
            elif pred not in abnormal and true in abnormal:
                fn += 1
            elif pred not in abnormal and true not in abnormal:
                tn += 1

        if tp + fn == 0 or tn + fp == 0:
            bal_err_rate = 1
        else:
            bal_err_rate = 1 - 0.5 * (tp * 1.0 /(tp + fn) + tn * 1.0 /(tn+fp))

        return (bal_err_rate, tp, fp, tn, fn, ns)

    #Finds the category with the highest confidence and the category
    # with the second highest. If the difference between the two
    # category does not meet the thresehold then it returns Not Sure
    @staticmethod
    def max_pred(labels, encoding):
        maxIdx = None
        maxVal = None
        for idx, val in enumerate(labels):
            if maxIdx is None or val > maxVal:
                maxIdx = idx 
                maxVal = val 

        return encoding[maxIdx]


    #Finds the category with the highest confidence and the category
    # with the second highest. If the difference between the two
    # category does not meet the thresehold then it returns Not Sure
    @staticmethod
    def is_it_normal(labels, image_confidance,
            confidance_count_threshold, maybe_threshold): 
        confidance_count = 0 
        for i in range(0,len(labels)):
            if labels[i][1] >= image_confidance:
                confidance_count += 1

        if confidance_count  >= confidance_count_threshold:
            return Constants.NORMAL
        elif confidance_count  >= maybe_threshold:
            return Constants.NOT_SURE
        else:
            return Constants.ABNORMAL
