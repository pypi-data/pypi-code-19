import os
import netCDF4
import csv
import re
import textwrap
from datetime import datetime

from numpy import any          as numpy_any
from numpy import arange       as numpy_arange
from numpy import arccos       as numpy_arccos
from numpy import arcsin       as numpy_arcsin
from numpy import array        as numpy_array
from numpy import clip         as numpy_clip
from numpy import column_stack as numpy_column_stack
from numpy import cos          as numpy_cos
from numpy import deg2rad      as numpy_deg2rad
from numpy import dtype        as numpy_dtype
from numpy import empty        as numpy_empty
from numpy import mean         as numpy_mean
from numpy import pi           as numpy_pi
from numpy import rad2deg      as numpy_rad2deg
from numpy import resize       as numpy_resize
from numpy import result_type  as numpy_result_type
from numpy import sin          as numpy_sin
from numpy import transpose    as numpy_transpose
from numpy import where        as numpy_where

from netCDF4 import date2num as netCDF4_date2num

from ..            import __version__, __Conventions__, __file__
from ..domain      import Domain
from ..coordinatereference import CoordinateReference
from ..field       import Field, FieldList
from ..cellmethods import CellMethods
from ..cfdatetime  import Datetime
from ..coordinate  import DimensionCoordinate, AuxiliaryCoordinate
from ..functions   import RTOL, ATOL, equals
from ..units       import Units
from ..functions   import (open_files_threshold_exceeded, close_one_file,
                           abspath)
from ..data.data import Data, Partition, PartitionMatrix

from .filearray     import UMFileArray
from .functions     import _open_um_file
from .umread.umfile import UMFileException

# --------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------
_pi_over_180 = numpy_pi/180.0

# PP missing data indicator
_pp_rmdi = -1.0e+30 

# Reference surface pressure in Pascals
_pstar     = 1.0e5

# --------------------------------------------------------------------
# Characters used in decoding LBEXP into a runid
# --------------------------------------------------------------------
_characters = ('a','b','c','d','e','f','g','h','i','j','k','l','m',
               'n','o','p','q','r','s','t','u','v','w','x','y','z', 
               '0','1','2','3','4','5','6','7','8','9')
_n_characters = len(_characters)

# --------------------------------------------------------------------
# Number matching regular expression
# --------------------------------------------------------------------
_number_regex = '([-+]?\d*\.?\d+(e[-+]?\d+)?)'

# --------------------------------------------------------------------
# Date-time object that copes with non-standard calendars
# --------------------------------------------------------------------
netCDF4_netcdftime_datetime = netCDF4.netcdftime.datetime

# --------------------------------------------------------------------
# Caches for derived values
# --------------------------------------------------------------------
_cache_latlon      = {}
_cached_runid      = {}
_cached_latlon     = {}
_cached_time       = {}
_cached_ctime      = {}
_cached_size_1_height_coordinate = {}
_cached_z_coordinate = {}
_cached_date2num = {}
_cached_model_level_number_coordinate = {}

_Units = {
    None                 : Units(),
    ''                   : Units(''),
    '1'                  : Units('1'),
    'Pa'                 : Units('Pa'),
    'm'                  : Units('m'),
    'hPa'                : Units('hPa'),
    'K'                  : Units('K'),
    'degrees'            : Units('degrees'),
    'degrees_east'       : Units('degrees_east'),
    'degrees_north'      : Units('degrees_north'),
    'days'               : Units('days'),
    'gregorian 1752-9-13': Units('days since 1752-9-13', 'gregorian'),
    '365_day 1752-9-13'  : Units('days since 1752-9-13', '365_day'),
    '360_day 0-1-1'      : Units('days since 0-1-1', '360_day'),
}

# --------------------------------------------------------------------
# Names of PP integer and real header items
# --------------------------------------------------------------------
_header_names = ('LBYR', 'LBMON', 'LBDAT', 'LBHR', 'LBMIN', 'LBDAY',
                 'LBYRD', 'LBMOND', 'LBDATD', 'LBHRD', 'LBMIND',
                 'LBDAYD', 'LBTIM', 'LBFT', 'LBLREC', 'LBCODE', 'LBHEM',
                 'LBROW', 'LBNPT', 'LBEXT', 'LBPACK', 'LBREL', 'LBFC',
                 'LBCFC', 'LBPROC', 'LBVC', 'LBRVC', 'LBEXP', 'LBEGIN', 
                 'LBNREC', 'LBPROJ', 'LBTYP', 'LBLEV', 'LBRSVD1',
                 'LBRSVD2', 'LBRSVD3', 'LBRSVD4', 'LBSRCE', 'LBUSER1',
                 'LBUSER2', 'LBUSER3', 'LBUSER4', 'LBUSER5', 'LBUSER6',
                 'LBUSER7',
                 'BRSVD1', 'BRSVD2', 'BRSVD3', 'BRSVD4', 
                 'BDATUM', 'BACC', 'BLEV', 'BRLEV', 'BHLEV', 'BHRLEV',
                 'BPLAT', 'BPLON', 'BGOR',
                 'BZY', 'BDY', 'BZX', 'BDX', 'BMDI', 'BMKS')

# --------------------------------------------------------------------
# Positions of PP header items in their arrays
# --------------------------------------------------------------------
(lbyr, lbmon, lbdat, lbhr, lbmin, lbday,
 lbyrd, lbmond, lbdatd, lbhrd, lbmind,
 lbdayd, lbtim, lbft, lblrec, lbcode, lbhem,
 lbrow, lbnpt, lbext, lbpack, lbrel, lbfc,
 lbcfc, lbproc, lbvc, lbrvc, lbexp, lbegin, 
 lbnrec, lbproj, lbtyp, lblev, lbrsvd1,
 lbrsvd2, lbrsvd3, lbrsvd4, lbsrce, lbuser1,
 lbuser2, lbuser3, lbuser4, lbuser5, lbuser6,
 lbuser7,
 ) = range(45)

(brsvd1, brsvd2, brsvd3, brsvd4, 
 bdatum, bacc, blev, brlev, bhlev, bhrlev,
 bplat, bplon, bgor,
 bzy, bdy, bzx, bdx, bmdi, bmks,
 ) = range(19)

# --------------------------------------------------------------------
# Map PP axis codes to CF standard names (The full list of field code
# keys may be found at
# http://cms.ncas.ac.uk/html_umdocs/wave/@header.)
# --------------------------------------------------------------------
_coord_standard_name = {
    0  : None, # Sigma (or eta, for hybrid coordinate data).
    1  : 'air_pressure', # Pressure (mb).
    2  : 'altitude', # Height above sea level (km).
    3  : 'atmosphere_hybrid_sigma_pressure_coordinate', # Eta (U.M. hybrid coordinates) only.
    4  : 'depth', # Depth below sea level (m)
    5  : 'model_level_number', # Model level.        
    6  : 'air_potential_temperature', # Theta
    7  : 'atmosphere_sigma_coordinate', # Sigma only.
    8  : None, # Sigma-theta
    10 : 'latitude',  # Latitude (degrees N). 
    11 : 'longitude', # Longitude (degrees E).
    13 : 'region', # Site number (set of parallel rows or columns e.g.Time series)
    14 : 'atmosphere_hybrid_height_coordinate',
    15 : 'height',
    20 : 'time', # Time (days) (Gregorian calendar (not 360 day year))
    21 : 'time', # Time (months)
    22 : 'time', # Time (years)
    23 : 'time', # Time (model days with 360 day model calendar)
    40 : None,   # pseudolevel
    99 : None,   # Other
    -10: 'grid_latitude',  # Rotated latitude (degrees). 
    -11: 'grid_longitude', # Rotated longitude (degrees).
    -20: 'radiation_wavelength',  
    }

# --------------------------------------------------------------------
# Map PP axis codes to CF long names.
# --------------------------------------------------------------------
_coord_long_name = {}

# --------------------------------------------------------------------
# Map PP axis codes to UDUNITS strings.
# --------------------------------------------------------------------
#_coord_units = {
_axiscode_to_units = {
    0  : '1',             # Sigma (or eta, for hybrid coordinate data)
    1  : 'hPa',           # air_pressure                      
    2  : 'm',             # altitude         
    3  : '1',             # atmosphere_hybrid_sigma_pressure_coordinate
    4  : 'm',             # depth                                  
    5  : '1',             # model_level_number                         
    6  : 'K',             # air_potential_temperature
    7  : '1',             # atmosphere_sigma_coordinate               
    10 : 'degrees_north', # latitude                               
    11 : 'degrees_east',  # longitude                                
    13 : '',              # region                                     
    14 : '1',             # atmosphere_hybrid_height_coordinate          
    15 : 'm',             # height                                      
    20 : 'days',          # time (gregorian)                    
    23 : 'days',          # time (360_day)
    40 : '1',             # pseudolevel
    -10: 'degrees', # rotated latitude  (not an official axis code)
    -11: 'degrees', # rotated longitude (not an official axis code)
}

# --------------------------------------------------------------------
# Map PP axis codes to cf.Units objects.
# --------------------------------------------------------------------
_axiscode_to_Units = {
    0  : _Units['1'],             # Sigma (or eta, for hybrid coordinate data)
    1  : _Units['hPa'],           # air_pressure                      
    2  : _Units['m'],             # altitude         
    3  : _Units['1'],             # atmosphere_hybrid_sigma_pressure_coordinate
    4  : _Units['m'],             # depth                                  
    5  : _Units['1'],             # model_level_number    
    6  : _Units['K'],             # air_potential_temperature
    7  : _Units['1'],             # atmosphere_sigma_coordinate  
    10 : _Units['degrees_north'], # latitude             
    11 : _Units['degrees_east'],  # longitude            
    13 : _Units[''],              # region               
    14 : _Units['1'],             # atmosphere_hybrid_height_coordinate
    15 : _Units['m'],             # height             
    20 : _Units['days'],          # time (gregorian)                    
    23 : _Units['days'],          # time (360_day)
    40 : _Units['1'],             # pseudolevel
    -10: _Units['degrees'], # rotated latitude  (not an official axis code)
    -11: _Units['degrees'], # rotated longitude (not an official axis code)
    }

# --------------------------------------------------------------------
# Map PP axis codes to CF axis attributes.
# --------------------------------------------------------------------
_coord_axis = {
    1  : 'Z',   # air_pressure                       
    2  : 'Z',   # altitude                                     
    3  : 'Z',   # atmosphere_hybrid_sigma_pressure_coordinate  
    4  : 'Z',   # depth                                        
    5  : 'Z',   # model_level_number                          
    6  : 'Z',   # air_potential_temperature
    7  : 'Z',   # atmosphere_sigma_coordinate                
    10 : 'Y',   # latitude                                     
    11 : 'X',   # longitude                                    
    13 : None,  # region                                       
    14 : 'Z',   # atmosphere_hybrid_height_coordinate          
    15 : 'Z',   # height                                       
    20 : 'T',   # time (gregorian)                                         
    23 : 'T',   # time (360_day)                                         
    40 : None,  # pseudolevel                                    
    -10: 'Y', # rotated latitude  (not an official axis code)
    -11: 'X', # rotated longitude (not an official axis code)         
    }

# --------------------------------------------------------------------
# Map PP axis codes to CF positive attributes.
# --------------------------------------------------------------------
_coord_positive = {
    1  : 'down',  # air_pressure                     
    2  : 'up',    # altitude                                  
    3  : 'down',  # atmosphere_hybrid_sigma_pressure_coordinate 
    4  : 'down',  # depth                                     
    5  : None,    # model_level_number                         
    6  : 'up',    # air_potential_temperature
    7  : 'down',  # atmosphere_sigma_coordinate               
    10 : None,    # latitude                                   
    11 : None,    # longitude                                   
    13 : None,    # region                                     
    14 : 'up',    # atmosphere_hybrid_height_coordinate         
    15 : 'up',    # height                                      
    20 : None,    # time (gregorian)                                          
    23 : None,    # time (360_day)                                        
    40 : None,    # pseudolevel                                    
    -10: None, # rotated latitude  (not an official axis code)
    -11: None, # rotated longitude (not an official axis code)
    }

