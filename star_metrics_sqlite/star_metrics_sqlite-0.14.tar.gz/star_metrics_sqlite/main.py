#!/usr/bin/env python

import argparse
import logging
import os
import sys

import sqlalchemy

from .metrics import star_alignreads_metrics
from .metrics import star_genomegenerate_metrics
#from .metrics import star_second_pass_metrics

def get_param(args, param_name):
    if vars(args)[param_name] == None:
        return None
    else:
        return vars(args)[param_name]
    return

def setup_logging(tool_name, args, uuid):
    logging.basicConfig(
        filename=os.path.join(uuid + '_' + tool_name + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def main():
    parser = argparse.ArgumentParser('star metrics tool')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Required flags.
    parser.add_argument('--metric_name',
                        required = True
    )
    parser.add_argument('--run_uuid',
                        required = True
    )

    # align reads
    parser.add_argument('--log_final_out_path',
                        required = False
    )
    parser.add_argument('--log_out_path',
                        required = False
    )
    parser.add_argument('--sj_out_tab_path',
                        required = False
    )

    # generate genome
    parser.add_argument('--chrlength_txt_path',
                        required = False
    )
    parser.add_argument('--chrnamelength_txt_path',
                        required = False
    )
    parser.add_argument('--chrname_txt_path',
                        required = False
    )
    parser.add_argument('--chrstart_txt_path',
                        required = False
    )
    parser.add_argument('--genomeparameters_txt_path',
                        required = False
    )
    parser.add_argument('--sjdb_info_txt_path',
                        required = False
    )
    parser.add_argument('--sjdblist_out_tab_path',
                        required = False
    )

    # setup required parameters
    args = parser.parse_args()
    metric_name = args.metric_name
    run_uuid = args.run_uuid

    logger = setup_logging(metric_name, args, run_uuid)

    sqlite_name = run_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    if metric_name == 'star_first_pass':
        logger.info('star_first_pass')
        log_final_out_path = get_param(args, 'log_final_out_path')
        log_out_path = get_param(args, 'log_out_path')
        sj_out_tab_path = get_param(args, 'sj_out_tab_path')
        star_alignreads_metrics.run_pass_1(run_uuid, engine, logger, metric_name,
                                           log_final_out_path, log_out_path, sj_out_tab_path)
    elif metric_name == 'star_generate_intermediate_genome':
        chrlength_txt_path = get_param(args, 'chrlength_txt_path')
        chrnamelength_txt_path = get_param(args, 'chrnamelength_txt_path')
        chrname_txt_path = get_param(args, 'chrname_txt_path')
        chrstart_txt_path = get_param(args, 'chrstart_txt_path')
        genomeparameters_txt_path = get_param(args, 'genomeparameters_txt_path')
        log_out_path = get_param(args, 'log_out_path')
        sjdb_info_txt_path = get_param(args, 'sjdb_info_txt_path')
        sjdblist_out_tab_path = get_param(args, 'sjdblist_out_tab_path')
        star_genomegenerate_metrics.run(run_uuid, engine, logger, metric_name,
                                        chrlength_txt_path, chrnamelength_txt_path, chrname_txt_path,
                                        chrstart_txt_path, genomeparameters_txt_path, log_out_path,
                                        sjdb_info_txt_path, sjdblist_out_tab_path)
    elif metric_name == 'star_second_pass':
        log_final_out_path = get_param(args, 'log_final_out_path')
        log_out_path = get_param(args, 'log_out_path')
        sj_out_tab_path = get_param(args, 'sj_out_tab_path')
        star_alignreads_metrics.run_pass_2(run_uuid, engine, logger, metric_name,
                                           log_final_out_path, log_out_path, sj_out_tab_path)
    else:
        sys.exit('No recognized tool was selected')
        
    return

if __name__ == '__main__':
    main()
