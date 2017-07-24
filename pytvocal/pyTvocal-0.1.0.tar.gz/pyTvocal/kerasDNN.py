import os
from time import time

import numpy
from keras.callbacks import EarlyStopping
from keras.layers import Dense, Dropout
from keras.models import Sequential, model_from_json
from sklearn.preprocessing import LabelEncoder

from preprocess import get_dataset_XY
# load dataset
from sklearnModel import get_acc

trainX, trainY, testX, testY, validX, validY = get_dataset_XY()
# fix random seed for reproducibility
seed = 1007
numpy.random.seed(seed)
# encode class values as integers
encoder = LabelEncoder()
encoder.fit(trainY)
trainY = encoder.transform(trainY)
testY = encoder.transform(testY)
validY = encoder.transform(validY)


# baseline model
def create_baseline():
    # create model
    model = Sequential()
    model.add(Dense(60, input_dim=12, init='normal', activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(30, init='normal', activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(20, init='normal', activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(10, init='normal', activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(1, init='normal', activation='sigmoid'))
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


# evaluate model with standardized dataset
def main():
    model_path = 'kerasModel/dnn.model'
    retrain = 0
    if retrain != 1 and os.path.isfile(model_path):
        # load json and create model
        json_file = open(model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        # load weights into new model
        model.load_weights(model_path.replace('.model', '.weights'))
        print("Loaded model from disk")
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    else:
        model = create_baseline()
        print model.summary()
        callbacks = [EarlyStopping(monitor='val_loss', patience=2, verbose=0)]
        model.fit(trainX, trainY, batch_size=100, nb_epoch=200, validation_data=(validX, validY), callbacks=callbacks,
                  verbose=2)
        if retrain == 1 or not os.path.isfile(model_path):
            # serialize model to JSON
            model_json = model.to_json()
            with open(model_path, "w") as json_file:
                json_file.write(model_json)
            # serialize weights to HDF5
            model.save_weights(model_path.replace('.model', '.weights'))
            print("Saved model to disk")

    pre_testY = model.predict_classes(testX)
    print model.summary()
    print '\n acc: ', get_acc(pre_testY, testY)

    return 0


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print 'It take times :%.2f s' % (end - start)