# --------------------------------------------------------------------
# Map LBVC codes to PP axis codes. (The full list of field code keys
# may be found at http://cms.ncas.ac.uk/html_umdocs/wave/@fcodes.)
# --------------------------------------------------------------------
_lbvc_to_axiscode = {
    1  :  2,   # altitude (Height) 
    2  :  4,   # depth (Depth)
    3  : None, # (Geopotential (= g*height))
    4  : None, # (ICAO height)
    6  :  4,   # model_level_number   # changed from 5
    7  : None, # (Exner pressure)
    8  :  1,   # air_pressure  (Pressure)
    9  :  3,   # atmosphere_hybrid_sigma_pressure_coordinate (Hybrid pressure)
    10 :  7,   # atmosphere_sigma_coordinate (Sigma (= p/surface p))   ## dch check
    16 : None, # (Temperature T)
    19 :  6,   # air_potential_temperature (Potential temperature)
    27 : None, # (Atmospheric) density
    28 : None, # (d(p*)/dt .  p* = surface pressure)
    44 : None, # (Time in seconds)
    65 : 14,   # atmosphere_hybrid_height_coordinate (Hybrid height)
    129: None, # Surface
    176: 10,   # latitude    (Latitude)
    177: 11,   # longitude   (Longitude)
    }

# --------------------------------------------------------------------
# Map model identifier codes to model names. The model identifier code
# is the last four digits of LBSRCE.
# --------------------------------------------------------------------
_lbsrce_model_codes = {1111: 'UM'}

# --------------------------------------------------------------------
# Names of PP extra data codes
# --------------------------------------------------------------------
_extra_data_name = {
    1 : 'x',
    2 : 'y',
    3 : 'y_domain_lower_bound',
    4 : 'x_domain_lower_bound',
    5 : 'y_domain_upper_bound',
    6 : 'x_domain_upper_bound',
    7 : 'z_domain_lower_bound',
    8 : 'x_domain_upper_bound',
    9 : 'title',
    10: 'domain_title',
    11: 'x_lower_bound',
    12: 'x_upper_bound',
    13: 'y_lower_bound',
    14: 'y_upper_bound',
    }

# --------------------------------------------------------------------
# LBCODE values for unrotated latitude longitude grids
# --------------------------------------------------------------------
_true_latitude_longitude_lbcodes = set((1, 2))

# --------------------------------------------------------------------
# LBCODE values for rotated latitude longitude grids
# --------------------------------------------------------------------
_rotated_latitude_longitude_lbcodes = set((101, 102, 111))

_axis = {'t'   : 'dim0',
         'z'   : 'dim1',
         'y'   : 'dim2',
         'x'   : 'dim3',
         'r'   : 'dim4', 
         'p'   : 'dim5',
         'area': None,
     }

class UMField(object):
    '''

'''
    _debug = False

    def __init__(self, var, fmt, byte_ordering, word_size, um_version,
                 set_standard_name, height_at_top_of_model, **kwargs):
        '''

**Initialization**

:Parameters:

    var: `cf.um.umread.umfile.Var`

    byte_ordering: `str`
        'little_endian' or 'big_endian'

    word_size: `int`
        Word size in bytes (4 or 8).

    fmt: `str`
        'PP' or 'FF'

    um_version : number
    
    set_standard_name : bool
        If True then set the standard_name CF property.

    height_at_top_of_model : float, optional

    **kwargs : *optional*
        Keyword arguments specifying CF properties for the UM field.

'''       
        self._nonzero = False
       
        self.fmt                    = fmt
        self.height_at_top_of_model = height_at_top_of_model
        self.byte_ordering          = byte_ordering
        self.word_size              = word_size

        self.atol = ATOL()

        self.domain = Domain()

        cf_properties = {}
        attributes    = {}

        self.fields = []

        filename = abspath(var.file.path)
        self.filename = filename
    
        groups = var.group_records_by_extra_data()

        n_groups = len(groups)

        if n_groups == 1:
            # There is one group of records
            groups_nz = [var.nz]
            groups_nt = [var.nt]
#            if  var.nz == 15:
#                print var.nz, var.nt            
#                print  groups[0][0].int_hdr
#                print  groups[0][1].int_hdr
        elif n_groups > 1:
            # There are multiple groups of records, distinguished by
            # different extra data.
            groups_nz = []
            groups_nt = []
            groups2 = []
            for group in groups:
                group_size = len(group)
                if group_size == 1:
                    # There is only one record in this group
                    split_group= False
                    nz = 1
                elif group_size > 1:
                    # There are multiple records in this group
                    # Find the lengths of runs of identical times
                    times   = [(self.header_vtime(rec), self.header_dtime(rec))
                               for rec in group]
                    lengths = [len(tuple(g)) for k, g in itertools.groupby(times)]
                    if len(set(lengths)) == 1: 
                        # Each run of identical times has the same
                        # length, so it is possible that this group
                        # forms a variable of nz x nt records. 
                        split_group = False
                        nz = lengths.pop()
                        z0 = [self.z for rec in group[:nz]]
                        for i in range(nz, group_size, nz):
                            z1 = [self.header_z(rec) for rec in group[i:i+nz]]
                            if z1 != z0:
                                split_group = True
                                break
                    else:  
                        # Different runs of identical times have
                        # different lengths, so it is not possible for
                        # this group to form a variable of nz x nt
                        # records.
                        split_group = True
                        nz = 1
                #--- End: if
                    
                if split_group:
                    # This group doesn't form a complete nz x nt
                    # matrix, so split it up into 1 x 1 groups.
                    groups2.extend([[rec] for rec in group])
                    groups_nz.extend([1] * group_size)
                    groups_nt.extend([1] * group_size)
                else:
                    # This group forms a complete nz x nt matrix, so
                    # it may be considered as a variable in its own
                    # right and doesn't need to be split up.
                    groups2.append(group)
                    groups_nz.append(nz)
                    groups_nt.append(group_size/nz)
            #--- End: for
            groups = groups2
        #--- End: if

        rec0 = groups[0][0]

        int_hdr = rec0.int_hdr
        self.int_hdr_dtype = int_hdr.dtype

        int_hdr  = int_hdr.tolist()
        real_hdr = rec0.real_hdr.tolist()
        self.int_hdr  = int_hdr
        self.real_hdr = real_hdr

        # ------------------------------------------------------------
        # Set some metadata quantities which are guaranteed to be the
        # same for all records in a variable
        # ------------------------------------------------------------
        LBNPT   = int_hdr[lbnpt]
        LBROW   = int_hdr[lbrow]
        LBTIM   = int_hdr[lbtim]
        LBCODE  = int_hdr[lbcode]
        LBPROC  = int_hdr[lbproc]
        LBVC    = int_hdr[lbvc]
        LBUSER5 = int_hdr[lbuser5]
        BPLAT = real_hdr[bplat]
        BPLON = real_hdr[bplon]
        BDX   = real_hdr[bdx]
        BDY   = real_hdr[bdy]
        
        self.lbnpt   = LBNPT
        self.lbrow   = LBROW
        self.lbtim   = LBTIM
        self.lbproc  = LBPROC
        self.lbvc    = LBVC
        self.bplat = BPLAT
        self.bplon = BPLON
        self.bdx   = BDX
        self.bdy   = BDY

        # ------------------------------------------------------------
        # Set some derived metadata quantities which are (as good as)
        # guaranteed to be the same for all records in a variable
        # ------------------------------------------------------------
        self.lbtim_ia, ib = divmod(LBTIM, 100)
        self.lbtim_ib, ic = divmod(ib, 10)
        
        if ic == 1:
            calendar = 'gregorian'
        elif ic == 4:
            calendar = '365_day'
        else:
            calendar = '360_day'
    
        self.calendar = calendar
        self.reference_time_Units()
    
        header_um_version, source = divmod(int_hdr[lbsrce], 10000)
       
        if header_um_version > 0 and int(um_version) == um_version: #len(um_version) <= 3:
#            header_um_version = str(header_um_version)
            model_um_version = header_um_version
            self.um_version  = header_um_version
        else:
            model_um_version = None
            self.um_version  = um_version
            
        # Set source
        source = _lbsrce_model_codes.setdefault(source, None)
        if source is not None and model_um_version is not None:
            source += ' vn%s' % model_um_version
        if source:
            cf_properties['source'] = source
            
        # ------------------------------------------------------------
        # Set the T, Z, Y and X axis codes. These are guaranteed to be
        # the same for all records in a variable.
        # ------------------------------------------------------------
        if LBCODE == 1 or LBCODE == 2:
            # 1 = Unrotated regular lat/long grid
            # 2 = Regular lat/lon grid boxes (grid points are box
            #     centres)
            ix = 11
            iy = 10
        elif LBCODE == 101 or LBCODE == 102:
            # 101 = Rotated regular lat/long grid
            # 102 = Rotated regular lat/lon grid boxes (grid points
            #       are box centres)
            ix = -11  # rotated longitude (not an official axis code)
            iy = -10  # rotated latitude  (not an official axis code)
        elif LBCODE >= 10000:
            # Cross section
            ix, iy = divmod(divmod(LBCODE, 10000)[1], 100)
        else:
            ix = None
            iy = None
        

        iz = _lbvc_to_axiscode.setdefault(LBVC, None)
        

