import os

from .metrics_util import get_year
from .metrics_util import get_star_version
from .metrics_util import get_default_parameters
from .metrics_util import get_command_line
from .metrics_util import get_initial_user_parameters_from_command_line
from .metrics_util import get_all_user_parameters_from_command_line
from .metrics_util import get_final_user_redefined_parameters
from .metrics_util import get_final_effective_command_line
from .metrics_util import get_final_parameters_after_user_input
from .metrics_util import get_final_log_out
from .metrics_util import chrlength_txt_tsv_to_df
from .metrics_util import chrnamelength_txt_tsv_to_df
from .metrics_util import chrname_txt_tsv_to_df
from .metrics_util import chrstart_txt_tsv_to_df
from .metrics_util import select_tsv_to_df
from .metrics_util import sjdb_info_txt_tsv_to_df
from .metrics_util import sjdblist_out_tab_tsv_to_df

import pandas as pd

def star_log_out_to_df(metric_path, engine, run_state, run_uuid, logger):
    df_list = list()
    table_name_list = list()

    year = get_year(metric_path, logger)

    star_version = get_star_version(metric_path, logger)
    star_version_dict = {'version': [star_version]}
    df = pd.DataFrame.from_dict(star_version_dict)
    table_name='star_log_out_version'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_default_parameters(metric_path, run_uuid, logger)
    if 'outFileNamePrefix' not in df:
        df['outFileNamePrefix'] = None
    table_name='star_log_out_default_parameters'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_command_line(metric_path, run_uuid, logger)
    table_name = 'star_log_outcommand_line'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_initial_user_parameters_from_command_line(metric_path, run_uuid, logger)
    if 'outFileNamePrefix' not in df:
        df['outFileNamePrefix'] = None
    table_name = 'star_log_out_initial_user_parameters_from_command_line'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_all_user_parameters_from_command_line(metric_path, run_uuid, logger)
    table_name = 'star_log_out_all_user_parameters_from_command_line'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_final_user_redefined_parameters(metric_path, run_uuid, logger)
    table_name = 'star_log_out_final_user_redefined_parameters'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_final_effective_command_line(metric_path, run_uuid, logger)
    table_name = 'star_log_out_final_effective_command_line'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_final_parameters_after_user_input(metric_path, run_uuid, logger)
    table_name = 'star_log_out_final_parameters_after_user_input'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    for i, df in enumerate(df_list):
        table_name = table_name_list[i]
        if df is not None:
            df.to_sql(table_name, engine, if_exists='append')
    return year

def star_log_final_out_to_df(metric_path, engine, year, run_state, run_uuid, logger):
    df = get_final_log_out(metric_path, year, run_uuid, logger)
    table_name = 'star_final_log_out'
    df['run_state'] = run_state
    df.to_sql(table_name, engine, if_exists='append')
    return

def star_chrlength_txt_to_df(chrlength_txt_path, engine, run_state, run_uuid, logger):
    df = chrlength_txt_tsv_to_df(chrlength_txt_path, logger)
    table_name='star_chrlength_txt'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return

def star_chrnamelength_txt_to_df(chrnamelength_txt_path, engine, run_state, run_uuid, logger):
    df = chrnamelength_txt_tsv_to_df(chrnamelength_txt_path, logger)
    table_name = 'star_chrnamelength_txt'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return

def star_chrname_txt_to_df(chrname_txt_path, engine, run_state, run_uuid, logger):
    df = chrname_txt_tsv_to_df(chrname_txt_path, logger)
    table_name = 'star_chrname_txt'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return

def star_chrstart_txt_to_df(chrstart_txt_path, engine, run_state, run_uuid, logger):
    df = chrstart_txt_tsv_to_df(chrstart_txt_path, logger)
    table_name = 'star_chrstart_txt'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return

def star_genomeparameters_txt_to_df(genomeparameters_txt_path, engine, run_state, run_uuid, logger):
    select = '###'
    df = select_tsv_to_df(genomeparameters_txt_path, select, run_uuid, logger)
    table_name = 'star_genomeparameters_txt'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return df

# https://groups.google.com/forum/#!topic/rna-star/OSBdj1REhus
def star_sjdb_info_txt_to_df(sjdb_info_txt_path, engine, run_state, run_uuid, logger):
    df = sjdb_info_txt_tsv_to_df(sjdb_info_txt_path, logger)
    table_name = 'star_sjdb_info_txt'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return

# https://groups.google.com/forum/#!topic/rna-star/OSBdj1REhus
def star_sjdblist_out_tab_to_df(sjdblist_out_tab_path, engine, run_state, run_uuid, logger):
    df = sjdblist_out_tab_tsv_to_df(sjdblist_out_tab_path, logger)
    table_name = 'star_sjdblist_out_tab'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return

def run(run_uuid, engine, logger, metric_name,
        chrlength_txt_path, chrnamelength_txt_path, chrname_txt_path, chrstart_txt_path,
        genomeparameters_txt_path, log_out_path, sjdb_info_txt_path, sjdblist_out_tab_path):
    run_state = 'generate_intermediate_genome'
    star_chrlength_txt_to_df(chrlength_txt_path, engine, run_state, run_uuid, logger)
    star_chrnamelength_txt_to_df(chrnamelength_txt_path, engine, run_state, run_uuid, logger)
    star_chrname_txt_to_df(chrname_txt_path, engine, run_state, run_uuid, logger)
    star_chrstart_txt_to_df(chrstart_txt_path, engine, run_state, run_uuid, logger)
    star_genomeparameters_txt_to_df(genomeparameters_txt_path, engine, run_state, run_uuid, logger)
    star_log_out_to_df(log_out_path, engine, run_state, run_uuid, logger)
    star_sjdb_info_txt_to_df(sjdb_info_txt_path, engine, run_state, run_uuid, logger)
    star_sjdblist_out_tab_to_df(sjdblist_out_tab_path, engine, run_state, run_uuid, logger)
    return

