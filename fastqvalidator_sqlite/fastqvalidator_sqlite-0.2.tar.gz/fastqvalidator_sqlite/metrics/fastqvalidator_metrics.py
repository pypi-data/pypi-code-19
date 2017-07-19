import os
import sys
from collections import defaultdict

import pandas as pd

def select_tsv_to_df(metric_path, select, logger):
    in_stat = False
    have_read_header = False
    data_dict = dict()
    with open(metric_path, 'r') as f_open:
        i = 0
        for line in f_open:
            line = line.strip('\n')
            if line.startswith(select):
                in_stat = True
            elif in_stat:
                if not have_read_header:
                    line_split = line.split('\t')
                    header = line_split
                    have_read_header = True
                else:
                    if len(line) < 1:
                        df = pd.DataFrame.from_dict(data_dict, orient='index')
                        # print('df=%s' % df)
                        # print('header=%s' % header)
                        # print('df.columns=%s' % df.columns)
                        # print('len(df.iloc[0])=%s' % len(df.iloc[0]))
                        # print('df.iloc[0]=%s' % df.iloc[0])
                        df.columns = header
                        return df
                    else:
                        line_split = line.split()
                        data_dict[i] = line_split
                        i += 1
    return None


def get_overall_average_phred_quality(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('Overall Average Phred Quality'):
                line_split = line.split('=')
                value = line_split[1].strip()
                return(float(value))
    return None


def get_lines_sequences(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('Finished processing'):
                line_split = line.split()
                fastq_lines = line_split[4]
                fastq_sequences = line_split[7]
                print('fastq_lines=%s' % fastq_lines)
                print('fastq_sequences=%s' % fastq_sequences)
                return int(fastq_lines), int(fastq_sequences)
    return None
    

def get_total_errors(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('There were a total of'):
                line_split = line.split()
                total_errors = line_split[5]
                return int(total_errors)
    return None


def get_return_values(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('Returning:'):
                line_split = line.split()
                return_int = line_split[1]
                return_code = line_split[3]
                return int(return_int), return_code
    return None


def get_fastq_name(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('Finished processing'):
                line_split = line.split()
                fastq_path = line_split[2]
                fastq_name = os.path.basename(fastq_path)
                return fastq_name
    return None


def run(run_uuid, metric_path, engine, logger):
    df_list = list()
    table_name_list = list()

    select = 'Base Composition Statistics:'
    df = select_tsv_to_df(metric_path, select, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append('fastqvalidator_base_composition_statistics')

    select = 'Average Phred Quality by Read Index (starts at 0):'
    df = select_tsv_to_df(metric_path, select, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append('fastqvalidator_average_phred_quality_by_read_index')

    # overall
    overall_average_phred_quality = get_overall_average_phred_quality(metric_path, logger)
    fastq_lines, fastq_sequences = get_lines_sequences(metric_path, logger)
    total_errors = get_total_errors(metric_path, logger)
    return_int, return_code = get_return_values(metric_path, logger)
    fastq_name = get_fastq_name(metric_path, logger)

    table_name = 'fastqvalidator_overall'
    overall_dict = dict()
    overall_dict['average_phred_quality'] = overall_average_phred_quality
    overall_dict['fastq_lines'] = fastq_lines
    overall_dict['fastq_sequences'] = fastq_sequences
    overall_dict['total_errors'] = total_errors
    overall_dict['return_int'] = return_int
    overall_dict['return_code'] = return_code
    overall_dict['fastq'] = fastq_name
    overall_dict['run_uuid'] = [run_uuid]
    overall_df = pd.DataFrame(overall_dict)
    overall_df.to_sql(table_name, engine, if_exists='append')

    for i, df in enumerate(df_list):
        df['run_uuid'] = run_uuid
        df['fastq'] = fastq_name
        table_name = table_name_list[i]
        df.to_sql(table_name, engine, if_exists='append')
    return
