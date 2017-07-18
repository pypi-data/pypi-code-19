import csv
from datetime import datetime
import json
import os
import sys

import pandas as pd

def get_key_interval_dicts_from_json(key_intervalname_json_path, logger):
    with open(key_intervalname_json_path, 'r') as json_path_open:
        json_data = json.load(json_path_open)
    return json_data

def all_tsv_to_df(tsv_path, logger):
    logger.info('all_tsv_to_df open: %s' % tsv_path)
    data_dict = dict()
    with open(tsv_path, 'r') as tsv_open:
        i = 0
        for line in tsv_open:
            line = line.strip('\n')
            line_split = line.split('\t')
            data_dict[i] = line_split
            i += 1
    logger.info('data_dict=\n%s' % data_dict)
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    logger.info('df=\n%s' % df)
    return df

def select_tsv_to_df(metric_path, select, run_uuid, logger):
    in_stat = False
    data_dict = dict()
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith(select):
                in_stat = True
                continue
            if in_stat:
                if line.startswith('#') or len(line) < 1:
                    break
                else:
                    line_split = line.split()
                    line_key = line_split[0]
                    line_values = line_split[1:]
                    line_values_str = ','.join(line_values)
                    data_dict[line_key] = line_values_str
    data_dict['run_uuid'] = [run_uuid]
    df = pd.DataFrame.from_dict(data_dict, orient='columns')
    return df

def select_end_tsv_to_df(metric_path, select, end, run_uuid, logger):
    in_stat = False
    data_dict = dict()
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith(select):
                in_stat = True
                continue
            if in_stat:
                if line.startswith(end):
                    data_dict['run_uuid'] = [run_uuid]
                    df = pd.DataFrame.from_dict(data_dict, orient='columns')
                    return df
                else:
                    line_split = line.split()
                    line_key = line_split[0]
                    line_values = line_split[1:]
                    line_values_str = ','.join(line_values)
                    data_dict[line_key] = line_values_str
    logger.debug('no data saved to df')
    sys.exit(1)
    return None

def get_line(metric_path, select, run_uuid, logger):
    in_stat = False
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith(select):
                in_stat = True
                continue
            if in_stat:
                line_dict = {'line': line}
                line_dict['run_uuid'] = [run_uuid]
                df = pd.DataFrame.from_dict(line_dict, orient='columns')
                return df
    return None

def get_complex_genome_loading_parameters(metric_path, run_uuid, logger):
    '''
    genome_size_given = None
    sa_size_given = None
    saindex_size_given = None
    genome_size_loaded = None
    sa_size_loaded = None
    saindex_size_loaded = None
    genomeSAindexNbases = None
    nSAi = None
    nGenome = None
    nSAbyte = None
    GstrandBit = None
    SA_number_of_indices = None
    '''

    select = 'Genome: size given as a parameter'
    in_stat = False
    data_dict = dict()
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith(select):
                in_stat = True
                line_split = line.split('=')
                value = line_split[1].strip()
                data_dict['genome_size_given'] = int(value)
            if in_stat:
                if line.startswith('SA: size given as a parameter'):
                    line_split = line.split('=')
                    value = line_split[1].strip()
                    data_dict['sa_size_given'] = int(value)
                elif line.startswith('/SAindex: size given as a parameter'):
                    line_split = line.split('=')
                    value = line_split[1].strip()
                    data_dict['saindex_size_given'] = int(value)
                elif line.startswith('Read from SAindex:'):
                    line_split = line.split(':')
                    genomeSAindexNbases = line_split[1].strip().split()[0]
                    nSAi = line_split[1].strip().split()[1]
                    genomeSAindexNbases_value = int(genomeSAindexNbases.split('=')[1].strip())
                    nSAi_value = int(nSAi.split('=')[1].strip())
                    data_dict['nSAi'] = nSAi_value
                    data_dict['genomeSAindexNbases'] = genomeSAindexNbases_value
                elif line.startswith('nGenome='):
                    line_split = line.split(';')
                    ngenome = line_split[0]
                    ngenome_value = int(ngenome.split('=')[1].strip())
                    nsabyte = line_split[1].strip()
                    nsabyte_value = int(nsabyte.split('=')[1].strip())
                    data_dict['nGenome'] = ngenome_value
                    data_dict['nSAbyte'] = nsabyte_value
                elif line.startswith('GstrandBit='):
                    line_split = line.split('SA number')
                    gstrandbit_value = int(line_split[0].split('=')[1].strip())
                    sa_number_of_indices = int(line_split[1].split('=')[1].strip())
                    data_dict['GstrandBit'] = gstrandbit_value
                    data_dict['SA_number_of_indices'] = sa_number_of_indices
                elif line.startswith('Loading Genome ... done!'):
                    line_split = line.split(';')
                    loaded = int(line_split[1].strip().split()[1])
                    data_dict['genome_size_loaded'] = loaded
                elif line.startswith('Loading SA ... done!'):
                    line_split = line.split(';')
                    loaded = int(line_split[1].strip().split()[1])
                    data_dict['sa_size_loaded'] = loaded
                elif line.startswith('Loading SAindex ... done:'):
                    line_split = line.split(':')
                    loaded = int(line_split[1].strip().split()[0])
                    data_dict['saindex_size_loaded'] = loaded
                elif line.startswith('Finished loading the genome'):
                    data_dict['run_uuid'] = [run_uuid]
                    df = pd.DataFrame.from_dict(data_dict, orient='columns')
                    return df
    logger.debug('no data saved to df')
    sys.exit(1)
    return None

