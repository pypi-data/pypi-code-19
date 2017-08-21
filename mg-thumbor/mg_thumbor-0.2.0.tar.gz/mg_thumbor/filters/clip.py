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

    @filter_method(BaseFilter.PositiveNumber)
    def clip(self, clip):
        upscale = False
        image_size = self.context.request.engine.size
        orientation = self.context.request.engine.get_orientation()
        if self.context.config.RESPECT_ORIENTATION and orientation in [5, 6, 7, 8]:
            original_size = [image_size[1], image_size[0]]
        else:
            original_size = [image_size[0], image_size[1]]

        logger.debug('filters.clip: we will crop up to ' + str(clip) + '%')
        new_size = [int(self.context.request.width), int(self.context.request.height)]
        zoomed_x = max(float(new_size[0]), float(new_size[1]*original_size[0]/original_size[1]))
        if clip >= 0 and clip < 100:
            clip = min(31, clip*32/100)
            must_be_shown = 1 - (clip / 31)
            zoomed_x = min(zoomed_x, new_size[0]/must_be_shown, new_size[1]*original_size[0]/(must_be_shown * original_size[1]))

        if upscale == False:
            zoomed_x = min(zoomed_x, original_size[0])

        zoomed_y = zoomed_x * original_size[1] / original_size[0]
        zoomed_size = [zoomed_x, zoomed_y]
        source_top_left = [0, 0]
        for it in range(0, 2):
            if (zoomed_size[it] > new_size[it]) :
                source_clip = original_size[it] * (zoomed_size[it] - new_size[it]) / zoomed_size[it]
                source_top_left[it] += source_clip * 0.5
                original_size[it] -= source_clip

        dest_left = int(source_top_left[0])
        dest_top = int(source_top_left[1])
        dest_right = int((source_top_left[0] + original_size[0]))
        dest_bottom = int((source_top_left[1] + original_size[1]))

        crop = crop = {
            'top': dest_top,
            'bottom': dest_bottom,
            'left': dest_left,
            'right': dest_right
        }
        self.context.request.should_crop = True
        self.context.request.crop = crop
        logger.debug('filters.clip: %s ', self.context.request.crop)
