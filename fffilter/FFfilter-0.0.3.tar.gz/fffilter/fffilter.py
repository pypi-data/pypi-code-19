#!/usr/bin/env python


"""
Filter media files by testing criteria against header metadata read by ffprobe.

Use: 
    fffilter /path/to/file --match display_aspect_ratio 4:3
    find . -name '*.mov' | fffilter --match height 1080 --match width 1920 -
    find . -name '*.mov' | fffilter - --show codec_type codec_name display_aspect_ratio width height
"""


import os
import sys
import json
import argparse
import subprocess


def _finditem(obj, key):
    '''
    Iterate through all key-value pairs in dictionary
    #See-- https://stackoverflow.com/a/14962509
    '''
    if key in obj:
        return obj[key]

    for k, v in obj.items():
        if isinstance(v, dict):
            item = _finditem(v, key)
            if item is not None:
                return item


def _say(message, out):
    '''
    Output given statment to std[out/err]
    '''
    out.write(message + '\n')
    out.flush()


def ffprobe(path):
    '''
    Return header json as dictionary
    '''
    options = ['ffprobe',
               '-i', path,
               '-print_format', 'json',
               '-show_streams',
               '-show_format',
               '-loglevel', 'quiet']

    try:
        s = subprocess.check_output(options)
        j = json.loads(s)
        return j
    except TypeError:
        j = json.loads(str(s, encoding='utf-8'))
        return j
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        return False


def match(path, **criteria):
    '''
    Extract header json and return True if all key-value pairs in [criteria] match
    '''
    results = show(path, criteria)
    if all(criteria[k] in results[k] for k in criteria):
        return True

    return False


def show(path, keys):
    '''
    Extract header json, and return a dictionary listing values for given keys
    '''
    matches = {}
    for k in keys:
        matches[k] = set()

    header = ffprobe(path)
    if header:

        try:
            streams = header['streams']
        except:
            streams = False

        for k in keys:
            v = _finditem(header, k)
            if v is not None:
                matches[k].add(v)

            if streams:
                for s in streams:
                    v = _finditem(s, k)
                    if v is not None:
                        matches[k].add(v)

        # Normalise sets to lists
        for i in matches:
            matches[i] = list(matches[i])

    return matches


def main():
    from colorama import init, Back, Style

    init()

    # Define CLI parameters
    parser=argparse.ArgumentParser()
    parser.add_argument(
        'file',
        help='Specify an input file, or set "-" to parse from stdout')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-m',
        '--match',
        action='append',
        nargs=2,
        metavar=('key','value'),
        help='''
            Lists files which match all criteria.
            Matching files are listed on stdout,
             non-matching files are listed on stderr.''')
    group.add_argument(
        '-s',
        '--show',
        nargs='+',
        help='Returns a tab-separated list of all possible values of occurrences of [key]')
    args = parser.parse_args()

    # Get file path from given file or stdin
    if args.file == '-':
        paths_str = sys.stdin.read().splitlines()
        paths = []
        for i in paths_str:
            paths.append(os.path.abspath(i))
    else:
        paths = [os.path.abspath(args.file)]

    # Process given file(s)
    for file in paths:
        message = False

        # --match
        if args.match:
            d = {}
            for k, v in args.match:
                d[k] = v

            status = match(file, **d)
            if status:
                _say(file, sys.stdout)
            else:
                _say(Back.RED + file + Style.RESET_ALL, sys.stderr)

        # --show
        elif args.show:
            results = show(file, args.show)

            output = []
            for k in args.show:
                output.append(','.join(str(x) for x in list(results[k])))

            message = file + '\t' + '\t'.join(output)
            _say(message, sys.stdout)


if __name__ == '__main__':
    main()