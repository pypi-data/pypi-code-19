import os
import sys
import shutil
import StringIO
import csv

import numpy as np

def _mygenfromtxt(f):
    # twice as fast as np.genfromtxt(..., names=True)
    spamreader = csv.reader(f, skipinitialspace = True, delimiter=" ")
    hdr = spamreader.next()
    dat = []
    for row in spamreader:
        dat.append( tuple(map(float, row)) )
    return np.array(dat, dtype=[(_, float) for _ in hdr])

class InputFile:
    '''
    A generic BOXMOX input file. Getting and setting of values
    works like a dictionary::

       print(inp['O3'])
       inp['O3'] = 0.040

    '''
    @property
    def nvar(self):
        '''
        Number of variables.
        '''
        return len( [ x for x in self.keys() if not x is self.__timeVar ] )
    def __getitem__(self, item):
        return [ self.__data[i] for i in item ] if isinstance(item, list) else self.__data[item]
    def __setitem__(self, item, values):
        try:
            for i, v in zip(item, values):
                self.__data[i] = v
        except:
            self.__data[item] = values
    def keys(self):
        return self.__data.keys()
    def read(self, fpath):
        '''
        Read input file from path.
        '''
        with open(fpath, 'rb') as f:
            self.nvar         = int(f.readline())
            self.timeFormat   = int(f.readline())
            dmp               = _mygenfromtxt(f)

        if not self.timeFormat == 0:
            self.__timeVar  = dmp.dtype.names[0]
        self.__data     = { x: dmp[x] for x in dmp.dtype.names }

    def __str__(self):
        f = StringIO.StringIO()
        self.write(f)
        return(f.getvalue())

    def write(self, f=sys.stdout):
        '''
        Write to <f>. <f> can be file handle or other connection. Defaults to sys.stdout.
        '''
        f.write('{0:1d}'.format(self.nvar)                  +'\n')
        f.write('{0:1d}'.format(self.timeFormat)            +'\n')

        column_names = [ key for key in self.keys() if key != self.__timeVar ]
        if self.__timeVar in self.keys() and str(self.timeFormat) != "0" :
            f.write('{0:s}' .format(' '.join([self.__timeVar] + column_names)) + '\n')

            for itime, xtime in enumerate(self.__data[self.__timeVar]):
                line = [ xtime ] + [ self.__data[key][itime] for key in column_names ]
                f.write(' '.join('{0:e}'.format(x) for x in line) + '\n')
        else:
            f.write('{0:s}' .format(' '.join( column_names)) +'\n')
            f.write(' '.join( '{0:e}'.format(float(self.__data[x])) for x in self.keys() ) + '\n')

    def __init__(self, fpath=None):
        #: Time format (0: constant, 1: seconds since start, 2: hour of diurnal cycle)
        self.timeFormat  = 0
        self.__timeVar   = 'time'
        self.__data      = {}

        #: File path of the underlying file (if it exists (yet))
        self.fpath       = fpath
        if not self.fpath is None:
            self.read(self.fpath)

class Output(object):
    '''
    Base output class. Simply an object that knows the output file name,
    can copy and remove it.
    '''
    def rm(self):
        '''
        Remove output file
        '''
        try:
            os.remove(self.fpath)
        except Exception:
            raise("Removing output file did not work: {:s}".format(str(e)))
    def copy(self, target_path):
        '''
        Copy output file to target_path

        :param str target_path: location where to copy the output file to.
        '''
        #TODO don't depend on the input file...
        shutil.copy(self.fpath, target_path)
    def __init__(self, fpath):
        '''
        :param str fpath: Output file path
        '''
        self.fpath = fpath

class ConcentrationOutput(Output):
    '''
    Concentration time series
    '''
    def __getitem__(self, items=None):
        if items is None:
            items = self.vars
        return self.data[items]
    def simplified(self, items=None):
        '''
        Get simple 2D NumPy array of concentration vs. time for <items>
        '''
        if items is None:
            items = self.vars
        if isinstance(self.vars, list):
            out = np.zeros( ( len(self.times), len(items) ) )
            for i in range(len(items)):
                out[:,i] = self.data[items[i]]
# old code - raises warning that it will break in the future (of numpy)
#            out = self.data[items].view(dtype=np.float, type=np.ndarray).reshape((len(self.times), len(items)))
        else:
            out = self.data
        return out
    def __str__(self):
        fout = StringIO.StringIO()
        with open(self.fpath, 'rb') as f:
            fout.write(f.read())
        return fout.getvalue()

    def __init__(self, fpath, vars=None):
        self.fpath = fpath
        with open(fpath, 'rb') as f:
            self.data = _mygenfromtxt(f)
        self.times = self.data['time']
        if not vars is None:
            self.data = self.data[vars]
            self.vars = vars
        else:
            self.vars = list(self.data.dtype.names)

