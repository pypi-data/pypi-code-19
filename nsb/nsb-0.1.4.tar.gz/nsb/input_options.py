"""
allskymaps python package.

Draws Allsky Nightsky Images with stars from the GAIA catalog

    This work has made use of data from the European Space Agency (ESA)
    mission {\\it Gaia} (\\url{https://www.cosmos.esa.int/gaia}), processed by
    the {\\it Gaia} Data Processing and Analysis Consortium (DPAC,
    \\url{https://www.cosmos.esa.int/web/gaia/dpac/consortium}). Funding
    for the DPAC has been provided by national institutions, in particular
    the institutions participating in the {\\it Gaia} Multilateral Agreement.

and draws moonlight corresponding to the Model from Krisciunas et al.

   author = {{Krisciunas}, K. and {Schaefer}, B.~E.},
    title = "{A model of the brightness of moonlight}",
  journal = {\pasp},
     year = 1991,
    month = sep,
   volume = 103,
    pages = {1033-1039},
      doi = {10.1086/132921},
   adsurl = {http://adsabs.harvard.edu/abs/1991PASP..103.1033K},


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

Created and maintained by Matthias Buechele [FAU].

"""

__author__ = "Matthias Buechele"
__copyright__ = "Copyright 2017, Matthias Büchele"
__credits__ = ["Matthias Buechele"]
__license__ = "GNU GPL v3"
__shortname__ = "nsb"
__longname__ = ("Draws nightsky allskymaps corresponding to KRISCIUNAS Model of the Brightness of Moonlight,\n"
                "together with star data obtained from the GAIA public data release catalog.\n"
                "The result is a 2D Pixel array with physical brightness values for each sky position.")
__version__ = "0.0.2"
__maintainer__ = "Matthias Buechele"
__email__ = "matthias.buechele[at]fau[dot]de"
__status__ = "Prototype"  # "Prototype", "Development", or "Production"


import os
from nsb import nsbtools



class ReadOptions():
    def __init__(self, input_options):
        # Lambda: http://docs.python.org/release/2.5.2/tut/node6.html [4.7.5]
        self.options = {'--h': lambda: 'show_help', '--help': lambda: 'show_help',
                        '--o': lambda: 'output', '--output': lambda: 'output',
                        '--t': lambda: 'time', '--time': lambda: 'time',
                        '--l': lambda: 'location', '--location': lambda: 'location',
                        '--altaz': lambda: 'altaz',
                        '--q': lambda: 'source', '--source': lambda: 'source',
                        '--fov': lambda: 'fov',
                        '--s': lambda: 'size', '--size': lambda: 'size',
                        '--b': lambda: 'brightness', '--brightness': lambda: 'brightness',
                        '--hp': lambda: 'healpixlevel',
                        '--k': lambda: 'extinction',
                        '--use': lambda: 'altconf',
                        '-mags': lambda: 'mag',
                        '-noscreen': lambda: 'noscreen',
                        '-savefits': lambda: 'savefits'
                        }

        self.show_help = False
        self.input_options = input_options
        self.inputfile_set = False
        self.savestats = False
        self.savefits = False
        self.noscreen = False
        self.altconfset = False
        self.source_set = False

        while len(self.input_options) > 1:
            input_option = self.options.get(self.input_options[1], lambda: None)()
            if input_option == 'show_help':
                self.show_help = True
                # Stop reading options. Program will halt
                self.input_options = []

            elif input_option == 'time':
                try:
                    self.time = nsbtools.makeDate(input_options[2], input_options[3])

                    #self.time = ephem.Date((year, month, day, hour, minute, second))
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'location':
                self.lat, self.lon, self.elevation = input_options[2], input_options[3], input_options[4]
                self.input_options.remove(self.input_options[1])
                self.input_options.remove(self.input_options[1])
                self.input_options.remove(self.input_options[1])
                self.input_options.remove(self.input_options[1])

            elif input_option == 'size':
                try:
                    self.imageSize = int(input_options[2])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'fov':
                try:
                    self.fov = float(input_options[2])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'source':
                try:
                    self.source_set = True
                    self.tracked_source_name = input_options[2]
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'altaz':
                try:
                    self.alt = float(input_options[2])
                    self.az = float(input_options[3])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'healpixlevel':
                try:
                    self.healpixlevel = int(input_options[2])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'extinction':
                try:
                    self.extinction = float(input_options[2])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'brightness':
                try:
                    self.B_zero = float(input_options[2])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'gauss':
                try:
                    self.gauss = float(input_options[2])
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                except Exception as e:
                    self.incorrect_parameter()
                    print(e)

            elif input_option == 'mag':
                self.use_mag = True
                self.input_options.remove(self.input_options[1])

            elif input_option == 'savefits':
                self.savefits = True
                self.input_options.remove(self.input_options[1])

            elif input_option == 'noscreen':
                self.noscreen = True
                self.input_options.remove(self.input_options[1])

            elif input_option == 'output':
                if os.path.exists(input_options[2]):
                    self.output_dir = input_options[2]
                    self.input_options.remove(self.input_options[1])
                    self.input_options.remove(self.input_options[1])
                else:
                    print('Output path doesnt exist!')
                    self.incorrect_parameter()

            elif input_option == 'altconf':
                self.conf = input_options[2]
                self.altconfset = True
                self.input_options.remove(self.input_options[1])
                self.input_options.remove(self.input_options[1])

            else:
                self.incorrect_parameter()


    def incorrect_parameter(self):
        print('\nERR: Incorrect parameter ' + str(self.input_options[1]))
        self.input_options = []
        self.show_help = True

    def no_parameters(self):
        print('\nERR: Need at least a date and time')
        self.input_options = []
        self.show_help = True
#