#        print LBVC, iz

        # Set it from the calendar type
        if iy in (20, 23) or ix in (20, 23):
            # Time is dealt with by x or y
            it = None
        elif calendar == 'gregorian':
            it = 20
        else:
            it = 23
        
        self.ix = ix
        self.iy = iy
        self.iz = iz
        self.it = it
    
        self.cf_info = {}
    
        # Set a identifying name based on the submodel and STASHcode
        # (or field code).
        stash    = int_hdr[lbuser4]
        submodel = int_hdr[lbuser7]
        self.stash = stash
    
        # The STASH code has been set in the PP header, so try to find
        # its standard_name from the conversion table
        stash_records = _stash2standard_name.get((submodel, stash), None)
    
        um_Units     = None
        long_name    = None
        um_condition = None
    
        if stash_records:
            um_version = self.um_version
            for (long_name, 
                 units,
                 valid_from,
                 valid_to, 
                 standard_name,
                 cf_info,
                 um_condition) in stash_records:
    
                # Check that conditions are met
                if not self.test_um_version(valid_from, valid_to, um_version):
                    continue
    
                if um_condition:
                    if not self.test_um_condition(um_condition,
                                                  LBCODE, BPLAT, BPLON):
                        continue
    
                # Still here? Then we have our standard_name, etc.
                if standard_name:
                    if set_standard_name:
                        cf_properties['standard_name'] = standard_name
                    else:
                        attributes['_standard_name'] = standard_name
                    
                cf_properties['long_name'] = long_name.rstrip()
    
                um_Units = _Units.get(units, None)
                if um_Units is None:
                    um_Units = Units(units)
                    _Units[units] = um_Units
    
                self.um_Units = um_Units
                self.cf_info  = cf_info
                
                break
            #--- End: for
        #--- End: if
    
        if stash:
            section, item = divmod(stash, 1000)
            um_stash_source = 'm%02ds%02di%03d' % (submodel, section, item)
            cf_properties['um_stash_source'] = um_stash_source 
            identity = 'UM_%s_vn%s' % (um_stash_source, self.um_version)
        else:
            identity = 'UM_%d_fc%d_vn%s' % (submodel, int_hdr[lbfc],
                                            self.um_version)
            
        if um_Units is None:
            self.um_Units = _Units[None]
    
        if um_condition:
            identity += '_%s' % um_condition
            
        if long_name is None:
            cf_properties['long_name'] = identity
                
        for recs, nz, nt in zip(groups, groups_nz, groups_nt):
            self.recs = recs
            self.nz = nz
            self.nt = nt
            self.z_recs = recs[:nz]
            self.t_recs = recs[::nz]
               
            LBUSER5 = recs[0].int_hdr.item(lbuser5,)

            self.cell_method_axis_name = {'area': 'area'}
    
            self.down_axes = set()
            self.z_axis    = 'z'
    
            # ------------------------------------------------------------
            # Get the extra data for this group
            # ------------------------------------------------------------
            extra = recs[0].get_extra_data()
            self.extra = extra

            # ------------------------------------------------------------
            # Set some derived metadata quantities
            # ------------------------------------------------------------
            if self._debug:
                print self.__dict__
                self.printfdr()
            
            # ------------------------------------------------------------
            # Create the 'T' dimension coordinate
            # ------------------------------------------------------------
            axiscode = it
            if axiscode is not None:         
                c = self.time_coordinate(axiscode)
    

            # ------------------------------------------------------------
            # Create the 'Z' dimension coordinate
            # ------------------------------------------------------------
            axiscode = iz
            if axiscode is not None:             
                # Get 'Z' coordinate from LBVC
                if axiscode == 3:
                    c = self.atmosphere_hybrid_sigma_pressure_coordinate(axiscode)
                elif axiscode == 2 and 'height' in self.cf_info:                
                    # Create the height coordinate from the information
                    # given in the STASH to standard_name conversion table
                    height, units = self.cf_info['height']
                    c = self.size_1_height_coordinate(axiscode, height, units)
                elif axiscode == 14:
                    c = self.atmosphere_hybrid_height_coordinate(axiscode)
                else:
                    c = self.z_coordinate(axiscode)
                             
   
                # Create a model_level_number auxiliary coordinate
                LBLEV = int_hdr[lblev]
                if LBVC in (2, 9, 65) or LBLEV in (7777, 8888): # CHECK!
                    self.LBLEV = LBLEV
                    c = self.model_level_number_coordinate(aux=bool(c)) 
            #--- End: if
     
            # ------------------------------------------------------------
            # Create the 'Y' dimension coordinate
            # ------------------------------------------------------------
            axiscode = iy
            yc = None
            if axiscode is not None:
                if axiscode in (20, 23):
                    # 'Y' axis is time-since-reference-date
                    if extra.get('y', None) is not None:                        
                        c = self.time_coordinate_from_extra_data(axiscode, 'y')
                    else:
                        LBUSER3 = int_hdr[lbuser3]
                        if LBUSER3 == LBROW:
                            self.lbuser3 = LBUSER3
                            c = self.time_coordinate_from_um_timeseries(axiscode,
                                                                       'y')
                else:
                    yc = self.xy_coordinate(axiscode, 'y')
            #--- End: if
    
            # ------------------------------------------------------------
            # Create the 'X' dimension coordinate
            # ------------------------------------------------------------
            axiscode = ix
            xc = None
            if axiscode is not None:
                if axiscode in (20, 23):
                    # X axis is time since reference date
                    if extra.get('x', None) is not None:                       
                        c = self.time_coordinate_from_extra_data(axiscode, 'x')
                    else:
                        LBUSER3 = int_hdr[lbuser3]
                        if LBUSER3 == LBNPT:
                            self.lbuser3 = LBUSER3
                            c = self.time_coordinate_from_um_timeseries(axiscode, 'x')
                else:
                    xc = self.xy_coordinate(axiscode, 'x')
            #--- End: if

            # -10: rotated latitude  (not an official axis code)
            # -11: rotated longitude (not an official axis code)


            if (iy, ix) == (-10, -11) or (iy, ix) == (-11, -10):
                # ----------------------------------------------------
                # Create a ROTATED_LATITUDE_LONGITUDE coordinate
                # reference
                # ----------------------------------------------------
                transform = CoordinateReference(
                    name='rotated_latitude_longitude',
                    grid_north_pole_latitude=BPLAT,
                    grid_north_pole_longitude=BPLON,
                    coords=(_axis['y'], _axis['x']))
    
                # --------------------------------------------------------
                # Create UNROTATED, 2-D LATITUDE and LONGITUDE auxiliary
                # coordinates
                # --------------------------------------------------------
                self.latitude_longitude_2d_aux_coordinates(yc, xc, transform)
    
                # Insert the coordinate reference into the domain
                self.domain.insert_ref(transform, copy=False)
            #--- End: if
    
            # ------------------------------------------------------------
            # Create a RADIATION WAVELENGTH dimension coordinate
            # ------------------------------------------------------------
            try:
                rwl, rwl_units = self.cf_info['below']
            except (KeyError, TypeError):
                pass
            else:
                c = self.radiation_wavelength_coordinate(rwl, rwl_units)
    
                # Set LBUSER5 to zero so that it is not confused for a
                # pseudolevel
                LBUSER5 = 0
            #--- End: try
    
            # ------------------------------------------------------------
            # Create a PSEUDOLEVEL dimension coordinate. This must be
            # done *after* the possible creation of a radiation
            # wavelength dimension coordinate.
            # ------------------------------------------------------------
            if LBUSER5 != 0:
                self.pseudolevel_coordinate(LBUSER5)
    
            attributes['int_hdr']  = int_hdr[:]
            attributes['real_hdr'] = real_hdr[:]
            attributes['file']     = filename        
            attributes['id']       = identity
            
            cf_properties['Conventions'] = __Conventions__
            cf_properties['runid']       = self.decode_lbexp()
            cf_properties['lbproc']      = str(LBPROC)
            cf_properties['lbtim']       = str(LBTIM)
            cf_properties['stash_code']  = str(stash)
    
            # ------------------------------------------------------------
            # Create cell methods
            # ------------------------------------------------------------
            cell_methods = self.create_cell_methods()
            if cell_methods is not None:
                cf_properties['cell_methods'] = cell_methods
    
            # ------------------------------------------------------------
            # Set the data and extra data
            # ------------------------------------------------------------
            data = self.create_data()

            cf_properties['_FillValue'] = data.fill_value

            # ------------------------------------------------------------
            # Create the field
            # ------------------------------------------------------------
            # Add kwargs to the CF properties
            cf_properties.update(kwargs)
            
            field = Field(domain=self.domain,
                          data=self.data,
                          axes=self.data_axes,
                          properties=cf_properties, 
                          attributes=attributes,
                          copy=False)
    
            # Check for decreasing axes that aren't decreasing
            down_axes = self.down_axes
            if down_axes:
                field.flip(down_axes, i=True)
                
            # Force cyclic X axis for paritcular values of LBHEM
            if int_hdr[lbhem] in (0, 1, 2, 4):
                field.cyclic('X', period=360)
                
            self.fields.append(field)
        #--- End: for

        self._nonzero = True
    #--- End: def

    def __nonzero__(self):
        '''

x.__nonzero__() <==> bool(x)

'''
        return self._nonzero
    #--- End: if

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return self.fdr()
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        out = [self.fdr()]        
        
        attrs = ('endian',
                 'reftime', 'vtime', 'dtime',
                 'um_version', 'source',
                 'it', 'iz', 'ix', 'iy', 
                 'site_time_cross_section', 'timeseries',
                 'file')

        for attr in attrs:
            out.append('%s=%s' % (attr, getattr(self, attr, None)))
            
        out.append('')

        return '\n'.join(out)   
    #--- End: def

    def atmosphere_hybrid_height_coordinate(self, axiscode):
        '''

**From appendix A of UMDP F3**

From UM Version 5.2, the method of defining the model levels in PP
headers was revised. At vn5.0 and 5.1, eta values were used in the PP
headers to specify the levels of model data, which was of limited use
when plotting data on model levels. From 5.2, the PP headers were
redefined to give information on the height of the level. Given a 2D
orography field, the height field for a given level can then be
derived. The height coordinates for PP-output are defined as:

  Z(i,j,k)=Zsea(k)+C(k)*orography(i,j)

where Zsea(k) and C(k) are height based hybrid coefficients.

  Zsea(k) = eta_value(k)*Height_at_top_of_model

  C(k)=[1-eta_value(k)/eta_value(first_constant_rho_level)]**2 forlevels less than or equal to first_constant_rho_level

  C(k)=0.0 for levels greater than first_constant_rho_level

where eta_value(k) is the eta_value for theta or rho level k. The
eta_value is a terrain-following height coordinate; full details are
given in UMDP15, Appendix B.

The PP headers store Zsea and C as follows :-

  * 46 = bulev = brsvd1  = Zsea of upper layer boundary
  * 52 = blev            = Zsea of level
  * 53 = brlev           = Zsea of lower layer boundary
  * 47 = bhulev = brsvd2 = C of upper layer boundary
  * 54 = bhlev           = C of level
  * 55 = bhrlev          = C of lower layer boundary

:Parameters:

    axiscode : int

:Returns:

    out : cf.DimensionCoordinate or None

        '''
        domain = self.domain
        zdim = _axis['z']

        # Insert new Z axis
        domain.insert_axis(self.nz, key=zdim)

        # "a" auxiliary coordinate
        array = numpy_array([rec.real_hdr[blev] for rec in self.z_recs],  # Zsea
                            dtype=float)
        bounds0 = numpy_array([rec.real_hdr[brlev] for rec in self.z_recs], #Zsea lower
                              dtype=float)
        bounds1 = numpy_array([rec.real_hdr[brsvd1] for rec in self.z_recs], #Zsea upper
                              dtype=float)
        bounds = numpy_column_stack((bounds0, bounds1))

        ac = AuxiliaryCoordinate()
        ac = self.coord_data(ac, array, bounds, units=_Units['m'])
        ac.id        = 'UM_atmosphere_hybrid_height_coordinate_a'
        ac.long_name = 'height based hybrid coeffient a'
        key_a = domain.insert_aux(ac, axes=[zdim], copy=False)

        # atmosphere_hybrid_height_coordinate dimension coordinate
        TOA_height = bounds1.max()
        if TOA_height <= 0:
            TOA_height = self.height_at_top_of_model
        if not TOA_height:
            dc = None
        else:            
            array  = array  / TOA_height
            bounds = bounds / TOA_height
                
            dc = DimensionCoordinate()
            dc = self.coord_data(dc, array, bounds, units=_Units[''])
            dc.standard_name = 'atmosphere_hybrid_height_coordinate'
            dc = self.coord_axis(dc, axiscode)
            dc = self.coord_positive(dc, axiscode, zdim)
            domain.insert_dim(dc, key=zdim, copy=False)
        #--- End: if

        # "b" auxiliary coordinate
        array = numpy_array([rec.real_hdr[bhlev] for rec in self.z_recs],
                            dtype=float)
        bounds0 = numpy_array([rec.real_hdr[bhrlev] for rec in self.z_recs],
                              dtype=float)
        bounds1 = numpy_array([rec.real_hdr[brsvd2] for rec in self.z_recs],
                              dtype=float)
        bounds = numpy_column_stack((bounds0, bounds1))

        ac = AuxiliaryCoordinate()
        ac = self.coord_data(ac, array, bounds, units=_Units['1'])
        ac.id        = 'UM_atmosphere_hybrid_height_coordinate_b'
        ac.long_name = 'height based hybrid coeffient b'
        key_b = domain.insert_aux(ac, axes=[zdim], copy=False)
        
        if bool(dc):
            self.cell_method_axis_name['z'] = dc.identity()
            
            # atmosphere_hybrid_height_coordinate coordinate reference
            ref = CoordinateReference(
                name='atmosphere_hybrid_height_coordinate',
                a=key_a, b=key_b,
                coords=(key_a, key_b), coord_terms=('a', 'b'))
            
            self.domain.insert_ref(ref, copy=False)
        #--- End: if

        return dc
    #--- End: def

    def depth_coordinate(self, axiscode):
        '''

:Parameters:

    axiscode : int

:Returns:

    out : cf.DimensionCoordinate or None

        '''
        dc = self.model_level_number_coordinate(aux=False)

        domain = self.domain
        zdim = _axis['z']

        array = numpy_array([rec.real_hdr[blev] for rec in self.z_recs],
                            dtype=float)
        bounds0 = numpy_array([rec.real_hdr[brlev] for rec in self.z_recs],
                              dtype=float)
        bounds1 = numpy_array([rec.real_hdr[brsvd1] for rec in self.z_recs],
                              dtype=float)
        bounds = numpy_column_stack((bounds0, bounds1))

        ac = AuxiliaryCoordinate()
        ac = self.coord_data(ac, array, bounds, units=_Units['m'])
        ac.id        = 'UM_atmosphere_hybrid_height_coordinate_ak'
        ac.long_name = 'atmosphere_hybrid_height_coordinate_ak'
        domain.insert_aux(ac, axes=[zdim], copy=False)

        array = numpy_array([rec.real_hdr[bhlev] for rec in self.z_recs],
                            dtype=float)
        bounds0 = numpy_array([rec.real_hdr[bhrlev] for rec in self.z_recs],
                              dtype=float)
        bounds1 = numpy_array([rec.real_hdr[brsvd2] for rec in self.z_recs],
                              dtype=float)
        bounds = numpy_column_stack((bounds0, bounds1))

        ac = AuxiliaryCoordinate()
        ac = self.coord_data(ac, array, bounds, units=_Units['1'])
        ac.id        = 'UM_atmosphere_hybrid_height_coordinate_bk'
        ac.long_name = 'atmosphere_hybrid_height_coordinate_bk'
        domain.insert_aux(ac, axes=[zdim], copy=False)
        
        if dc:
            self.cell_method_axis_name['z'] = dc.identity()

        return dc
    #--- End: def

    def atmosphere_hybrid_sigma_pressure_coordinate(self, axiscode):
        '''

atmosphere_hybrid_sigma_pressure_coordinate when not an array axis

:Parameters:

    axiscode : int

:Returns:

    out : cf.DimensionCoordinate

'''