def get_complex_splicing_parameters(metric_path, run_uuid, logger):
    '''
    sjdbN=None
    sjdbOverhang=None
    '''
    select = 'Processing splice junctions database'
    in_stat = False
    data_dict = dict()
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith(select):
                in_stat = True
                line_split = line.split(',')
                sjdbN = int(line_split[0].split('=')[1])
                sjdbOverhang = int(line_split[1].split('=')[1])
                data_dict['sjdbN'] = sjdbN
                data_dict['sjdbOverhang'] = sjdbOverhang
            if in_stat:
                if 'winBinNbits' in line:
                    line_split = line.split('redefined')
                    winBinNbits = line_split[1].strip()
                    winBinNbits_value =  int(winBinNbits.split('=')[1])
                    data_dict['winBinNbits'] = winBinNbits_value
                elif 'winFlankNbins' in line:
                    line_split = line.split('redefined')[1].strip()
                    winFlankNbins = line_split.split()[0]
                    winAnchorDistNbins = line_split.split()[2]
                    winFlankNbins_value = int(winFlankNbins.split('=')[1].strip())
                    winAnchorDistNbins_value = int(winAnchorDistNbins.split('=')[1].strip())
                    data_dict['winFlankNbins'] = winFlankNbins_value
                    data_dict['winAnchorDistNbins'] = winAnchorDistNbins_value
                elif line.startswith('Starting to map file'):
                    data_dict['run_uuid'] = [run_uuid]
                    df = pd.DataFrame.from_dict(data_dict, orient='columns')
                    return df
    return None

def get_complex_mate_names(metric_path, run_uuid, logger):
    select = 'Starting to map file'
    end = 'Thread'
    in_stat = False
    data_dict = dict()
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith(select):
                in_stat = True
                continue
            if in_stat:
                if line.startswith(end):
                    #data_dict['run_uuid'] = [run_uuid]
                    df = pd.DataFrame.from_dict(data_dict, orient='index')
                    df.index.names = ['mate']
                    df.columns = ['file_name']
                    return df
                elif line.startswith('mate'):
                    line_split = line.split(':')
                    mate = line_split[0]
                    mate_int = int(mate.split()[1].strip())
                    file_path = line_split[1].strip()
                    file_name = os.path.basename(file_path)
                    data_dict[mate_int] = file_name
    return None

def get_final_log_out(metric_path, year, run_uuid, logger):
    data_dict = dict()
    in_section = str()
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n').strip()
            if len(line) < 1:
                continue
            if line.endswith(':'):
                in_section = line.replace(' ', '_').rstrip(':')
            elif '|' in line:
                line_split = line.split('|')
                key = line_split[0].strip().replace(' ', '_')
                if len(in_section) > 1:
                    key = in_section + '_' + key
                value = line_split[1].strip()
                if ' ' in value:
                    datetime_value = datetime.strptime(year + ' ' + value, "%Y %b %d %H:%M:%S")
                    datetime_iso = datetime_value.isoformat()
                    data_dict[key] = datetime_iso
                elif '%' in value:
                    value = value.strip('%')
                    value_float = float(value)
                    data_dict[key] = value_float
                elif '.' in value:
                    value_float = float(value)
                    data_dict[key] = value_float
                else:
                    value_int = int(value)
                    data_dict[key] = value_int
    data_dict['run_uuid'] = [run_uuid]
    df = pd.DataFrame.from_dict(data_dict, orient='columns')
    return df

def sj_out_tab_tsv_to_df(metric_path, logger):
    header = ['chromosome', 'first_base_of_the_intron',
              'last_base_of_the_intron', 'strand',
              'intron_motif', 'annotated',
              'number_of_uniquely_mapping_reads_crossing_the_junction',
              'number_of_multi-mapping_reads_crossing_the_junction',
              'maximum_spliced_alignment_overhang']
    df = pd.read_csv(metric_path, sep='\t', header=None, names=header)
    return df

def chrlength_txt_tsv_to_df(metric_path, logger):
    header = ['Length']
    df = pd.read_csv(metric_path, sep='\t', header=None, names=header)
    return df

def chrnamelength_txt_tsv_to_df(metric_path, logger):
    header = ['chrName', 'Length']
    df = pd.read_csv(metric_path, sep='\t', header=None, names=header)
    return df

def chrname_txt_tsv_to_df(metric_path, logger):
    header = ['chrName']
    df = pd.read_csv(metric_path, sep='\t', header=None, names=header)
    return df

