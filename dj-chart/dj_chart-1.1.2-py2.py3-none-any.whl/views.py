# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

import json
import random
import string
from datetime import date

from django.utils.safestring import mark_safe

from dateutil.relativedelta import relativedelta

from .constants import (PIE, DOUGHNUT, BAR, BAR_STACKED, LINE,
                        DISPLAY_GRID, DONT_DISPLAY_GRID,
                        POSITION_BOTTOM, POSITION_TOP, DEFAULT_COLORS,
                        WEEK, MONTH, YEAR)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class ChartMixin(object):
    template_name = "chart.html"

    chart_id = ''
    chart_title_show = True
    chart_title_position = POSITION_TOP
    chart_title = "Chart Title"

    chart_types_available = [PIE, DOUGHNUT, BAR, BAR_STACKED, LINE]
    chart_type = ''
    chart_stacked = False

    show_grid = False

    show_legend = True
    show_tooltips = True
    animation = True

    chart_data = {'labels': [], 'datasets': [{"label": '',
                                              "backgroundColor": [],
                                              "data": []}]}
    chart_options = {"title": {"display": True,
                               "position": chart_title_position,
                               "text": ""},
                     "tooltips": {"enabled": show_tooltips,
                                  "mode": "index",
                                  },
                     "legend": {"position": POSITION_BOTTOM, },
                     "maintainAspectRatio": False,
                     "scales": DONT_DISPLAY_GRID,
                     }
    if animation:
        chart_options["animation"] = {"animateRotate": True,
                                      "animateScale": True,
                                      "duration": 500}
    else:
        chart_options["animation"] = {"animateRotate": False,
                                      "animateScale": False,
                                      "duration": 0}

    label_urls = {}

    # Colors
    opacity = 0.5
    how_many_colors = 150
    colors = []
    border_colors = []

    def __init__(self, *args, **kwargs):
        # Unique ID of Chart
        self.chart_id = id_generator()

        # Chart Type
        if not self.chart_type:
            self.chart_type = self.chart_types_available[0]

        # Chart Data
        self.chart_data = {'labels': [], 'datasets': [{"label": '',
                                                       "backgroundColor": [],
                                                       "data": []}]}

        self.colors = []
        self.border_colors = []

    def _set_chart_options(self):
        # Title
        if self.chart_title_show:
            self.chart_options["title"]['display'] = True
        else:
            self.chart_options["title"]['display'] = False

        self.chart_options["title"]['position'] = self.chart_title_position
        self.chart_options["title"]['fontSize'] = 14
        self.chart_options["title"]['text'] = "%s" % self.chart_title

        # Legend
        if self.show_legend:
            self.chart_options["legend"]['display'] = True
        else:
            self.chart_options["legend"]['display'] = False

        # Chart Colors
        self._create_colors()

        # Chart Show Grid
        if self.show_grid:
            self.chart_options["scales"] = DISPLAY_GRID
        else:
            self.chart_options["scales"] = DONT_DISPLAY_GRID

        if self.chart_type in [PIE, DOUGHNUT]:
            self.chart_options["scales"]["xAxes"][0]["display"] = False
            self.chart_options["scales"]["yAxes"][0]["display"] = False
        else:
            self.chart_options["scales"]["xAxes"][0]["display"] = True
            self.chart_options["scales"]["yAxes"][0]["display"] = True

        if self.chart_type in [BAR, BAR_STACKED]:
            if self.chart_type == BAR_STACKED:
                self.chart_options["scales"]["xAxes"][0]["stacked"] = True
                self.chart_options["scales"]["yAxes"][0]["stacked"] = True
            else:
                self.chart_options["scales"]["xAxes"][0]["stacked"] = False
                self.chart_options["scales"]["yAxes"][0]["stacked"] = False
            self.chart_type = BAR

        if self.animation:
            self.chart_options["animation"] = {"animateRotate": True,
                                               "animateScale": True,
                                               "duration": 500}
        else:
            self.chart_options["animation"] = {"animateRotate": False,
                                               "animateScale": False,
                                               "duration": 0}

    def get_chart_data(self):
        """populate self.chart_data"""
        self.chart_data = {'labels': [], 'datasets': [{"label": [],
                                                       "backgroundColor": [],
                                                       "data": []}]}

    def set_labels_and_filter_values_for_xaxes(self, steps=6, type=MONTH):
        """populate self.chart_data['labels'] and self.filter_values
           self.chart_data['labels'] = ['11.16', '12.16', '01.17', '02.17', '03.17', '04.17']
           self.filter_values [datetime.date(2016, 11, 1), datetime.date(2016, 12, 1), datetime.date(2017, 1, 1), datetime.date(2017, 2, 1), datetime.date(2017, 3, 1), datetime.date(2017, 4, 1), datetime.date(2017, 5, 1)]
        """
        steps += 1
        today = date.today()
        if type not in (WEEK, MONTH, YEAR):
            type = MONTH

        if type == WEEK:
            self.filter_values = [today.replace(day=1)]
            self.chart_data['labels'].append("%s/%s" % (today.isocalendar()[1], today.isocalendar()[0]))
            for i in range(1, steps):
                next_week = today + relativedelta(weeks=+i)
                self.filter_values.append(next_week.replace(day=1))
                if steps - i != 1:
                    self.chart_data['labels'].append("%s/%s" % (next_week.isocalendar()[1], next_week.strftime('%y')))

        if type == MONTH:
            self.filter_values = [today.replace(day=1)]
            self.chart_data['labels'].append(today.strftime('%m/%y'))
            for i in range(1, steps):
                next_month = today + relativedelta(months=+i)
                self.filter_values.append(next_month.replace(day=1))
                if steps - i != 1:
                    self.chart_data['labels'].append(next_month.strftime('%m/%y'))

        if type == YEAR:
            self.filter_values = [today.replace(day=1)]
            self.chart_data['labels'].append(today.strftime('%Y'))
            for i in range(1, steps):
                next_year = today.replace(day=1, month=1) + relativedelta(years=+i)
                self.filter_values.append(next_year.replace(day=1))
                if steps - i != 1:
                    self.chart_data['labels'].append(next_year.strftime('%Y'))

    def write_chart_to_context(self, context):
        self._set_chart_options()
        context['chart_id'] = self.chart_id
        context['chart_type'] = self.chart_type
        context['chart_options'] = mark_safe(json.dumps(self.chart_options))
        self.get_chart_data()
        context['chart_data'] = mark_safe(json.dumps(self.chart_data))

        # Urls for Labels
        context['datasets'] = len(self.chart_data['datasets'])
        context['label_urls'] = mark_safe(json.dumps(self.label_urls))

        return context

    def _create_colors(self):
        for i in DEFAULT_COLORS:
            self.colors.append('rgba(%i, %i, %i, %f)' % (i[0], i[1], i[2], self.opacity))
            self.border_colors.append('rgba(%i, %i, %i, 1)' % i)

        max_value = 16581375  # 255**3
        step = int(max_value / self.how_many_colors)
        colors = [hex(i)[2:].zfill(6) for i in range(0, max_value, step)]

        rgbs = [(int(i[1:2], 16), int(i[2:4], 16), int(i[4:], 16)) for i in colors]
        for i in rgbs:
            if ('rgba(%i, %i, %i, %f)' % (i[0], i[1], i[2], self.opacity)) in self.colors:
                # logger.debug("Color %s already in self.colors" % (i,))
                continue
            self.colors.append('rgba(%i, %i, %i, %f)' % (i[0], i[1], i[2], self.opacity))
            self.border_colors.append('rgba(%i, %i, %i, 1)' % i)
