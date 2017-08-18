# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""Miscellaneous small functions that don't need to be class methods."""

from __future__ import unicode_literals
from __future__ import print_function

import atexit
import codecs
import copy
import datetime
import json
import logging
import os
import re
import shutil
import tempfile
from six.moves.urllib.parse import urlparse, urlencode
from six.moves.urllib.request import urlopen, Request
from six.moves.urllib.error import URLError, HTTPError
from productmd.images import (SUPPORTED_IMAGE_TYPES, SUPPORTED_IMAGE_FORMATS)
import productmd.composeinfo

import fedfind.const

logger = logging.getLogger(__name__)

# Cache handling stuff
CACHEDIR = os.path.join(os.path.expanduser('~'), '.cache', 'fedfind')
try:
    if not os.path.exists(CACHEDIR):
        os.makedirs(CACHEDIR)
    if not os.access(CACHEDIR, os.W_OK):
        raise OSError("Write access to {0} denied!".format(CACHEDIR))
except (IOError, OSError) as err:
    logger.warning("Cannot use permanent cache! Using temporary cache, valid only for process")
    logger.warning("Error: %s", err)
    CACHEDIR = tempfile.mkdtemp()
    @atexit.register
    def _clean_cache():
        """Clean up the temporary cache."""
        logger.debug("Removing temporary cache %s", CACHEDIR)
        shutil.rmtree(CACHEDIR, True)

# cache for pkgdb collections JSON, as there are cases where we want
# to re-use it
COLLECTIONS = None

def date_check(value, fail_raise=True, out='obj'):
    """Checks whether a value is a date, and returns it if so. Valid
    dates are datetime.date instances or a string or int 'YYYYMMDD'.
    If out is set to 'obj', returns a datetime.date object. If out is
    set to 'both', returns a (string, object) tuple. If out is set to
    'str' (or anything else), returns a 'YYYYMMDD' string.

    On failure - empty or non-date-y input - will raise an exception
    if fail_raise is set, otherwise will return False.
    """
    if isinstance(value, datetime.date):
        dateobj = value
    else:
        try:
            dateobj = datetime.datetime.strptime(str(value), '%Y%m%d')
        except ValueError:
            if fail_raise:
                newerr = "{0} is not a valid date.".format(value)
                raise ValueError(newerr)
            else:
                return False

    if out == 'obj':
        return dateobj
    else:
        datestr = dateobj.strftime('%Y%m%d')
        if out == 'both':
            return (datestr, dateobj)
        else:
            return datestr

def urlopen_retries(url, tries=5):
    """Simple attempt to open a URL and return the response, with
    retries.
    """
    tries = 5
    resp = None
    while not resp and tries:
        try:
            resp = urlopen(url)
        except (ValueError, URLError, HTTPError):
            logger.debug("HTTP error! Retrying...")
            tries -= 1
    if not resp:
        raise ValueError("urlopen_retries: Failed to open {0}!".format(url))
    return resp

def download_json(url):
    """Given a URL that should give us some JSON, download and return
    it.
    """
    resp = urlopen_retries(url)
    # We can't just use json.load on the response because of a bytes/
    # str type issue in Py3: https://stackoverflow.com/questions/6862770
    rawjson = resp.read().decode('utf8')
    return json.loads(rawjson)

def url_exists(url):
    """Checks whether a URL exists, by trying to open it."""
    scheme = urlparse(url).scheme
    if 'http' in scheme:
        logger.debug("url_exists: checking %s as HTTP", url)
        try:
            urlopen(url)
            return True
        except (ValueError, URLError, HTTPError):
            return False
    else:
        raise ValueError("Invalid or unhandled URL! URL: {0}".format(url))

def get_size(url):
    """Get the size of URL (Content-Length header for HTTP). Currently
    only supports HTTP.
    """
    logger.debug("Checking size of %s", url)
    if not url.startswith('http'):
        raise ValueError("Can only check HTTP URLs.")
    headers = urlopen_retries(url).info()
    size = headers.get('Content-Length')
    if not size:
        raise ValueError("Size could not be found!")
    return int(size)

def comma_list(string):
    """Split a comma-separated list of values into a list (used by the
    CLI for passing query parameters etc). Also lower-cases the string
    because it's convenient to do that here...
    """
    return string.lower().split(',')

def _get_collections():
    """Download the collections JSON if we haven't already, and cache
    it at the module level.
    """
    global COLLECTIONS
    if not COLLECTIONS:
        logger.debug("collections not cached, downloading...")
        gotjson = download_json(
            'https://admin.fedoraproject.org/pkgdb/api/collections/')
        COLLECTIONS = gotjson['collections']
    return COLLECTIONS