def chrstart_txt_tsv_to_df(metric_path, logger):
    header = ['Start']
    df = pd.read_csv(metric_path, sep='\t', header=None, names=header)
    return df

def sjdb_info_txt_tsv_to_df(metric_path, logger):
    header = ['col1', 'col2', 'col3', 'col4', 'col5', 'col6']
    df = pd.read_csv(metric_path, sep='\t', header=None, names=header)
    return df

def sjdblist_out_tab_tsv_to_df(metric_path, logger):
    header = ['chromosome', 'first_base', 'last_base', 'strand']
    df = pd.read_csv(metric_path, sep='\t', header=None, names=header)
    return df

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
    if 'alignIntronMax' not in df:
        df['alignIntronMax'] = None
    if 'alignMatesGapMax' not in df:
        df['alignMatesGapMax'] = None
    if 'alignSJDBoverhangMin' not in df:
        df['alignSJDBoverhangMin'] = None
    if 'genomeDir' not in df:
        df['genomeDir'] = None
    if 'genomeFastaFiles' not in df:
        df['genomeFastaFiles'] = None
    if 'genomeLoad' not in df:
        df['genomeLoad'] = None
    if 'outFilterMatchNminOverLread' not in df:
        df['outFilterMatchNminOverLread'] = None
    if 'outFilterMismatchNmax' not in df:
        df['outFilterMismatchNmax'] = None
    if 'outFilterMultimapNmax' not in df:
        df['outFilterMultimapNmax'] = None
    if 'outFilterMultimapScoreRange' not in df:
        df['outFilterMultimapScoreRange'] = None
    if 'outFilterScoreMinOverLread' not in df:
        df['outFilterScoreMinOverLread'] = None
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
    if 'outSAMstrandField' not in df:
        df['outSAMstrandField'] = None
    if 'outSAMtype' not in df:
        df['outSAMtype'] = None
    if 'outSAMunmapped' not in df:
        df['outSAMunmapped'] = None
    if 'limitBAMsortRAM' not in df:
        df['limitBAMsortRAM'] = None
    if 'readFilesCommand' not in df:
        df['readFilesCommand'] = None
    if 'readFilesIn' not in df:
        df['readFilesIn'] = None
    if 'runMode' not in df:
        df['runMode'] = None
    if 'runThreadN' not in df:
        df['runThreadN'] = None
    if 'sjdbFileChrStartEnd' not in df:
        df['sjdbFileChrStartEnd'] = None
    if 'sjdbOverhang' not in df:
        df['sjdbOverhang'] = None
    if 'sjdbScore' not in df:
        df['sjdbScore'] = None
    return df

def get_final_user_redefined_parameters(metric_path, run_uuid, logger):
    select = '##### Final user re-defined parameters-----------------:'
    df = select_tsv_to_df(metric_path, select, run_uuid, logger)
    if 'alignIntronMax' not in df:
        df['alignIntronMax'] = None
    if 'alignMatesGapMax' not in df:
        df['alignMatesGapMax'] = None
    if 'alignSJDBoverhangMin' not in df:
        df['alignSJDBoverhangMin'] = None
    if 'genomeDir' not in df:
        df['genomeDir'] = None
    if 'genomeFastaFiles' not in df:
        df['genomeFastaFiles'] = None
    if 'genomeLoad' not in df:
        df['genomeLoad'] = None
    if 'outFilterMatchNminOverLread' not in df:
        df['outFilterMatchNminOverLread'] = None
    if 'outFilterMismatchNmax' not in df:
        df['outFilterMismatchNmax'] = None
    if 'outFilterMultimapNmax' not in df:
        df['outFilterMultimapNmax'] = None
    if 'outFilterMultimapScoreRange' not in df:
        df['outFilterMultimapScoreRange'] = None
    if 'outFilterScoreMinOverLread' not in df:
        df['outFilterScoreMinOverLread'] = None
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
    if 'outSAMstrandField' not in df:
        df['outSAMstrandField'] = None
    if 'outSAMtype' not in df:
        df['outSAMtype'] = None
    if 'outSAMunmapped' not in df:
        df['outSAMunmapped'] = None
    if 'limitBAMsortRAM' not in df:
        df['limitBAMsortRAM'] = None
    if 'readFilesCommand' not in df:
        df['readFilesCommand'] = None
    if 'readFilesIn' not in df:
        df['readFilesIn'] = None
    if 'runMode' not in df:
        df['runMode'] = None
    if 'runThreadN' not in df:
        df['runThreadN'] = None
    if 'sjdbFileChrStartEnd' not in df:
        df['sjdbFileChrStartEnd'] = None
    if 'sjdbOverhang' not in df:
        df['sjdbOverhang'] = None
    if 'sjdbScore' not in df:
        df['sjdbScore'] = None
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

def get_year(metric_path, logger):
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('Started loading the genome:'):
                line_split = line.split()
                year = line_split[-1].strip()
                return year
    return None

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