# 46 BULEV Upper layer boundary or BRSVD(1)
# 
# 47 BHULEV Upper layer boundary or BRSVD(2)
# 
#         For hybrid levels:
#         - BULEV is B-value at half-level above.
#         - BHULEV is A-value at half-level above.
# 
#         For hybrid height levels (vn5.2-, Smooth heights)
#         - BULEV is Zsea of upper layer boundary
#             * If rho level: Zsea for theta level above
#         * If theta level: Zsea for rho level above
#         - BHLEV is C of upper layer boundary
#             * If rho level: C for theta level above
#             * If theta level: C for rho level above

        array     = []
        bounds    = []
        ak_array  = []
        ak_bounds = []
        bk_array  = []
        bk_bounds = []

        for rec in self.z_recs:
            BLEV, BRLEV, BHLEV, BHRLEV, BULEV, BHULEV = self.header_bz(rec)

            array.append(BLEV + BHLEV/_pstar)
            bounds.append([BRLEV + BHRLEV/_pstar, BULEV + BHULEV/_pstar])
            
            ak_array.append(BHLEV)
            ak_bounds.append((BHRLEV, BHULEV))
            
            bk_array.append(BLEV)
            bk_bounds.append((BRLEV , BULEV))
        #--- End: for    
   
        array     = numpy_array(array    , dtype=float)
        bounds    = numpy_array(bounds   , dtype=float)
        ak_array  = numpy_array(ak_array , dtype=float)
        ak_bounds = numpy_array(ak_bounds, dtype=float)
        bk_array  = numpy_array(bk_array , dtype=float)
        bk_bounds = numpy_array(bk_bounds, dtype=float)
        
        domain = self.domain

        zdim  = _axis['z']

        dc = DimensionCoordinate()
        dc = self.coord_data(
            dc, array, bounds,
            units=_axiscode_to_Units.setdefault(axiscode, None))
        dc = self.coord_positive(dc, axiscode, zdim)
        dc = self.coord_axis(dc, axiscode)
        dc = self.coord_names(dc, axiscode)
        domain.insert_dim(dc, key=zdim, copy=False)

        ac = AuxiliaryCoordinate()
        ac = self.coord_data(ac, ak_array, ak_bounds, units=_Units['Pa'])
        ac.id        = 'UM_atmosphere_hybrid_sigma_pressure_coordinate_ak'
        ac.long_name = 'atmosphere_hybrid_sigma_pressure_coordinate_ak'
        domain.insert_aux(ac, axes=[zdim], copy=False)

        ac = AuxiliaryCoordinate()
        ac = self.coord_data(ac, bk_array, bk_bounds, units=_Units['1'])
        domain.insert_aux(ac, axes=[zdim], copy=False)
        ac.id        = 'UM_atmosphere_hybrid_sigma_pressure_coordinate_bk'
        ac.long_name = 'atmosphere_hybrid_sigma_pressure_coordinate_bk'

        self.cell_method_axis_name['z'] = dc.identity()

        return dc
    #--- End: def
           
    def create_cell_methods(self):
        '''Create the cell methods

        '''
        cell_methods = []
        
        LBPROC = self.lbproc
        LBTIM_IB = self.lbtim_ib
        tmean_proc = 0
        if LBTIM_IB in (2, 3) and LBPROC in (128, 192, 2176, 4224, 8320):
            tmean_proc = 128
            LBPROC -= 128
                    
        # ------------------------------------------------------------
        # Area cell methods
        # ------------------------------------------------------------
        # -10: rotated latitude  (not an official axis code)
        # -11: rotated longitude (not an official axis code)
        if self.ix in (10, 11, 12, -10, -11) and self.iy in (10, 11, 12, -10, -11):
            cf_info = self.cf_info

            if 'where' in cf_info:
                cell_methods.append('area: mean')
                
                cell_methods.append(cf_info['where'])
                if 'over' in cf_info:
                    cell_methods.append(cf_info['over'])
             #--- End: if
   
            if LBPROC == 64:
               cell_methods.append('x: mean')

            # dch : do special zonal mean as as in pp_cfwrite
            
        # ------------------------------------------------------------
        # Vertical cell methods
        # ------------------------------------------------------------
        if LBPROC == 2048:
            cell_methods.append('z: mean')
    
        # ------------------------------------------------------------
        # Time cell methods
        # ------------------------------------------------------------
        if LBTIM_IB == 0 or LBTIM_IB == 1:
            cell_methods.append('t: point')
        elif LBPROC == 4096:
            cell_methods.append('t: minimum')
        elif LBPROC == 8192:
            cell_methods.append('t: maximum')
        if tmean_proc == 128:
            if LBTIM_IB == 2:
                cell_methods.append('t: mean')
            elif LBTIM_IB == 3:
                cell_methods.append('t: mean within years')
                cell_methods.append('t: mean over years')
        #--- End: if
    
        if not cell_methods:
            return None

        cell_methods = CellMethods(' '.join(cell_methods))
            
        cell_method_axis_name = self.cell_method_axis_name
        for c in cell_methods:
            names0 =  c.names[0]
            c.axes  = [_axis[name]                 for name in names0]
            c.names = [cell_method_axis_name[name] for name in names0]
        #--- End: for

        return cell_methods
    #--- End: def
  
    def coord_axis(self, c, axiscode):
        axis = _coord_axis.setdefault(axiscode, None)
        if axis is not None:
            c.axis = axis

        return c
    #--- End: def

    def coord_data(self, c, array=None, bounds=None,
                   units=None, fill_value=None, climatology=False):
        '''
   
Set the data array of a coordinate construct.

 :Parameters:
   
       c : cf.DimensionCoordinate or cf.AuxiliaryCoordinate
   
       data : array-like, optional
           The data array.
             
       bounds : array-like, optional
           The Cell bounds for the data array.
              
       units : cf.Units, optional
           The units of the data array.

       fill_value : optional

       climatology : bool, optional
           Whether or not the coordinate construct is a time
           climatology. By default it is not.

 :Returns:
   
       out : cf.Coordinate
        
        '''
        if array is not None:
            array = Data(array, units=units, fill_value=fill_value)
            
        if bounds is not None:
            bounds = Data(bounds, units=units, fill_value=fill_value)
            if climatology:
                c.climatology = True
        #--- End: if

        c.insert_data(array, bounds=bounds, copy=False)
   
        return c
    #--- End: def

    def coord_names(self, c, axiscode):
        '''
        '''
        standard_name = _coord_standard_name.setdefault(axiscode, None)
        if standard_name is not None:
            c.setprop('standard_name', standard_name)
            c.ncvar = standard_name
        else:
            long_name = _coord_long_name.setdefault(axiscode, None)
            if long_name is not None:
                c.long_name = long_name

        return c
    #--- End: def

    def coord_positive(self, c, axiscode, dim):
        positive = _coord_positive.setdefault(axiscode, None)
        if positive is not None:
            c.positive = positive
            if positive == 'down' and axiscode != 4:
                self.down_axes.add(dim)
        #--- End: def

        return c
    #--- End: def

    def ctime(self, rec):
        '''
        '''
        reftime = self.refUnits
        LBVTIME = tuple(self.header_vtime(rec))
        LBDTIME = tuple(self.header_dtime(rec))

        key = (LBVTIME, LBDTIME, self.refunits, self.calendar)
        ctime = _cached_ctime.get(key, None)
        if ctime is None:
