# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

PIE = 'pie'
DOUGHNUT = 'doughnut'
BAR = 'bar'
BAR_STACKED = 'bar-stacked'
LINE = 'line'

DISPLAY_GRID = {"xAxes": [{"ticks": {"autoSkip": False, }, "display": True, "gridLines": {"display": True}, }],
                "yAxes": [{"ticks": {"beginAtZero": True, }, "display": True, "gridLines": {"display": True}, }],
                }

DONT_DISPLAY_GRID = {"xAxes": [{"ticks": {"autoSkip": False, }, "display": True, "gridLines": {"display": False}, }],
                     "yAxes": [{"ticks": {"beginAtZero": True, }, "display": True, "gridLines": {"display": False}, }],
                     }

POSITION_TOP = "top"
POSITION_LEFT = "left"
POSITION_BOTTOM = "bottom"
POSITION_RIGHT = "right"


# http://www.rapidtables.com/web/color/RGB_Color.htm
# https://en.wikipedia.org/wiki/Web_colors
DEFAULT_COLORS = []
DEFAULT_COLORS.append((0, 128, 0))
DEFAULT_COLORS.append((255, 0, 0))
DEFAULT_COLORS.append((255, 165, 0))
DEFAULT_COLORS.append((170, 121, 66))
DEFAULT_COLORS.append((0, 0, 255))
DEFAULT_COLORS.append((255, 255, 0))
DEFAULT_COLORS.append((192, 192, 192))
DEFAULT_COLORS.append((128, 0, 0))
DEFAULT_COLORS.append((128, 128, 0))
DEFAULT_COLORS.append((0, 255, 0))
DEFAULT_COLORS.append((0, 255, 255))
DEFAULT_COLORS.append((0, 128, 128))
DEFAULT_COLORS.append((0, 0, 128))
DEFAULT_COLORS.append((255, 0, 255))
DEFAULT_COLORS.append((128, 0, 128))
DEFAULT_COLORS.append((255, 160, 122))
DEFAULT_COLORS.append((178, 34, 34))
DEFAULT_COLORS.append((240, 230, 140))
DEFAULT_COLORS.append((85, 107, 47))
DEFAULT_COLORS.append((175, 238, 238))
DEFAULT_COLORS.append((238, 130, 238))
DEFAULT_COLORS.append((75, 0, 130))
DEFAULT_COLORS.append((139, 69, 19))


WEEK = 0
MONTH = 1
YEAR = 2

TIME_UNITS_CHOICES = ((WEEK, _('Week')),
                      (MONTH, _('Month')),
                      (YEAR, _('Year')),
                      )
