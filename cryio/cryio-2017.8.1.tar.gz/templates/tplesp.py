#!/usr/bin/python
# -*- coding: utf-8 -*-

esperantoStr = u"""
{#- Jinja2 template -#}
ESPERANTO FORMAT 1 CONSISTING OF 25 LINES OF 256 BYTES EACH
IMAGE {{ shape }} {{ shape }} 1 1 "{% if datatype %}{{ datatype }}{% else %}4BYTE_LONG{% endif %}"
SPECIAL_CCD_1 0 0 0 0 0 0
SPECIAL_CCD_2 0 0 0 0 0
SPECIAL_CCD_3 0 0 0 0 0
SPECIAL_CCD_4 0 0 0 0 0 0 0 0
SPECIAL_CCD_5 0 0 0 0
TIME {{ Exposure_time }} 0 0
MONITOR {% if Flux %}{{ Flux }}{% else %}0{% endif %} 0 0 0
PIXELSIZE {{ pixel_size }} {{ pixel_size }}
TIMESTAMP "{{ datetime }}"
GRIDPATTERN ""
STARTANGLESINDEG {{ omega }} {{ theta }} {{ kappa }} {{ phi }}
ENDANGLESINDEG {{ omega + domega }} {{ theta + dtheta }} {{ kappa + dkappa }} {{ phi + dphi }}
GONIOMODEL_1 0 0 0 0 0 {{ center_x }} {{ center_y }} {{ alpha }} 0 {{ dist }}
GONIOMODEL_2 0 0 0 0
WAVELENGTH {{ l1 }} {{ l2 }} {{ l12 }} {{ b }}
MONOCHROMATOR {{ mono }} {{ monotype }}
ABSTORUN 0
HISTORY "(c) ID11 ESRF, Vadim Dyadkin, diadkin@esrf.fr"






"""