#            LTIME = list(LBDTIME)
#            LTIME[0] =  LBVTIME[0]
            ctime = Datetime(*LBDTIME)
            ctime.year = LBVTIME[0]
            if ctime < Datetime(*LBVTIME):
                ctime.year += 1
            ctime = Data(ctime, reftime).array.item()
            _cached_ctime[key] = ctime
        #--- End: if

        return ctime
    #--- End: def

    def header_vtime(self, rec):
        '''

Return the list [LBYR, LBMON, LBDAT, LBHR, LBMIN] for the given
record.

:Parameters:

    rec : 

:Returns:

    out : list 

:Examples:

>>> u.header_vtime(rec)
[1991, 1, 1, 0, 0]

        '''
        return rec.int_hdr[lbyr:lbmin+1]
    #--- End: def

    def header_dtime(self, rec):
        '''

Return the list [LBYRD, LBMOND, LBDATD, LBHRD, LBMIND] for the
given record.

:Parameters:

    rec : 

:Returns:

    out : list 

:Examples:

>>> u.header_dtime(rec)
[1991, 2, 1, 0, 0]

        '''
        return rec.int_hdr[lbyrd:lbmind+1]
    #--- End: def

    def header_bz(self, rec):
        '''

Return the list [BLEV, BRLEV, BHLEV, BHRLEV, BULEV, BHULEV] for the
given record.

:Parameters:

    rec : 

:Returns:

    out : list 

:Examples:

>>> u.header_bz(rec)


'''
        real_hdr = rec.real_hdr
        return (real_hdr[blev:bhrlev+1].tolist()    +  # BLEV, BRLEV, BHLEV, BHRLEV
                real_hdr[brsvd1:brsvd2+1].tolist())    # BULEV, BHULEV
    #--- End: def
    
    def header_lz(self, rec):
        '''

Return the list [LBLEV, LBUSER5] for the given record.

:Parameters:

    rec : 

:Returns:

    out : list 

:Examples:

>>> u.header_lz(rec)


'''
        int_hdr = rec.int_hdr
        return [int_hdr.item(lblev,), int_hdr.item(lbuser5,)]
    #--- End: def

    def header_z(self, rec):
        '''

Return the list [LBLEV, LBUSER5, BLEV, BRLEV, BHLEV, BHRLEV, BULEV,
BHULEV] for the given record.

:Parameters:

    rec : 

:Returns:

    out : list 

:Examples:

>>> u.header_z(rec)


'''
        # ------------------------------------------------------------
        # These header items are used by the compare_levels function
        # in compare.c
        # ------------------------------------------------------------
        return self.header_lz + self.header_bz
    #--- End: def

    def create_data(self):
        '''

Sets the `!data` and `!data_axes` attributes.
    
:Returns:

    None
    
'''
        LBROW = self.lbrow
        LBNPT = self.lbnpt

        yx_shape = (LBROW, LBNPT)
        yx_size  = LBROW * LBNPT

        nz   = self.nz
        nt   = self.nt
        recs = self.recs

        units = self.um_Units

        data_type_in_file = self.data_type_in_file

        filename = self.filename

        data_axes = [_axis['y'], _axis['x']]

        if len(recs) == 1:
            # --------------------------------------------------------
            # 0-d partition matrix
            # --------------------------------------------------------            
            rec = recs[0]            
            data = Data(UMFileArray(file=filename, 
                                    ndim=2,
                                    shape=yx_shape,
                                    size=yx_size,
                                    dtype=data_type_in_file(rec),
                                    header_offset=rec.hdr_offset,
                                    data_offset=rec.data_offset,
                                    disk_length=rec.disk_length,
                                    fmt=self.fmt,
                                    word_size=self.word_size,
                                    byte_ordering=self.byte_ordering),
                        units=units,
                        fill_value=rec.real_hdr.item(bmdi,))
        else:
            # --------------------------------------------------------
            # 1-d or 2-d partition matrix
            # --------------------------------------------------------
            file_data_types = set()
            word_sizes = set()

            # Find the partition matrix shape
            pmshape = [n for n in (nt, nz) if n > 1]
            pmndim  = len(pmshape)
                      
            partitions = []
            empty_list = []
            partitions_append = partitions.append

            zero_to_LBROW = (0, LBROW)
            zero_to_LBNPT = (0, LBNPT)

            if pmndim == 1:
                # ----------------------------------------------------
                # 1-d partition matrix
                # ----------------------------------------------------
                data_ndim = 3
                if nz > 1:
                    pmaxes = [_axis[self.z_axis]]
                    data_shape = (nz, LBROW, LBNPT)
                    data_size  = nz * yx_size
                else:
                    pmaxes = [_axis['t']]
                    data_shape = (nt, LBROW, LBNPT)
                    data_size  = nt * yx_size

                partition_shape = [1, LBROW, LBNPT]

                for i, rec  in enumerate(recs):
                    # Find the data type of the array in the file
                    file_data_type = data_type_in_file(rec)
                    file_data_types.add(file_data_type)

                    subarray = UMFileArray(file=filename, 
                                           ndim=2,
                                           shape=yx_shape,
                                           size=yx_size,
                                           dtype=file_data_type,
                                           header_offset=rec.hdr_offset,
                                           data_offset=rec.data_offset,
                                           disk_length=rec.disk_length,
                                           fmt=self.fmt,
                                           word_size=self.word_size,
                                           byte_ordering=self.byte_ordering)

                    partitions_append(Partition(
                        subarray = subarray,
                        location = [(i, i+1), zero_to_LBROW, zero_to_LBNPT],
                        shape    = partition_shape,
                        axes     = data_axes,
                        flip     = empty_list,
                        part     = empty_list,
                        Units    = units))
                #--- End: for

                # Populate the 1-d partition matrix
                matrix = numpy_array(partitions, dtype=object)
            else:
                # ----------------------------------------------------
                # 2-d partition matrix
                # ----------------------------------------------------
                pmaxes = [_axis['t'], _axis[self.z_axis]]
                data_shape = (nt, nz, LBROW, LBNPT)
                data_size  = nt * nz * yx_size
                data_ndim  = 4

                partition_shape = [1, 1, LBROW, LBNPT]

                for i, rec  in enumerate(recs):
                    # Find T and Z axis indices
                    t, z = divmod(i, nz)
                 
                    # Find the data type of the array in the file
                    file_data_type = data_type_in_file(rec)
                    file_data_types.add(file_data_type)

                    subarray = UMFileArray(file=filename,  
                                           ndim=2,
                                           shape=yx_shape,
                                           size=yx_size,
                                           dtype=file_data_type,
                                           header_offset=rec.hdr_offset,
                                           data_offset=rec.data_offset,
                                           disk_length=rec.disk_length,
                                           fmt=self.fmt,
                                           word_size=self.word_size,
                                           byte_ordering=self.byte_ordering)

                    partitions_append(Partition(
                        subarray=subarray,
                        location=[(t, t+1), (z, z+1), zero_to_LBROW, zero_to_LBNPT],
                        shape=partition_shape,
                        axes=data_axes,
                        flip=empty_list,
                        part=empty_list,
                        Units=units))
                #--- End: for

                # Populate the 2-d partition matrix
                matrix = numpy_array(partitions, dtype=object)
                matrix.resize(pmshape)                
            #--- End: if
                       
            data_axes = pmaxes + data_axes

            # Set the data array
            data = Data(units=units, fill_value=recs[0].real_hdr.item(bmdi,))

            data._axes      = data_axes
            data._shape     = data_shape 
            data._ndim      = data_ndim
            data._size      = data_size
            data.partitions = PartitionMatrix(matrix, pmaxes)
            data.dtype      = numpy_result_type(*file_data_types)
        #--- End: if

        self.data      = data
        self.data_axes = data_axes

        return data
    #---End: def

    def decode_lbexp(self):
        '''Decode the integer value of LBEXP in the PP header into a runid.
    
If this value has already been decoded, then it will be returned from
the cache, otherwise the value will be decoded and then added to the
cache.

:Returns:

    out : str
       A string derived from LBEXP. If LBEXP is a negative integer
       then that number is returned as a string.

:Examples:

>>> self.decode_lbexp()
'aaa5u'
>>> self.decode_lbexp()
'-34'

        '''
        LBEXP = self.int_hdr[lbexp]

        runid = _cached_runid.get(LBEXP, None)
        if runid is not None:
            # Return a cached decoding of this LBEXP
            return runid
    
        if LBEXP < 0:
            runid = str(LBEXP)
        else:
            # Convert LBEXP to a binary string, filled out to 30 bits with
            # zeros
            bits = bin(LBEXP)
            bits = bits.lstrip('0b').zfill(30)
        
            # Step through 6 bits at a time, converting each 6 bit chunk into
            # a decimal integer, which is used as an index to the characters
            # lookup list.
            runid = []
            for i in xrange(0,30,6):
                index = int(bits[i:i+6], 2) 
                if index < _n_characters:
                    runid.append(_characters[index])
            #--- End: for
            runid = ''.join(runid)
        #--- End: def

        # Enter this runid into the cache
        _cached_runid[LBEXP] = runid
    
        # Return the runid
        return runid
    #--- End: def 

    def dtime(self, rec):
        '''
        '''
        reftime = self.refUnits
        units    = self.refunits
        calendar = self.calendar

        LBDTIME = tuple(self.header_dtime(rec))

        key = (LBDTIME, units, calendar)
        time = _cached_date2num.get(key, None)
        if time is None:
            # It is important to use the same time_units as vtime
            if self.calendar == 'gregorian':
                time = netCDF4_date2num(
                    datetime(*LBDTIME), units, calendar)
            else:
                time = netCDF4_date2num(
                    netCDF4_netcdftime_datetime(*LBDTIME), units, calendar)
            _cached_date2num[key] = time
        #--- End: if

        return time
    #--- End: def

    def fdr(self):
        '''Return a the contents of PP field headers as strings.

This is a bit like printfdr in the UKMO IDL PP library.

:Returns:

    out : list

'''
        out2 = []
        for i, rec in enumerate(self.recs):
            out = ['Field %d:' % i]

            x = ['%s::%s' % (name, value)
                 for name, value in zip(_header_names,
                                        self.int_hdr + self.real_hdr)]
            
            x = textwrap.fill(' '.join(x), width=79)
            out.append(x.replace('::', ': '))
            
            if self.extra:
                out.append('EXTRA DATA:')
                for key in sorted(self.extra):
                    out.append('%s: %s' % (key, str(self.extra[key])))
            #--- End: if

            out.append('file: '+self.filename)
            out.append('format, byte order, word size: %s, %s, %d' % 
                       (self.fmt, self.byte_ordering, self.word_size))

            out.append('')

            out2.append('\n'.join(out))
        #--- End: for

        return out2
    #--- End: def

    def latitude_longitude_2d_aux_coordinates(self, yc, xc, transform):
        '''
'''
        BDX   = self.bdx
        BDY   = self.bdy
        LBNPT = self.lbnpt
        LBROW = self.lbrow
        BPLAT = self.bplat
        BPLON = self.bplon
        
        # Create the unrotated latitude and longitude arrays if we
        # couldn't find them in the cache
        cache_key = (LBNPT, LBROW, BDX, BDY, BPLAT, BPLON)
        lat, lon = _cache_latlon.get(cache_key, (None, None))

        if lat is None:
            lat, lon = self.unrotated_latlon(yc.varray, xc.varray,
                                             BPLAT, BPLON) 

            atol = self.atol
            if abs(BDX) >= atol and abs(BDY) >= atol:
                _cache_latlon[cache_key] = (lat, lon)
        #--- End: if

#        if xc.hasbounds and yc.hasbounds:
#            cache_key = ('bounds',) + cache_key
#            lat_bounds, lon_bounds = _cache_latlon.get(cache_key, (None, None))
#            print lat_bounds
#            if lat_bounds is None:
#                print  'CALC BOUNDS'
#                xb = numpy_empty(xc.size+1)
#                yb = numpy_empty(yc.size+1)
#                xb[:-1] = xc.bounds.subspace[ :, 0].squeeze(1, i=True).array
#                xb[-1 ] = xc.bounds.subspace[-1, 1].squeeze(1, i=True).array
#                yb[:-1] = yc.bounds.subspace[ :, 0].squeeze(1, i=True).array
#                yb[-1 ] = yc.bounds.subspace[-1, 1].squeeze(1, i=True).array
#                
#                lat_bounds, lon_bounds = self.unrotated_latlon(yb, xb, BPLAT, BPLON) 
#
#                print lat_bounds
#                print lat_bounds.shape
#                yyy = numpy_empty(lat.shape + (4,))
#
#                
#
#                print lat.shape, yyy.shape
#
#            atol = self.atol
#            if abs(BDX) >= atol and abs(BDY) >= atol:
#                _cache_latlon[cache_key] = (lat, lon)
        #--- End: if

        axes = [_axis['y'], _axis['x']]
        
        for axiscode, array in zip((10,  11),
                                   (lat, lon)):
            ac = AuxiliaryCoordinate()
            ac = self.coord_data(ac, array,
                                 units=_axiscode_to_Units.setdefault(axiscode, None))
            ac = self.coord_names(ac, axiscode)
            
            key = self.domain.insert_aux(ac, axes=axes, copy=False)
            
            transform.coords.add(key)
        #--- End: for
    #--- End: def

    def model_level_number_coordinate(self, aux=False):
        '''model_level_number dimension or auxiliary coordinate

:Parameters:

    aux : bool

:Returns:

    out : cf.AuxiliaryCoordinate or cf.DimensionCoordinate or None

''' 
        array = tuple([rec.int_hdr.item(lblev,) for rec in self.z_recs])

        key = array
        c = _cached_model_level_number_coordinate.get(key, None)

        if c is not None:
            if aux:
                self.domain.insert_aux(c, axes=[_axis['z']], copy=True)
            else:
                self.domain.insert_dim(c, key=_axis['z'], copy=True)
                self.cell_method_axis_name['z'] = c.identity()
        else:
            array = numpy_array(array, dtype=self.int_hdr_dtype)
            
            if array.min() < 0:
                return

            array = numpy_where(array==9999, 0, array)
        
            axiscode = 5
    
            if aux:
                c = AuxiliaryCoordinate()
                c = self.coord_data(c, array, units=Units('1'))
                c = self.coord_names(c, axiscode)
                self.domain.insert_aux(c, axes=[_axis['z']], copy=False)
            else:
                c = DimensionCoordinate()
                c = self.coord_data(c, array, units=Units('1'))
                c = self.coord_names(c, axiscode)
                c = self.coord_axis(c, axiscode)
                self.domain.insert_dim(c, key=_axis['z'], copy=False)
    
                self.cell_method_axis_name['z'] = c.identity()
            #--- End: if
            _cached_model_level_number_coordinate[key] = c
        #--- End: if

        return c
    #--- End: def

    def data_type_in_file(self, rec):
        '''Return the data type of the data array.

:Parameters:

    rec : umfile.Rec

:Returns:

    out : numpy.dtype

:Examples:

'''
        # Find the data type
        if rec.int_hdr.item(lbuser2,) == 3:
            # Boolean
            return numpy_dtype(bool)
        else:
            # Int or float
            return rec.get_type_and_num_words()[0]
