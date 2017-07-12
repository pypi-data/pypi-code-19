"""
solprim_solarradiation.py
=====
Python functions related to solar radiation

developed with Python3.5, tested with Python2.7

call package with 'import solprim_pckg.solarradiation as sr'

functions:
    - solar_spectrum_table_AM0 ()
    - solar_spectrum_table_AM15 ()
    - Planck_distribution (temp, wlen0, wlen1,steps)


'solprimer' Python Solar Energy Calculation Primer
Copyright (C) 2017 by Gianguido Piani
contact information : <solarprimer@mailbox.org>

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

For a full copy of the GNU General Public License see 
<http://www.gnu.org/licenses/>.

"""
# ===== ensure backward compatibility with Python2.7
from __future__ import division


import math

import matplotlib.pyplot as plt




def solar_spectrum_table_AM0 ():

    """
    tabulated values for the AM0 solar spectrum values

    input:
    - none
    
    returns:
    - extraterrestrial ETR solar spectrum AM0
    in the wavelenth range 0.3..4.0 micrometers

    irradiance values in W/ m2/ micrometer 
    
    the values are tabulated as tuple of two lists at fixed wavelength 
    points. The first list contains wavelenghts, the second list contains 
    energy density values.

    data source: Bird Simple Spectral Model @ NREL, USA
    http://rredc.nrel.gov/solar/models/spectral/SPCTRAL2/ 

    """
    
    # sol_spectr is a tuple of two lists: sol_spectr[0] contains the
    # wavelengths and sol_spectr[1] the corresponding radiation density
    # [W/m2 um]

    sol_spectr = [(0.300,0.305,0.310,0.315,0.320,0.325,0.330,0.335,
                   0.340,0.345,0.350,0.360,0.370,0.380,0.390,0.400,
                   0.410,0.420,0.430,0.440,0.450,0.460,0.470,0.480,
                   0.490,0.500,0.510,0.520,0.530,0.540,0.550,0.570,
                   0.593,0.610,0.630,0.656,0.668,0.690,0.710,0.718,
                   0.724,0.740,0.753,0.758,0.763,0.768,0.780,0.800,
                   0.816,0.824,0.832,0.840,0.860,0.880,0.905,0.915,
                   0.925,0.930,0.937,0.948,0.965,0.980,0.994,1.040,
                   1.070,1.100,1.120,1.130,1.145,1.161,1.170,1.200,
                   1.240,1.270,1.290,1.320,1.350,1.395,1.443,1.463,
                   1.477,1.497,1.520,1.539,1.558,1.578,1.592,1.610,
                   1.630,1.646,1.678,1.740,1.800,1.860,1.920,1.960,
                   1.985,2.005,2.035,2.065,2.100,2.148,2.198,2.270,
                   2.360,2.450,2.500,2.600,2.700,2.800,2.900,3.000,
                   3.100,3.200,3.300,3.400,3.500,3.600,3.700,3.800,
                   3.900,4.000),
                  (535.9,558.3,622.0,692.7,715.1,832.9,961.9,931.9,
                   900.6,911.3,975.5,975.9,1119.9,1103.8,1033.8,1479.1,
                   1701.3,1740.4,1587.2,1837.0,2005.0,2043.0,1987.0,
                   2027.0,1896.0,1909.0,1927.0,1831.0,1891.0,1898.0,
                   1892.0,1840.0,1768.0,1728.0,1658.0,1524.0,1531.0,
                   1420.0,1399.0,1374.0,1373.0,1298.0,1269.0,1245.0,
                   1223.0,1205.0,1183.0,1148.0,1091.0,1062.0,1038.0,
                   1022.0,998.7,947.2,893.2,868.2,829.7,830.3,814.0,
                   786.9,768.3,767.0,757.6,688.1,640.7,606.2,585.9,
                   570.2,564.1,544.2,533.4,501.6,477.5,442.7,440.0,
                   416.8,391.4,358.9,327.5,317.5,307.3,300.4,292.8,
                   275.5,272.1,259.3,246.9,244.0,243.5,234.8,220.5,
                   190.8,171.1,144.5,135.7,123.0,123.8,113.0,108.5,
                   97.5,92.4,82.4,74.6,68.3,63.8,49.5,48.5,38.6,
                   36.6,32.0,28.1,24.8,22.1,19.6,17.5,15.7,14.1,
                   12.7,11.5,10.4,9.5,8.6)]

    return sol_spectr



