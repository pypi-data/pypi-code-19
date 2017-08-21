#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from __future__ import division
import thumbor.filters
from thumbor.filters import BaseFilter, filter_method
from thumbor.utils import logger

class Filter(BaseFilter):
    phase = thumbor.filters.PHASE_AFTER_LOAD

    @filter_method(BaseFilter.Number)
    def clip(self, value):
        image_size = self.context.request.engine.size
        orientation = self.context.request.engine.get_orientation()
        if self.context.config.RESPECT_ORIENTATION and orientation in [5, 6, 7, 8]:
            image_size = (image_size[1], image_size[0])
        requested_ratio = int(self.context.request.width) / int(self.context.request.height)
        source_ratio = int(image_size[0]) / int(image_size[1])

        logger.debug('filters.clip: source file: %dx%d ' % image_size)
        logger.debug('filters.clip: source ratio: %.2f ' % (source_ratio))
        logger.debug('filters.clip: requested: %dx%d ' % (self.context.request.width, self.context.request.height))
        logger.debug('filters.clip: requested ratio %.2f ' % (requested_ratio))

        if (requested_ratio > 1 and source_ratio < 1) or (requested_ratio < 1 and source_ratio < 1):
            pixels_to_crop = value * image_size[1] / 100
            crop = crop = {
                'left': 0,
                'right': image_size[0],
                'top': int(pixels_to_crop / 2),
                'bottom': image_size[1] - (int(pixels_to_crop / 2))
            }
            self.context.request.should_crop = True
            self.context.request.crop = crop
            logger.debug('filters.clip: we will crop from height by ' + str(value) + '%')
            logger.debug('filters.clip: %s ', self.context.request.crop)

        elif (requested_ratio < 1 and source_ratio > 1) or (requested_ratio > 1 and source_ratio > 1):
            pixels_to_crop = value * image_size[0] / 100
            crop = crop = {
                'top': 0,
                'bottom': image_size[1],
                'left': int(pixels_to_crop / 2),
                'right': image_size[0] - (int(pixels_to_crop / 2))
            }
            self.context.request.should_crop = True
            self.context.request.crop = crop
            logger.debug('filters.clip: we will crop from width by ' + str(value) + '%')
            logger.debug('filters.clip: %s ', self.context.request.crop)
