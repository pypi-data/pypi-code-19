from flask import Flask
from flask import request
from datetime import datetime
import os
import shutil
from PIL import Image
import numpy as np


class ImgServ():
    def __init__(self, handler, host = '0.0.0.0', port_number = 12222, save_loc = '.', incoming_fname = 'image.jpg', image_prefix = 'img_', image_format = '.jpg', datetime_delimiter = '_'):
        self.handler = handler
        self.host = host
        self.port_number = port_number

        self.app = Flask(__name__)

        self.save_loc = save_loc
        self.incoming_fname = incoming_fname
        self.image_prefix = image_prefix
        self.image_format = image_format
        self.datetime_delimiter = datetime_delimiter

        def imgToNp(imgPath, dtype='int32'):
            image = Image.open(imgPath)
            image.load()
            npArr = np.asarray(image, dtype=dtype)
            image.close()
            return npArr


        @self.app.route('/', methods=['POST'])
        def serve():
            imgName = self.image_prefix + str(datetime.now())[:-7].replace(':', self.datetime_delimiter) + self.image_format
            save_path = os.path.join(self.save_loc, imgName)
            request.files[self.incoming_fname].save(save_path)
            npImage = imgToNp(save_path)
            return handler(npImage)


    def run(self, threaded = True):
        self.app.run(host=self.host, port = self.port_number, threaded=threaded)
