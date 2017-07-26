from shapely.geometry import shape, MultiPolygon, mapping
import pandas as pd
import geopandas as gpd
import geohash as gh
from memoized_property import memoized_property

class Polygeohash(object):

  BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"

  def __init__(self, geojson):
    self.geojson = geojson

  @memoized_property
  def polygon(self):
    if self.geojson["type"] == "FeatureCollection":
      df = pd.DataFrame(self.geojson["features"])
      df["polygon"] = df.geometry.map(lambda x: shape(x))
      return MultiPolygon(self._flatten(map(self._multi_polygon_to_polygons, df["polygon"].values)))
    elif self.geojson["type"] == "Feature":
      return shape(self.geojson["geometry"])

  @memoized_property
  def center(self):
    centroid = mapping(self.polygon.centroid)["coordinates"]
    return {
        "latitude": centroid[1],
        "longitude": centroid[0]
      }

  def center_geohash(self, precision=4):
    return gh.encode(self.center["latitude"], self.center["longitude"], precision=precision)


  def geohashes(self, precision=6):
    """ returns list of geohashes that intersects with geojson """

    # start with center geohash and neighboors at precision 2
    p = min(2, precision)
    center_geohash = self.center_geohash(precision=p)
    geohashes = [center_geohash] + gh.neighbors(center_geohash)
    geohashes = self.filter_intersected_geohashes(geohashes)

    while p < precision:
      geohashes = self._generate_inner_geohashes_for_geohashes(geohashes)
      geohashes = self.filter_intersected_geohashes(geohashes)
      p += 1

    return geohashes

  def filter_intersected_geohashes(self, geohashes):
    df = gpd.GeoDataFrame(geohashes, columns=["geohash"])
    df["geometry"] = df.apply(lambda x: self._geohash_to_shape(x["geohash"]), axis=1)
    return list(df[df.intersects(self.polygon)].geohash)

  def _multi_polygon_to_polygons(self, geom):
    if geom.geom_type == 'MultiPolygon':
      return list(geom)
    else:
      return [geom]

  def _flatten(self,lyst):
    return [item for sublist in lyst for item in sublist]

  def _generate_inner_geohashes_for_geohashes(self, geohashes=[]):
    return self._flatten(map(self._generate_inner_geohashes_for_geohash, geohashes))

  def _generate_inner_geohashes_for_geohash(self, geohash=""):
    return ["%s%s" % (geohash, l) for l in list(self.BASE32)]

  def _geohash_to_shape(self, geohash):
    box = gh.bbox(geohash)
    coords = [
        [box["w"], box["s"]],
        [box["w"], box["n"]],
        [box["e"], box["n"]],
        [box["e"], box["s"]],
        [box["w"], box["s"]],
    ]
    return shape({"type": "Polygon", "coordinates": [coords]})
