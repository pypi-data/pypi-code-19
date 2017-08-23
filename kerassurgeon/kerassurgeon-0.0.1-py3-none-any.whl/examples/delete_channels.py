import numpy as np
import keras
from keras import layers
from keras import models
from tensorflow.examples.tutorials.mnist import input_data

from kerassurgeon.identify import high_apoz
from kerassurgeon import identify
from kerassurgeon.operations import delete_channels

input_1 = layers.Input(shape=(28, 28, 1))
conv_1 = layers.Conv2D(32, (3, 3), name='conv_1', activation='relu')
conv_2 = layers.Conv2D(64, (3, 3), name='conv_2', activation='relu')
maxpool_1 = layers.MaxPool2D((2, 2))
cat_1 = layers.Concatenate()
flatten_1 = layers.Flatten()
dense_1 = layers.Dense(128, name='dense_1', activation='relu')
dense_2 = layers.Dense(10, name='dense_2', activation='relu')

x = conv_1(input_1)
x = maxpool_1(x)
x = conv_2(x)
y = conv_1(input_1)
y = maxpool_1(y)
y = conv_2(y)
z = cat_1([x, y])
z = flatten_1(z)
z = dense_1(z)
output_1 = dense_2(z)

model = models.Model(input_1, output_1)

training_verbosity = 2
# Download data if needed and import.
mnist = input_data.read_data_sets('tempData', one_hot=True, reshape=False)
# Create LeNet model


model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss',
                                               min_delta=0,
                                               patience=15,
                                               verbose=training_verbosity,
                                               mode='auto')
reduce_lr_on_plateau = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.1,
    patience=10,
    verbose=training_verbosity,
    mode='auto',
    epsilon=0.0001,
    cooldown=0,
    min_lr=0)

# Train LeNet on MNIST
results = model.fit(mnist.train.images,
                    mnist.train.labels,
                    epochs=20,
                    batch_size=128,
                    verbose=2,
                    validation_data=(mnist.validation.images,
                                     mnist.validation.labels),
                    callbacks=[early_stopping, reduce_lr_on_plateau])

loss = model.evaluate(mnist.validation.images,
                      mnist.validation.labels,
                      batch_size=128,
                      verbose=2)
print('original model loss:', loss, '\n')

layer_name = 'conv_2'

while True:
    apoz = identify.get_apoz(model,
                             model.get_layer(layer_name),
                             mnist.validation.images)
    high_apoz_channels = identify.high_apoz(apoz)
    model = delete_channels(model,
                            model.get_layer(layer_name),
                            high_apoz_channels)
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    loss = model.evaluate(mnist.validation.images,
                          mnist.validation.labels,
                          batch_size=128,
                          verbose=2)
    print('model loss after pruning: ', loss, '\n')

    results = model.fit(mnist.train.images,
                        mnist.train.labels,
                        epochs=20,
                        batch_size=128,
                        verbose=training_verbosity,
                        validation_data=(mnist.validation.images,
                                         mnist.validation.labels),
                        callbacks=[early_stopping, reduce_lr_on_plateau])

    loss = model.evaluate(mnist.validation.images,
                          mnist.validation.labels,
                          batch_size=128,
                          verbose=2)
    print('model loss after retraining: ', loss, '\n')

main()

