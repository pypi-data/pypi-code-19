from concurrent.futures import ThreadPoolExecutor

import PIL.Image
from PyQt5.QtGui import QImage

from .kmean import Kmeans

__all__ = ["mImage"]

class mImage(object):

    def __init__(self,img):

        self.path = img
        self.dominant = None
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.current_process = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self,p):
        if p:
            self._path = p
            self.qImage = QImage(p)
            self.pil = PIL.Image.open(p)



    def callbackDominant(self,thread):
        self.dominant = thread.result()


    def getDominant(self,callback=None):
        """
        Async dominant color request
        :param callback:
        :return:
        """
        # Quality goes from 1-10 1 being the greater.


        k = Kmeans()

        #result = k.run(self.img)
        self.current_process = self.executor.submit(k.run, self.pil)
        self.current_process.add_done_callback(self.callbackDominant)

        if callback:
            self.current_process.add_done_callback(callback)


    def average_colour(self):

        image = self.pil

        colour_tuple = [None, None, None]
        for channel in range(3):

            # Get data for one channel at a time
            pixels = image.getdata(band=channel)

            values = []
            for pixel in pixels:
                values.append(pixel)

            colour_tuple[channel] = sum(values) / len(values)

        return tuple(colour_tuple)


    def most_frequent_colour(self):

        image = self.pil
        w, h = image.size
        pixels = image.getcolors(w * h)

        most_frequent_pixel = pixels[0]

        for count, colour in pixels:
            if count > most_frequent_pixel[0]:
                most_frequent_pixel = (count, colour)

        return most_frequent_pixel[1]

