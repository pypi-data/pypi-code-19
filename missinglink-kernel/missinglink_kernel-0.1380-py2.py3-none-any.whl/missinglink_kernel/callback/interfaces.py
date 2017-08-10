import abc
import warnings

import six
import hashlib
import base64
import uuid
import numpy
from collections import defaultdict
from .exceptions import MissingLinkException, ImageUnavailableException
from six.moves.urllib.parse import urlparse
# noinspection PyUnresolvedReferences
from six.moves.urllib.request import urlopen
# noinspection PyUnresolvedReferences
from six.moves.http_client import HTTPException


class ImageDimOrdering(object):
    # N -- number of examples, C -- channels, H -- height, W -- width
    NCHW = "nchw"
    NHWC = "nhwc"


@six.add_metaclass(abc.ABCMeta)
class ModelHashInterface(object):
    @abc.abstractmethod
    def get_weights_hash(self, net):
        pass

    @abc.abstractmethod
    def _get_structure_hash(self, net):
        pass


def _import_cv2():
    try:
        import cv2
    except ImportError:
        cv2 = None

    return cv2


@six.add_metaclass(abc.ABCMeta)
class BaseInterface(object):
    @classmethod
    def _get_image(cls, uri, preprocess=False, flip_colors=False):
        parse_result = urlparse(uri)
        if parse_result.scheme in ("file", ""):
            image = cls.cv2.imread(parse_result.path)
        else:
            # assume this is some kind of resource on a network
            try:
                resp = urlopen(uri)
                image = numpy.asarray(bytearray(resp.read()), dtype="uint8")
                image = cls.cv2.imdecode(image, cls.cv2.IMREAD_COLOR)
                if preprocess:
                    # in bgr
                    # noinspection PyUnresolvedReferences
                    image[0, :, :] = numpy.add(image[0, :, :], -103.939)
                    # noinspection PyUnresolvedReferences
                    image[1, :, :] = numpy.add(image[1, :, :], -116.779)
                    # noinspection PyUnresolvedReferences
                    image[2, :, :] = numpy.add(image[2, :, :], -123.68)
                if flip_colors:
                    b, g, r = cls.cv2.split(image)  # get b,g,r
                    image = cls.cv2.merge([r, g, b])
            except HTTPException:
                raise ImageUnavailableException("Was not able to get image!")
        # keep in mind: by default cv2 loads an image in HWC order
        return image


@six.add_metaclass(abc.ABCMeta)
class BaseImageInterface(BaseInterface):
    cv2 = _import_cv2()

    def validate_cv2(self):
        if self.cv2 is None:
            self.logger.error('opencv package is missing, please install it in order to use process_image')

        if self.cv2 is None:
            raise MissingLinkException("Install OpenCV to be able to use this feature!")

    @classmethod
    @abc.abstractmethod
    def _get_input_dim(cls, model):
        """
        Method should return input that the network expects
        :param model: Model object
        :return: (depth, height, width) that are expected by a model
        """
        pass

    @classmethod
    def __check_shape(cls, shape):
        # shape should be in CHW order here
        if len(shape) == 3:
            depth, height, width = shape
        elif len(shape) == 4:
            # we assume NCHW order
            _, depth, height, width = shape
        else:
            raise MissingLinkException("Unrecognized input shape for network, %s" % shape)
        return depth, height, width

    def _get_scaled_input(self, image, shape):
        if shape is None:
            # this means we got a preprocessed input
            depth, height, width = self.__check_shape(image.shape)
            input_ = image
        else:
            depth, height, width = self.__check_shape(shape)
            input_ = self.cv2.resize(image, (width, height))
        return input_, depth, height, width

    @classmethod
    def _im2double(cls, im):
        return cls.cv2.normalize(im.astype('float'), None, 0.0, 1.0, cls.cv2.NORM_MINMAX)

    @classmethod
    def _map2jpg(cls, heatmap, threshold=0.15):
        heatmap[numpy.where(heatmap < threshold)] = 0
        heatmap_x = numpy.round(heatmap * 255).astype(numpy.uint8)
        return cls.cv2.applyColorMap(heatmap_x, cls.cv2.COLORMAP_JET)

    @classmethod
    def _convert_to_jpg(cls, img):
        return cls.cv2.imencode('.jpg', img)[1]

    @classmethod
    def _remove_blue(cls, img, intensity=128):
        b_channel, g_channel, r_channel = cls.cv2.split(img)
        b_channel[numpy.where(b_channel == intensity)] = 0
        return cls.cv2.merge((b_channel, g_channel, r_channel))

    @classmethod
    def _relu(cls, x):
        """
        simple Relu function: f(x) = max(0, x)
        :param x: numpy.array
        :return: numpy.array
        :rtype: numpy.array
        """
        x = x * (x > 0)
        return x