def get_current_release(branched=False):
    """Find out what the 'current' Fedora release is, according to
    the pkgdb API. If 'branched' is truth-y, will return the Branched
    release number if there is one.
    """
    # HACK HACK HACK: pkgdb has been disabled, and PDC can't yet
    # distinguish between branched and stable. So for now we're just
    # hard coding the current 'right answers'.
    if branched:
        return 27
    else:
        return 26

def get_current_stables():
    """Returns a list of the release numbers of all current stable
    releases (according to pkgdb).
    """
    # HACK HACK HACK: pkgdb has been disabled, and PDC can't yet
    # distinguish between branched and stable. So for now we're just
    # hard coding the current 'right answers'.
    return [25, 26]

def create_image_dict(path):
    """Synthesize a productmd-style image metadata dict by analyzing
    the image's path. Used for pre-Pungi 4 releases, and Pungi 4
    releases that were split and had metadata stripped when synced to
    mirrors.
    """
    logger.debug("Synthesizing image metadata for %s", path)
    imgdict = {'path': path.strip('/')}
    path = path.lower()
    filename = path.split('/')[-1]

    # Find arch
    imgdict['arch'] = ""
    for arc in fedfind.const.ARCHES:
        if any(val in path for val in arc.values):
            imgdict['arch'] = arc.name

    # Find format
    imgdict['format'] = ""
    for form in SUPPORTED_IMAGE_FORMATS:
        if filename.endswith(form):
            imgdict['format'] = form

    # Find type
    imgdict['type'] = ""
    # we invent a types for the 'multiple' images that contain
    # multiple live or installer images together with a boot menu.
    # these will have 'Multi' subvariant
    types = SUPPORTED_IMAGE_TYPES + ['multi-desktop', 'multi-install']
    for typ in types:
        # Some types are basically formats...
        if '-' in typ and typ.replace('-', '.') in filename:
            imgdict['type'] = typ
        # Others are more token-y.
        elif "-{0}-".format(typ) in filename:
            imgdict['type'] = typ
    # Sometimes we have to be a bit more relaxed.
    if not imgdict['type']:
        for typ in types:
            if typ != "cd" and typ in filename:
                imgdict['type'] = typ
    # and this is just magic.
    if not imgdict['type'] and "disc" in filename:
        imgdict['type'] = "cd"
    # Pungi config uses the type 'boot' for netinst images, so follow
    # that
    if imgdict['type'] == 'netinst':
        imgdict['type'] = 'boot'
    # Various special handlings for awkward ostree installer images
    # Since 2016-10-10 with up-to-date Pungi the filenames should have
    # -ostree- in them...
    if '-ostree-' in filename:
        imgdict['type'] = "dvd-ostree"
    # ...but as of 2016-10-08 F24 two-week Atomic composes, the
    # filename is e.g.: Fedora-Atomic-dvd-x86_64-24-20161008.0.iso
    if '-atomic-dvd-' in filename:
        imgdict['type'] = "dvd-ostree"
    # F23 release case: Fedora-Cloud_Atomic-x86_64-23.iso
    if imgdict['type'] in ("", "dvd") and "cloud_atomic" in filename:
        imgdict['type'] = "dvd-ostree"
    # awkward case from F25 Beta, where we got a Workstation atomic
    # installer image with a bad filename:
    # Fedora-Workstation-dvd-x86_64-25_Beta-1.1.iso
    # probably too broad to keep forever, drop when 25 Beta is gone
    if '-workstation-dvd-' in filename:
        imgdict['type'] = "dvd-ostree"
    # live respins don't have 'live' in the filenames, find them with
    # the regex
    if not imgdict['type'] and fedfind.const.RESPINRE.search(path):
        imgdict['type'] = "live"

    # Find subvariant
    imgdict['subvariant'] = ''
    # these are a couple of nasty special cases taken
    # from fedfind 1.x
    if re.match(r'.*Fedora-(x86_64|i386)-\d{2,2}-\d{8,8}'
                r'(\.\d|)-sda\.(qcow2|raw.xz)',
                imgdict['path']):
        # F19/20-era cloud image, before Cloud flavor.
        imgdict['subvariant'] = 'Cloud'

    if re.match(r'.*(Fedora-|F)\d{1,2}-(x86_64|i686|Live)'
                r'-(x86_64|i686|Live)\.iso', imgdict['path']):
        # < F14 Desktop lives. Ew.
        imgdict['subvariant'] = 'Desktop'

    for load in fedfind.const.SUBVARIANTS:
        if any(val in imgdict['path'].lower()
               for val in load.values):
            imgdict['subvariant'] = load.name
    # Try to identify 'generic' media (call them
    # 'Everything' as that's what productmd does)
    if not imgdict['subvariant'] and (imgdict['type'] in
                                      ('dvd', 'boot', 'cd')):
        imgdict['subvariant'] = 'Everything'

    # assign disc number
    # FIXME: can't do disc_count very well with this approach
    imgdict['disc_number'] = 1
    match = re.search(r'-disc(\d+)', filename)
    if match:
        imgdict['disc_number'] = int(match.group(1))

    return imgdict

