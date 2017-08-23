import keras

model = keras.models.load_model('inception_flowers_pruning_5percent.h5', compile=False)