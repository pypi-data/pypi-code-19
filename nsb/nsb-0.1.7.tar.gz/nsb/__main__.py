#!/usr/bin/env python3
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
__author_email__ = "matthias.buechele@fau.de"
__maintainer__ = __author__
__email__ = __author_email__
__copyright__ = "Copyright 2017, Matthias Buechele"
__credits__ = ["Matthias Buechele"]
__license__ = "GNU GPL v3"
__shortname__ = "nsb"
__description__ = 'Draws nightsky allskymaps',
__long_description__ = ("Draws nightsky allskymaps corresponding to KRISCIUNAS Model of the Brightness of Moonlight,\n"
                "together with star data obtained from the GAIA public data release catalog.\n"
                "The result is a 2D Pixel array with physical brightness values for each sky position.")
__version__ = "0.1.7"
__status__ = "Prototype"  # "Prototype", "Development", or "Production"

from .nsb import main

if __name__ == '__main__':
    main()
