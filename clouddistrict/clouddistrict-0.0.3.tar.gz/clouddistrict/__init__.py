'''
clouddistrict

Generate occupants and occupations for your custom village, town or city! (for D&D purposes or related) (please do not imbibe clouddistrict while under the influence of other medications)
'''

__title__ = 'clouddistrict'
__version__ = '0.0.3'
__all__ = ()
__author__ = 'Johan Nestaas <johannestaas@gmail.com>'
__license__ = 'GPLv3+'
__copyright__ = 'Copyright 2017 Johan Nestaas'

from sys import exit
import yaml
from .town import Town


def main():
    import argparse
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest='cmd')

    p = subs.add_parser('create')
    p.add_argument('output_dir')
    p.add_argument('--config', '-c', default='town.yml')

    p = subs.add_parser('load')
    p.add_argument('raw_town_data')

    args = parser.parse_args()

    if args.cmd == 'create':
        try:
            town = Town(args.config)
        except ValueError as e:
            print(str(e))
            print('You might need to put less businesses and more residents.')
            exit(1)
        town.dump(args.output_dir)
        print('Dumped all files to directory: {}'.format(args.output_dir))
    elif args.cmd == 'load':
        with open(args.raw_town_data) as f:
            data = yaml.load(f.read())
        town = data['town']
        town.reload()
        print('loaded town (nothing implemented yet, will have shell later)')
    else:
        parser.print_usage()
        exit(1)


if __name__ == '__main__':
    main()
