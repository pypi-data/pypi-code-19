#!/usr/bin/env python

""" Top level api for dcmfetch package.

Provides high level routines for downloading DICOM series
and a command line program "dcmfetch"
"""

from __future__ import print_function, division, absolute_import

from os.path import join, isdir, normpath, abspath, isfile, exists
from os import mkdir, access, W_OK, X_OK
from shutil import rmtree, move
from tempfile import mkdtemp
from zipfile import ZipFile, is_zipfile, ZIP_STORED
from io import BytesIO
from fnmatch import fnmatchcase
from collections import Sequence, Callable
from glob import glob
from itertools import chain
from operator import attrgetter

try:
    import pydicom as dcm
except ImportError:
    import dicom as dcm

try:
    from . queryinterface import QueryInterface
    from . version import __version__
except (ImportError, ValueError):
    from dcmfetch.queryinterface import QueryInterface
    from dcmfetch.version import __version__

__all__ = ['fetch_series', 'fetch_series_to_disk', 'read_series']

# PY3K
try:
    basestring
except NameError:
    basestring = str


def fetch_series(patid, stuid='1', sernos=1, server=None, aettable=None, localaet=None):
    '''Fetch QA series from DICOM store.

       Parameters
       ----------
       patid : str
               Patient ID
       stuid : str
               Study ID (allows glob style matching)
       sernos: int or list of ints (or convertible to int)
               Series number(s) to fetch
       server: str
               Key for server in aet table (default: first one defined in nodes file)
       aettable: str
               Dicom nodes file to use (default: search as defined in QueryInterface)
       localaet: str
               Calling aet (default: construct based on hostname)

       Returns
       -------
       dobjs : list of dicom objects
               dicom objects sorted on series and instance number
    '''

    qi = QueryInterface(aettable=aettable, localaet=localaet)
    if server is None:
        # first entry in table by default
        server = next(iter(qi.aettable))

    # Fix up for strings and single objects
    if isinstance(sernos, basestring) or not isinstance(sernos, Sequence):
        sernos = [sernos]
    sernos = list(map(int, sernos))

    # Remove duplicates
    sernos = list(set(sernos))

    seriess = [
        s for s in qi.combo_find(server, patid)
        if fnmatchcase(s.studyid, stuid) and s.seriesnumber in sernos
    ]

    # Fetch series from server to a temporary directory and read from there
    tempdir = mkdtemp()

    # Retrieve each series in turn: a generator hence list() to force iteration
    for series in seriess:
        list(qi.series_level_fetch(
            server,
            patid=patid, studyuid=series.studyuid, seriesuid=series.seriesuid,
            savedir=tempdir
        ))

    dobjs = sorted(read_series(tempdir, globspec='*'),
                   key=lambda d: (int(d.SeriesNumber), int(d.InstanceNumber)))
    rmtree(tempdir)
    return dobjs


def read_series(fileordirname, key=None, numeric=False, reverse=False, globspec='*.dcm'):
    '''
    Read a DICOM series from a directory or a zip file of DICOM files, optionally sorting the series.

    Parameters
    ----------
    fileordirname:
        A list of files, the name of directory containing dicom files, a zip file or a single dicom file.
    key:
        Sort key - either a unary function, a dicom tagname or a list of tag names.
    numeric:
        Sort keys numerically (if a DICOM Tag Name)
    reverse:
        Whether to reverse the direction of sorting
    globspec:
        Glob specification (or list of specs) to match files to read. It is ignored in the case of a zip file

    Returns
    -------
    out:
        List of dicom objects.
    '''
    if not isinstance(fileordirname, basestring):
        # Assume a sequence is just a list of simple filenames
        dobjs = [dcm.read_file(fname) for fname in sorted(set(fileordirname))]
    elif isdir(fileordirname):
        # A directory name
        if isinstance(globspec, basestring):
            # General case is a list of globspecs
            globspec = [globspec]
        # NB: set() takes account of duplicate matches for multiple glob patterns
        files = sorted(set([f for pattern in globspec for f in glob(join(fileordirname, pattern))]))
        dobjs = [dcm.read_file(fname) for fname in files]
    elif is_zipfile(fileordirname):
        zf = ZipFile(fileordirname)
        # Unfortunately, the filelike object returned by ZipFile.open()
        # does not provide tell(), which is needed by pydicom.read_file()
        # so we have to go via a StringIO buffer.
        dobjs = []
        for finfo in zf.infolist():
            sio = BytesIO(zf.read(finfo))
            dobjs.append(dcm.read_file(sio))
            sio.close()
        zf.close()
    elif isfile(fileordirname):
        # Degenerate case - single time point
        dobjs = [dcm.read_file(fileordirname)]
    elif not exists(fileordirname):
        raise IOError("Specified file or directory '%s' does not exist" % fileordirname)
    else:
        raise IOError(
            "%s' is neither a list of files, nor a directory, nor a zip file nor yet a plain file" % fileordirname)

    if key is not None:
        if isinstance(key, Callable):
            dobjs.sort(key=key, reverse=reverse)
        elif isinstance(key, str):
            if numeric:
                dobjs.sort(key=lambda d: float(getattr(d, key)), reverse=reverse)
            else:
                dobjs.sort(key=attrgetter(key), reverse=reverse)
        elif isinstance(key, Sequence) and all([isinstance(x, str) for x in key]):
            dobjs.sort(key=attrgetter(*key), reverse=reverse)
        else:
            raise TypeError('Sort key %s should be a string, a sequence of strings or a callable' % str(key))

    return dobjs


