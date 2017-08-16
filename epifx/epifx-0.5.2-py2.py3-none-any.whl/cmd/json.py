"""Convert epidemic forecasts into JSON files for online viewing."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import codecs
import datetime
import errno
import h5py
import json
import logging
import numpy as np
import os.path
import pypfilt.text

from . import settings


def convert(files, most_recent, locn_id, out_file, replace, pretty, cis=None):
    """
    Convert a set of epidemic forecasts into a JSON file for online viewing.

    :param files: A list of forecast files (HDF5).
    :param most_recent: Whether to use only the most recent forecast in each
        file.
    :param locn_id: The forecasting location identifier.
    :param out_file: The output file name.
    :param replace: Whether to replace (overwrite) an existing JSON file,
        rather than updating it with the provided forecasts.
    :param pretty: Whether the JSON output should be pretty-printed.
    :param cis: The credible intervals to record (default: ``[0, 50, 95]``).
    """
    logger = logging.getLogger(__name__)
    fs_fmt = "%Y-%m-%d %H:%M:%S"
    d_fmt = "%Y-%m-%d"

    def dtime(dstr):
        """Convert datetime strings to datetime instances."""
        dstr = pypfilt.text.to_unicode(dstr)
        return datetime.datetime.strptime(dstr, fs_fmt)

    def date_str(dstr):
        """Convert datetime strings to date strings."""
        dstr = pypfilt.text.to_unicode(dstr)
        dt = datetime.datetime.strptime(dstr, fs_fmt).date()
        return dt.strftime(d_fmt)

    locn_settings = settings.local(locn_id)

    if cis is None:
        cis = [0, 50, 95]

    # If we're updating an existing file, try to load the current contents.
    json_data = None
    if (not replace) and os.path.isfile(out_file):
        # The output file already exists and we're not replacing it.
        try:
            with codecs.open(out_file, 'rb', encoding='utf-8') as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            logger.warning("Could not read file '{}'".format(out_file))

    # If we're generating a new file, or the current file could not be loaded,
    # start with empty content.
    if json_data is None:
        json_data = {
            'obs': {},
            'forecasts': {},
            'timing': {},
            'obs_model': {},
            'location': locn_id,
            'location_name': locn_settings['name'],
            'obs_axis_lbl': locn_settings['obs_axis_lbl'],
            'obs_axis_prec': locn_settings['obs_axis_prec'],
            'obs_datum_lbl': locn_settings['obs_datum_lbl'],
            'obs_datum_prec': locn_settings['obs_datum_prec'],
        }

    first = True
    # Note: files may be in any order, sorting yields deterministic ouput.
    for hdf5_file in sorted(files):
        with h5py.File(hdf5_file, 'r') as f:
            obs_models = f['meta']['param']['obs'].values()
            if len(obs_models) != 1:
                raise ValueError("Found {} observation models".format(
                    len(obs_models)))
            # Note: in Python 3, h5py group methods such as keys(), values(),
            # and items() return view-like objects that cannot be sliced or
            # indexed like lists, but which support iteration.
            for om in obs_models:
                if first:
                    # Record the observation model parameters.
                    for key in om.keys():
                        json_data['obs_model'][key] = om[key][()].item()
                    first = False
                else:
                    # Check the observation model parameters are consistent.
                    for key in om.keys():
                        if key not in json_data['obs_model']:
                            # A new observation model parameter has appeared.
                            logger.warning("New parameter {} in {}".format(
                                key, hdf5_file))
                            continue
                        ok = json_data['obs_model'][key] == om[key][()].item()
                        if not ok:
                            logger.warning("Param {} differs".format(key))

            # Extract the forecast credible intervals.
            fs = f['data']['forecasts'][()]
            conds = tuple(fs['prob'] == p for p in cis)
            keep = np.logical_or.reduce(conds)
            fs = fs[keep]

            fs_dates = np.unique(fs['fs_date'])
            ci_levels = np.unique(fs['prob'])
            if len(ci_levels) < len(cis):
                msg = "expected CIs: {}; only found: {}"
                expect = ", ".join(str(p) for p in sorted(cis))
                found = ", ".join(str(p) for p in sorted(ci_levels))
                logger.warning(msg.format(expect, found))

            # Ignore the estimation run, if present.
            sim_end = max(dtime(dstr) for dstr in fs['date']).strftime(fs_fmt)
            sim_end = pypfilt.text.to_bytes(sim_end)
            if len(fs_dates) == 1 and fs_dates[0] == sim_end:
                # If the file only contains the result of an estimation run,
                # inform the user and keep these results --- they can result
                # from directly using pypfilt.run() to produce forecasts.
                logger.warning('Estimation run only: {}'.format(hdf5_file))
            else:
                fs_dates = [d for d in fs_dates if d != sim_end]

            if most_recent:
                # Only retain the more recent forecast.
                fs_dates = [max(dtime(dstr) for dstr in fs_dates)]
                fs_dates = [pypfilt.text.to_bytes(d.strftime(fs_fmt))
                            for d in fs_dates]

            # Store the forecast credible intervals.
            for fs_date in fs_dates:
                fs_rows = fs[fs['fs_date'] == fs_date]
                ci_dict = {}
                for ci in ci_levels:
                    ci_rows = fs_rows[fs_rows['prob'] == ci]
                    ci_dict[str(ci)] = [
                        {"date": date_str(date),
                         "ymin": ymin,
                         "ymax": ymax}
                        for (_, _, _, date, _, ymin, ymax) in ci_rows]
                json_data['forecasts'][date_str(fs_date)] = ci_dict

            # Extract the peak timing credible intervals.
            try:
                pk = f['data']['peak_cints'][()]
            except KeyError:
                # If this table is not present, return an empty array with the
                # minimal set of required columns.
                logger.warning("No 'peak_cints' table: {}'".format(hdf5_file))
                pk = np.zeros(0, dtype=[('prob', int), ('fs_date', 'S0')])
            conds = tuple(pk['prob'] == p for p in cis)
            keep = np.logical_or.reduce(conds)
            pk = pk[keep]
            fs_dates = np.unique(pk['fs_date'])
            ci_levels = np.unique(pk['prob'])
            if len(ci_levels) < len(cis):
                msg = "expected CIs: {}; only found: {}"
                expect = ", ".join(str(p) for p in sorted(cis))
                found = ", ".join(str(p) for p in sorted(ci_levels))
                logger.warning(msg.format(expect, found))

            for fs_date in fs_dates:
                pk_rows = pk[pk['fs_date'] == fs_date]
                ci_dict = {}
                for ci in ci_levels:
                    ci_rows = pk_rows[pk_rows['prob'] == ci]
                    ci_dict[str(ci)] = [
                        {"date": date_str(fs_date),
                         "ymin": date_str(tmin),
                         "ymax": date_str(tmax)}
                        for (_, _, _, _, _smin, _smax, tmin, tmax) in ci_rows]
                json_data['timing'][date_str(fs_date)] = ci_dict

            # Extract the observations at this time.
            obs_units = f['data']['obs'].keys()
            if len(obs_units) != 1:
                raise ValueError("Found {} observation models".format(
                    len(obs_units)))
            first_unit = None
            for unit in obs_units:
                first_unit = unit
            obs = f['data']['obs'][first_unit][()]
            cols = obs.dtype.names
            bs_cols = [c for c in cols if obs.dtype[c].kind == 'S']
            for fs_date in fs_dates:
                obs_dict = [
                    {c: obs_row[c].item() for c in cols}
                    for obs_row in obs]
                for o in obs_dict:
                    # Convert byte string to Unicode strings.
                    for c in bs_cols:
                        o[c] = pypfilt.text.to_unicode(o[c])
                    # Ensure the date is stored as 'YYYY-MM-DD'.
                    o['date'] = date_str(o['date'])

                json_data['obs'][date_str(fs_date)] = obs_dict

    if pretty:
        indent = 2
        separators = (', ', ': ')
    else:
        indent = None
        separators = (',', ':')

    # Create the output directory (and missing parents) as needed.
    # The directory will be empty ('') if out_file has no path component.
    out_dir = os.path.dirname(out_file)
    if out_dir and not os.path.isdir(out_dir):
        # Create with mode -rwxr-x---.
        try:
            logger.info('Creating {}'.format(out_dir))
            os.makedirs(out_dir, mode=0o750)
        except OSError as e:
            # Potential race condition with multiple script instances.
            if e.errno != errno.EEXIST:
                logger.warning('Could not create {}'.format(out_dir))
                raise

    logger.debug("Writing {}".format(out_file))
    with codecs.open(out_file, 'wb', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False,
                  sort_keys=True, indent=indent, separators=separators)


def parser():
    """Return the command-line argument parser for ``epifx-json``."""
    p = settings.common_parser(locns=False)

    ip = p.add_argument_group('Input arguments')
    ip.add_argument(
        '-i', '--intervals', action='store', metavar='CIs',
        help='Credible intervals (default: 0,50,95)')
    ip.add_argument(
        '-m', '--most-recent', action='store_true',
        help='Use only the most recent forecast in each file')

    op = p.add_argument_group('Output arguments')
    op.add_argument(
        '-o', '--output', action='store', type=str, default='output.json',
        help='The name of the JSON output file')
    op.add_argument(
        '-p', '--pretty', action='store_true',
        help='Pretty-print the JSON output')
    op.add_argument(
        '-r', '--replace', action='store_true',
        help='Replace the output file (default: update if it exists)')

    rp = p.add_argument_group('Required arguments')
    rp.add_argument(
        '-l', '--location', action='store', type=str, default=None,
        help='The location to which the forecasts pertain')
    rp.add_argument(
        'files', metavar='HDF5_FILE', type=str, nargs='*',
        help='Forecast data file(s)')

    return p


def main(args=None):
    """The entry point for ``epifx-json``."""
    p = parser()
    if args is None:
        args = vars(p.parse_args())
    else:
        args = vars(p.parse_args(args))

    if args['location'] is None:
        p.print_help()
        return 2

    if not args['files']:
        p.print_help()
        return 2

    if args['intervals'] is not None:
        vals = args['intervals'].split(",")
        for ix, val in enumerate(vals):
            try:
                vals[ix] = int(val)
            except ValueError:
                p.error("Invalid credible interval '{}'".format(val))
        args['intervals'] = vals

    logging.basicConfig(level=args['loglevel'])
    convert(files=args['files'], most_recent=args['most_recent'],
            locn_id=args['location'], out_file=args['output'],
            replace=args['replace'], pretty=args['pretty'],
            cis=args['intervals'])
