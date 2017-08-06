#! coding:utf-8
"""
station.py

"""
from __future__ import absolute_import

import os
import sys
import shutil
from pathlib import Path
import importlib


import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
# Used in visualization
from keras.callbacks import ModelCheckpoint
from keras.callbacks import TensorBoard
from keras.utils import plot_model
from keras.callbacks import Callback

import sklearn
from sklearn.model_selection import train_test_split
# from sklearn.metrics import confusion_matrix
import numpy as np

from .configs import Station, Config
from . import globalvars as g


class Trainer:

    """Trainer Class"""

    current_dir = ""  # type: str
    model_name = ""  # type: str
    setting_name = ""  # type; str
    isTest = False

    def __init__(self, current_dir, model_name, setting_name, isTest=False):
        self.current_dir = current_dir
        self.model_name = model_name
        self.setting_name = setting_name
        self.isTest = isTest


    def run(self):
        os.chdir(Path(self.current_dir).as_posix())
        RootDir = Path(self.current_dir).resolve()

        # Check Current dir has Stationfile
        if not RootDir.joinpath("Stationfile").exists():
            raise FileNotFoundError("nothing => {}".format(RootDir.as_posix()))

        # Result Dir
        result_dir_name = self.model_name+"_"+self.setting_name
        ResultDir = RootDir.joinpath(g.ResultsDir).joinpath(result_dir_name)

        try:
            # private runner
            self._run()
            # success
            with open(ResultDir.joinpath("success.txt").as_posix(), "w") as fp:
                fp.write("success")
        except Exception as e:
            # error
            with open(ResultDir.joinpath("error.txt").as_posix(), "w") as fp:
                fp.write(str(e))
            print(str(e))


    def _run(self):
        # ==================================================== #
        # Config
        # ==================================================== #
        RootDir = Path(self.current_dir).resolve()

        os.chdir(RootDir.as_posix())
        print("Current Dir is :{}".format(os.getcwd()))

        # Station Coonfig
        station = Station(RootDir.joinpath(g.Stationfile))
        config = station.get_config()

        # Setting Config
        setting = Config(RootDir.joinpath(g.SettingsDir).joinpath(
            self.setting_name+g.settingfile_ext))

        train_setting = setting.get_config()

        if self.isTest:
            epochs = 2
            batch_size = 5
        else:
            epochs = train_setting["train"]["epochs"]
            batch_size = 32

        batch_size = 32
        print("isTest : {}".format(self.isTest))
        print("epochs : {}".format(epochs))
        print("batch_size : {}".format(batch_size))

        random_state = 21
        # ==================================================== #
        # Dir
        # ==================================================== #
        result_dir_name = self.model_name+"_"+self.setting_name
        ResultDir = RootDir.joinpath(g.ResultsDir).joinpath(result_dir_name)
        if not ResultDir.exists():
            ResultDir.mkdir()

        print("Result Dir is :{}".format(ResultDir.as_posix()))

        # ==================================================== #
        # Change Current Dir
        # ==================================================== #
        # ==================================================== #
        # Load Dataset
        # ==================================================== #
        print("Current Dir is :{}".format(os.getcwd()))

        from importlib import machinery
        loader = machinery.SourceFileLoader('dataset_loader', '/home/fifi/OpenATS/tests/TestStation/dataset/dataset_loader.py')
        module = loader.load_module()
        X, y = module.load_data()
        # dataset_loader = importlib.import_module("dataset.dataset_loader")
        # dataset_loader = module.import_module("dataset.dataset_loader")
        # X, y = dataset_loader.load_data()
        # ==================================================== #
        # Dimennsion Check
        # ==================================================== #
        X = X[:, :,  np.newaxis]

        x_train, x_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state)
        print('x_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')
        print(x_test.shape[0], 'test samples')
        # ==================================================== #
        # Load Model
        # ==================================================== #
        # Module load
        model_file = RootDir.joinpath(g.ModelsDir).joinpath(self.model_name+".py").as_posix()
        loader = machinery.SourceFileLoader(self.model_name, model_file)
        model_module = loader.load_module()

        # model_module = importlib.import_module("models."+self.model_name)

        model = model_module.get_model(x_train.shape[1], 'adam')
        model.summary()  # print model summary
        # ==================================================== #
        # Report of Model
        # ==================================================== #
        with open(ResultDir.joinpath("mode.json").as_posix(), "w") as fp:
            fp.write(model.to_json())

        try:
            from keras.utils import plot_model
            plot_model(model, to_file=ResultDir.joinpath(
                "model.png").as_posix(), show_shapes=True)
        except Exception as e:
            print(e)

        # ==================================================== #
        # Call Back 1  CSV
        # ==================================================== #
        result_csv_path = ResultDir.joinpath("training.csv")
        cb_csvlogger = keras.callbacks.CSVLogger(
            result_csv_path.as_posix(), separator=',', append=False)

        # ==================================================== #
        # Fit
        # ==================================================== #
        model.fit(x_train, y_train,
                  batch_size=batch_size,
                  epochs=epochs,
                  validation_data=(x_test, y_test),
                  shuffle=True,
                  callbacks=[cb_csvlogger])

        # ==================================================== #
        # evaluate model
        # ==================================================== #
        predicted = model.predict(x_test, batch_size=batch_size, verbose=1)
        y_true = np.argmax(y_test, axis=1)
        y_pred = np.argmax(predicted, axis=1)
        target_names = ['No Sairen', 'On Sairen']

        print("sklearn.metrics.classification_report ==> ")
        class_report = sklearn.metrics.classification_report(
            y_true, y_pred,
            target_names=target_names,
            digits=3)

        with open(ResultDir.joinpath("classification_report.txt").as_posix(), "w") as fp:
            fp.write(class_report)
            print(class_report)

        print("confusion_matrix ==> ")
        print(sklearn.metrics.confusion_matrix(y_true, y_pred))
        confusion_matrix = sklearn.metrics.confusion_matrix(y_true, y_pred)

        with open(ResultDir.joinpath("confusion_matrx.txt").as_posix(), "w") as fp:
            fp.write(str(confusion_matrix[0, 0]))
            fp.write(",")
            fp.write(str(confusion_matrix[0, 1]))
            fp.write("\n")
            fp.write(str(confusion_matrix[1,0]))
            fp.write(",")
            fp.write(str(confusion_matrix[1,1]))
            fp.write("\n")

        print("Trainer.run end ...")