#            rec_file = rec.file
##            data_type = rec_file.c_interface.get_type_and_length(
#            data_type = rec_file.c_interface.get_type_and_num_words(rec.int_hdr)[0]
#            if data_type == 'int':
#                # Integer
#                data_type = 'int%d' % (rec_file.word_size * 8)
#            else:
#                # Float
#                data_type = 'float%d' % (rec_file.word_size * 8)
#        #--- End: if
#
#        return numpy_dtype(data_type)
    #--- End: def

    def printfdr(self):
        '''Print out the contents of PP field headers.

This is a bit like printfdr in the UKMO IDL PP library.

:Examples:

>>> u.printfdr()

'''
        for header in self.fdr():
            print header
    #--- End: def

    def pseudolevel_coordinate(self, LBUSER5):
        '''
'''
#        print 'self.nz = ', self.nz
        if self.nz == 1:            
            array = numpy_array((LBUSER5,), dtype=self.int_hdr_dtype)
        else:
            # 'Z' aggregation has been done along the pseudolevel axis
            array = numpy_array([rec.int_hdr.item(lbuser5,)
                                 for rec in self.z_recs],
                                dtype=self.int_hdr_dtype)
            self.z_axis = 'p'
        #--- End: if
#        print 'array =', array
        axiscode = 40

        dc = DimensionCoordinate()
        dc = self.coord_data(
            dc, array,
            units=_axiscode_to_Units.setdefault(axiscode, None))
        dc.long_name = 'pseudolevel' # for PP stash_code %d' % self.stash
        dc.id = 'UM_pseudolevel'

        self.domain.insert_dim(dc, key=_axis['p'], copy=False)        

        self.cell_method_axis_name['p'] = dc.identity()

        return dc
    #--- End: def

    def radiation_wavelength_coordinate(self, rwl, rwl_units):
        '''
'''
        array  = numpy_array((rwl,), dtype=float)
        bounds = numpy_array(((0.0, rwl)), dtype=float)

        units = _Units.get(rwl_units, None)
        if units is None:
            units = Units(rwl_units)
            _Units[rwl_units] = units
 
        axiscode = -20
        dc = DimensionCoordinate()
        dc = self.coord_data(dc, array, bounds, units=units)
        dc = self.coords_names(dc, axiscode)
        
        self.domain.insert_dim(dc, key=_axis['r'], copy=False)

        self.cell_method_axis_name['r'] = dc.identity()

        return dc
    #--- End: def

    def reference_time_Units(self):
        '''
        '''
        time_units = 'days since %d-1-1' % self.int_hdr[lbyr]
        calendar = self.calendar

        key = time_units+' calendar='+calendar
        units = _Units.get(key, None)
        if units is None:
            units = Units(time_units, calendar)
            _Units[key] = units
        #--- End: if

        self.refUnits = units
        self.refunits = time_units

        return units
    #--- End: def
    
    def size_1_height_coordinate(self, axiscode, height, units):
        # Create the height coordinate from the information given in the
        # STASH to standard_name conversion table

        key = (axiscode, height, units)
        dc = _cached_size_1_height_coordinate.get(key, None)

        zdim = _axis['z']

        if dc is not None:            
            copy = True
        else:
            height_units = _Units.get(units, None)
            if height_units is None:
                height_units = Units(units)
                _Units[units] = height_units
    
            array = numpy_array((height,), dtype=float)

            dc = DimensionCoordinate()
            dc = self.coord_data(dc, array, units=height_units)
            dc = self.coord_positive(dc, axiscode, zdim)
            dc = self.coord_axis(dc, axiscode)
            dc = self.coord_names(dc, axiscode)

            _cached_size_1_height_coordinate[key] = dc            
            copy = False
        #--- End: def 

        self.domain.insert_dim(dc, key=zdim, copy=copy)

        self.cell_method_axis_name['z'] = dc.identity()

        return dc
    #--- End: def
        
    def test_um_condition(self, um_condition, LBCODE, BPLAT, BPLON):
        '''Return True if a field satisfies the condition specified for a
STASH code to standard name conversion.
    
:Parameters:
    
    um_condition : str

    LBCODE : int        

    BPLAT : float

    BPLON : float

:Returns:
    
    out : bool
        True if a field satisfies the condition specified, False
        otherwise.
   
:Examples:
    
>>> ok = u.test_um_condition('true_latitude_longitude', ...)

        '''
        if um_condition == 'true_latitude_longitude':
            if LBCODE in _true_latitude_longitude_lbcodes:
                return True
    
            # Check pole location in case of incorrect LBCODE
            atol = self.atol
            if (abs(BPLAT-90.0) <= atol + RTOL()*90.0 and 
                abs(BPLON) <= atol):
                return True
    
        elif um_condition == 'rotated_latitude_longitude':
            if LBCODE in _rotated_latitude_longitude_lbcodes:
                return True
    
            # Check pole location in case of incorrect LBCODE
            atol = self.atol
            if not (abs(BPLAT-90.0) <= atol + RTOL()*90.0 and 
                    abs(BPLON) <= atol):
                return True
            
        else:
            raise ValueError(
                "Unknown UM condition in STASH code conversion table: '%s'" %
                um_condition)
    
        # Still here? Then the condition has not been satisfied.
        return
    #--- End: def

    def test_um_version(self, valid_from, valid_to, um_version):
        '''Return True if the UM version applicable to tghis field is
        within the given range.
    
If possible, the UM version is derived from the PP header and stored
in the metadata object. Otherwise it is taken from the *um_version*
parameter.
    
:Parameters:

    valid_from : int, float or None

    valid_to : int, float or None

    um_version : int or float

:Returns:

    out : bool
        True if the UM version applicable to this field is within the
        range, False otherwise.

:Examples:

>>> ok = u.test_um_version(401, 505, 1001)
>>> ok = u.test_um_version(401, None, 606.3)
>>> ok = u.test_um_version(None, 405, 401)

''' 
        if valid_to is None:
            if valid_from <= um_version:
                return True 
        elif valid_from is None:
            if um_version <= valid_to:
                return True 
        elif valid_from <= um_version <= valid_to:
            return True 

        return False    

#        if valid_from is '':
#        valid_from = None
#    
#        if valid_to is '':
#            if valid_from <= um_version:
#                return True 
#        elif valid_from <= um_version <= valid_to:
#            return True 
#    
#        return False
    #--- End: def

    def time_coordinate(self, axiscode):
        '''

Return the T dimension coordinate

'''

        recs = self.t_recs
        vtimes = numpy_array([self.vtime(rec) for rec in recs], dtype=float)
        dtimes = numpy_array([self.dtime(rec) for rec in recs], dtype=float)
        
        IB = self.lbtim_ib

        if IB <= 1 or vtimes.item(0,) >= dtimes.item(0,): 
            array  = vtimes
            bounds = None
            climatology = False                
        elif IB == 3:
            # The field is a time mean from T1 to T2 for each year
            # from LBYR to LBYRD
            ctimes = numpy_array([self.ctime(rec) for rec in recs])
            array  = 0.5*(vtimes + ctimes)
            bounds = numpy_column_stack((vtimes, dtimes))
            climatology = True                    
        else:
            array  = 0.5*(vtimes + dtimes)
            bounds = numpy_column_stack((vtimes, dtimes))
            climatology = False                
        #--- End: if            

        dc = DimensionCoordinate()
        dc = self.coord_data(dc, array, bounds,
                             units=self.refUnits,
                             climatology=climatology)
        dc = self.coord_axis(dc, axiscode)
        dc = self.coord_names(dc, axiscode)

        self.domain.insert_dim(dc, key=_axis['t'], copy=False)

        self.cell_method_axis_name['t'] = dc.identity()

        return dc
    #--- End: def

    def time_coordinate_from_extra_data(self, axiscode, axis):
        '''
'''     
        extra = self.extra
        array = extra[axis]
        bounds = extra.get(axis+'_bounds', None)

        calendar = self.calendar
        if calendar == '360_day':
            units = _Units['360_day 0-1-1']
        elif calendar == 'gregorian':
            units = _Units['gregorian 1752-9-13']
        elif calendar == '365_day':
            units = _Units['365_day 1752-9-13']
        else:
            units = None
                
        dc = DimensionCoordinate()
        dc = self.coord_data(dc, array, bounds, units=units)
        dc = self.coord_axis(dc, axiscode)
        dc = self.coord_names(dc, axiscode)

        self.domain.insert_dim(dc, key=_axis[axis], copy=False)

        self.cell_method_axis_name[axis] = dc.identity()
        self.cell_method_axis_name['t'] = self.cell_method_axis_name[axis]

        return dc
    #--- End: def        

    def time_coordinate_from_um_timeseries(self, axiscode, axis):
        # This PP/FF field is a timeseries. The validity time is
        # taken to be the time for the first sample, the data time
        # for the last sample, with the others evenly between.
        rec = self.recs[0]
        vtime = self.vtime(rec)
        dtime = self.dtime(rec)
        
        size  = self.lbuser3 - 1.0
        delta = (dtime - vtime)/size
        
        array = numpy_arange(vtime, vtime+delta*size, size, dtype=float)
                
        dc = DimensionCoordinate()
        dc = self.coord_data(dc, array, units=units)
        dc = self.coord_axis(dc, axiscode)
        dc = self.coord_names(dc, axiscode)

        self.domain.insert_dim(dc, key=_axis[axis], copy=False)

        self.cell_method_axis_name['t'] = dc.identity()

        return dc
    #--- End: def        

    def vtime(self, rec):
        '''
        '''
        reftime  = self.refUnits
        units    = self.refunits
        calendar = self.calendar

