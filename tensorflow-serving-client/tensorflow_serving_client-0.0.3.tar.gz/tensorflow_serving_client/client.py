import tensorflow as tf
import numpy as np

from grpc.beta import implementations
from PIL import Image

from tensorflow_serving_client.protos import prediction_service_pb2, predict_pb2
from tensorflow_serving_client.proto_util import copy_message


class TensorflowServingClient(object):

    def __init__(self, host, port, model_name, target_size):
        self.host = host
        self.port = port
        self.model_name = model_name
        self.target_size = target_size

        self.channel = implementations.insecure_channel(self.host, self.port)
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)

    def classify_image(self, image_path, input_tensor_name='image', timeout=10.0, image_preprocessor=None):
        img = self._load_image(image_path, target_size=self.target_size)
        if image_preprocessor:
            img = image_preprocessor(img)
        image_data = np.expand_dims(np.asarray(img, dtype=np.float32), axis=0)
        return self.make_prediction(image_data, input_tensor_name, timeout=timeout)

    def execute(self, request, timeout=10.0):
        return self.stub.Predict(request, timeout)

    def make_prediction(self, input_data, input_tensor_name, timeout=10.0):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = self.model_name

        copy_message(tf.contrib.util.make_tensor_proto(input_data), request.inputs[input_tensor_name])
        response = self.execute(request, timeout=timeout)

        results = {}
        for key in response.outputs:
            tensor_proto = response.outputs[key]
            nd_array = tf.contrib.util.make_ndarray(tensor_proto)
            results[key] = nd_array.tolist()

        return results

    def _load_image(self, path, target_size=None):
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        if target_size:
            height_width = (target_size[1], target_size[0])
            if img.size != height_width:
                img = img.resize(height_width)
        return img
