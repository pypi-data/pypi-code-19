#!/usr/bin/env python

import argparse
import logging
import os
import sys

import sqlalchemy

from .metrics import fastqvalidator_metrics

def setup_logging(tool_name, args, run_uuid):
    logging.basicConfig(
        filename=os.path.join(run_uuid + '_' + tool_name + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def main():
    parser = argparse.ArgumentParser('fastqvalidator to sqlite tool')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Required flags.
    parser.add_argument('--metric_path',
                        required = False
    )
    parser.add_argument('--run_uuid',
                        required = True,
                        help = 'run_uuid string',
    )

    
    # setup required parameters
    args = parser.parse_args()
    metric_path = args.metric_path
    run_uuid = args.run_uuid

    logger = setup_logging('fastqvalidator_sqlite', args, run_uuid)

    sqlite_name = run_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    fastqvalidator_metrics.run(run_uuid, metric_path, engine, logger)
        
    return

if __name__ == '__main__':
    main()