class RatesOutput(Output):
    '''
    Reaction rate time series
    '''
    def __init__(self, fpath):
        self.fpath = fpath
        with open(self.fpath, 'r') as f:
            # First line contains the number of reactions:
            num_of_reacs = int( f.readline() )

            # Skip reaction lines:
            reacStr = []
            for ireac in range( num_of_reacs ):
                reacStr.append( f.readline().strip() )

            # Load rate constants ------------------------------------------------------
            # Every 10000 columns a line break is made ...
            # e.g. column names lines with 30000 reactions (data structure is the same):
            #              line 1 ->   time     1     2     3  ...  10000
            #              line 2 ->  10001 10002 10003 10004  ...  20000
            #              line 3 ->  20001 20002 20003 20004  ...  30000
            #              and so on ...
            rateFormat = num_of_reacs/10000 + 1

            for x in range( rateFormat ):
                # Column names are not needed ...
                _ = f.readline()

            # Length :: number_of_timesteps * rateFormat:
            ratesRaw = [map(float, xline.strip().split()) for xline in f.readlines()]

        # "Unfold" the raw data:
        ratesUnfold = ratesRaw[ ::rateFormat]
        for x in range( 1, rateFormat, 1 ):
            ratesHelp   = ratesRaw[x::rateFormat]
            ratesUnfold = [ratesUnfold[ir]+xr for ir,xr in enumerate(ratesHelp)]

        rates = np.array( ratesUnfold )

        # The 0'th row just contains zeros; here the rate constant of the 1'st row is
        # assumed:
        rates[0,:] = rates[1,:]

        # Extract time
        time    = rates[:,0]
        # The 0'th time step has been deleted (line with "rates[0,:] = rates[1,:]")...
        time[0] = 0.0

        # Create output dictionary:
        ratesDict = {xreac:rates[:,ireac+1] for ireac,xreac in enumerate(reacStr)}

        self.rates = ratesDict
        self.time  = time

class JacobianOutput(Output):
    '''
    Jacobian time series
    '''
    def __init__(self, fpath):
        self.fpath = fpath

class HessianOutput(Output):
    '''
    Hessian time series
    '''
    def __init__(self, fpath):
        self.fpath = fpath

class AdjointOutput(Output):
    '''
    Adjoint
    '''
    def __getitem__(self, item1, item2):
        return self.matrix[item1, item2]
    def sensitivity ( self, state, obs ):
        '''
        A BOXMOX adjoint output file is taken and the matrix of the adjoints of
        the species in the state vector is loaded (<adj_mat>: with the function
        read_adjoint).
        With <adj_mat> (= dX(t_final)/dY(t_initial)) the adjoint sensitivities
        of the species in the state vector to the observed species are
        calculated by using the chain rule.

        Calculation of adjoint sensitivities by using adjoints:

        dX(t_final)/dY(t_final) = dX(t_final)/dY(t_initial) * (dY(t_final)/dY(t_initial))^-1

        where:   X  state species
                 Y  observed species

        :param str fname: BOXMOX adjoint output file
        :param str/list state: State vector; single species or list of species which exists/exist in the BOXMOX run
        :param str/list obs: Observed species; single species or list of species which exists/exist in the BOXMOX run

        :return: adjoint sensitivity of the species in the state vector to the observed species
        :rtype: numpy.ndarray (dim_obs, dim_state)
        '''

        # If <state>/<obs> is a single species and not a list a <state>/<obs>-list will be
        # generated
        state = state if type(state)==list else [state]
        obs   = obs   if type(obs  )==list else [obs  ]

        # Get dimensions:
        dim_obs, dim_state = len(obs), len(state)

        # Calculate adjoint sensitivity ::  dX(t_final)/dY(t_final) =
        #                          = dX(t_final)/dY(t_final) * (dY(t_final)/dY(t_initial))^-1
        # shape :: (dim_obs,dim_state)
        adj_sen = np.zeros( (dim_obs,dim_state), dtype=float )
        for iobs,xobs in enumerate( obs ):
            ind_obs_state = state.index( xobs )

            for istate in range( dim_state ):
                # Prevent division by zero ...
                if self.matrix[ind_obs_state,ind_obs_state]!=0.0:
                    # dX(t_final)/dY(t_final) =
                    #            = dX(t_final)/dY(t_initial) * (dY(t_final)/dY(t_initial))^-1
                    adj_sen[iobs,istate] = self.matrix[istate       ,ind_obs_state] *     \
                                           self.matrix[ind_obs_state,ind_obs_state]**-1
                else:
                    adj_sen[iobs,istate] = 0.0

        return adj_sen

    def __init__(self, fpath, state=None):
        self.fpath = fpath
        # Read adjoint file ...
        # Shape of file:
        # Line 0: species names
        # Column 0: "d/d"
        # Column 1: species names
        # (Line :: 1-end, column :: 2-end): data
        with open(self.fpath, 'r') as f:
            # first line species names; entry 0 :: "spc" -> "[1:]"
            spec_names = f.readline ().split()[1:]
            com_data   = f.readlines()

        # Split lines:
        data = []
        for line in com_data:
            # column  0 :: "d/d"; column 1 :: species names -> "[2:]"
            data.append( line.split()[2:] )

        if state is None:
            state = spec_names
        # If <state> is a single species and not a list a <state>-list will be generated
        state = state if type(state) == list else [state]

        # Get dimension:
        dim_state = len(state)

        # Get the indices of the columns of the species in <state>
        # (These indices are equal to the indices of the lines of the species in <state>):
        state_ind = []
        for xstate in state:
            state_ind.append( spec_names.index( xstate ) )

        # Read the adjoints of the species in the state vector
        # shape :: (dim_state,dim_state)
        adj_mat = np.zeros((dim_state,dim_state), dtype=float)
        for istate_ind,xstate_ind in enumerate(state_ind):
            for jstate_ind,ystate_ind in enumerate(state_ind):
                try:
                    adj_mat[istate_ind,jstate_ind] = float( data[xstate_ind][ystate_ind] )
                except Exception as e:
                    print("Problem reading adjoint value <{:s}>: {:s}".format(data[xstate_ind][ystate_ind], str(e)))

        self.matrix = adj_mat