#        LBVTIME = tuple(rec.int_hdr[lbyr: lbmin+1])
        LBVTIME = tuple(self.header_vtime(rec))

        key = (LBVTIME, units, calendar)
        time = _cached_date2num.get(key, None)
        if time is None:
            # It is important to use the same time_units as dtime
            if self.calendar == 'gregorian':
                time = netCDF4_date2num(
                    datetime(*LBVTIME), units, calendar)
            else:                
                time = netCDF4_date2num(
                    netCDF4_netcdftime_datetime(*LBVTIME), units, calendar)
            _cached_date2num[key] = time
        #--- End: if

        return time
    #--- End: def

    def dddd(self):
        for axis_code, extra_type in zip((11 , 10 ),
                                         ('x', 'y')):
            coord_type = extra_type + '_domain_bounds'
            
            if coord_type in p.extra:
                p.extra[coord_type]
                # Create, from extra data, an auxiliary coordinate should   
                # with 1) data and bounds, if the upper and lower  be       
                # bounds have no missing values; or 2) data but no the      
                # bounds, if the upper bound has missing values  axis     
                # but the lower bound does not.                  # which    
                file_position = ppfile.tell()                                             # has      
                bounds = p.extra[coord_type][...]                                         # axis_code
                # Reset the file pointer after reading the extra                          # 13       
                # data into a numpy array
                ppfile.seek(file_position, os.SEEK_SET)
                data = None
                if numpy_any(bounds[..., 1] == _pp_rmdi): # dch also test in bmdi?
                    if not numpy_any(bounds[...,0] == _pp_rmdi): # dch also test in bmdi?
                        data = bounds[...,0]
                    bounds = None
                else:
                    data = numpy_mean(bounds, axis=1)

                if (data, bounds) != (None, None):
                    aux   = 'aux%(auxN)d' % locals()           
                    auxN += 1                        # Increment auxiliary number
                    
                    coord = _create_Coordinate(domain, aux, axis_code, p=p,
                                               array        = data,
                                               aux=True,
                                               bounds_array = bounds, 
                                               pubattr      = {'axis': None},
                                               dimensions   = [xdim]) # DCH      
                                                                    # xdim?    
                                                                    # should   
                                                                    # be       
                                                                    # the      
                                                                    # axis     
                                                                    # which    
                                                                    # has      
                                                                    # axis_code
                                                                    # 13       
                #--- End: if
            else:
                coord_type = '%s_domain_lower_bound' % extra_type
                if coord_type in p.extra:
                    # Create, from extra data, an auxiliary
                    # coordinate with data but no bounds, if the
                    # data noes not contain any missing values
                    file_position = ppfile.tell()
                    data = p.extra[coord_type][...]
                    # Reset the file pointer after reading the
                    # extra data into a numpy array
                    ppfile.seek(file_position, os.SEEK_SET)
                    if not numpy_any(data == _pp_rmdi): # dch also test in bmdi?   
                        aux   = 'aux%(auxN)d' % locals()           
                        auxN += 1                        # Increment auxiliary number
                        coord = _create_Coordinate(domain, aux, axis_code, p=p,
                                                   aux=True,
                                                   array=numpy_array(data),
                                                   pubattr={'axis': None}, 
                                                   dimensions=[xdim])# DCH xdim?    
           #--- End: if
       #--- End: for
    #--- End: if
        
        # --------------------

    def unrotated_latlon(self, rotated_lat, rotated_lon, pole_lat, pole_lon):
        '''
    
    Create 2-d arrays of unrotated latitudes and longitudes.
        
:Parameters:

rotated_lat, rotated_lon, pole_lat, pole_lon

    '''
        # Make sure rotated_lon and pole_lon is in [0, 360)
        pole_lon = pole_lon % 360.0
    
        # Convert everything to radians
        pole_lon *= _pi_over_180
        pole_lat *= _pi_over_180
    
        cos_pole_lat = numpy_cos(pole_lat)
        sin_pole_lat = numpy_sin(pole_lat)
    
        # Create appropriate copies of the input rotated arrays
        rot_lon = rotated_lon.copy()
        rot_lat = rotated_lat.view()
    
        # Make sure rotated longitudes are between -180 and 180
        rot_lon %= 360.0
        rot_lon = numpy_where(rot_lon < 180.0, rot_lon, rot_lon-360)
    
        # Create 2-d arrays of rotated latitudes and longitudes in radians
        nlat = rot_lat.size
        nlon = rot_lon.size
        rot_lon = numpy_resize(numpy_deg2rad(rot_lon), (nlat, nlon))    
        rot_lat = numpy_resize(numpy_deg2rad(rot_lat), (nlon, nlat))
        rot_lat = numpy_transpose(rot_lat, axes=(1,0))
    
        # Find unrotated latitudes
        CPART = numpy_cos(rot_lon) * numpy_cos(rot_lat)
        sin_rot_lat = numpy_sin(rot_lat)
        x = cos_pole_lat * CPART + sin_pole_lat * sin_rot_lat
        x = numpy_clip(x, -1.0, 1.0)
        unrotated_lat = numpy_arcsin(x)
        
        # Find unrotated longitudes
        x = -cos_pole_lat*sin_rot_lat + sin_pole_lat*CPART
        x /= numpy_cos(unrotated_lat)   # dch /0 or overflow here? surely
                                        # lat could be ~+-pi/2? if so,
                                        # does x ~ cos(lat)?
        x = numpy_clip(x, -1.0, 1.0)
        unrotated_lon = -numpy_arccos(x)
        
        unrotated_lon = numpy_where(rot_lon > 0.0, 
                                    -unrotated_lon, unrotated_lon)
        if pole_lon >= self.atol:
            SOCK = pole_lon - numpy_pi
        else:
            SOCK = 0
        unrotated_lon += SOCK
    
        # Convert unrotated latitudes and longitudes to degrees
        unrotated_lat = numpy_rad2deg(unrotated_lat)
        unrotated_lon = numpy_rad2deg(unrotated_lon)
    
        # Return unrotated latitudes and longitudes
        return unrotated_lat, unrotated_lon
    #--- End: def

    def xy_coordinate(self, axiscode, axis):
        '''

Create an X or Y dimension coordinate from header entries or extra
data.

:Parameters:

    axiscode : int

    axis : str
        'x' or 'y'

:Returns:

    out : cf.DimensionCoordinate

        '''
        if axis == 'y':
            delta  = self.bdy
            origin = self.real_hdr[bzy]
            size   = self.lbrow    
        else:
            delta  = self.bdx
            origin = self.real_hdr[bzx]
            size   = self.lbnpt

        if abs(delta) > self.atol:
            # Create regular coordinates from header items
            if axiscode == 11 or axiscode == -11:
                origin -= divmod(origin + delta*size, 360.0)[0] * 360
                while origin + delta*size > 360.0:
                    origin -= 360.0
                while origin + delta*size < -360.0:
                    origin += 360.0
            #--- End: if

            array = numpy_arange(origin+delta, origin+delta*(size+0.5), delta,
                                 dtype=float)

            # Create the coordinate bounds
            if axiscode in (13, 31, 40, 99):
                # The following axiscodes do not have bounds:
                # 13 = Site number (set of parallel rows or columns
                #      e.g.Time series)
                # 31 = Logarithm to base 10 of pressure in mb
                # 40 = Pseudolevel
                # 99 = Other
                bounds = None
            else:
                delta_by_2 = 0.5 * delta
                bounds = numpy_empty((size, 2), dtype=float)
                bounds[:, 0] = array - delta_by_2
                bounds[:, 1] = array + delta_by_2                
        else:
            # Create coordinate from extra data
            array  = self.extra.get(axis, None)
            bounds = self.extra.get(axis+'_bounds', None)
        #--- End: if

        dc = DimensionCoordinate()
        dc = self.coord_data(
            dc, array, bounds,
            units=_axiscode_to_Units.setdefault(axiscode, None))
        dc = self.coord_positive(dc, axiscode, _axis[axis])
        dc = self.coord_axis(dc, axiscode)
        dc = self.coord_names(dc, axiscode)

        self.domain.insert_dim(dc, key=_axis[axis], copy=False)       

        self.cell_method_axis_name[axis] = dc.identity()

        return dc
    #--- End: def

    def z_coordinate(self, axiscode):
        '''Create a Z dimension coordinate from BLEV

:Parameters:

    axiscode : int

:Returns:

    out : cf.DimensionCoordinate

        '''
        z_recs = self.z_recs
        array   = tuple([rec.real_hdr.item(blev,) for rec in z_recs])        
        bounds0 = tuple([rec.real_hdr[brlev]      for rec in z_recs]) # lower level boundary
        bounds1 = tuple([rec.real_hdr[brsvd1]     for rec in z_recs]) # bulev
#        if len(array) == 15:
#            print 'z_coordinate axiscode=', axiscode
#            print 'array =', array
#            print rec.real_hdr
        if _coord_positive.get(axiscode, None) == 'down':
            bounds0, bounds1 = bounds1, bounds0        

#        key = (axiscode, array, bounds0, bounds1)
#        dc = _cached_z_coordinate.get(key, None)

#        if dc is not None:
#            copy = True
#        else:
        copy = False
        array   = numpy_array(array, dtype=float)
        bounds0 = numpy_array(bounds0, dtype=float)
        bounds1 = numpy_array(bounds1, dtype=float)
        bounds  = numpy_column_stack((bounds0, bounds1))

        if (bounds0 == bounds1).all():
            bounds = None
        else:
            bounds = numpy_column_stack((bounds0, bounds1))
#        print '        array=', array
        dc = DimensionCoordinate()
        dc = self.coord_data(
            dc, array, 
            bounds=bounds,
            units=_axiscode_to_Units.setdefault(axiscode, None))
        dc = self.coord_positive(dc, axiscode, _axis['z'])
        dc = self.coord_axis(dc, axiscode)
        dc = self.coord_names(dc, axiscode)
        
#        _cached_z_coordinate[key] = dc
#        #--- End: if

        self.domain.insert_dim(dc, key=_axis['z'], copy=copy)

        self.cell_method_axis_name['z'] = dc.identity()
        
        return dc
    #--- End: def
    
    def z_reference_coordinate(self, axiscode):        
        '''
'''
        array = numpy_array([rec.real_hdr.item(brlev,) for rec in self.z_recs],
                            dtype=float)

        LBVC = self.lbvc

        key = (axiscode, LBVC, array)
        dc = _cached_z_reference_coordinate.get(key, None)

        if dc is not None:
            copy = True
        else:
            if not 128 <= LBVC <= 139:
                bounds = []
                for rec in self.z_recs: 
                    BRLEV  = rec.real_hdr.item(brlev,)
                    BRSVD1 = rec.real_hdr.item(brsvd1,)
                    
                    if abs(BRSVD1-BRLEV) >= ATOL:
                        bounds = None
                        break
                        
                    bounds.append((BRLEV, BRSVD1))
                #--- End: for    
            else:
                bounds = None
    
            if bounds:
                bounds = numpy_array((bounds,), dtype=float)                
    
            dc = DimensionCoordinate()
            dc = self.coord_data(
                dc, array, bounds,
                units=_axiscode_to_Units.setdefault(axiscode, None))
            dc = self.coord_axis(dc, axiscode)
            dc = self.coord_names(dc, axiscode)

            if not dc.get('positive', True): # ppp
                dc.flip(i=True)

            _cached_z_reference_coordinate[key] = dc
            copy = False
        #--- End: def

        self.domain.insert_dim(dc, key=_axis['z'], copy=copy)

        return dc
    #--- End: def

#--- End: class

_stash2standard_name = {}