def solar_spectrum_table_AM15 ():

    """
    tabulated values for the AM1.5 solar spectrum values

    input:
    - none
    
    returns:
    - global terrestrial solar spectrum AM1.5 according to
    the Bird model with default assumptions in the wavelenth
    range 0.3..4.0 micrometers

    irradiance values in W/ m2/ micrometer 
    
    the values are tabulated as tuple of two lists at fixed wavelength
    points. The first list contains wavelenghts, the second list contains
    energy density values.

    data source: Bird Simple Spectral Model @ NREL, USA
    http://rredc.nrel.gov/solar/models/spectral/SPCTRAL2/ 

    """
    
    # sol_spectr is a tuple of two lists: sol_spectr[0] contains the
    # wavelengths and sol_spectr[1] the corresponding radiation density
    # [W/m2 um]

    sol_spectr = [(0.3050,0.3100,0.3150,0.3200,0.3250,0.3300,0.3350,0.3400,
                   0.3450,0.3500,0.3600,0.3700,0.3800,0.3900,0.4000,0.4100,
                   0.4200,0.4300,0.4400,0.4500,0.4600,0.4700,0.4800,0.4900,
                   0.5000,0.5100,0.5200,0.5300,0.5400,0.5500,0.5700,0.5900,
                   0.6100,0.6300,0.6500,0.6700,0.6900,0.7100,0.7180,0.7244,
                   0.7400,0.7525,0.7575,0.7625,0.7675,0.7800,0.8000,0.8160,
                   0.8237,0.8315,0.8400,0.8600,0.8800,0.9050,0.9150,0.9250,
                   0.9300,0.9370,0.9480,0.9650,0.9800,0.9935,1.0400,1.0700,
                   1.1000,1.1200,1.1300,1.1300,1.1370,1.1610,1.1800,1.2000,
                   1.2350,1.2900,1.3200,1.3500,1.3950,1.4425,1.4625,1.4770,
                   1.4970,1.5200,1.5390,1.5580,1.5780,1.5920,1.6100,1.6300,
                   1.6460,1.6780,1.7400,1.8000,1.8600,1.9200,1.9600,1.9850,
                   2.0050,2.0350,2.0650,2.1000,2.1480,2.1980,2.2700,2.3600,
                   2.4500,2.4940,2.5370,2.9410,2.9730,3.0050,3.0560,3.1320,
                   3.1560,3.2040,3.2450,3.3170,3.3440,3.4500,3.5730,3.7650,
                   4.0450),
                  (9.2,40.8,103.9,174.4,237.9,381.0,376.0,419.5,423.0,
                   466.2,501.4,642.1,686.7,694.6,976.4,1116.2,1141.1,
                   1033.0,1254.8,1470.7,1541.6,1523.7,1569.3,1483.4,1492.6,
                   1529.0,1431.1,1515.4,1494.5,1504.9,1447.1,1344.9,1431.5,
                   1382.1,1368.4,1341.8,1089.0,1269.0,973.7,1005.4,1167.3,
                   1150.6,1132.9,619.8,993.3,1090.1,1042.4,818.4,756.5,
                   883.2,925.1,943.4,899.4,721.4,643.3,665.3,389.0,248.9,
                   302.2,507.7,623.0,719.7,665.5,614.4,397.6,105.0,182.2,
                   182.2,127.4,326.7,443.3,408.2,463.1,398.1,241.1,31.3,
                   1.5,53.7,101.3,101.7,175.5,253.1,264.3,265.0,235.7,
                   238.4,220.4,235.6,226.3,212.5,165.3,29.6,1.9,1.2,20.4,
                   87.8,25.8,95.9,58.2,85.9,79.2,68.9,67.7,59.8,20.4,17.8,
                   3.1,4.2,7.3,6.3,3.1,5.2,18.7,1.3,3.1,12.6,3.1,12.8,11.5,
                   9.4,7.2)]

    return sol_spectr



def planck_distribution (temp, wlen0=0.3, wlen1=4.0, steps=120):
    
    """
    calculate Planck radiation distribution as function of wavelength

    input:
    - temp, blackbody temperature in Kelvin, float
    - wlen0, starting value for the calculation of Planck distribution
    in micrometer (um), float, default=0.3
    - wlen1, end value for the calculation, float, default=4.0
    the default values for wlen0, wlen1 encompass the most important
    part of the solar spectrum
    - steps, number of steps for the calculation, integer, default=120

    return:
    - tuple with two lists of length 'steps':
    - wavelength, float 
    - radiation value, float
    
    """

    # physical constants
    h_const = 6.626070e-34  # Planck constant h [J s]
    k_const = 1.380648e-23  # Boltzmann constant k [J/K]
    c_const = 299792458     # speed of light c [m/s]
    
    # intermediate coefficients
    two_h_c2 = 2 * h_const * (c_const ** 2)
    h_c = h_const * c_const
    k_t = k_const * temp

    # step length
    wlen_step = (wlen1 - wlen0)/(steps-1)

    # calculate Planck function at each wavelength point in the
    # range [wlen0..wlen1]

    planck_wlen = []        # list for wavelengths
    planck_rad = []         # list for radiation density values

    density_max = 0      # maximum value for radiation density 
    wlen_max = 0        # wavelength for maximum rad.density
    
    # irradiance correction for solid angle, distance sun-earth
    # scale the outcome to the value of solar irradiation
    # reaching the earth outer atmosphere
    # 1. multiply by pi * solar_radius^2
    # 2. divide by the square of the sun-earth distance
    # 3. divide by 10^6 to convert meter to micrometer
    
    d_se = 1.49e11  # mean distance sun-earth in meter (149 mln km)
                    # squared value is one steradians at sun-earth
                    # distance

    s_radius = 6.957e8  # solar radius in meter


    for i in range (0, steps):  
        wlen = wlen0 + i*wlen_step     # wavelength values for curve plot
        planck_wlen.append(wlen)
        
        # Planck radiation density at current wavelength
        wlen_m = wlen / 1e6  # convert wavelength from micrometers to meters
        fract_1 = two_h_c2 / (wlen_m**5) 
        fract_2 = math.exp(h_c / (wlen_m * k_t)) - 1 
        rad_wlen = fract_1 / fract_2  # Planck radiation at given wavelength

        # find max value for radiation, corresponding wavelength
        if rad_wlen > density_max:       
            density_max = rad_wlen 
            wlen_max = wlen             
            
        # scaling
        rad_wlen_e = rad_wlen*math.pi*(s_radius **2) /( (d_se**2) * 1e6)
        
        planck_rad.append(rad_wlen_e)


    density_e = density_max*math.pi*(s_radius **2) /( (d_se**2) * 1e6)
    

    print ('max value for Planck density function is ' +
           str(density_max))
    print ('equivalent to ' + str(round(density_e, 3)) +
           ' W/m2 micrometer')
    print ('at wavelength = ' + str(wlen_max))


    return planck_wlen, planck_rad  




