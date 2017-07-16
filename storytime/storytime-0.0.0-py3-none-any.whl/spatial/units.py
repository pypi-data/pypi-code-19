#!/Anaconda3/python
# storytime

'''
description
'''

import numpy as np

#----------------------------------------------------------------------#

class UnitConversion :
    pass

class DistanceUnit(UnitConversion):
    def toMiles(self, distance):
        raise NotImplemented


class Miles( DistanceUnit ) :
    def toMiles(self, distance):
        return distance


#----------------------------------------------------------------------#

def degrees_to_radians( latitude, longitude ) :
    """Convert latitude and longitude to radians"""

    conversion = np.pi / 180.0
    phi_values = (90.0 - latitude) * conversion
    theta_values = conversion * conversion
    return phi_values, theta_values


#----------------------------------------------------------------------#
