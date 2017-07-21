#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check if talend job runned without problem
"""
from datetime import datetime
import configparser
import argparse
import glob
import sys
import os
import re


config = {}

def get_time(line):
    try:
        strTime = re.split(' |;', line)[1]
        return datetime.strptime(strTime, "%H:%M:%S")
    except (IndexError, ValueError):
        raise Exception("Wrong format for line of log file")


def get_latest_job(job):    # pragma: no cover
    try:
        path = config['basePath'] + job + '/*'
        list_of_files = glob.glob(path)
        latest = max(list_of_files, key=os.path.getctime)
        return latest
    except ValueError:
        raise Exception("Path %s non-existant" % path)


def check_log_file(pathToFile):
    try:
        with open(pathToFile) as logFile:
            lines = logFile.readlines()

        startTime = get_time(lines[0])
        endTime = get_time(lines[-2])
        elapsedTime = endTime - startTime

        if config['endingString'] in lines[-2]:
            message = "OK: task run in {0}s | time={1}".format(
                                                            elapsedTime.seconds,
                                                            elapsedTime.total_seconds())
            return message, 0
        else:
            message = "CRITICAL: {0} | time={1}".format(
                                                        lines[-2].strip(),
                                                        elapsedTime.total_seconds())
            return message, 2

    except IOError:
        return "UNKNOWN: File %s not found" % pathToFile, 3
    except IndexError:  # Too few lines
        return "UNKNOWN: Not a talend log file", 3
    except Exception as e:
        return "UNKNOWN: " + " ".join(e.args), 3


def parse_args():   # pragma: no cover
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-j', '--job', required=True, help='Name of job')
    return argp.parse_args()


def create_conf():
    cfg = configparser.ConfigParser()
    cfg.add_section('main')


    global config
    config['basePath'] = input("Enter path to all job logs (ex : 'C:\SomeDir\\'): ")
    config['endingString'] = input("Enter string ending a correct talend log (ex ';END\\n') : ")

    cfg.set('main', 'basePath', config['basePath'])
    cfg.set('main', 'endingString', config['endingString'])

    cfg.write(open(sys.prefix+'/config.ini', 'w'))


def configure():
    cfg = configparser.ConfigParser()
    cfg.read(sys.prefix+"/config.ini")
    try:
        global config
        config['basePath'] = cfg.get('main', 'basePath')
        config['endingString'] = cfg.get('main', 'basePath')
    except configparser.NoSectionError:
        create_conf()


def main():
    args = parse_args()
    configure()

    message, status = check_log_file(get_latest_job(args.job))
    print(message)
    exit(status)


if __name__ == '__main__':  # pragma: no cover
    main()
