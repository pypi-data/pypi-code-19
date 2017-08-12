import sys
import numpy as np
import math
import os
import pkg_resources

import boxmox

samples_data_path = pkg_resources.resource_filename(__name__,
                            os.path.join('data','samples'))

def createEnvironment(ds, ds_args, scale_factor=1.0, diurnal_cycle=False, f=None):
    '''
    Create a BOXMOX Environment.csv input file using the dataset provided. Currently, this
    consists simply of values for temperature. The resulting file is written to f.
    '''
    env = boxmox.InputFile()

    TEMP = ds.get_temperature(**ds_args)
    TEMP = TEMP * scale_factor

    # timeFormat: "0" -> "TEMP" is constant with time
    #              "1" -> "seconds since simulation start"
    #              "2" -> "diurnal cycle"
    env.timeFormat    = 0
    env['TEMP']        = TEMP

    # if a time dependent "Environment.csv"-file is generated, the <LOCAL_SUN_TIME> (contained
    # in the dataset files) and "Environment_sample.csv"-file must be loaded; the
    # sample file contains an idealized diurnal temperature cycle (contained in the
    # "<chainDir>/data"-folder):
    if diurnal_cycle:

        LOCAL_SUN_TIME = ds.get_local_sun_time(**ds_args)

        # from boxmox sample file:
        with open(os.path.join(samples_data_path, 'Environment.csv'), 'rb') as f:
            env_sample = boxmox.InputFile(f)
        time_dcs = env_sample['time']
        TEMP_dcs = env_sample['TEMP']

        norm_fac = np.interp(LOCAL_SUN_TIME, time_dcs, TEMP_dcs)
        # The diurnal temperature cycle (TEMP_dcs) is normed with the the temperature at
        # <LOCAL_SUN_TIME> and multiplied with the dataset's temperature
        # <TEMP> to get a diurnal temperature cycle with
        # temperature(<LOCAL_SUN_TIME>)=<TEMP>:
        TEMP_ts = TEMP_dcs * TEMP / norm_fac   # Scaled because <TEMP> is scaled!

        env.timeFormat = 2
        env['time']     = time_dcs
        env['TEMP']     = TEMP_ts

    if not f is None:
        env.write(f)

    return env


def createInitialConditions(ds, ds_args, translator, mechanism, scale_factor=1.0, scale_species='none',
                                    static_species={ "M" : 1e6, "O2" : 0.20946e6, "N2" : 0.78084e6, "H2" : 0.5, "N2O" : 0.320 }, # fixed value species in ppmv
                                    f=None):
    '''
    Create a BOXMOX InitialConditions.csv input file using the dataset provided. A number of static species,
    provided as dictionary to the routine, are added as well. Those need to conform to the target mechanism naming
    and units (e.g. ppmv). The resulting file is written to f.
    '''

    # extract measurements
    flight_data_raw = ds.get_data(avg=True, **ds_args)

    # unit conversion - target is ppmv
    def unit_conversion(x):
        return {
            'ppmv' : 1.0,
            'ppbv' : 1.0e-3,
            'pptv' : 1.0e-6,
            'ppt'  : 1.0e-6,
        }.get(x, -9999999)    # default if x not found

    flight_data     = {}
    for key in ds.species_used:
        if key in flight_data_raw.keys():
            raw                 = flight_data_raw[key]
            units               = ds.get_units(key)
            flight_data[key]    = raw * unit_conversion(units)
            if not np.isfinite(flight_data[key]):
                del flight_data[key]

    # --- now, values contains all measurements we want to use in correct units

    # contains lists of tuples [(prefactor, ds species name), ...] for each mechanism species
    lumping = { key: translator.translate(key, mechanism, ds.name) for key in translator.mechs[mechanism].speciesnames }

    ic = boxmox.InputFile()
    ic.timeFormat = 0

    for key in translator.mechs[mechanism].speciesnames:
        for res in lumping[key].result:
            if res[1] in flight_data.keys():
                if not key in ic.keys():
                    ic[key] = 0.0
                # add each contributing ds species, weighted by their prefactor, to the mechanism species
                ic[key] += res[0] * flight_data[res[1]]

    # add static species
    for key in static_species.keys():
        ic[key] = static_species[key]

    # scale species
    for aScaleSpec in scale_species.split(','):
        if aScaleSpec in ic.keys():
            ic[aScaleSpec] *= scale_factor

    if not f is None:
        ic.write(f)

    return ic


