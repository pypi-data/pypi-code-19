'''This script goes along the blog post
"Building powerful image classification models using very little data"
from blog.keras.io.
It uses data that can be downloaded at:
https://www.kaggle.com/c/dogs-vs-cats/data
In our setup, we:
- created a data/ folder
- created train/ and validation/ subfolders inside data/
- created cats/ and dogs/ subfolders inside train/ and validation/
- put the cat pictures index 0-999 in data/train/cats
- put the cat pictures index 1000-1400 in data/validation/cats
- put the dogs pictures index 12500-13499 in data/train/dogs
- put the dog pictures index 13500-13900 in data/validation/dogs
So that we have 1000 training examples for each class, and 400 validation examples for each class.
In summary, this is our directory structure:
```
data/
    train/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
    validation/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
```
'''
import functools
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
from keras.layers import Dense, Input
from keras import applications, optimizers
from keras.callbacks import CSVLogger

# dimensions of our images.
img_width, img_height = 299, 299

top_model_weights_path = 'bottleneck_fc_model_inceptionv3.h5'
train_data_dir = '/home/benj/git/tensorflow/models/inception/inception/data/flowers-data/raw-data/train'
validation_data_dir = '/home/benj/git/tensorflow/models/inception/inception/data/flowers-data/raw-data/validation'
nb_train_samples = 3170
nb_validation_samples = 500
epochs = 500
batch_size = 16


def save_bottleneck_features():
    datagen = ImageDataGenerator(preprocessing_function=
                                 applications.inception_v3.preprocess_input)

    # build the Inception V3 network
    model = applications.inception_v3.InceptionV3(include_top=False,
                                                  weights='imagenet',
                                                  input_tensor=None,
                                                  input_shape=None,
                                                  pooling='avg')

    # Save the bottleneck features for the training data set
    generator = datagen.flow_from_directory(train_data_dir,
                                            target_size=(img_width, img_height),
                                            batch_size=batch_size,
                                            class_mode='sparse',
                                            shuffle=False)

    features = model.predict_generator(generator,
                                       nb_train_samples // batch_size)
    labels = np.eye(generator.num_class, dtype='uint8')[generator.classes]
    labels = labels[0:(nb_train_samples // batch_size)*batch_size]
    np.save(open('bottleneck_features_train.npy', 'wb'), features)
    np.save(open('bottleneck_labels_train.npy', 'wb'), labels)

    # Save the bottleneck features for the validation data set
    generator = datagen.flow_from_directory(validation_data_dir,
                                            target_size=(img_width, img_height),
                                            batch_size=batch_size,
                                            class_mode=None,
                                            shuffle=False)
    features = model.predict_generator(generator,
                                       nb_validation_samples // batch_size)
    labels = np.eye(generator.num_class, dtype='uint8')[generator.classes]
    labels = labels[0:(nb_validation_samples // batch_size) * batch_size]
    np.save(open('bottleneck_features_validation.npy', 'wb'), features)
    np.save(open('bottleneck_labels_validation.npy', 'wb'), labels)


def train_top_model():
    train_features = np.load(open('bottleneck_features_train.npy', 'rb'))
    train_labels = np.load(open('bottleneck_labels_train.npy', 'rb'))

    validation_features = np.load(open('bottleneck_features_validation.npy', 'rb'))
    validation_labels = np.load(open('bottleneck_labels_validation.npy', 'rb'))

    top_input = Input(shape=train_features.shape[1:])
    top_output = Dense(5, activation='softmax')(top_input)
    model = Model(top_input, top_output)

    model.compile(optimizer=optimizers.SGD(lr=1e-4, momentum=0.9),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    csv_logger = CSVLogger('top_model_training.csv')
    model.fit(train_features, train_labels,
              epochs=epochs,
              batch_size=batch_size,
              validation_data=(validation_features, validation_labels),
              callbacks=[csv_logger])
    model.save_weights(top_model_weights_path)

# save_bottleneck_features()
train_top_model()
