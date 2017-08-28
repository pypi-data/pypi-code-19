import logging
import os

import cv2
import numpy as np
import rasterio
from geoalchemy2 import WKTElement
from shapely.affinity import affine_transform
from shapely.geometry import Polygon
from glob import glob
from os.path import join, splitext, exists
from scipy.misc import imread, imresize


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


def tif16to8(img, lower_pct=1, upper_pct=99):
    """Rescale the bands of a multichannel image"""
    img_scaled = np.zeros(img.shape, np.uint8)
    for i in range(img.shape[2]):
        band = img[:, :, i]
        lower, upper = np.percentile(band, [lower_pct, upper_pct])
        band = (band - lower) / (upper - lower) * 255
        img_scaled[:, :, i] = np.clip(band, 0, 255).astype(np.uint8)
    return img_scaled


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

class Record:
    def __init__(self, image, mask):
        print(image, mask)
        self.image = image
        self.mask = mask
        self.geotransform = None
        self.image_np = None
        self.mask_np = None


class BatchDataset:
    files = []
    images = []
    annotations = []
    image_options = {}
    batch_offset = 0
    epochs_completed = 0

    def __init__(self, directory, ext, resize, img_size,
                 channels=8, classes=2, images='images', masks='masks',  mask_ext='png', filename=None):
        """
        Initialize a generic file reader with batching for list of files
        :param mask_ext:
        :param ext:
        :param directory:
        sample record: {'image': f, 'annotation': annotation_file, 'filename': filename}
        Available options:
        resize = True/ False
        resize_size = #size of output image - does bilinear resize
        color=True/False
        """
        self.classes = classes
        self.channels = channels
        self.mask_fn = masks
        self.records = []
        self.image_fn = images
        if filename and exists(join(directory, filename)):
                with open(join(directory, filename)) as f:
                    file_list = [join(directory, self.image_fn, image) for image in f.read().split()]
        else:
            file_list = glob(join(directory, self.image_fn, '*.{}'.format(ext)))

        if not file_list:
            print('No files found')
            raise FileNotFoundError(join(directory, self.image_fn, '*.{}'.format(ext)))
        else:
            for f in file_list:
                filename = splitext(f.split("/")[-1])[0]
                mask_file = join(directory, self.mask_fn, filename + '.' + mask_ext)
                if exists(mask_file):
                    self.records.append(Record(f, mask_file))
                else:
                    print("Annotation file not found for %s - Skipping" % filename)

        self.ext = ext
        self.resize = resize
        self.img_size = img_size
        self.total_fetched = 0
        self.batch_offset = 0
        self.count = len(self.records)
        self.indexes = np.random.randint(0, self.count, size=[self.count]).tolist()

        print('No. of %s files: %d' % (directory, (len(self.records))))

    def open_png(self, image, mask=False):
        image = imread(image)
        if self.resize:
            image = np.array(imresize(image, [self.img_size, self.img_size], interp='nearest'))

        if not mask and len(image.shape) < 3:  # make sure images are of shape(h,w,3)
            image = np.array([image] * self.channels)
        elif not mask and image.shape[-1] < self.channels:  # make sure images are of shape(h,w,3)
            image = np.dstack([image] * (1 + self.channels // image.shape[-1]))[:, :, :self.channels]

        if mask and image.shape[-1] > 1:
            # image = np.dot(image[..., :3], [0.299/128, 0.587/128, 0.114/128])
            image = (image.sum(axis=-1) > 0).astype(np.int)

        return np.array(image)

    def open_mask(self, image):
        image = imread(image)
        if self.resize:
            image = np.array(imresize(image, [self.img_size, self.img_size], interp='nearest'))

        if len(image.shape) > 2 and image.shape[-1] > 1:
            image = image.sum(axis=-1) // 3

        for val in np.unique(image):
            if val >= self.classes:
                image = (image > 0) * 1
                print('NUM_OF_CLASSES < Mask Label Values: ', np.unique(image), self.classes)
                break

        return np.expand_dims(np.array(image), axis=3)

    def open_tif(self, image):
        with rasterio.open(image) as f:
            i = np.array(f.read())

        if self.resize:
            i = np.array([imresize(layer, [self.img_size, self.img_size], interp='nearest') for layer in i])
        i = i.transpose([1, 2, 0])
        return i

    def next_batch(self, batch_size):
        start = self.batch_offset

        if self.batch_offset + batch_size > self.count:
            self.epochs_completed += 1
            print("****************** Epochs completed: " + str(self.epochs_completed) + "******************")
            self.indexes = np.random.randint(0, self.count, size=[self.count]).tolist()  # Shuffle the data
            start = self.batch_offset = 0  # Start next epoch

        self.batch_offset += batch_size
        return self.grab_imgs(start, self.batch_offset), self.grab_masks(start, self.batch_offset)

    def grab_imgs(self, start, end, indexes=None):
        if indexes is None:
            indexes = self.indexes
        if self.ext == "tif":
            return np.array([self.open_tif(self.records[ind].image) for ind in indexes[start:end]])
        else:
            return np.array([self.open_png(self.records[ind].image) for ind in indexes[start:end]])

    def grab_masks(self, start, end, indexes=None):
        if indexes is None:
            indexes = self.indexes
        return np.array([self.open_mask(self.records[ind].mask) for ind in indexes[start:end]])

    def grab_records(self, start, end, indexes=None):
        if indexes is None:
            indexes = self.indexes
        return np.array([self.records[ind] for ind in indexes[start:end]])

    def get_random_batch(self, batch_size):
        indexes = np.random.randint(0, self.count, size=[batch_size]).tolist()
        return (self.grab_imgs(0, batch_size, indexes),
                self.grab_masks(0, batch_size, indexes),
                [self.records[index] for index in indexes])

    def get(self, batch_size=1):
        for _ in range(batch_size):
            if self.total_fetched < self.count:
                yield self.images[self.total_fetched], self.annotations[self.total_fetched], self.records[
                    self.total_fetched]
                self.total_fetched += 1

    def getn(self, batch_size=1):
        start = self.batch_offset

        if self.batch_offset + batch_size > self.count:
            self.epochs_completed += 1
            print("****************** Epochs completed: " + str(self.epochs_completed) + "******************")
            self.indexes = np.random.randint(0, self.count, size=[self.count]).tolist()  # Shuffle the data
            start = self.batch_offset = 0  # Start next epoch

        self.batch_offset += batch_size
        return (self.grab_imgs(start, self.batch_offset),
                self.grab_masks(start, self.batch_offset),
                self.grab_records(start, self.batch_offset))
