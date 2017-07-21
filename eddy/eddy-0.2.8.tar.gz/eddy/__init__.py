#!/usr/bin/env python3
import logging, argparse, datetime, sys, importlib.util

from eddy import log
from eddy.readers import MDReader, RSTReader
from eddy.fs import FSystem
from eddy.settings import merge_settings, merge

from eddy.generators import Generator

__version__ = "0.3.0"
def parse() -> argparse.Namespace:
    """Command line flags logic"""
    parser = argparse.ArgumentParser(
        description="Static site generator with markdown.")

    parser.add_argument('-v', '--verbose', action='store_const',
                        const=logging.INFO, dest='verbosity',
                        help='Show all messages.')

    parser.add_argument('-q', '--quiet', action='store_const',
                        const=logging.CRITICAL, dest='verbosity',
                        help='Show only critical errors.')

    parser.add_argument('-D', '--debug', action='store_const',
                        const=logging.DEBUG, dest='verbosity',
                        help='Show all messages, including debug messages.')

    parser.add_argument('path', type=str, help="Statically instace path")
    return parser.parse_args()

def main():
    starting_time = datetime.datetime.now()
    args = parse()
    
    #Start logger
    logger = log.init_logging(__name__, args.verbosity, sys.stdout)
    logger.debug('Eddy version: %s', __version__)
    logger.debug('Python version: %s', sys.version.split()[0])

    fsystem = FSystem(args.path)

    known_readers = ['MDReader', 'RSTReader']
    readers = []
    
    #get user settings, complement with defaults
    settings = merge_settings(logger, fsystem.settings)
    for reader in known_readers+settings['READERS']:
        readers.append(eval(reader+"(logger, settings.get('URL', ''), settings['EXTENSIONS'].get(reader, None))"))

    generator = Generator(logger, fsystem)
    #traverse content folder
    for file, ext in fsystem.traverse():
        for reader in readers:
            if ext[1:] in reader.ext:
                file_data = reader.convert(file+ext) #read file
                file_data = merge(logger, file_data, settings)
                generator.get_context(file_data)

    generator.generate()

    print("Done in:", (datetime.datetime.now() - starting_time).total_seconds(), "seconds")

if __name__ == "__main__":
    main()
