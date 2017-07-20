#!/usr/bin/env python

from argparse import ArgumentParser
from logging import basicConfig, DEBUG, getLogger, INFO
import os
from subprocess import check_output

def allow_create_fail(sql_path, logger):
    shell_cmd = "sed -i 's/CREATE TABLE/CREATE TABLE if not exists/g' " + sql_path
    check_output(shell_cmd, shell=True)
    shell_cmd = "sed -i 's/CREATE INDEX/CREATE INDEX if not exists/g' " + sql_path
    check_output(shell_cmd, shell=True)
    return

def get_table_column_list(sql_path, logger):
    table_column_list = list()
    with open(sql_path, 'r') as f_open:
        in_table = False
        for line in f_open:
            if line.startswith('CREATE TABLE'):
                in_table = True
                continue
            if line.startswith(');'):
                return table_column_list
            if in_table:
                line = line.strip().strip('\n').lstrip().rstrip(',')
                line_split = line.split()
                column_name = ' '.join(line_split[:-1])
                table_column_list.append(column_name)
    sys.exit('failed on file: %s' % sql_path)
    return

def alter_insert(table_column_list, sql_path, logger):
    specific_insert_file = 'specific_insert.sql'
    alter_sql_open = open(specific_insert_file, 'w')
    with open(sql_path, 'r') as f_open:
        for line in f_open:
            if line.startswith('INSERT INTO'):
                line = line.strip('\n')
                specific_columns = '(' + ','.join(table_column_list) + ')'
                logger.info('specific_columns=%s' % specific_columns)
                line_split = line.split()
                line_split.insert(3, specific_columns)
                new_line = ' '.join(line_split) + '\n'
                alter_sql_open.write(new_line)
            else:
                alter_sql_open.write(line)
    alter_sql_open.close()
    return specific_insert_file

def specific_column_insert(sql_path, logger):
    table_column_list = get_table_column_list(sql_path, logger)
    specific_insert_file = alter_insert(table_column_list, sql_path, logger)
    return specific_insert_file

def setup_logging(args, run_uuid):
    basicConfig(
        filename=os.path.join(run_uuid + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    getLogger('sqlalchemy.engine').setLevel(INFO)
    logger = getLogger(__name__)
    return logger

def main():
    parser = ArgumentParser('merge an arbitrary number of sqlite files')
    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = INFO)

    parser.add_argument('-s', '--source_sqlite',
                        action='append',
                        required=False
    )
    parser.add_argument('-u', '--run_uuid',
                        required=True
    )
    args = parser.parse_args()

    source_sqlite_list = args.source_sqlite
    run_uuid = args.run_uuid

    logger = setup_logging(args, run_uuid)

    if source_sqlite_list is None:
        logger.info('empty set, create 0 byte file')
        db_name = run_uuid + '.db'
        cmd = ['touch', db_name]
        output = check_output(cmd, shell=False)
    else:
        for source_sqlite_path in source_sqlite_list:
            logger.info('source_sqlite_path=%s' % source_sqlite_path)
            source_sqlite_name = os.path.splitext(os.path.basename(source_sqlite_path))[0]

            #dump
            source_dump_path = source_sqlite_name + '.sql'
            cmd = ['sqlite3', source_sqlite_path, "\'.dump\'", '>', source_dump_path ]
            shell_cmd = ' '.join(cmd)
            output = check_output(shell_cmd, shell=True)

            #alter text create table/index
            allow_create_fail(source_dump_path, logger)

            #specific column insert
            specific_insert_file = specific_column_insert(source_dump_path, logger)

            #load
            destination_sqlite_path = run_uuid + '.db'
            cmd = ['sqlite3', destination_sqlite_path, '<', specific_insert_file]
            shell_cmd = ' '.join(cmd)
            output = check_output(shell_cmd, shell=True)

if __name__ == '__main__':
    main()