def createPhotolysisRates(ds, ds_args, tuv, scale_factor=1.0, diurnal_cycle=False, f=None):
    '''
    Create a BOXMOX PhotolysisRates.csv input file using the dataset provided. TUV values are used
    to complement missing measurements. The resulting file is written to f.
    '''

    # does only work for strings
    def flatten(l):
        if len(l) > 0:
            return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]
        else:
            return []

    # get unique elements of list
    def unique(l):
        l = flatten(l)
        l = list(set(l))
        l.sort()
        l = [ x for x in l if x != '' ]
        return( l )

    # extract measurements
    flight_data_raw     = ds.get_data(avg=True, **ds_args)

    flight_data     = {}
    for key in ds.photrates_used:
        if key in flight_data_raw.keys():
            raw                 = flight_data_raw[key]
            flight_data[key]    = raw

    # --- now, values contains all measurements we want to use in correct units
    # next step - lumping

    lumping = tuv.translate(flight_data.keys(), 'TUV', 'BOXMOX')

    # photolysis rates we want:
    all_rates = unique(tuv.translator['BOXMOX'])

    # prep them all
    phot             = boxmox.InputFile()
    phot.timeFormat = 0
    for rate in all_rates:
        phot[rate]= float('NaN')

    # get the measured ones
    for ds_rate,mech_rates in lumping.iteritems():
        targets = flatten(mech_rates)
        targets = [ x for x in targets if x != '' ]
        nout = len(targets)
        if nout > 0:
            for target in targets:
                if (math.isnan(phot[target])):
                    phot[target] = 0.0
                phot[target] += flight_data[ds_rate]

    missing_rates       = [ key for key in phot.keys() if math.isnan(phot[key])]
    missing_rates_tuv   = tuv.translate(missing_rates, 'BOXMOX', 'TUV')

    # TUV photolysis rates

    db_settings = tuv.get_default_settings()

    # fill with dataset values, if available:
    for dim, variable in db_settings.iteritems():
        value = ds.get_var(variable[0], **ds_args)
        if (math.isnan(value)):
            value = variable[1]
        db_settings[dim][1] = value

    #      - 'timestamp' as datetime
    timestamp   = ds.get_timestamp(**ds_args)

    #      - 'height' in m
    height      = db_settings['height'][1] * 1000.0
    #      - 'o3col' in DU
    o3col       = db_settings['o3col'][1]
    #      - 'lat' in degrees
    lat         = db_settings['lat'][1]

    modeled_values, modeled_values_dc = tuv.get_phot_rates( timestamp, lat, height, o3col )

    # unit conversion?

    # create diurnal cycle out of measured rates
    if diurnal_cycle:

        # using jNO2 as reference
        scale_dc = modeled_values_dc['NO2->NO+O(3P)']
        scale_dc = scale_dc / max(scale_dc)

        scale_hours = modeled_values_dc['time']

        phot.timeFormat = 2
        phot['time']     = scale_hours

        import datetime

        meas_time = timestamp.time()
        meas_hour = meas_time.hour

        from numpy import interp

        scale = interp(meas_hour, scale_hours, scale_dc)

        if scale < 1e-10:
            import sys
            raise Exception("Can't handle photolysis measurements at dusk or night.")

        for key in [ x for x in phot.keys() if not x is 'time' ]:
            if not math.isnan(phot[key]):
                phot[key] = scale_dc * phot[key] / scale

        phot['time'] = scale_hours


    for mech_rate,tuv_rates in missing_rates_tuv.iteritems():
        targets = flatten(tuv_rates)
        targets = [ x for x in targets if x != '' ]

        nout = len(targets)
        if nout > 0:
            phot[mech_rate] = 0.0
            for target in targets:
                if diurnal_cycle:
                    phot[mech_rate] += modeled_values_dc[target]
                else:
                    phot[mech_rate] += modeled_values[target]


    # Scale photolysis rates:
    for key in phot.keys():
        if not key is 'time':
            phot[key] *= scale_factor

    # Create output file...
    if not f is None:
        phot.write(f)

    return phot