def pdc_query(path, params=None):
    """Light 'API client', sorta, for PDC. Just handles sending a
    request to a given API path with the appropriate header to get
    a JSON response, parsing the response, and handling multi-page
    responses. params is a dict of query params. Caches certain
    responses which are very unlikely ever to change in fedfind's
    cache directory.
    """
    logger.debug("pdc_query: path is %s", path)
    # load the query cache
    cachefile = os.path.join(CACHEDIR, 'pdcquery.json')
    try:
        with codecs.open(cachefile, 'r', encoding='utf-8') as cachefh:
            cache = json.loads(cachefh.read())
    except (IOError, OSError):
        # file doesn't exist, etc.
        cache = {}

    # handle params (as we use them in the cache key)
    if not params:
        params = []
    # turn param dict into tuple list (we need to handle both dicts
    # and tuple lists, and you can't always turn a tuple list into a
    # dict because parameter names can be repeated)
    try:
        params = list(params.items())
    except AttributeError:
        pass
    baseurl = '/'.join((fedfind.const.PDC_API, path.strip('/')))
    # cache key is the URL of the query, but without the page param
    cachekey = '?'.join((baseurl, urlencode(params)))

    # check cache, return if hit
    try:
        ret = cache[cachekey]
        logger.debug("pdc_query: cache hit!")
        return ret
    except KeyError:
        pass

    # otherwise, actually do the query
    results = []
    # we figured out the params earlier, for the cache key, just add
    # 'page' and re-do the URL
    pgcnt = 1
    params.append(('page', str(pgcnt)))
    url = '?'.join((baseurl, urlencode(params)))
    headers = {'Content-type': 'application/json'}
    req = Request(url, headers=headers)
    nxt = True
    while nxt:
        resp = download_json(req)
        try:
            # paged query
            results.extend(resp['results'])
            params.remove(('page', str(pgcnt)))
            pgcnt += 1
            params.append(('page', str(pgcnt)))
            url = '?'.join((baseurl, urlencode(params)))
            req = Request(url, headers=headers)
            nxt = resp['next']
        except KeyError:
            # non-paged query. just take the response
            results = resp
            break

    # decide whether to cache results
    writecache = False
    # we always cache compose-images results, as if we get a result
    # it's a 'hit' and will never change (query for non-existent
    # compose gives a 404)
    if path.startswith('compose-images/'):
        logger.debug("pdc_query: caching result for %s", path)
        cache[cachekey] = results
        writecache = True
    # we cache 'composes' results if they're specific and we got a
    # result
    if path == 'composes' and results:
        parkeys = [param[0] for param in params]
        if 'compose_id' in parkeys or all(key in parkeys for key in ('release', 'compose_label')):
            logger.debug("pdc_query: caching 'composes' result")
            cache[cachekey] = results
            writecache = True

    # write cache if we decided to
    if writecache:
        # I've seen CACHEDIR suddenly vanish, when it's a temp dir; let's
        # check and re-create it if necessary
        if not os.path.exists(CACHEDIR):
            os.makedirs(CACHEDIR)

        with codecs.open(cachefile, 'w', encoding='utf-8') as cachefh:
            cachefh.write(json.dumps(cache, separators=(',', ':'), indent=0))

    return results

def find_cid(string):
    """Find a Fedora compose ID (or a fedfind fake CID) in a string."""
    # the 'rules' are really pretty lax, see productmd.composeinfo
    # _validate_id's regex:
    # r".*\d{8}(\.nightly|\.n|\.ci|\.test|\.t)?(\.\d+)?"
    # it just has to be a string with 8 digits in it somewhere. We are
    # stricter, though, for Fedora. We require:
    # (dist)-(version)-(date)<.type>.(respin)
    # the type is optional, but all others must be present. The dist
    # must start with 'Fedora', but can have more text after that (and
    # can contain dashes, because life is awful; in the rest of the ID
    # dashes can only be separators).
    cidpatt = re.compile(r'(Fedora|FACD).*-[^-]+-\d{8,8}(\.\w)?\.\d+')
    match = cidpatt.search(string)
    if match:
        return match.group(0)
    else:
        return ''

