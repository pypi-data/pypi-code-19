#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from keras_datasets.dummy_image_dataset import ImageDataset

class MyTest(TestCase):

    def test_download(self):
        dataset_cls = ImageDataset()
        self.assertTrue(dataset_cls.download_dataset("."))