@six.add_metaclass(abc.ABCMeta)
class GradCAMInterface(BaseImageInterface):

    def generate_guided_grad_cam(self):
        # not using @abc.abstractmethod here because it should not be compulsory to implement this
        raise NotImplementedError("This method should be implemented in subclasses")

    @classmethod
    @abc.abstractmethod
    def _get_activation_and_grad_for_last_conv(cls, model, scores, input_=None):
        """
        This method should return activations and weights for the last conv layer.
        :param model: Model object
        :param scores: 1d or 2d array of probabilities (output of a network)
        :param input_: 3d array of an image or None if input can be extracted from the network like in PyCaffe
        :return: (activations, weights per conv map) for the last conv layer
        """
        return (), ()

    @abc.abstractmethod
    def _get_prediction(self, model, image, shape=None):
        """
        Given the input which can be a raw image with different dimentions than the network expects
        get a prediction from model
        :param model: Model object
        :param image: 3d array
        :param shape: (height, width) if you need to scale input
        :return: (3d array of input, 1d array of probabilities)
        """
        return (), ()

    @classmethod
    def _get_heatmaps(cls, image, heatmap, name=None, write_local=False, prefix=""):
        height = image.shape[0]
        width = image.shape[1]
        cur_cam_map_large_crops = cls.cv2.resize(heatmap, (width, height), interpolation=cls.cv2.INTER_CUBIC)
        current_heatmap = cls.cv2.resize(cls._im2double(cur_cam_map_large_crops), (width, height))
        current_heatmap = cls._im2double(current_heatmap)
        current_heatmap = cls._map2jpg(current_heatmap)
        current_heatmap = cls._remove_blue(current_heatmap)
        result_heatmap = cls.cv2.addWeighted(image, 1, current_heatmap, 0.8, 0)
        if write_local:
            cls.cv2.imwrite(prefix + "-" + str(name) + ".jpg", current_heatmap)
            cls.cv2.imwrite(prefix + str(name) + ".jpg", result_heatmap)
        return result_heatmap, current_heatmap

    @classmethod
    def _get_representation(cls, top_probs, top_predictions, class_mapping=None):
        class_mapping = class_mapping or defaultdict(lambda: None)
        result = []
        for i, el in enumerate(top_probs):
            try:
                class_name = class_mapping[top_predictions[i]]
            except IndexError:
                class_name = None
            row = {"class": top_predictions[i],
                   "class_name": class_name,
                   "probability": el}
            result.append(row)
        return result

    def generate_grad_cam(self, uri, model, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NCHW, expected_class=None):
        """
        This method implements GradCAM algo. Method is only applicable for classification problem
        :param uri: URI of an image. It can be url. e.g.
        https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Googlelogo.png/220px-Googlelogo.png.
        It can also be a local file starting with "file://" or just a pure path like "/home/user/image.jpg"
        :param input_array: Image preprocessed the same way as it would be used to feed to the network.
        Usually a 3d or 4d array. If this is None we assume no preprocessing is needed and just load an image.
        :param model: instance of a model
        :param top_classes: display this number of most probable classes.
        :param top_images: display this number of CAMs for most probable classes
        :param class_mapping: a list or a dict which maps class numbers with human-readable values.
        :param dim_order: order of dimentions for image
        :param expected_class: expected class number (ground truth)
        :return: List of dictionaries with images and metadata
        """

        if class_mapping is not None:
            warnings.warn("class_mapping attribute is deprecated. please use 'set_properties' instead", DeprecationWarning)

        class_mapping = self._class_mapping or class_mapping

        self.validate_cv2()

        prediction_id = uuid.uuid4().hex

        image = self._get_image(uri)
        if input_array is not None:
            input_, scores = self._get_prediction(model, input_array)
        else:
            shape = self._get_input_dim(model)
            input_, scores = self._get_prediction(model, image, shape)

        ascending_order = numpy.argsort(scores)
        idx_category = ascending_order[::-1]
        top_predictions = idx_category[:top_classes]
        top_probs = [scores[i] for i in top_predictions]
        if len(top_predictions) < top_images:  # in case we have less classes than images we are trying to draw
            top_images = len(top_predictions)

        old_scores = numpy.copy(scores)
        result_images_data = list()
        for number in range(top_images):
            scores = numpy.copy(old_scores)
            # noinspection PyUnresolvedReferences
            scores[numpy.where(scores != top_probs[number])] = 0
            activation_last_conv, a_weights = self._get_activation_and_grad_for_last_conv(model, scores, input_)
            if dim_order == ImageDimOrdering.NCHW:
                # noinspection PyUnresolvedReferences
                cur_cam_map_crops = numpy.zeros(activation_last_conv.shape[2:], dtype=numpy.float32)
            elif dim_order == ImageDimOrdering.NHWC:
                # noinspection PyUnresolvedReferences
                cur_cam_map_crops = numpy.zeros(activation_last_conv.shape[1:3], dtype=numpy.float32)
            else:
                self.logger.error("Unable to recognize image ordering!")
                raise MissingLinkException("Unknown dim ordering for image")
            for i, w in enumerate(a_weights):
                if dim_order == ImageDimOrdering.NCHW:
                    weighted = w * activation_last_conv[0][i, :, :]
                elif dim_order == ImageDimOrdering.NHWC:
                    weighted = w * activation_last_conv[0][:, :, i]
                else:
                    self.logger.error("Unable to recognize image ordering!")
                    raise MissingLinkException("Unknown dim ordering for image")
                cur_cam_map_crops += weighted

            cur_cam_map_crops = self._relu(cur_cam_map_crops)
            result_heatmap, current_heatmap = self._get_heatmaps(image, cur_cam_map_crops, name=number, prefix="_grad_")
            pure_image = self._convert_to_jpg(image)
            heatmap = self._convert_to_jpg(current_heatmap)
            overlay = self._convert_to_jpg(result_heatmap)
            image_key = hashlib.sha224(base64.b64encode(overlay)).hexdigest()
            hash_key = self.get_weights_hash(model)
            representations = self._get_representation(top_probs, top_predictions, class_mapping)
            meta = {
                "prediction_id": prediction_id,
                "number": number,
                "algo": "grad_cam",
                "path": uri,
                "expected_class": expected_class,
                "class_name": representations[number]["class_name"],
                "class": representations[number]["class"],
                "top": representations,
                "probability": representations[number]["probability"]
            }
            entry = {
                "hash_key": hash_key, "image_key": image_key, "images": [overlay, pure_image, heatmap], "meta": meta
            }
            result_images_data.append(entry)

        return result_images_data


