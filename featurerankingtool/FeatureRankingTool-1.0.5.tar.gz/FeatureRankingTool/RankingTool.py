import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
import random
import numpy as np
from sklearn.datasets import make_multilabel_classification
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelBinarizer
from sklearn import datasets
import numpy as np
import random


def GetLearningResult(DF,model,featuresName,targets,modeltype='',use_cv=False):

    targets, features = DF[[targets]], DF[featuresName]
    targets, features = targets.as_matrix(columns=None), features.as_matrix(columns=None)

    targets = targets.ravel()

    lac = []
    feature_coef = []
    error_list = []
    learning_outcome = {}

    if use_cv and int(use_cv) > 1:
        kf = KFold(n_splits=use_cv, shuffle=True)
        kf.get_n_splits(features)
        train_test_fold = kf.split(features)
    else:
        train_index = random.sample(range(0,len(features)),int(0.8*len(features)))
        test_index = [item for item in range(len(features)) if item not in train_index]
        train_test_fold = [[train_index,test_index]]

    for train_index, test_index in train_test_fold:

        print train_index, test_index, len(features)

        tr_features,tst_features = features[train_index], features[test_index]
        tr_target, tst_target = targets[train_index], targets[test_index]

        model.fit(tr_features, tr_target)

        if modeltype == 'linear':
            feature_coef.append(model.coef_)
        elif modeltype == 'tree':
            feature_coef.append(model.feature_importances_)


        tr_prediction = model.predict(tr_features)
        tst_prediction = model.predict(tst_features)

        tr_accuracy = np.mean(abs(tr_prediction - tr_target))
        tst_accuracy = np.mean(abs(tst_prediction - tst_target))

        tst_prediction = np.array(tst_prediction)
        tst_target = np.array(tst_target)

        tst_error = tst_prediction == tst_target
        error_list.append(tst_error)

        lac.append(tst_accuracy)


    learning_outcome['test_error'] = np.mean(lac)
    learning_outcome['misclassified'] =error_list

    if modeltype == 'linear':
        print pd.DataFrame(np.concatenate(tuple(feature_coef)), columns=featuresName).mean().sort_values()
        output_ranking = pd.DataFrame(np.concatenate(tuple(feature_coef)), columns=featuresName).mean().sort_values()
    elif modeltype == 'tree':
        print pd.DataFrame(feature_coef, columns=featuresName).abs().mean().sort_values()
        output_ranking = pd.DataFrame(feature_coef, columns=featuresName).abs().mean().sort_values()


    learning_outcome['feature_ranking'] =output_ranking

    return  learning_outcome



iris = datasets.load_iris()

X = iris.data
Y = np.array(iris.target)
Y = Y.reshape(len(Y),1)

XY = np.concatenate((X,Y),axis=1)

print XY.shape

XY = pd.DataFrame(XY,columns=['sepal_length','sepal_width','petal_length','petal_width','target'])

print XY
#classif = SVC(kernel='linear')
classif = RandomForestRegressor()

classifier = OneVsRestClassifier(SVC(kernel='linear', probability=True))
classifier.fit(X, Y.ravel())

result = GetLearningResult(XY,classif,['sepal_length','sepal_width','petal_length','petal_width'],'target',modeltype='tree',use_cv=5)

print result