"""Generate forecasts from live data snapshots."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import codecs
import datetime
import json
import logging
import numpy as np
import os.path
import pypfilt
import warnings

from .. import cmd
from .. import summary
from . import settings
from .json import convert


def run(om_params, descr, extra):
    logger = logging.getLogger(__name__)

    fs_dates = extra['fs_dates']
    obs_table = extra['obs_table']
    s = extra['locn_settings']
    year = extra['year']
    no_json = extra['no_json']
    json_src = extra['json_src']

    # Record the forecast files that are produced.
    fs_files = []

    if 'start' in extra:
        start = extra['start'](year)
    else:
        start = datetime.datetime(year, 3, 1)
    if 'until' in extra:
        until = extra['until'](year)
    else:
        until = datetime.datetime(year, 10, 31)

    for fs_date in fs_dates:
        obs = obs_table[fs_date]
        params = settings.get_params(s)
        out_file = settings.filename_for_forecast(s, fs_date, descr)
        fs_files.append(os.path.join(params['out_dir'], out_file))
        observer = s['obs_model']
        observer.define_params(params, **om_params)

        for o in obs:
            o['period'] = observer.period
            o['unit'] = observer.unit
            o['source'] = json_src
            if isinstance(o['value'], int):
                o['value'] = np.int32(o['value'])
            elif isinstance(o['value'], float):
                o['value'] = np.float64(o['value'])
            else:
                msg = "observed value is not int or float: {} ({})"
                raise ValueError(msg.format(o['value'], type(o['value'])))

        # TODO: forecast!
        logger.info(" {} {}".format(fs_date, out_file))
        sim_start = datetime.datetime.now()
        logger.debug("forecast() beginning at {}".format(
            sim_start.strftime("%H:%M:%S")))
        # Allow local settings to define the summary tables.
        make = extra.get('make_summary', summary.make)
        stats = make(params, obs, first_day=True, only_fs=True)
        pypfilt.forecast(params, start, until, [obs], [fs_date], stats,
                         filename=out_file)
        logger.debug("forecast() finishing at {}".format(
            datetime.datetime.now().strftime("%H:%M:%S")))

    if no_json:
        return

    out_file = settings.filename_for_forecast_json(s, year, descr)
    if os.path.abspath(out_file) == os.path.abspath(json_src):
        logger.warning("Will not overwrite input file {}".format(json_src))
        return

    # Write the forecasts to a single JSON file.
    logger.info("Writing {}".format(out_file))
    convert(fs_files, True, s['id'], out_file, replace=True, pretty=False)


def replay_iter(args):
    logger = logging.getLogger(__name__)

    sets = args['sets']
    subset = args['subset']
    json_file = args['json_file']
    no_json = args['no_json']
    locn_id = args['location']

    try:
        with codecs.open(json_file, 'rb', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Could not read file '{}'".format(json_file))
        raise e

    if locn_id is None:
        locn_id = json_data['location']

    s = settings.local(locn_id)
    s['out_dir'] = settings.override('out_dir', '.', args, s)
    s['tmp_dir'] = settings.override('tmp_dir', '.', args, s)
    s['json_dir'] = settings.override('json_dir', '.', args, s)

    fs_dates = sorted([datetime.datetime.strptime(d, '%Y-%m-%d')
                       for d in json_data['forecasts'].keys()])

    obs_table = {}
    for fs_date in fs_dates:
        obs_table[fs_date] = json_data['obs'][str(fs_date.date())]
        for o in obs_table[fs_date]:
            o['date'] = datetime.datetime.strptime(o['date'], '%Y-%m-%d')

    # Use zero-based counting for partitions.
    counter = 0
    subset -= 1

    # TODO: year
    year = fs_dates[0].year

    # Perform the forecasting scan.
    for (om_params, descr, _) in settings.locn_forecasts(s, year):
        # for fs_date in fs_dates:
        #     extra = {'year': year, 'locn_settings': s, 'obs': obs[fs_date],
        #              'fs_date': fs_date, 'no_json': no_json}
        extra = {'year': year, 'locn_settings': s, 'obs_table': obs_table,
                 'fs_dates': fs_dates, 'no_json': no_json,
                 'json_src': json_file}
        if 'extra_args' in s:
            extra.update(s['extra_args'])
        # Only yield simulations in the chosen subset.
        if counter == subset:
            yield (om_params, descr, extra)
        counter = (counter + 1) % sets


def parser():
    """Return the command-line argument parser for ``epifx-replay``."""
    p = settings.common_parser(locns=False)

    cg = p.add_argument_group('Computation settings')
    cg.add_argument(
        '--spawn', metavar='N', type=int, default=1,
        help='Spawn N separate processes')
    cg.add_argument(
        '--subset', metavar='I', type=int, default=None,
        help='Run the Ith subset of the simulations')
    cg.add_argument(
        '--sets', metavar='S', type=int, default=1,
        help='Divide the simulations into S subsets.')

    og = p.add_argument_group(title='Output settings')
    og.add_argument(
        '--out-dir', type=str, default=None, metavar='DIR',
        help='The directory where forecast outputs will be saved')
    og.add_argument(
        '--tmp-dir', type=str, default=None, metavar='DIR',
        help='The directory where temporary files will be saved')

    jg = og.add_mutually_exclusive_group()
    jg.add_argument(
        '-j', '--json-dir', metavar='DIR', default=None,
        help='The directory in which JSON forecasts will be written')
    jg.add_argument(
        '-n', '--no-json', action='store_true',
        help='Do not write JSON forecasts')

    fg = p.add_argument_group(title='Forecast settings')
    fg.add_argument(
        'json_file', type=str,
        help='The JSON file containing the live data snapshots')
    fg.add_argument(
        'location', type=str, nargs='?', default=None,
        help='The forecasting location identifier (optional)')

    return p


def main(args=None):
    """Generate forecasts from live data snapshots."""
    p = parser()
    if args is None:
        args = vars(p.parse_args())
    else:
        args = vars(p.parse_args(args))
    logging.basicConfig(level=args['loglevel'])

    try:
        valid_locns = settings.locations()
    except settings.NoLocalSettings as e:
        print(e)
        return(2)

    if args['location'] is not None and args['location'] not in valid_locns:
        msg = "ERROR: invalid location: {}".format(args['location'])
        print(msg)
        return 2

    if args['sets'] == 1:
        if args['subset'] is not None and args['subset'] != 1:
            p.error('subset cannot exceed the number of sets')
        elif args['subset'] is None:
            args['subset'] = 1
    elif args['sets'] < 1:
            p.error('the number of sets must be positive')
    elif args['subset'] is None:
        p.error('the subset must be defined when there are multiple sets')
    elif args['subset'] < 1:
        p.error('the subset must be positive')
    elif args['subset'] > args['sets']:
        p.error('the subset cannot exceed the number of sets')

    warnings.simplefilter('error', category=BytesWarning)

    n_proc = args['spawn']
    if n_proc < 1:
        p.error('must use at least one process')
    elif n_proc == 1:
        for details in replay_iter(args):
            run(*details)
    else:
        cmd.run_in_parallel(run, replay_iter(args), n_proc)
