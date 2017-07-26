"""
Defines all Exceptions used by the GeoPlot package
"""


class GeoPlotError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class GeomapError(GeoPlotError):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class GeofieldError(GeoPlotError):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