def parse_cid(origcid, dist=False):
    """If dist is false-y, get (release, date, type, respin) values
    from a Pungi 4 compose id. If dist is truth-y, get (dist, release,
    date, type, respin) values from a Pungi 4 compose id.
    """
    # Normalize and check cid
    cid = find_cid(origcid)
    if not cid:
        raise ValueError("{0} does not appear to be a valid Pungi 4 Fedora "
                         "compose ID!".format(origcid))
    # The dist can have '-' in it, of course, because life is awful
    # FIXME: This is very stupid and will break on layered products,
    # which have a lot more - in them. It can theoretically break in
    # several other cases, but I don't know if Fedora is currently
    # hitting any of those. I'm currently thinking about how to deal
    # with this. See:
    # https://github.com/release-engineering/productmd/issues/77
    # We may just have to rejig things to require the full compose
    # metadata and give up on parsing compose IDs at all. That would
    # be a lot of work for fedfind. A somewhat uglier alternative for
    # fedfind's purposes would be to give it special knowledge of the
    # Fedora product shortnames with - in them, or a generic handler
    # for 'Fedora-(FOO)' or something.
    (gotdist, release, _) = cid.rsplit('-', 2)
    release = release.lower()
    (date, typ, respin) = productmd.composeinfo.get_date_type_respin(cid)
    if dist:
        return (gotdist, release, date, typ, respin)
    else:
        return (release, date, typ, respin)

def cid_from_label(release, label, short='fedora'):
    """Get the compose ID for a compose by label. Must also specify
    the release as labels are re-used per release. Can specify a
    shortname, because not just 'Fedora' composes have labels; the
    stable release nightly composes (Cloud, Atomic, Docker) also do.
    We can't tell from the label itself what the shortname might be,
    in fact each day we should get three composes with identical
    labels, so there's really no option but to require the user to
    specify. Uses PDC.
    """
    short = short.lower()
    params = {'release': "{0}-{1}".format(short, release), 'compose_label': label}
    res = pdc_query('composes', params)
    if res:
        return res[0]['compose_id']
    return ''

def label_from_cid(cid):
    """Get the compose label for a compose by ID. Only completed
    production composes have discoverable labels; will return the
    empty string for other composes.
    """
    typ = parse_cid(cid)[2]
    if typ != 'production':
        return ''
    params = {'compose_id': cid}
    res = pdc_query('composes', params)
    if res:
        return res[0]['compose_label']
    return ''

def get_weight(imgdict, arch=True):
    """Given a productmd image dict, return a number that tries to
    represent how 'important' that image is. This is intended for use
    in producing things like download tables, so you can order the
    images sensibly. Used for e.g. wikitcms download tables. Consider
    arch if arch is truth-y, otherwise don't.
    """
    archscores = (
        (('x86_64', 'i386'), 2000),
    )
    loadscores = (
        (('everything',), 300),
        (('workstation',), 220),
        (('server',), 210),
        (('cloud', 'desktop', 'cloud_base', 'docker_base', 'atomic'), 200),
        (('kde',), 190),
        (('minimal',), 90),
        (('xfce',), 80),
        (('soas',), 73),
        (('mate',), 72),
        (('cinnamon',), 71),
        (('lxde',), 70),
        (('source',), -10),
    )
    imgscore = 0
    if arch:
        for (values, score) in archscores:
            if imgdict['arch'] in values:
                imgscore += score
    for (values, score) in loadscores:
        if imgdict['subvariant'].lower() in values:
            imgscore += score
    return imgscore

def correct_image(imgdict):
    """This function is intended to make 'corrections' to the image
    dict to handle cases where the metadata produced by pungi are
    problematic. The passed dict is copied and the modified dict
    returned.
    """
    newdict = copy.deepcopy(imgdict)
    # ostree installer images get type 'boot', but this is unviable
    # because network install images also get type 'boot' and thus
    # we cannot distinguish between an ostree installer image and a
    # network install image for the same subvariant, and since
    # 2016-10, Fedora has both a Workstation network install image
    # and a Workstation ostree installer image. This is filed as
    # https://pagure.io/pungi/issue/417 . Until it gets fixed, we'll
    # work around it here, by substituting the proposed 'dvd-ostree'
    # type value.
    if imgdict['type'] == 'boot':
        filename = imgdict['path'].split('/')[-1]
        if '-dvd-' in filename or '-ostree-' in filename:
            newdict['type'] = 'dvd-ostree'
    return newdict

