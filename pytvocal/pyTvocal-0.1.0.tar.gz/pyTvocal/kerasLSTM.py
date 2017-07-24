import os
from time import time

import numpy
from keras.callbacks import EarlyStopping
from keras.layers import LSTM, Dense
from keras.models import Sequential, model_from_json

from preprocess import get_dataset_XY

trainX, trainY, testX, testY, validX, validY = get_dataset_XY()


def format_dataX_with_steps(dataX, dataY, step=7):
    finalX = []
    finalY = []
    for item_y in range(0, len(dataY), step):
        if list(dataY[item_y:item_y + step]).count('sing') == step:
            finalX.append(dataX[item_y:item_y + step])
            finalY.append(1)
        if list(dataY[item_y:item_y + step]).count('nosing') == step:
            finalX.append(dataX[item_y:item_y + step])
            finalY.append(0)
    return numpy.array(finalX), numpy.array(finalY)


trainX, trainY = format_dataX_with_steps(trainX, trainY)
testX, testY = format_dataX_with_steps(testX, testY)
validX, validY = format_dataX_with_steps(validX, validY)


def build_model():
    model_path = 'kerasModel/lstm.model'
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
        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])
    else:
        print('Build model...')
        model = Sequential()
        model.add(LSTM(60, input_shape=(7, 12), dropout_U=0.2, dropout_W=0.2, return_sequences=True))
        model.add(LSTM(60, dropout_U=0.2, dropout_W=0.2))
        model.add(Dense(1, activation='sigmoid'))

        # try using different optimizers and different optimizer configs
        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        print('Train...')
        callbacks = [EarlyStopping(monitor='val_loss', patience=2, verbose=0)]
        model.fit(trainX, trainY,
                  batch_size=100,
                  validation_data=(validX, validY), nb_epoch=2, callbacks=callbacks, verbose=2)
        if retrain == 1 or not os.path.isfile(model_path):
            # serialize model to JSON
            model_json = model.to_json()
            with open(model_path, "w") as json_file:
                json_file.write(model_json)
            # serialize weights to HDF5
            model.save_weights(model_path.replace('.model', '.weights'))
            print("Saved model to disk")
    score, acc = model.evaluate(testX, testY,
                                batch_size=100)
    print model.summary()
    print('Test score:', score)
    print('Test accuracy:', acc)
    return model


def main():
    build_model()
    return 0


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print 'It take times :%.2f s' % (end - start)