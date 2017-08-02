# Boilerplate imports.
import tensorflow as tf
import numpy as np
import PIL.Image
from matplotlib import pylab as P
import pickle
import tensorflow.contrib.slim as slim
from tensorflow.contrib.framework import get_or_create_global_step

# From https://github.com/tensorflow/models/tree/master/slim.
from models.slim.nets import inception_v3

# From our repository.
from tefla.core.saliency import SaliencyMask
from tefla.core.saliency import GradientSaliency
from tefla.core.saliency import GuidedBackprop
from tefla.core.saliency import IntegratedGradients
from tefla.core.saliency import Occlusion

# Boilerplate methods.


def ShowImage(im, title='', ax=None):
    if ax is None:
        P.figure()
    P.axis('off')
    im = ((im + 1) * 127.5).astype(np.uint8)
    P.imshow(im)
    P.title(title)


def ShowGrayscaleImage(im, title='', ax=None):
    if ax is None:
        P.figure()
    P.axis('off')

    P.imshow(im, cmap=P.cm.gray, vmin=0, vmax=1)
    P.title(title)


def ShowDivergingImage(grad, title='', percentile=99, ax=None):
    if ax is None:
        fig, ax = P.subplots()
    else:
        fig = ax.figure

    P.axis('off')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    im = ax.imshow(grad, cmap=P.cm.coolwarm, vmin=-1, vmax=1)
    fig.colorbar(im, cax=cax, orientation='vertical')
    P.title(title)


def LoadImage(file_path):
    im = PIL.Image.open(file_path)
    im = np.asarray(im)
    return im / 127.5 - 1.0


def load_model():
    graph = tf.Graph()
    tf_global_step = get_or_create_global_step()

    with graph.as_default():
        images = tf.placeholder(tf.float32, shape=(None, 299, 299, 3))

        with slim.arg_scope(inception_v3.inception_v3_arg_scope()):
            _, end_points = inception_v3.inception_v3(
                images, is_training=False, num_classes=1001)

            # Restore the checkpoint
            sess = tf.Session(graph=graph)
            saver = tf.train.Saver()
            saver.restore(sess, './inception_v3.ckpt')

        # Construct the scalar neuron tensor.
        logits = graph.get_tensor_by_name(
            'InceptionV3/Logits/SpatialSqueeze:0')
        neuron_selector = tf.placeholder(tf.int32)
        y = logits[0][neuron_selector]

    # Construct tensor for predictions.
    prediction = tf.argmax(logits, 1)


def test1():
    # Load the image
    im = LoadImage('./images/doberman.png')
    # Show the image
    ShowImage(im)
    # Make a prediction.
    prediction_class = sess.run(prediction, feed_dict={images: [im]})[0]
    # Should be a doberman, class idx = 237
    print("Prediction class: " + str(prediction_class))