@six.add_metaclass(abc.ABCMeta)
class VisualBackPropInterface(BaseImageInterface):

    @abc.abstractmethod
    def _get_feature_maps(self, model, image, shape=None):
        return (), ()

    @classmethod
    def _step(cls, c_layer, n_layer, dim_ordering):
        if dim_ordering == ImageDimOrdering.NHWC:
            meaned_next_ = numpy.mean(n_layer, axis=(2,))
        elif dim_ordering == ImageDimOrdering.NCHW:
            meaned_next_ = numpy.mean(n_layer, axis=(0,))
        else:
            raise MissingLinkException("Unknown image ordering!")

        # here meaned_next_.shape[::-1] is used because cv2 expects new shape to be (width, height) and the
        # default orientation of an image in most models is (height, width)
        upscaled_ = cls.cv2.resize(c_layer, meaned_next_.shape[::-1], interpolation=cls.cv2.INTER_LINEAR)
        # noinspection PyUnresolvedReferences
        current_layer_ = numpy.multiply(upscaled_, meaned_next_)
        return current_layer_

    def visual_back_prop(self, uri, model, input_val=None, dim_order=ImageDimOrdering.NCHW, expected_output=None):
        self.validate_cv2()

        original_image = self._get_image(uri)

        if input_val is not None:
            feature_maps, output = self._get_feature_maps(model, input_val)
        else:
            shape = self._get_input_dim(model)
            feature_maps, output = self._get_feature_maps(model, original_image, shape=shape)

        relu_fm = [self._relu(fm) for fm in feature_maps]

        i = len(relu_fm) - 1
        current_layer = relu_fm[i]
        if dim_order == ImageDimOrdering.NHWC:
            current_layer = numpy.mean(current_layer[0], axis=(2,))
        elif dim_order == ImageDimOrdering.NCHW:
            current_layer = numpy.mean(current_layer[0], axis=(0,))
        else:
            self.logger.error("Unknown image ordering %s" % dim_order)
            raise MissingLinkException("Unknown image ordering!")

        while i >= 1:
            next_layer = relu_fm[i - 1]
            current_layer = self._step(current_layer, next_layer[0], dim_order)
            i -= 1

        current_heatmap = self._im2double(current_layer)
        current_heatmap = self._map2jpg(current_heatmap)

        height = original_image.shape[0]
        width = original_image.shape[1]
        upscaled_ = self.cv2.resize(current_heatmap, (width, height), interpolation=self.cv2.INTER_LINEAR)
        overlay = self.cv2.addWeighted(original_image, 1, upscaled_, 0.8, 0)
        image_key = hashlib.sha224(base64.b64encode(overlay)).hexdigest()
        model_hash = self.get_weights_hash(model)
        meta = {
            "path": uri,
            "output": output,
            "algo": "visual_backprop",
            "expected_output": expected_output
        }
        result = {
            "model_hash": model_hash,
            "image_key": image_key,
            "images": [self._convert_to_jpg(overlay),
                       self._convert_to_jpg(original_image),
                       self._convert_to_jpg(upscaled_)],
            "meta": meta
        }
        return result
