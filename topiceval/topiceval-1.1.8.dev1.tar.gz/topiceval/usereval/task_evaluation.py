from __future__ import print_function
from __future__ import division

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

import time


def folder_prediction_task(model, email_network):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    X_train, X_test, y_train, y_test = email_network.folders_X_train, email_network.folders_X_test, \
                                       email_network.folders_y_train, email_network.folders_y_test
    W = model.document_topic_matrix
    X_train_matrix = np.zeros((len(X_train), model.num_topics))
    for i, idx in enumerate(X_train):
        X_train_matrix[i, :] = W[:, idx]
    X_test_matrix = np.zeros((len(X_test), model.num_topics))
    for i, idx in enumerate(X_test):
        X_test_matrix[i, :] = W[:, idx]

    # start = time.time()
    param_grid = [{'C': np.arange(0.1, 7, 0.3)}]
    # scores = ['accuracy', 'recall_micro', 'f1_micro', 'precision_micro', 'recall_macro', 'f1_macro',
    # 'precision_macro',
    #           'recall_weighted', 'f1_weighted', 'precision_weighted']  # , 'accuracy', 'recall', 'f1']
    scores = ['accuracy']
    for score in scores:
        # substart = time.time()
        # print("# Tuning hyper-parameters for", score, "\n")
        clf = GridSearchCV(LinearSVC(C=1), param_grid, cv=5, scoring='%s' % score)
        clf.fit(X_train_matrix, y_train)
        print("Best parameters set found on development set:\n")
        print(clf.best_params_)
        # print("Best value for ", score, ":\n")
        # print(clf.best_score_)
        Y_true, Y_pred = y_test, clf.predict(X_test_matrix)
        print("Report")
        print(classification_report(Y_true, Y_pred, digits=6))
        # print(Y_true, Y_pred)
        print("Accuracy: ", clf.score(X_test_matrix, y_test))
        # print("Time taken:", time.time() - substart, "\n")
    endtime = time.time()
    # print("Total time taken: ", endtime - start, "seconds.")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return