def load_stash2standard_name(table=None, delimiter='!'):
    '''Load a STASH to standard name conversion table.

:Parameters:

    table : str, optional
        Use the conversion table at this file location. By default the
        table will be looked for at
        ``os.path.join(os.path.dirname(cf.__file__),'etc/STASH_to_CF.txt')``

    delimiter : str, optional
        The delimiter of the table columns. By default, ``!`` is taken
        as the delimiter.

:Returns:

    None

*Examples:*

>>> load_stash2standard_name()
>>> load_stash2standard_name('my_table.txt')
>>> load_stash2standard_name('my_table2.txt', ',')

    '''
    # 0  Model           
    # 1  STASH code      
    # 2  STASH name      
    # 3  units           
    # 4  valid from UM vn
    # 5  valid to   UM vn
    # 6  standard_name   
    # 7  CF extra info   
    # 8  PP extra info

    if table is None:
        # Use default conversion table
        package_path = os.path.dirname(__file__)
        table = os.path.join(package_path, 'etc/STASH_to_CF.txt')
    #--- End: if

    lines = csv.reader(open(table, 'r'), 
                       delimiter=delimiter, skipinitialspace=True)

    raw_list = []
    [raw_list.append(line) for line in lines]

    # Get rid of comments
    for line in raw_list[:]:
        if line[0].startswith('#'):
            raw_list.pop(0)
            continue
        break
    #--- End: for

    # Convert to a dictionary which is keyed by (submodel, STASHcode)
    # tuples

    (model, stash, name,
     units, 
     valid_from, valid_to,
     standard_name, cf, pp) = range(9)
        
    stash2sn = {}
    for x in raw_list:
        key = (int(x[model]), int(x[stash]))

        if not x[units]:
            x[units] = None

        try:            
            cf_info = {}
            if x[cf]:
                for d in x[7].split():
                    if d.startswith('height='): 
                        cf_info['height'] = re.split(_number_regex, d,
                                                     re.IGNORECASE)[1:4:2]
                        if cf_info['height'] == '':
                            cf_info['height'][1] = '1'

                    if d.startswith('below_'):
                        cf_info['below'] = re.split(_number_regex, d,
                                                     re.IGNORECASE)[1:4:2]
                        if cf_info['below'] == '':
                            cf_info['below'][1] = '1'

                    if d.startswith('where_'):         
                        cf_info['where'] = d.replace('where_', 'where ', 1)
                    if d.startswith('over_'):         
                        cf_info['over'] = d.replace('over_', 'over ', 1)

            x[cf] = cf_info                    
        except IndexError:
            pass

        try:
            x[valid_from] = float(x[valid_from])
        except ValueError:
            x[valid_from] = None

        try:
            x[valid_to] = float(x[valid_to])
        except ValueError:
            x[valid_to] = None

        x[pp] = x[pp].rstrip()

        line = (x[name:],)

        if key in stash2sn:
            stash2sn[key] += line
        else:
            stash2sn[key] = line

    #--- End: for

    _stash2standard_name.clear()
    _stash2standard_name.update(stash2sn)

#    return stash2sn
#--- End: def

# ---------------------------------------------------------------------
# Create the STASH code to standard_name conversion dictionary
# ---------------------------------------------------------------------
#_stash2standard_name = load_stash2standard_name()
load_stash2standard_name()

def read(filename, um_version=405, verbose=False, aggregate=True,
         endian=None, word_size=None, set_standard_name=True,
         height_at_top_of_model=None, fmt=None):
    '''Read fields from a PP file or UM fields file.

The file may be big or little endian, 32 or 64 bit

:Parameters:

    filename : file or str
        A string giving the file name, or an open file object, from
        which to read fields.

    um_version : number, optional
        The Unified Model (UM) version to be used when decoding the PP
        header. Valid versions are, for example, ``402`` (v4.2),
        ``606.3`` (v6.6.3) and ``1001`` (v10.1). The default version
        is ``405`` (v4.5). The version is ignored if it can be
        inferred from the PP headers, which will generally be the case
        for files created at versions 5.3 and later. Note that the PP
        header can not encode tertiary version elements (such as the
        ``3`` in ``606.3``), so it may be necessary to provide a UM
        version in such cases.
    
    verbose : bool, optional

    set_standard_name : bool, optional

:Returns:

    out : FieldList
        The fields in the file.

:Examples:

>>> f = read('file.pp')
>>> f = read('*/file[0-9].pp', um_version=708)

    '''    
    history = 'Converted from UM by cf-python v%s' % __version__

    if endian:
        byte_ordering = endian+'_endian'
    else:        
        byte_ordering = None

    f = _open_um_file(filename,
                      byte_ordering=byte_ordering,
                      word_size=word_size,
                      fmt=fmt)

    um = [UMField(var, f.format, f.byte_ordering, f.word_size,
                  um_version, set_standard_name, history=history,
                  height_at_top_of_model=height_at_top_of_model)                  
          for var in f.vars]

#    # Clear the cache of unrotated latitude and longitude arrays
#    _cache_latlon.clear()

    return FieldList([field
                      for x in um
                      for field in x.fields
                      if field])
#--- End: def

def _atmosphere_hybrid_sigma_pressure_coordinate(f):
    # atmosphere_hybrid_sigma_pressure_coordinate
    real_hdr = f.real_hdr
    
    BLEV, BRLEV, BHLEV, BHRLEV = real_hdr[blev:bhrlev+1]
    BRSVD1, BRSVD2             = real_hdr[brsvd1:brsvd2+1]
    
    if 'z' not in pmaxes:
        indices = [0] * pmndim
        indices[pmaxes.index('z')] = slice(1, None, None)
        
        for rec in var.recs[tuple(indices)]:
            BLEV, BRLEV, BHLEV, BHRLEV = rec.real_hdr[blev:bhrlev+1]
            BRSVD1, BRSVD2             = rec.real_hdr[brsvd1:brsvd2+1]
            
            array.append(BLEV + BHLEV/_pstar)
            bounds.append([BRLEV + BHRLEV/_pstar, BRSVD1 + BRSVD2/_pstar])
            
            ak_array.append(BHLEV)
            ak_bounds.append([BHRLEV, BRSVD2])
            
            bk_array.append(BLEV)
            bk_bounds.append([BRLEV , BRSVD1])

            array     = numpy_array(array    , dtype=float)
            bounds    = numpy_array(bounds   , dtype=float)
            ak_array  = numpy_array(ak_array , dtype=float)
            ak_bounds = numpy_array(ak_bounds, dtype=float)
            bk_array  = numpy_array(bk_array , dtype=float)
            bk_bounds = numpy_array(bk_bounds, dtype=float)
            
            domain = f.field.domain
            
            coord = _create_Coordinate(domain, vdim, axis_code=axis_code,
                                       p=p,
                                       array=array,
                                       bounds_array=bounds,
                                       dimensions=[vdim])
            
            coord = _create_Coordinate(
                domain, aux, axis_code=None,
                p=p,
                pubattr={'standard_name':
                         'atmosphere_hybrid_sigma_pressure_coordinate_ak'},
                units=_units['Pa'],
                array=ak_array,
                bounds_array=ak_array,
                dimensions=[vdim],
                aux=True)
            
            coord = _create_Coordinate(
                domain, aux, axis_code=None,
                p=p,
                pubattr={'standard_name':
                         'atmosphere_hybrid_sigma_pressure_coordinate_bk'},
                units=_units['1'],
                array=bk_array,
                bounds_array=bk_array,
                dimensions=[vdim],
                aux=True)
            
        else:
            cache_key = ('atmosphere_hybrid_sigma_pressure_coordinate',
                         BLEV, BHLEV, BRLEV, BHRLEV, BRSVD1, BRSVD2)
            cache_key_ak = ('atmosphere_hybrid_sigma_pressure_coordinate_ak',
                            BLEV, BHLEV, BRLEV, BHRLEV, BRSVD1, BRSVD2)
            cache_key_bk = ('atmosphere_hybrid_sigma_pressure_coordinate_bk',
                            BLEV, BHLEV, BRLEV, BHRLEV, BRSVD1, BRSVD2)
            if cache_key in _cached_coordinate:
                c = _cached_coordinate[cache_key]
                domain.insert_dim(c, key=vdim, copy=True)
                c = _cached_coordinate[cache_key_ak]
                domain.insert_aux(c, axes=[vdim], copy=True)
                c = _cached_coordinate[cache_key_bk]
                domain.insert_aux(c, axes=[vdim], copy=True)
            else:                                                        
                array  = numpy_array((BLEV + BHLEV/_pstar,), dtype=float)
                bounds = numpy_array(((BRLEV  + BHRLEV/_pstar,
                                       BRSVD1 + BRSVD2/_pstar)), dtype=float)
                
                ak_array  = numpy_array((BHLEV,)          , dtype=float)
                ak_bounds = numpy_array(((BHRLEV, BRSVD2)), dtype=float)
                
                bk_array  = numpy_array((BLEV,)          , dtype=float)
                bk_bounds = numpy_array(((BRLEV, BRSVD1)), dtype=float)
                
                coord = _create_Coordinate(domain, vdim, axis_code=axis_code,
                                           p=p,
                                           array=array,
                                           bounds_array=bounds,
                                           dimensions=[vdim],
                                           cache_key=cache_key)
                
                coord = _create_Coordinate(
                    domain, aux, axis_code=None,
                    p=p,
                    pubattr={'standard_name':
                             'atmosphere_hybrid_sigma_pressure_coordinate_ak'},
                    units=_units['Pa'],
                    array=ak_array,
                    bounds_array=ak_array,
                    dimensions=[vdim],
                    aux=True,
                    cache_key=cache_key_ak)
                
                coord = _create_Coordinate(
                    domain, aux, axis_code=None,
                    p=p,
                    pubattr={'standard_name':
                             'atmosphere_hybrid_sigma_pressure_coordinate_bk'},
                    units=_units['1'],
                    array=bk_array,
                    bounds_array=bk_array,
                    dimensions=[vdim],
                    aux=True,
                    cache_key=cache_key_bk)
#--- End: def
          
def is_um_file(filename):
    '''Return True if a file is a PP file or UM fields file.

Note that the file type is determined by inspecting the file's
contents and any file suffix is not not considered.

:Parameters:

    filename : str

:Returns:

    out : bool

:Examples:

>>> is_um_file('myfile.pp')
True
>>> is_um_file('myfile.nc')
False
>>> is_um_file('myfile.pdf')
False
>>> is_um_file('myfile.txt')
False

    ''' 
    try:
        f = _open_um_file(filename)
    except:
        return False

    try:
        f.close_fd()
    except:
        pass

    return True
#--- End: def
      
'''
Problems:

Z and P coordinates
/home/david/data/pp/aaaao/aaaaoa.pmh8dec.03328.pp

/net/jasmin/chestnut/data-24/david/testpp/026000000000c.fc0607.000128.0000.00.04.0260.0020.1491.12.01.00.00.pp
skipping variable stash code=0, 0, 0 because: grid code not supported
umfile: error condition detected in routine list_copy_to_ptr_array
umfile: error condition detected in routine process_vars
umfile: error condition detected in routine file_parse
OK 2015-04-01

/net/jasmin/chestnut/data-24/david/testpp/026000000000c.fc0619.000128.0000.00.04.0260.0020.1491.12.01.00.00.pp
skipping variable stash code=0, 0, 0 because: grid code not supported
umfile: error condition detected in routine list_copy_to_ptr_array
umfile: error condition detected in routine process_vars
umfile: error condition detected in routine file_parse
OK 2015-04-01

/net/jasmin/chestnut/data-24/david/testpp/lbcode_10423.pp
skipping variable stash code=0, 0, 0 because: grid code not supported
umfile: error condition detected in routine list_copy_to_ptr_array
umfile: error condition detected in routine process_vars
umfile: error condition detected in routine file_parse
OK 2015-04-01

/net/jasmin/chestnut/data-24/david/testpp/lbcode_11323.pp
skipping variable stash code=0, 0, 0 because: grid code not supported
umfile: error condition detected in routine list_copy_to_ptr_array
umfile: error condition detected in routine process_vars
umfile: error condition detected in routine file_parse
OK 2015-04-01

EXTRA_DATA:
/net/jasmin/chestnut/data-24/david/testpp/ajnjgo.pmm1feb.pp

SLOW: (Not any more! 2015-04-01)
/net/jasmin/chestnut/data-24/david/testpp/xgdria.pdk949a.pp
/net/jasmin/chestnut/data-24/david/testpp/xhbmaa.pm27sep.pp

RUN LENGTH ENCODED dump (not fields file)
/home/david/data/um/xhlska.dak69h0
Field 115 (stash code 9)

dch@eslogin008:/nerc/n02/n02/dch> ff2pp xgvwko.piw96b0 xgvwko.piw96b0.pp

file xgvwko.piw96b0 is a byte swapped 64 bit ieee um file 

'''
