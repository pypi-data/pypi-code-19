import os

from .metrics_util import get_complex_genome_loading_parameters
from .metrics_util import get_complex_mate_names
from .metrics_util import get_complex_splicing_parameters
from .metrics_util import get_final_log_out
from .metrics_util import get_line
from .metrics_util import select_end_tsv_to_df
from .metrics_util import select_tsv_to_df
from .metrics_util import sj_out_tab_tsv_to_df
from .metrics_util import chrnamelength_txt_tsv_to_df
from .metrics_util import chrname_txt_tsv_to_df
from .metrics_util import chrlength_txt_tsv_to_df
from .metrics_util import chrstart_txt_tsv_to_df
from .metrics_util import sjdb_info_txt_tsv_to_df
from .metrics_util import sjdblist_out_tab_tsv_to_df

import pandas as pd

def get_star_version(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('STAR version='):
                line_split = line.split('=')
                star = line_split[1]
                star_split = star.split('_')
                star_version = star_split[1]
                return star_version
    return None

def get_command_line(metric_path, run_uuid, logger):
    select = '##### Command Line:'
    df = get_line(metric_path, select, run_uuid, logger)
    return df

def get_default_parameters(metric_path, run_uuid, logger):
    select = '##### DEFAULT parameters:'
    df = select_tsv_to_df(metric_path, select, run_uuid, logger)
    return df

def get_initial_user_parameters(metric_path, run_uuid, logger):
    select = '##### Initial USER parameters from Command Line:'
    df = select_tsv_to_df(metric_path, select, run_uuid, logger)
    return df

def get_all_user_parameters(metric_path, run_uuid, logger):
    select = '###### All USER parameters from Command Line:'
    df = select_tsv_to_df(metric_path, select, run_uuid, logger)
    return df

def get_final_user_redefined_parameters(metric_path, run_uuid, logger):
    select = '##### Final user re-defined parameters-----------------:'
    df = select_tsv_to_df(metric_path, select, run_uuid, logger)
    return df

def get_final_effective_command_line(metric_path, run_uuid, logger):
    select = '##### Final effective command line:'
    line = get_line(metric_path, select, run_uuid, logger)
    return line

def get_final_parameters_after_user_input(metric_path, run_uuid, logger):
    select = '##### Final parameters after user input--------------------------------:'
    end = '-'
    df = select_end_tsv_to_df(metric_path, select, end, run_uuid, logger)
    return df

def get_genome_generation_parameters(metric_path, run_uuid, logger):
    select = 'Reading genome generation parameters:'
    end = 'Genome version is compatible with current STAR version'
    df = select_end_tsv_to_df(metric_path, select, end, run_uuid, logger)
    return df

def get_genome_loading_parameters(metric_path, run_uuid, logger):
    df = get_complex_genome_loading_parameters(metric_path, run_uuid, logger)
    return df

def get_splicing_parameters(metric_path, run_uuid, logger):
    df = get_complex_splicing_parameters(metric_path, run_uuid, logger)
    return df

def get_mate_names(metric_path, run_uuid, logger):
    df = get_complex_mate_names(metric_path, run_uuid, logger)
    return df

def get_year(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('Started loading the genome:'):
                line_split = line.split()
                year = line_split[-1].strip()
                return year
    return None

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

    df = get_initial_user_parameters(metric_path, run_uuid, logger)
    if 'outFileNamePrefix' not in df:
        df['outFileNamePrefix'] = None
    table_name = 'star_log_out_initial_user_parameters'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_all_user_parameters(metric_path, run_uuid, logger)
    if 'outFileNamePrefix' not in df:
        df['outFileNamePrefix'] = None
    if 'outSAMattributes' not in df:
        df['outSAMattributes'] = None
    if 'outSAMattrRGline' not in df:
        df['outSAMattrRGline'] = None
    if 'outSAMheaderHD' not in df:
        df['outSAMheaderHD'] = None
    if 'outSAMmode' not in df:
        df['outSAMmode'] = None
    if 'outSAMunmapped' not in df:
        df['outSAMunmapped'] = None
    if 'limitBAMsortRAM' not in df:
        df['limitBAMsortRAM'] = None
    table_name = 'star_log_out_all_user_parameters'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_final_user_redefined_parameters(metric_path, run_uuid, logger)
    if 'outFileNamePrefix' not in df:
        df['outFileNamePrefix'] = None
    if 'outSAMattributes' not in df:
        df['outSAMattributes'] = None
    if 'outSAMattrRGline' not in df:
        df['outSAMattrRGline'] = None
    if 'outSAMheaderHD' not in df:
        df['outSAMheaderHD'] = None
    if 'outSAMmode' not in df:
        df['outSAMmode'] = None
    if 'outSAMunmapped' not in df:
        df['outSAMunmapped'] = None
    if 'limitBAMsortRAM' not in df:
        df['limitBAMsortRAM'] = None
    table_name = 'star_log_out_final_user_redefined_parameters'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = get_final_effective_command_line(metric_path, run_uuid, logger)
    table_name = 'star_log_out_final_effective_command_line'
    df['run_state'] = run_state
    df_list.append(df)
    table_name_list.append(table_name)

    df = final_parameters_after_user_input = get_final_parameters_after_user_input(metric_path, run_uuid, logger)
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

def star_sjdb_info_txt_to_df(metric_path, engine, run_state, run_uuid, logger):
    df = tsv_to_df(metric_path, logger)
    table_name = 'star_sj_out_tab'
    df['run_state'] = run_state
    df['run_uuid'] = run_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return

def get_chrlength(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            chrlength = int(line.strip('\n'))
            return chrlength
    return None

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
    star_log_out_to_df(log_out_path, engine, bam, run_state, run_uuid, logger)
    star_sjdb_info_txt_to_df(sjdb_info_txt_path, engine, run_state, run_uuid, logger)
    star_sjdblist_out_tab_to_df(sjdblist_out_tab_path, engine, run_state, run_uuid, logger)
    return

