#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Fri 17 Jun 2016 10:41:36 CEST

import numpy
import os
from . import Extractor, download_file
import logging
logger = logging.getLogger(__name__)


class VGGFace(Extractor):
    """
    Extract features using the VGG model
    http://www.robots.ox.ac.uk/~vgg/software/vgg_face/
    """

    def __init__(self, end_cnn):
        """
        VGG constructor

        Parameters
        ----------
        end_cnn : str
            The name of the layer that you want to use as a feature
        """

        deploy_architecture = os.path.join(
            VGGFace.get_vggpath(),
            "VGG_FACE_deploy.prototxt")
        model = os.path.join(
            VGGFace.get_vggpath(),
            "vgg_face_caffe", "VGG_FACE.caffemodel")

        # Average image provided in
        # http://www.robots.ox.ac.uk/~vgg/software/vgg_face/
        self.average_img = [129.1863, 104.7624, 93.5940]

        if not (os.path.exists(deploy_architecture) and os.path.exists(model)):
            VGGFace.download_vgg()

        super(VGGFace, self).__init__(
            deploy_architecture, model, end_cnn
        )

    def __call__(self, image):
        """
        Forward the image with the loaded neural network.

        **Parameters**
          image: Input image in RGB format

        **Returns**
            Features

        """

        # The input must be 1,c,w,h
        # if RGB
        if len(image.shape) == 3:
            R = image[0, :, :] - self.average_img[0]
            G = image[1, :, :] - self.average_img[1]
            B = image[2, :, :] - self.average_img[2]

            # Converting to
            bgr_image = numpy.zeros(shape=image.shape)
            bgr_image[0, :, :] = B
            bgr_image[1, :, :] = G
            bgr_image[2, :, :] = R

            return super(VGGFace, self).__call__(bgr_image)
        else:
            raise ValueError("Image should have 3 channels")

    @staticmethod
    def get_vggpath():
        import pkg_resources
        return pkg_resources.resource_filename(__name__, 'data')

    @staticmethod
    def download_vgg():
        """
        Download and extract the VGG files in ./bob/ip/caffe_extractor
        """
        import os
        import tarfile
        urls = [
            # This is a private link at Idiap to save bandwidth.
            "http://beatubulatest.lab.idiap.ch/private/wheels/gitlab/"
            "vgg_face_caffe.tar.gz",
            # this works for everybody
            "http://www.robots.ox.ac.uk/~vgg/software/vgg_face/src/"
            "vgg_face_caffe.tar.gz",
        ]

        tmp_file = os.path.join(VGGFace.get_vggpath(), "vgg_face_caffe.tar.gz")
        for url in urls:
            try:
                logger.info(
                    "Downloading the LightCNN model from "
                    "{} ...".format(url))
                download_file(url, tmp_file)
                break
            except Exception:
                pass
        else:  # else is for the for loop
            if not os.path.isfile(tmp_file):
                raise RuntimeError("Could not download the tar file.")

        # Unzip
        logger.info("Unziping in {0}".format(VGGFace.get_vggpath()))
        with tarfile.open(name=tmp_file, mode='r:gz') as t:
            t.extractall(VGGFace.get_vggpath())
