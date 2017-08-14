#!python

import argparse
import os
from datetime import datetime

import ycm.parse as yp


# get command line args
# [source] [dest] flags

parser = argparse.ArgumentParser(description='Compile components in a Yaff project')
parser.add_argument('source', metavar='source', type=str, action='store',
                    help='source folder for the components')
parser.add_argument('target', metavar='target', type=str, action='store',
                    help='target folder for the compiled project')
parser.add_argument('-mkdir', dest='mkdir', action='store_const', const=True, default=False,
                    help='[optional] creates target directory if it does not exist')
parser.add_argument('-l', '--html', dest='html', action='store_const', const=True, default=False,
                    help='[optional] process component html')
parser.add_argument('-c', '--css', dest='css', action='store_const', const=True, default=False,
                    help='[optional] process component css')
parser.add_argument('-j', '--js', dest='js', action='store_const', const=True, default=False,
                    help='[optional] process component js')
parser.add_argument('-t', '--templates', dest='templates', action='store_const', const=True, default=False,
                    help='[optional] process project templates')

args = parser.parse_args()
process_flags = {'html': args.html, 'css': args.css, 'js': args.js, 'templates': args.templates}

# get working directories and check existence, creating target if not exists

cwd = os.getcwd()
source_path = os.path.join(cwd, args.source)
target_path = os.path.join(cwd, args.target)

if not os.path.exists(source_path):
    raise ValueError('Source path ' + source_path + ' does not exist')

if not os.path.exists(target_path):
    if not args.mkdir:
        print('YCompile exited unsuccessfully with the following error:')
        print('Target path ' + target_path + ' does not exist and mkdir flag not set')
        exit()
    else:
        os.makedirs(target_path)

# create a project object with source and targets
project = yp.YaffProject(source_path, target_path, process_flags)
print "Getting source file list..."
project.get_source_file_list()
print "Parsing header file..."
project.parse_header_file()
print "Getting source files..."
project.get_sources()

# write the output files
print "Writing target files..."
project.write_target_files()
print "Target files written. \nFinished compiling"

# write a log file
with open(os.path.join(target_path, 'yaff_compile.log'), 'w') as f:
    f.write('Compiled by Yaff Compiler v0.1.2\n')
    f.write('Timestamp: ' + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
    f.write('API version: {}'.format(project.headers['headers']['API_version']))
    f.close()