def identify_image(imgdict, out='tuple', undersub=False, lower=False):
    """Produce an 'image identifier' from the image dict. We use the
    combination of subvariant, type, and format to 'identify' a given
    image all over the place; by having them all use this function we
    can make sure they're all consistent, handle special cases and
    ease changing the identifier in future if necessary. If 'out' is
    'string', you get a single string joined with dashes. If 'out' is
    'tuple', you get a tuple. If 'undersub' is true, dashes in the
    metadata values will be replaced by underscores (this is so the
    string form can be reliably split into the component parts). If
    lower is True, values will be forced to all lower case.
    """
    # 'correct' the imgdict first
    imgdict = correct_image(imgdict)

    # get the values
    subv = imgdict['subvariant']
    typ = imgdict['type']
    form = imgdict['format']

    if undersub:
        # sub - to _
        subv = subv.replace('-', '_')
        typ = typ.replace('-', '_')
        form = form.replace('-', '_')

    if lower:
        # lowercase
        subv = subv.lower()
        typ = typ.lower()
        form = form.lower()

    # construct the tuple
    ret = (subv, typ, form)

    if out == 'string':
        # produce the string
        ret = '-'.join(ret)

    return ret

def _get_filelist(flist='fedora', record=None):
    """Get a (read mode) filehandle for one of the create-filelist
    generated image lists from the mirrors. flist can be 'fedora',
    'alt' or 'archive'. record, if set, should be a dict. It will be
    given 'cache' and 'downfail' keys that are set to True or False
    depending on whether the cached file was returned, and whether the
    remote file download failed. This is really just for the use of
    the tests and shouldn't be considered part of the API.
    May raise OSError or IOError if cache file cannot be written, or
    ValueError if imagelist download fails and we don't have a cached
    copy. There's a bit of hidden magic here where we write the
    last-modified string from the request header as the first line of
    the cached file, then always iterate it out before returning the
    file handle.
    """
    if record is not None:
        record['cache'] = False
        record['downfail'] = False
    # Determine the URL
    if flist not in ('fedora', 'alt', 'archive'):
        raise ValueError("_get_filelist: must be fedora, archive or alt!")
    fname = 'imagelist-{0}'.format(flist)
    url = '/'.join((fedfind.const.HTTPS_DL, flist, fname))
    logger.debug("_get_filelist: url is %s", url)

    # Determine the cache location
    cachefile = os.path.join(CACHEDIR, fname)
    logger.debug("_get_filelist: cachefile is %s", cachefile)

    # Get the cache file handle, if file is present
    try:
        cachefh = codecs.open(cachefile, 'r', encoding='utf-8')
    except (IOError, OSError):
        cachefh = None

    # Get the response and last modified date
    try:
        resp = urlopen_retries(url)
        modified = resp.headers['last-modified']
    except ValueError:
        if cachefh:
            logger.warning("Could not access image list {0}! Using cached "
                           "copy. Cache may be outdated!")
            if record:
                record['downfail'] = True
                record['cache'] = True
            # iterate out the date line
            next(cachefh)
            return cachefh
        else:
            # We can't do anything useful, just raise the error
            raise

    # Check if our cache is up-to-date, if present. If it is, go ahead
    # and return the file handle, with the date line already gone
    if cachefh:
        try:
            cachedate = next(cachefh).strip()
        except StopIteration:
            # file is empty
            cachedate = ''
        if cachedate == modified:
            logger.debug("_get_filelist: cache hit, returning")
            if record:
                logger.debug("Updating record")
                record['cache'] = True
            return cachefh

    # If we got here, either we don't have a cache file at all or the
    # dates don't match. So we need to re-download it

    # I've seen CACHEDIR suddenly vanish, when it's a temp dir; let's
    # check and re-create it if necessary
    if not os.path.exists(CACHEDIR):
        os.makedirs(CACHEDIR)

    with codecs.open(cachefile + '.tmp', 'w', encoding='utf-8') as cachefh:
        # Write the modified date line
        cachefh.write(modified + '\n')
    with open(cachefile + '.tmp', 'ab') as cachefh:
        # Now download and write the file, in 1MB chunks at a time
        while True:
            chunk = resp.read(1024 * 1024)
            if chunk:
                cachefh.write(chunk)
                cachefh.flush()
            else:
                break

    os.rename(cachefile + '.tmp', cachefile)

    # Now open the read-only filehandle, iterate out the date line,
    # and return
    cachefh = codecs.open(cachefile, 'r', encoding='utf-8')
    next(cachefh)
    return cachefh

# vim: set textwidth=100 ts=8 et sw=4:
