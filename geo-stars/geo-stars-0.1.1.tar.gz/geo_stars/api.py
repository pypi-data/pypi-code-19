"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Ontology Engineering Group
        http://www.oeg-upm.net/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2016 Ontology Engineering Group.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

import json
from datetime import datetime

import astropy.coordinates as coord
import astropy.units as u
from SPARQLWrapper import SPARQLWrapper, JSON
from astropy.time import Time
from flask import Flask, request, jsonify
from flask_cache import Cache
from os.path import dirname, realpath

__author__ = 'Fernando Serena'

voc_path = dirname(realpath(__file__))
with open(voc_path + '/catalog.json') as f:
    catalog = json.loads(f.read())

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
sparql.setReturnFormat(JSON)

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'cache'})


def make_cache_key(*args, **kwargs):
    path = request.path
    items = request.args.items()
    args = {}
    for (arg, v) in items:
        v = float(v)
        v = int(float(v) * 1000) / 1000.0 if arg == 'lat' or arg == 'lon' else v
        args[arg] = v
    args = str(hash(frozenset(args.items())))
    print args
    return (path + args).encode('utf-8')


def search_wiki_entity(hd_id):
    sparql.setQuery("""
       SELECT ?item ?itemLabel
       WHERE
       {
          ?item wdt:P528 "%s" .    
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
       }
   """ % str(hd_id))
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        yield result["item"]["value"].replace('http://www.wikidata.org/entity/', ''), result.get("itemLabel", {}).get(
            "value", '')


sky_coords = {}
id_coords = {}
wd_ids = {}
for hd_id in catalog.keys():
    coords = catalog[hd_id]['coordinates']
    ra = coords['ra']
    dec = coords['dec']
    sky_coords[(ra, dec)] = coord.SkyCoord(unit=u.deg, frame='icrs', ra=ra, dec=dec)
    id_coords[(ra, dec)] = hd_id
    # try:
    #     wd_id, label = list(search_wiki_entity(hd_id)).pop()
    #     print hd_id, wd_id, label
    #     catalog[hd_id]["entity"] = wd_id
    #     catalog[hd_id]["label"] = label
    # except IndexError:
    #     pass


# with open('catalog.json', 'w') as f:
#     f.write(json.dumps(catalog, indent=3))


def filter_ra_dec(ra, dec, region):
    return region[0][0] <= ra <= region[1][0] and region[0][1] <= dec <= region[1][1]


def seek_visible_stars(address=None, angle=None, center_object=None, center_az=None, center_alt=None, lat=None,
                       lon=None):
    if address is not None:
        observing_location = coord.EarthLocation.of_address(address)
    else:
        observing_location = coord.EarthLocation.from_geodetic(lat=lat * u.degree, lon=lon * u.degree)
    observing_time = Time(datetime.utcnow())  # Time('2017-03-27 23:47')
    aa = coord.AltAz(location=observing_location, obstime=observing_time)

    if angle is None:
        angle = 10.0
    if center_alt is None:
        center_alt = 90.0
    if center_az is None:
        center_az = 0.0

    if center_object is not None:
        centerRadec = coord.SkyCoord.from_name(center_object)
        centerAltAz = centerRadec.transform_to(aa)
        # centerRadec = centerAltAz.icrs
    else:
        centerAltAz = coord.SkyCoord(alt=center_alt * u.deg, az=center_az * u.deg, obstime=observing_time,
                                     frame='altaz',
                                     location=observing_location)
        centerRadec = centerAltAz.icrs

    region = [(centerRadec.ra.degree - angle / 2.0, centerRadec.dec.degree - angle / 2.0),
              (centerRadec.ra.degree + angle / 2.0, centerRadec.dec.degree + angle / 2.0)]

    print 'center ra/dec', centerRadec.ra.degree, centerRadec.dec.degree
    print 'center alt/az', centerAltAz.alt.degree, centerAltAz.az.degree

    filtered_radecs = filter(lambda (ra, dec): filter_ra_dec(ra, dec, region), sky_coords.keys())
    for (ra, dec) in filtered_radecs:
        o_aa = sky_coords[(ra, dec)].transform_to(aa)
        if o_aa.alt.degree <= 0:
            print 'skipping'
            continue
        distance = centerAltAz.separation(o_aa)
        if abs(distance.degree) <= angle:
            star = {
                'id': id_coords[(ra, dec)],
                'coordinates': {
                    'alt': o_aa.alt.degree,
                    'az': o_aa.az.degree
                },
                'common_names': catalog[id_coords[(ra, dec)]].get('common_names', []),
                # 'identifiers': catalog[id_coords[(ra, dec)]].get('identifiers', []),
                'magnitude': catalog[id_coords[(ra, dec)]].get('magnitude')
            }
            wd_entity = catalog[id_coords[(ra, dec)]].get('entity')
            label = catalog[id_coords[(ra, dec)]].get('label')
            if wd_entity is not None:
                star['wd_entity'] = wd_entity
            if label is not None:
                star['label'] = label
            yield star


@app.route('/stars')
@cache.cached(timeout=60, key_prefix=make_cache_key)
def get_stars():
    center_object = request.args.get('center')
    angle = float(request.args.get('angle', 45.0))
    location = request.args.get('location')
    center_az = request.args.get('center_az')
    center_alt = request.args.get('center_alt')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if lat is not None:
        lat = float(lat)
    if lon is not None:
        lon = float(lon)

    stars = list(seek_visible_stars(address=location, angle=angle, center_object=center_object,
                                    center_az=center_az, center_alt=center_alt, lat=lat, lon=lon))
    return jsonify(stars)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, use_reloader=False, debug=False)
