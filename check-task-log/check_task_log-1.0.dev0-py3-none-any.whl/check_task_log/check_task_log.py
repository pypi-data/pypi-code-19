#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check if task job runned without problem
"""
from datetime import datetime
import configparser
import argparse
import glob
import os
import re


def get_time(line):
    try:
        strTime = re.split(' |;', line)[1]
        return datetime.strptime(strTime, "%H:%M:%S")
    except (IndexError, ValueError):
        raise Exception("Wrong format for line of log file")


def get_latest_job(job, basePath):    # pragma: no cover
    try:
        path = basePath + job + '/*'
        list_of_files = glob.glob(path)
        latest = max(list_of_files, key=os.path.getctime)
        return latest
    except ValueError:
        raise Exception("Path %s non-existant" % path)


def check_log_file(pathToFile, endingString, lineNumber):
    # TODO: possibility to look for regex in line
    # TODO: possibility to look in whole file instead of line
    try:
        with open(pathToFile) as logFile:
            lines = logFile.readlines()

        startTime = get_time(lines[0])
        endTime = get_time(lines[lineNumber])
        elapsedTime = endTime - startTime

        if endingString in lines[lineNumber]:
            message = "OK: task run in {0}s | time={1}".format(
                                                            elapsedTime.seconds,
                                                            elapsedTime.total_seconds())
            return message, 0
        else:
            message = "CRITICAL: {0} | time={1}".format(
                                                        lines[lineNumber].strip(),
                                                        elapsedTime.total_seconds())
            return message, 2

    except IOError:
        return "UNKNOWN: %s is not a file" % pathToFile, 3
    except IndexError:  # Too few lines
        return "UNKNOWN: this line does not exist (file too short)", 3
    except Exception as e:
        return "UNKNOWN: " + " ".join(e.args), 3


def parse_args():   # pragma: no cover
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-j', '--job', required=True, help='Name of job')
    argp.add_argument('-p', '--path', help="Path to folder containing jobs")
    argp.add_argument('-s', '--str', help="String to look for OK jobs (ex: ';END')")
    argp.add_argument('-l', '--line', default=-2, type=int,
                      help="Line where to look for string (default to -2)")
    return argp.parse_args()


def configure(args):
    cfg = configparser.ConfigParser()
    cfg.read(os.path.dirname(__file__)+"/config.ini")
    try:
        if not args.path:
            args.path = cfg.get('main', 'basePath')
        if not args.str:
            args.str = cfg.get('main', 'endingString')
    except configparser.NoSectionError:
        cfg.add_section('main')
        args.path = input("Enter path to all job logs (ex : 'C:\SomeDir\\'): ")
        args.str = input("Enter string ending a correct task log (ex ';END\\n') : ")

        cfg.set('main', 'basePath', args.path)
        cfg.set('main', 'endingString', args.str)

        cfg.write(open(os.path.dirname(__file__)+'/config.ini', 'w'))

    return args


def main():
    args = parse_args()
    args = configure(args)

    jobFile = get_latest_job(args.job, args.path)
    message, status = check_log_file(jobFile, args.str, args.line)
    print(message)
    exit(status)


if __name__ == '__main__':  # pragma: no cover
    main()