def fetch_series_to_disk(patid, outdir, studyid='1', sernos=1, server=None, usezip=False):
    """Fetch (multiple) series from DICOM store to disk.
       Parameters
       ----------
       patid : str
               Patient ID
       outdir : str
               Output directory
       stuid : str
               Study ID (allows glob style matching)
       sernos: list of integers
               Series number(s) to fetch
       server: Optional[str]
               DICOM server key in nodes table (default is first entry)
       usezip: Optional[bool]
               package dicom files into zip archive

       Returns
       -------
       int : number of series downloaded
    """

    qi = QueryInterface()
    if server is None:
        # first entry in table by default
        server = next(iter(qi.aettable))

    # Fix up for strings and single objects
    if isinstance(sernos, basestring) or not isinstance(sernos, Sequence):
        sernos = [sernos]
    sernos = list(map(int, sernos))

    # Remove duplicates
    sernos = list(set(sernos))

    # Filter for the specified study ids and series numbers
    seriess = [
        s for s in qi.combo_find(server, patid)
        if fnmatchcase(s.studyid, studyid) and s.seriesnumber in sernos
    ]

    # Retrieve each series in turn
    count = 0
    for series in seriess:
        # Download initially to temp area
        tempdir = mkdtemp()

        # NB Generator function hence use of list() to force instatiation
        list(qi.series_level_fetch(
            server,
            patid=patid, studyuid=series.studyuid, seriesuid=series.seriesuid,
            savedir=tempdir
        ))

        # filenames constructed from series details - attempts to be unique
        name = '%(modality)s-%(patid)s-%(studydate)s-%(studyid)s-%(seriesnumber)03d' % series._asdict()
        # protect from wildcards in patid
        name = "".join(x for x in name if x.isalnum() or x in '_-')
        imagefiles = glob(join(tempdir, '*'))
        if imagefiles:
            if usezip:
                savefile = normpath(join(outdir, name)) + '.zip'
                zipf = ZipFile(savefile, "w", compression=ZIP_STORED, allowZip64=True)
                for n, pathelement in enumerate(imagefiles):
                    archfile = "%s/%05d.dcm" % (name, n + 1)
                    zipf.write(pathelement, archfile)
                zipf.close()
            else:
                savedir = normpath(join(outdir, name))
                if not isdir(savedir):
                    mkdir(savedir)
                for n, pathelement in enumerate(imagefiles):
                    move(pathelement, join(savedir, '%05d.dcm' % (n + 1)))
            count += 1

        rmtree(tempdir)

    return count


def main():

    import argparse
    import sys

    def output_directory(string):
        ''' Argparse type handler for an output directory to write DICOM files to.
            Returns an absolute path.
        '''
        path = abspath(string)
        if not isdir(path):
            raise argparse.ArgumentTypeError('the output directory "%s" must exist already' % string)
        if not access(path, W_OK | X_OK):
            raise argparse.ArgumentTypeError('the output directory "%s" must be writable' % string)
        return path

    def series_numbers(string):
        ''' Argparse type handler for series numbers defined by a single integer, an integer range or
            a comma separated list of integers and ranges. Returns a list of integers.
        '''
        # NB easier to map 'all' to a very large range here then handle it in fetch_series
        MAXSERIESNO = 1000
        if string.lower() == 'all':
            return list(range(1, MAXSERIESNO + 1))

        try:
            seriesnos = []
            numbers_and_ranges = string.split(',')
            for item in numbers_and_ranges:
                range_tokens = item.split('-')
                if len(range_tokens) > 1:
                    # a range
                    start, stop = int(range_tokens[0]), int(range_tokens[-1])
                    seriesnos += list(range(start, stop + 1))
                else:
                    # a number
                    seriesnos += [int(item)]
            seriesnos = list(set(seriesnos))
            if not seriesnos or not all(1 <= n <= MAXSERIESNO for n in seriesnos):
                raise ValueError('series numbers must be between 1 and %d' % MAXSERIESNO)
            return seriesnos
        except ValueError:
            raise argparse.ArgumentTypeError('"%s" is not a valid series number, list or range' % string)

    parser = argparse.ArgumentParser(
        description='Fetch DICOM series from Archive Server',
        epilog='Specify series numbers as a comma separated list of integers and ranges without spaces e.g. "-s 1-5,7,8,10-12".'
    )

    parser.add_argument('-a', '--archive', action='store', help='Name of archive server in dicom nodes file')
    parser.add_argument('-p', '--patid', required=True, help='Patient to retrieve scans for (an exact string only)')
    parser.add_argument('-S', '--study', default='*', help='Study to retrieve scans for (may be a glob pattern) ')
    parser.add_argument('-s', '--series', required=True, action='append', type=series_numbers, help='Series number, list or range; can specify multiple times')
    parser.add_argument('-z', '--zip', action='store_true', help='Pack dicom objects into zip file')
    parser.add_argument('-o', '--out', action='store', default='.', type=output_directory, help='Output directory to store series in')
    parser.add_argument('-V', '--version', action='version', version='%%(prog)s %s' % __version__)

    args = parser.parse_args()

    # flatten list of lists
    sernos = list(chain.from_iterable(args.series))

    nseries = fetch_series_to_disk(
        patid=args.patid,
        outdir=args.out,
        studyid=args.study,
        sernos=sernos,
        server=args.archive,
        usezip=args.zip
    )

    if nseries < 1:
        print('No series found on server matching the specification', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
