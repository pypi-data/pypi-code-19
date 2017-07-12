# Copyright (c) 2017 Peter Tonner
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


def main():

    parser = argparse.ArgumentParser(
        prog='phenom', description='functional phenotype model.')

    parser.add_argument("--verbose", action='store_true')
    parser.add_argument('--dataFile', default='data.csv',
                        help='name of the data file on disk')
    parser.add_argument('--metaFile', default='meta.csv',
                        help='name of the meta file on disk')

    directory = parser.add_argument(
        'directory', help='directory containing the data for model inference')
