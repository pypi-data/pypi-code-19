import logging
import os

import cv2
import numpy as np
import rasterio
from geoalchemy2 import WKTElement
from shapely.affinity import affine_transform
from shapely.geometry import Polygon

log = logging.getLogger()
log.setLevel(logging.INFO)

def get_polygons(mask):
    _, contours, _ = cv2.findContours(mask.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [Polygon(cont[:, 0, :])
            for cont in contours if cont[:, 0, :].shape[0] > 3]

def transform(geom, tform):
    return affine_transform(geom, list(np.array(tform)[[0, 1, 3, 4, 2, 5]]))


# Use GeoAlchemy's WKTElement to create a geom with SRID
def create_wkt_element(geom):
    return WKTElement(geom.wkt, srid=4326)


class ImageGrab:
    """
    Extract features in a geojson from imagery
    """

    def __init__(self, image_file, image_size=300, batch_size=4, bands=3):
        """
        Get inputs
        """

        self.objects = []
        self.output = '.'
        self.image_size = image_size
        self.batch_size = batch_size
        self.bands = bands

        self.image_file = image_file

        self.tif = rasterio.open( self.image_file)
        self.height = self.tif.height
        self.width = self.tif.width
        self.x = self.y = 0

        os.makedirs(self.output, exist_ok=True)

    def inside(self):
        return self.x < self.width and self.y < self.height

    def get_window(self):
        window = ((self.y, self.y + self.image_size), (self.x, self.x + self.image_size))
        if self.x > self.width:
            self.x = 0
            self.y += self.image_size
        self.x += self.image_size
        return window

    def read_tile(self, window):
        return (
            self.tif.read(window=window, boundless=True).transpose([1, 2, 0])[:, :, :self.bands],
            self.tif.window_transform(window)
        )

    def get_batch(self):
        batch = []
        while self.inside() and len(batch) < self.batch_size:
            w = self.get_window()
            batch.append(self.read_tile(w))
        images_batch, transform_batch = zip(*batch)
        return np.array(images_batch), transform_batch


