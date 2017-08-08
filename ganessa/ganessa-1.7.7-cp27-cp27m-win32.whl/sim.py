# -*- coding: utf-8 -*-
#****g* ganessa.sim/About
# PURPOSE
#   The module ganessa.sim provides a Python interface to Picwin32.dll
#   and Ganessa_SIM.dll/Ganessa_TH.dll kernels. It will be extended as needed.
# INSTALLATION
#   numpy must be installed
#
#   The package expects the Picwin32.dll/Ganessa_SIM.dll to be found either in the %PATH
#   or in one of the folders "Safege/Ganessa_<lang>" or
#   "Gfi Progiciels/Piccolo6_<lang>" or "Adelior/Piccolo5_<lang>"
#   in Program Files folder (x86 under Windows 7) on drive C: or D:
# USE
#   Syntax:
#   * import ganessa.sim as gk
#   * gk.cmdfile('my file.dat')
#   Or:
#   * from ganessa.sim import *
#   * cmdfile('my file.dat')
#
#   the import will perform the following initialisation tasks:
#   * locate Ganessa_SIM.dll or Picwin32.dll kernel
#   * initialise it
#   * locate result.bin in a working subdirectory
#   * bind termination to ctrl+Z
# CONTENT
#   The package provides the following content:
#   * constants for calling API functions
#   * iterators for browsing objects and selections
#   * functions for loading .bin file
#   * functions for executing command files / command strings / running simulations
#   * functions for catching simulation errors and retrieving unstable items
#   * functions for retrieving individual objects attributes
#   * functions for retrieving table entries and object count
#   * functions for retrieving result or measurements time series
#   * functions for retrieving min / max / avg values for all objects
#
# REMARKS
#   * Most of the functions are getter. A few direct setter functions are provided
#     (setbranchattr, setdensity, defcalind, *SHL functions). The general purpose
#     addcmdw, cmd, execute and cmdfile can be used for all other settings.
#   * Any suggestion for extending / improving can be mailed to: piccolo@safege.fr
#
# HISTORY
#   The history of the packages is:
#   * 1.0.3: plotmesx png takes care of measurement type
#   * 1.0.4: added demand getter for a demand code or for all
#   * 1.0.5: added Windows 7 paths 'program files (x86)';
#            added option to get TS by measurement step 'tsvalbymts';
#            added 'refdate' : retireval of REFDATE
#   * 1.0.6: correction to the grid adjustment in plotmes (util)
#   * 1.0.7: getMinMax can be called with a selection name
#   * 1.0.8: save function
#   * 1.0.9: SimulationError exception catching + save(identical to MMI);
#            requires numpy 1.8.1
#   * 1.1.0: same as 1.0.9 but requires only numpy 1.7.1
#   * 1.1.1: minor change to codewinfile=winstr
#   * 1.1.2: added 'execute' for multiple commands as strings (\n managed as a separator)
#   * 1.1.3: (141104) disable useoffset for Y axes in 'util.plotmes'
#   * 1.1.4: (141118) handling Picwin32.dll provided by GFI after 18-11-2014 (best 03-12-2014)
#   * 1.1.5: (141205) handling ts < ms in tsvalbymts
#   * 1.1.6: (150127) nodexyz added + bugfix in attrs documentation
#   * 1.1.7: (150309) minor grammatical changes
#   * 1.2.0: (150507) change in folder search order (ws7 priority) + language - OK with Picwin32 151203
#   * 1.2.1: (150527) Picalor enabled  as ganessa.th + density and SHL management;
#            (150603) added 'meanattr';
#            (150610) added 'addSHLtype'
#   * 1.2.2: (150709) bug fix calls select* from Selected
#   * 1.2.3: (150812) bug fix: return value of browseWQ; getall
#   * 1.2.4: (150910) constants added (WQ, Inverse Pb) + demandcodes
#   * 1.2.5: (150922) utils: tuning of plotmes subtitle fontsize for large titles
#                      + constants (MOD, NOD ...) + 'areas' function
#   * 1.2.6: (151128) added tsdemand and tsdemandlen, tsdevice and tsdevicelen;
#                     added tables (material, area etc.) access;
#                     utils: added list2file
#   * 1.3.0: (151202) added support for compatibility with Picwin32 12/2014, 12/2015 and Ganessa;
#            (151206) addl constants (BRA, DYN, RSV);
#            (151218) reviewed compatibility with Picwin32 (2015+ -> Piccolo6), (2014 -> Piccolo5)
#   * 1.3.1: (160108) header, footer and suffix optional args for utils.list2file;
#            (160113) added memory allocation error exception (inverse module)
#   * 1.3.2: (160118) added retrieval of problematic devices;
#            (160126) added 'H' tank attribute in util.plotmes(x)
#   * 1.3.3: (160226) added getindex, tankattrs, linkattr and linkattrs
#   * 1.3.4: (160301) added constants for inverse pb;
#            (160309) added inverse simulation summary;
#            (160318) added added nxxxxattr and nxxxxatrs function for getting attributes by index;
#            (160325) added file quote as needed in save function;
#            (160329) corrected doc (selectlen/select);
#            (160405) corrected doc, added linkXYZV
#            (160408) utils: strloc, strf3loc
#   * 1.3.5: (160410) added init(folder)
#   * 1.3.6: (160511) added 'symmetric_node' (Ganessa_TH)
#            (160531) reviewed compatibility with dll versions since 2014.
#   * 1.3.7: (160622) added OpenFileMMI classes: SelectModel, SelectFile, ExecStatus
#            (160706) added 'dist2link'; added 'util.dist_to_poly' as pure python backup
#                     OpenFileMMI uses simulation interface from caller, or None
#                     changed all classes to new style
#                     added 'len' method to 'Selected' and 'Elements'; added 'Graph'
#   * 1.4.0: (160715) setup changed to build whl from source files
#            (160719) minor bug fix in util.plotmes - reuse same fig in non interactive mode
#   * 1.4.1: (160820) OpenFileMMI SelectFile with null extension; load error handling
#   * 1.4.2: (160830) added AUTO and QUAL storestep constants; minor fix in gencmd
#                     added include_depth optional attribute to 'linkxyzv'
#            (160915) added version_2016b in the Picwin32 lookup table
#            (160919) added SelectFolder in OpenFileMMI
#            (160922) added setlinkattr as a synonym of setbranchattr
#            (160927) intermediate API for Piccolo6 2016 B (dec-2016)
#   * 1.5.0: (161010) added 'getkeyword'
#            (161019) minor change in util.plotmes: 160719 patch reviewed for better output
#            (161124) added 'stat_quantiles', 'stat_duration', and 'Dynamic_Stats'
#   * 1.5.1  (161212) bug fix on ts* functions without result file
#                     added 'retry' optional argument to full_solveH
#   * 1.5.2  (170105) added folder= option in util.list2file
#            (170110) build with numpy 1.11.0 - compatible with
#   * 1.7.0  (170119) build with BIND(C) instead of DEC$ATTRIBUTE C, REFERENCE
#                     required with ganessa_SIM > 170117 (renamed API functions)
#            (170125) added fixed_interval to tsdevice, now return float values
#   * 1.7.1  (170221) minor changes in util.Inifile (default encoding utf-8)
#                     switch to unicode_literals in sim, util and prot
#            (170223) added compiled util.dist, util.dist_p_seg, util.dist_to_poly
#   * 1.7.2  (170228) added OpenFileMMI.setlanguage function (FR/US or UK)
#            (170304) fix getMinMax/getallminmax break in 1.7.0
#   * 1.7.3  (170313) added WQ, MOD and LNK constants; added DICT.END;
#                     added modulekeyword and attrkeyword;
#            (170331) added shearstr; match Piccolo 2017 --> NO !
#   * 1.7.4  (170407) added silent option to init
#            (170424) added default '@safege.com' domain to util.envoi_msg
#   * 1.7.5  (170426) improved util.plotmes(x) for horizon > 24h
#            (170512) added module 'multithread'
#            (170515) fix parent.inidir error in OpenFileMMI; added solveH
#   * 1.7.6  (170613) added constants (STATIC, QUA.VISUSTEP) and util.group
#                     minor bug fix in Selected, GetMinMax and Dynamic_Stats
#            (170618) added title to OpenFileMMI.SelectFile and SelectFolder
#                     added util.pageplot
#            (170620) replaced litteral symbols with attrkeyword()
#            (170627) match Piccolo 2017 (apr 2017)
#   * 1.7.7  (170705) added cwfold
#            (170707) optional arg for sim.close(arg) and prot.close(arg)
#                     added C1 in util.plotmes for chlorine plots
#****
#****g* ganessa.sim/Compatibility
# PURPOSE
#   The installation of pyganessa is compatible with several versions of Picwin32.dll
#  (regular Piccolo / Picalor). Missing functions in older versions should NOT be called.
# HISTORY
#   *  2014  -> 141203 Piccolo5 -- release 2014
#   * (2015a -> 151217 Piccolo6 & Picalor6 -- release 2015 (unstable)) - discarded
#   *  2015  -> 160121 Piccolo6 -- release 2015 sp1
#   *  2016  -> 160419 Piccolo6 & Picalor6 -- release 2016
#   *  2016a -> 160930 Piccolo6 release 2016b (incomplete; compatible with 1.4.2)
#   *  2016b -> 161216 Piccolo6 & Picalor6 -- release 2016b (1.5.0 - 1.5.2)
#   *  2017  -> 170627 Piccolo6 & Picalor6 -- release 2017  (1.7.7)
# REMARK
#   pyganessa is compatible with matching or newer versions of Ganessa_SIM/Ganessa_TH.dll only;
#   except a compatibility break on 170117.
#****
from __future__ import unicode_literals
from __future__ import print_function
import os.path
import os
import sys
import atexit
import numbers
from itertools import product, izip
from collections import Counter
from importlib import import_module
from util import winstr, _add_dir_to_path, quotefilename, hhmmss, dist_to_poly

# Version of the package
__version__ =  '1.7.7'

try:
    import numpy
except ImportError:
    print('Error importing "ganessa.sim": "numpy" is required.')
    sys.exit('Required component for ganessa.sim not found.')

# call from ganessa.th --> Picalor
_bth = __name__.endswith('th')

# public API
__all__ = ['debuglevel', 'doc', 'help',
           'LINK', 'ARC', 'BRANCH', 'NOEUD', 'NODE', 'TANK', 'RSV' 'RESERVOIR',
           'M', 'DICT',
           'Selected', 'Elements', 'Nodes', 'Branches', 'Reservoirs',
           'Demands', 'DemandCodes', 'Table', 'getMinMax', 'Unstable',
           'GanessaError', 'SimulationError',
           'init', 'setbatchmode', 'quit', 'close', 'useExceptions', 'cwfold',
           'addcmdw', 'cmd', 'cmdfile', 'execute', 'gencmdw', 'gencmd', 'commit',
           'reset', 'loadbin', 'loadres', 'getkeyword', 'modulekeyword', 'attrkeyword',
           'nbobjects', 'getselectlen', 'getselect', 'getid', 'getindex',
           'linkattr', 'nodeattr', 'tankattr', 'attr', 'branchattr', 'rsvattr', 'meanattr',
           'linkattrs', 'nodeattrs', 'tankattrs', 'branchattrs', 'attrs',
           'nlinkattr', 'nnodeattr', 'ntankattr', 'nattr', 'shearstr',
           'nlinkattrs', 'nnodeattrs', 'ntankattrs', 'nattrs',
           'setlinkattr', 'setbranchattr',
           'getdemandbycode', 'getcodedemandinit', 'nextcodedemand',
           'getcodescount', 'nextcode', 'areas', 'tablecount', 'unstablecount',
           'extrnodes', 'linkXYZV', 'nodeXYZ', 'branchXYZV', 'dist2link'
           'refdate', 'getvar', 'getunitname', 'Graph',
           'save', 'savemodel',
           'addSHLtype', 'addSHL', 'updateSHL', 'delSHL'
           ]
if _bth:
    __all__.extend(['solveTH', 'setdensity', 'symmetric_node'])
else:
    __all__.extend(['solveh', 'solveH', 'full_solveH', 'browseH', 'browseWQ',
                    'getallminmax', 'msmooth', 'inv_summary',
                    'tslen', 'tsinterv', 'mslen', 'ts', 'ms', 'tsvalbymts',
                    'tsdemandlen', 'tsdemand', 'tsdevicelen', 'tsdevice',
                    'defcalind', 'getcalind', 'Dynamic_Stats',
                    'stat_quantiles', 'stat_duration'])

# the path to Ganessa_xxx.dll must be known
debuglevel = 0
drive = ('C:', 'D:')
path = ('/program files (x86)', u'/Program Files')
editor = ('Safege', 'Gfi Progiciels', 'Adelior')
if _bth:
    sdir = ('Ganessa_', 'Picalor6_')
    dll_2 = 'Ganessa_TH.dll'
else:
    sdir = ('Ganessa_', 'Piccolo6_', 'Piccolo5_')
    dll_2 = 'Ganessa_SIM.dll'
dll_1 = 'Picwin32.dll'
lang = ('FR', 'esp', 'eng', 'UK')
_ganessa_dir = 'GANESSA_DIR'

class EnvSearchError(Exception):
    pass

def _import_ganessa(f, test= True):
    '''Search for the most recent version of compatible pyganessa dll '''
    try:
        if f == dll_1:
            if _bth:
                trials = ('_pygan_th2017', '_pygan_th2016b','_pygan_th2016', '_pygan_th2015')
            else:
                trials = ('_pygansim2017',
                          '_pygansim2016b', '_pygansim2016a', '_pygansim2016',
                          '_pygansim2015', '_pygansim2014')
            for pydll in trials:
                try:
                    _mod = import_module('ganessa.' + pydll)
                    break               # found -> stop iteration
                except ImportError:
                    if debuglevel > 2:
                        print(f, 'do not fit', pydll, '; mode=', 'test' if test else 'activation')
                    continue
            else:
                # sequence exhausted w/o finding a suitable dll
                raise ImportError
        elif f == dll_2:
            pydll = '_pygan_th' if _bth else '_pygansim'
            _mod = import_module('ganessa.' + pydll)
        if debuglevel > 0:
            print(f, 'is OK for use with', pydll, '; mode=', 'test' if test else 'activation')
        if test:
            del _mod
            return True
        else:
            print('using interface', pydll, 'for', f)
            return _mod
    except ImportError:
        if debuglevel > 0:
            print(f, 'error; mode=', 'test' if test else 'activation')
        return False

try:
    # On commence par GANESSA_DIR
    gandir = os.environ[_ganessa_dir]
    if _add_dir_to_path(gandir, dll_2):
        print(dll_2, 'found in environment variable', _ganessa_dir)
        f = dll_2
        if not _import_ganessa(f):
            raise EnvSearchError
    else:
        print(dll_2, ' ** NOT ** found in environment variable', _ganessa_dir)
        raise EnvSearchError
except (KeyError, EnvSearchError):
    # Puis par le PATH
    for gandir in os.environ['path'].split(';'):
        for f in (dll_2, dll_1):
            if os.path.exists(os.path.join(gandir, f)):
                if debuglevel > 0: print(f + ' found in Path: ' + gandir)
                if _import_ganessa(f):
                    break
                else:
                    continue
    else:
    # Puis par la liste predefinie
        for d, p, e, s, l, f in product(drive, path, editor, sdir, lang, (dll_2, dll_1)):
            if s.startswith('Gan') and f == dll_1:
                continue
            gandir = os.path.join(d, p, e, s + l)
            if debuglevel > 1: print(' ... examining ' + gandir + '/' + f)
            if _add_dir_to_path(gandir, f):
                if debuglevel > 0: print(' ... testing ' + gandir + '/' + f)
                if _import_ganessa(f):
                    if debuglevel > 0: print(f + ' responding from ' + gandir)
                    del d, p, e, s, l
                    break
                else:
                    print(f + ' found in ' + gandir + ' but *NOT* responding')
                    continue
        else:
        # On n'a pas trouve
            raise ImportError('Unable to find an adequate '+ dll_1 + ' or ' + dll_2)

# Binary result file
for subdir in ('Trabajo',  'Work', 'Travail', ''):
    _fresult = os.path.join(gandir, subdir, 'result.bin')
    if os.path.exists(_fresult):
        break
else:
    _fresult = ''

#import _pygansim as _ganessa
_ganessa = _import_ganessa(f, test= False)
if not _ganessa:
    raise ImportError('DLL ' + f + ': not found or too old.\n')

_dll_name = f
_dll_version = 0
# functions not defined when older dll are used
_fn_undefined = []

try:
    _lang = gandir.split('_')[-1]
except IndexError:
    _lang = 'FR'

del drive, path, editor, sdir, dll_1, dll_2, gandir, subdir, _ganessa_dir, lang
del os

#****g* ganessa.sim/Constants
# DESCRIPTION
#   Several categories of constants are available:
#   * constants defining a type of element: see BRANCH or LINK, NODE, RESERVOIR or TANK
#   * constants defining a command module: M.COM or M.ROOT, M.GEN, M.SIM etc.
#   * constants defining a command within a module: M.SIM.EXEC
#   * keywords
#
#****
#****g* ganessa.sim/Functions
#****
#****g* ganessa.sim/Iterators
#****
#****g* ganessa.sim/Classes
#****
#****c* Constants/BRANCH, LINK, NODE, NOEUD, TANK, RESERVOIR, RSV
# DESCRIPTION
#   Those constants allow to select one of the three types of model elements:
#   * LINK or BRANCH: branches elements such as pipes, pumps, valves
#   * NODE or NOEUD
#   * TANK or RESERVOIR or or RSV
# REMARK
#   M.LNK, M.NOD and M.RSV are object constants for calling BRANCH, NODE and RESERVOIR modules
#****
LINK = BRANCH = ARC = 1
NOEUD = NODE = 2
TANK = RESERVOIR = RSV = 3

# Class for the dictionary tree for keywords by modules
#****c* Constants/M, NONE
# DESCRIPTION
#   The M class provide a dictionnary tree for modules. It provides a
#   hierarchical naming of the commands by modules, for building
#   language-independant commands using  gencmd, gencmdw, _gencmdw functions.
# SYNTAX
#   One of the following:
#   * M.MODULE_SYMBOLIC_NAME
#   * M.MODULE_SYMBOLIC_NAME.COMMAND__SYMBOLIC_NAME or
#   * M.MODULE_SYMBOLIC_NAME..NONE or M.NONE or M.VOID
# CONTENT
#   The available MODULE_SYMBOLIC_NAME are:
#
#   ROOT: modules names: BRA, NOD, RSV, DYN, MOD, SIM, QUA, MES, LAB, FIR, INV, OPT.
#   They can be used in three forms, as first argument for the functions above:
#   * M.ROOT.SIM or M.SIM.ROOT: equals the index of the module name
#   * M.SIM: can be used in gencmd and gencmdw only as first argument
#
#   GEN: general purpose commands:
#   * LOAD: load a binary file
#   * OPEN and CLOSE: open and close an output file
#   * QUIT: the quit command
#   * READ: read a command language or data file
#     |html <br>example: <i>gencmd(M.GEN, M.GEN.OPEN, DICT.EXPORT, 'filename.txt')</i>
#   * EXPORT, SAVE: export or save to a (previously opened) file
#   * IMPORT: import attributes for a type of element from a file
#   * FIND: command for retrieving a given period or instant
#   * MESSAGE: writes a message to the console
#   * DEFPARAM, DEFVAR: define a positional parameter (%1 ... %9) or variable
#   * UNIT: redefine units name and coef
#   * EOF: the end-of-file command
#   LNK: link commands and submodules, including link types (.PIPE .PUMP .NRV .PRV .PSV .FCV .TCV etc.)
#
#   NOD: node commands and submodules:
#   * CONS: demand acquisition submodule
#   * COEF, AREA: demand coefficient by demand type and area
#   * TOPO: topograpy submodule
#   RSV: reservoir command and submodules:
#   * CHAR: characteristics
#   * LEVEL: initial level acquisition submodule
#   MES: measurement commands:
#   * SMOOTH: allow to define the smoothing interval
#   SIM: simulation commands:
#   * FILE: define a result file name
#   * EXEC: runs the simulation
#   QUA: Water quality module commands
#
# REMARK
#   The above codes are not exhaustive. Please refer to the script.
#****
class _CST(object):
    def __init__(self, cst):
        self.ROOT = cst
        self.NONE = -1
class M(object):
    NONE = VOID = -1
    GEN = _CST(0)
    GEN.CLOSE = 13
    GEN.CMPT = GEN.COMPAT = 65
    GEN.DEFP = GEN.DEFPARAM = 51  # DefParam
    GEN.DEFV = GEN.DEFVAR = 66  # defvar
    GEN.ECHO = 16
    GEN.EOF = 3
    GEN.EXPT = GEN.EXPORT = 39  # Export
    GEN.FIND = 18  # Find (instant)
    GEN.IMPT = GEN.IMPORT = 48
    GEN.INIT = 6
    GEN.LOAD = 17  # Load file.bin
    GEN.MESG = GEN.MESSAGE = 45  # Message
    GEN.OPEN = 12
    GEN.PATH = 23  # Path
    GEN.QUIT = 2
    GEN.READ = 5
    GEN.SAVE = 4
    GEN.STOP = 69 # stop-on error
    GEN.UNIT = 22
    GEN.WORD = GEN.WORDING = 52  # Libelle

    COM = _CST(1)   # COMMAND root level
    ROOT = COM
    BRA = _CST(2)
    ARC = BRA
    LNK = BRA

    BRA.BEND = 28
    BRA.BOOST = 8
    BRA.CUST = 24           # Picalor
    BRA.DENSITY = 18
    BRA.DIAM = 27
    BRA.DIAPH = 4
    BRA.ENVP = 23           # Picalor
    BRA.GPV = BRA.PRBR = 14
    BRA.HLEQ = 9
    BRA.FCV = BRA.FCTV = 7
    BRA.HEAT = 16           # Picalor
    BRA.MANV = 6
    BRA.MAT = 15
    BRA.NRV = BRA.CHECKV = BRA.CV = 3
    BRA.PIPE = 1
    BRA.PRV = 12
    BRA.PSV = 13
    BRA.PUMP = 2
    BRA.SHLT = 32
    BRA.SING = BRA.SHL= 33
    BRA.SST = 19
    BRA.TCV = BRA.THRV = 20
    BRA.VISC = 17

    NOD = _CST(3)
    NOD.AREA = 14 # demand coef by area
    NOD.CONS = 2
    NOD.COEF = 3  # demand coef by code
    NOD.CSMP = 8 # pressure dependant demand
    NOD.INIT = 24
    NOD.P0 = 9
    NOD.P1 = 10
    NOD.TOPO = 1

    RSV = _CST(4)
    TNK = RSV
    RSV.CHAR = 1
    RSV.FEED = 3
    RSV.LEVEL = 2
    RSV.OUT = 4

    DYN = _CST(5)  # dynam
    DYN.CTRL = DYN.REGU = 5
    DYN.CTRL_ENT = 8
    DYN.DATA = 1
    DYN.DSTEP = 3
    DYN.NSTEP = 2


    MOD = _CST(7)  # Modification
    MOD.ADD = 4
    MOD.ALLOC = 15
    MOD.CLOSE = 8
    MOD.DEL = 1
    MOD.DIV = 3
    MOD.INSERT = 13
    MOD.MERGE = 10
    MOD.MULT = 2
    MOD.OPEN = 7
    MOD.PURGE = 17
    MOD.REPLACE = 6
    MOD.REVERSE = 12
    MOD.SPLIT = 11

    SIM = _CST(8)
    SIM.CANCEL = SIM.ANNULER = 13
    SIM.EXEC = 1
    SIM.FILE = 25
    SIM.IVER = SIM.IVERB = 8
    SIM.STOP_DYN = 52
    SIM.STOP_ON = 51

    QUA = _CST(10)
    WQ = QUA
    QUA.AGE = 8
    QUA.ALTC = 40
    QUA.CLEAR = QUA.CLEAN = 5
    QUA.CONTINUE = QUA.CONT = QUA.STEP = 13
    QUA.CORROSION = QUA.CORR = 29
    QUA.DECAY = QUA.CONST = 6
    QUA.EXEC = 3
    QUA.FILE = QUA.NODEFILE = 18
    QUA.FILELINK = QUA.LINKFILE = 32
    QUA.INIT = 17
    QUA.INITRSV = 31
    QUA.IVERC = QUA.KOPT = 19
    QUA.ORDER = QUA.KINEXP = 39
    QUA.POLNOE = QUA.POL = 2
    QUA.POLRSV = 7
    QUA.REGIME = 4
    QUA.RESTIMINI = 43
    QUA.SAVESTATE = 42
    QUA.STORSTEPNODE = 12
    QUA.STORSTEPLINK = 33
    QUA.VISUSTART = 9
    QUA.VISUEND = 24
    QUA.VISUSTEP = 10

    MES = _CST(15)
    MES.SMOOTH = 6
    LAB = _CST(16)
    FIR = _CST(19)

    INV = _CST(20)
    INV.BFACT = 11
    INV.CONS = INV.DEMAND = 13
    INV.DTSMOOTH = 7
    INV.EXEC = 8
    INV.FTOL = 32
    INV.INIT = 29
    INV.KMAT = 18
    INV.SHL = 26
    INV.NITER = 2
    INV.PARAM = 6
    INV.RMAT = 12
    INV.TSTART = INV.TDEB = INV.TBEG = 4
    INV.TEND = INV.TFIN = 5
    INV.TYPE = INV.METHOD = 1
    INV.WEIGHT = 24
    INV.ZMES = 23
    INV.ZTNK = 28

    OPT = _CST(21)
    OPT.CIL = 1
    OPT.CIN = 2
    OPT.CIT = 3
    OPT.WQINIT = 7

# Build M.ROOT data from M.x.ROOT
for attr, val in M.__dict__.iteritems():
    if attr[0:2] == '__' : continue
    if attr in  ('ROOT', 'COM', 'NONE', 'VOID') : continue
    setattr(M.ROOT, attr, val.ROOT)

# Class for the isolated keywords
#****c* Constants/DICT
# DESCRIPTION
#   The DICT class provide a dictionnary tree for keywords
# SYNTAX
#   DICT.SYMBOLIC_NAME
# CONTENT
#   * FULLPER: extended simulation (ENCHAINE in French)
#   * EXPORT
#   * INSTANT
#****
class DICT(object):
    AND = 11
    AUTO = 5
    AVERAGE = AVG = 76
    BINARY = 54
    BY = PAR = 114
    COMMA = VIRGULE = 122
    SEMICOMMA = POINTVIRGULE = CSV = 123
    DATA = 28
    DCF = TCB = 171
    DISTANCE = 155
    DYNAM = 75
    END = 9
    EXPORT  = 92
    FILE = 8
    FNODE = TONODE = 168
    FULLPER = 91  # Full-period = enchaine
    INSTANT = 97
    INODE = FROMNODE = 167
    INVERS = REVERSE = 106
    ON = 32
    OFF = 33
    PATH = PARCOURS = 157
    STATIC = PERMANENT = 74
    TEXT = 65
    TO = 10
    TREE = 90

class SIMERR(object):
    SIMERR = 1024
    ISOL = 2
    SLOW_CV = 4
    UNSTABLE = 6
    FCTAPP = 8
    DIVERGE = 10
    STRUCT = 12
    MEMALLOC = 16

#****k* Iterators/Elements
# SYNTAX
#   for id in Elements(typelt):
# ARGUMENT
#   int typelt: type element constants LINK, NODE, TANK
# RESULT
#   string id: id of each element of the given type in turn
#****
class Elements(object):
    def __init__(self, typelt):
        if isinstance(typelt, numbers.Number):
            self.type = typelt
            self.nbmax = _ganessa.nbobjects(self.type)
        self.index = 1
    def __iter__(self):
        return self
    def next(self):
        if self.index > self.nbmax:
            raise StopIteration
        (elem, ls) = _ganessa.getid(self.type, self.index)
        self.index += 1
        return elem[0:ls]
    def len(self):
        return self.nbmax
#****k* Iterators/Branches, Links
# SYNTAX
#   * for id in Branches():
#   * for id in Links():
# RESULT
#   string id: returns each branch id in turn
# REMARK
#   Branches and Links are synonyms
#****
#****k* Iterators/Nodes
# SYNTAX
#   for id in Nodes():
# RESULT
#   Returns each node id in turn
#****
#****k* Iterators/Tanks, Reservoirs
# SYNTAX
#   * for id in Tanks():
#   * for id in Reservoirs():
# RESULT
#   string id: returns each reservoir id in turn
#****
# Iterators for browsing model elements

class Nodes(Elements):
    def __init__(self):
        Elements.__init__(self, NODE)

class Branches(Elements):
    def __init__(self):
        Elements.__init__(self, BRANCH)

class Links(Elements):
    def __init__(self):
        Elements.__init__(self, LINK)

class Reservoirs(Elements):
    def __init__(self):
        Elements.__init__(self, RESERVOIR)

class Tanks(Elements):
    def __init__(self):
        Elements.__init__(self, TANK)

def doc(fname):
    print(eval('_ganessa.' + fname + '.__doc__'))

def _ret_errstat(*args):
    return -1

#****f* Functions/init
# SYNTAX
#   init([folder])
# ARGUMENT
#   str folder: optional folder name where journal and work files will be created
# RESULT
#   Initialises the ganessa simulation/command language engine
# REMARKS
#   - Starting with version 1.3.5, a session should be started by calling init() or init(folder).
#     however for compatibility with previous releases where init was called at import time,
#     init is automatically called at 1st call of cmd, cmdfile, execute, load, loadbin
#   - A session should be terminated by calling quit() or typing <Ctrl>+Z
# HISTORY
#   introduced in 1.3.5
#****
try:
    setbatchmode = _ganessa.batchmode
except AttributeError:
    setbatchmode = _ganessa.setbatchmode

def init(folder= None, silent= False):
    global _dll_version
    if _dll_version:
        return
    # Initialisation of ganessa
    if folder is None or not folder:
        _dll_version = _ganessa.inipic()
    else:
        try:
            _dll_version = _ganessa.inipicfld(folder)
        except AttributeError:
            _dll_version = _ganessa.inipic()
            _fn_undefined.append('init(folder)')

    # 2 places to check : here and pyGanSim.f90 (inipic)
    if _dll_version < 0:
        jj = -_dll_version
        aa, mm, jj = jj/10000, (jj/100) % 100, jj%100
        comment = 'DLL {:s} too old: {:02d}-{:02d}-{:02d}\n'.format(_dll_name, jj, mm, aa)
        print(comment)
        raise ImportError(comment)
    else:
        print('\t* pyganessa:', __version__, '-', _dll_name + ':', _dll_version, _lang,'*')
    _precmode = setbatchmode(1)
    if silent:
        _ganessa.gencmd(M.SIM.ROOT, M.SIM.IVER, M.NONE, '-9')
        istat = _ganessa.commit(0)

#****f* Functions/setbatchmode
# SYNTAX
#   oldmode = setbatchmode(mode)
# ARGUMENT
#   int mode: batch mode to activate
# RESULT
#   int oldmode: batch mode that was in effect
# REMARK
#   Defaults to 1 (True)
#****

#****f* Functions/quit, close
# SYNTAX
#   ret = quit([True])
# ARGUMENT
#   optional bool verbose: if set to True, a message is printed. 
#   Defaults to False.
# RESULT
#   text ret: text string telling that he module has been unloaded.
#   Terminates the ganessa session and unloads the module ganessa.sim
# REMARKS
#   - quit() is automatically called when quitting with <Ctrl>+Z
#   - close() is a synonym for quit()
#   - A session should be terminated by calling quit() or typing <Ctrl>+Z
#   - sys.exit() automatically trigers quit()
#****
def _close(*args):
    global _ganessa, _dll_version
    if _dll_version:
        try:
            text = 'Ganessa unloaded.'
            _ganessa.closepic()
            # _dll_version = 0
            del _ganessa
        except NameError:
            text = 'Ganessa already unloaded...'
    else:
        text = 'Ganessa was not loaded!'
    if args and args[0]:
        print (text)
    return text
# Register closepic function for proper exit
atexit.register(_close)
quit = _close
close = _close

#****f* Functions/cwfold
# SYNTAX
#   ret = cwfold(folder)
# ARGUMENT
#   str folder: folder name where journal (piccolo.jnl) and work files will be created
# RESULT
#   bool ret: True if folder exists; False otherwise
# HISTORY
#   introduced in 1.7.7 (170705)
#****
try:
    cwfold = _ganessa.cwfold
except AttributeError:
    _fn_undefined.append('cwfold(folder)')
    cwfold = lambda x: False

# Execution error management
#****f* Functions/useExceptions, GanessaError, SimulationError
# SYNTAX
#   * oldstat = useExceptions([status])
#   * try: ... except GanessaError:
#   * try: ... except SimulationError [as exc]:
# ARGUMENTS
#   bool status: if True, errors will raise exceptions
# RESULT
#   * bool oldstat: previous error handling mode
#   * exception exc: excetion object. The attribute exc.reason will provide
#     additional information on the origin of error
# DESCRIPTION
#   SimulationError is a derived class of GanessaError.
#   The simulation error subtypes are the following:
#   * SIMERR.ISOL: Isolated nodes
#   * SIMERR.SLOW_CV: Slow convergence (convergence not obtained within max iteration count)
#   * SIMERR.UNSTABLE: Unstability (flip between 2 or more equilibrium points)
#   * SIMERR.FCTAPP: Equipment(s) or storage(s) do not operate properly;
#     they can be retrieved with the Unstable() iterator
#   * SIMERR.DIVERGE: Divergence (convergence error increase)
#   * SIMERR.STRUCT: Structural inconsistency
#   * SIMERR.MEMALLOC: Memory allocation error (WQ or inverse problem)
# REMARK
#   Defaults to False: errors do not raise 'GanessaError' exceptions. If set to True,
#   errors raise exceptions with a string name giving the error message and a int reason
#   giving the type of exception.
#****
class GanessaError(Exception):
    def __init__(self, number, reason, text):
        self.number = number
        self.reason = reason
        self.text = text
    def __str__(self):
        return _dll_name + ' ERROR : ({:d}) : {:s}'.format(self.number, self.text)

class SimulationError(GanessaError):
    def __str__(self):
        sreason = {SIMERR.ISOL: 'Isolated nodes',
                   SIMERR.SLOW_CV: 'Slow convergence',
                   SIMERR.UNSTABLE: 'Instability',
                   SIMERR.FCTAPP: 'Equipment or storage do not operate properly',
                   SIMERR.DIVERGE: 'Divergence',
                   SIMERR.STRUCT: 'Structural inconsistency',
                   SIMERR.MEMALLOC: 'Memory allocation error'}.get(self.reason, 'Unknown')
        detail = 'Hydraulic Simulation Error ({:d}) : {:s}\n{:s}'
        return detail.format(self.reason, sreason, GanessaError.__str__(self))

_ganessa_raise_exceptions = False
def useExceptions(enable= True):
    global _ganessa_raise_exceptions
    _ganessa_raise_exceptions = enable

def _checkExceptions(inum, istat, text= ''):
    if _ganessa_raise_exceptions and istat:
        stat = abs(istat)
        SIM_ERR = SIMERR.SIMERR
        if stat & SIM_ERR:     # simulation error code
            raise SimulationError(inum, stat^SIM_ERR, text)
        elif istat > 0:
            raise GanessaError(inum, istat, text)
        else:
            print ('WARNING: ({:d})'.format(inum), text, 'status=', str(istat))

# Execute a command, a set of commands, a command file
#****f* Functions/cmd, addcmdw, execute, cmdfile
# SYNTAX
#   * istat = cmd(scmd)
#   * istat = cmdfile(fname [, args])
#   * istat = addcmdw(scmd)
#   * istat = execute(scmd1 [ ..., scmdn][, dbg= True])
# ARGUMENTS
#   * string scmd: command line to be executed
#   * string fname: data/command file name to be read/executed
#   * string args: optional argument(s) to the command file, as one single string
#   * string scmd1: command line(s) to be executed ('\n' is handled as a command delimiter)
#   * string scmdn: optional command lines(s) to be executed (same as scmd1)
#   * boolean dbg: optional, makes commands to be echoed in the log file.
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - cmd executes the given command
#   - cmdfile reads/executes the commands from the file.
#   - addcmdw pushes the command onto the command stack.
#   - execute pushes the given commands on the stack and executes them
#
#   If an error occurs while reading a file or nested files, the execution stops.
#   If the useException mode is set, the error will raise a GanessaError
#****
addcmdw = _ganessa.addcmd
def cmd(scmd):
    if not _dll_version: init()
    istat = _ganessa.cmd(winstr(scmd))
    _checkExceptions(1, istat, 'Syntax error in command: ' + scmd)
    return istat

def cmdfile(fname, *args):
    if not _dll_version: init()
    istat = _ganessa.cmdfile(winstr(fname), *args)
    _checkExceptions(8, istat, 'Syntax error in file: ' + fname)
    return istat

def execute(*args, **kwargs):
    '''Executes a tuple of commands in turn
    Handles multiple commands separated with \n as well'''
    if not _dll_version: init()
    try:
        dbg = kwargs['dbg']
    except KeyError:
        dbg = False

    if dbg: _ganessa.gencmd(M.GEN.ROOT, M.GEN.ECHO, DICT.ON)
    for arg in args:
        for cmdline in arg.split('\n'):
            if cmdline: _ganessa.addcmd(cmdline)
    if dbg: _ganessa.gencmd(M.GEN.ROOT, M.GEN.ECHO, DICT.OFF)
    istat = _ganessa.commit(0)
    _checkExceptions(4, istat, 'Multiple Commands execution error!')
    return istat

# Execute a command, a set of commands, a command file
#****f* Functions/gencmd, gencmdw, _gencmdw
# PURPOSE
#   Those fuctions allow to generate a language independant command line
#   based upon the keywords id of a module and its commands (see M).
# SYNTAX
#   * istat =  gencmd (module, icmd, [word, scmd, extmode])
#   * istat =  gencmdw(module, icmd, [word, scmd, extmode])
#   * istat = _gencmdw(module, icmd, [word, scmd, extmode])
# ARGUMENTS
#   * module: constant id for the module
#   * icmd:   constant id for the command in the module (or NONE)
#   * word:   constant id for a keyword (or NONE) (optional)
#   * scmd:   additional string (optional)
#   * extmode: if set to 1, the command is appended to the previous one (optional)
#   * string scmd: command line to be executed
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - gencmd builds and executes the given command
#   - gencmdw and _gencmdw build the command and push it onto the command stack
#   - gencmd and gencmdw allow a more flexible entry of the first 2 arguments
#   - If the useException mode is set, an error will raise a GanessaError
# EXAMPLES
#   The following are equivalent:
#   * istat = _gencmdw(M.SIM.ROOT, M.SIM.EXEC, DICT.FULLPER)
#   * istat = gencmdw(M.SIM, "EXEC", DICT.FULLPER)
#   The following are equivalent:
#   * istat = _gencmdw(M.SIM.ROOT, M.SIM.EXEC, scmd="15:30")
#   * istat = gencmdw(M.SIM, "EXEC", scmd="15:30")
#****
# Wrapping for 'gencmd': allow the class name as arg1 and if so the attribute name as arg2
_gencmdw = _ganessa.gencmd
def gencmdw(module, cmde, *args, **kwargs):
    if not _dll_version: init()
    if isinstance(module, numbers.Number):
        modul = module
    else:
        modul = module.ROOT
    if isinstance(cmde, numbers.Number):
        attr = cmde
    else:
        try:
            attr = getattr(modul, cmde.upper())
        except:
            attr = M.NONE
            print ('Command or keyword not recognised:', repr(cmde), '\n')
    _ganessa.gencmd(modul, attr, *args, **kwargs)

def gencmd(modul, cmde, *args, **kwargs):
    gencmdw(modul, cmde, *args, **kwargs)
    istat =  _ganessa.commit(0)
    _checkExceptions(3, istat, 'Syntax error in command: ')
    return istat

#****f* Functions/getkeyword, modulekeyword, attrkeyword
# PURPOSE
#   Get keyword or command name by index  - for building
#   command language independant functions
# SYNTAX
#   * sret = getkeyword(code)
#   * sret = modulekeyword(module, submodule)
#   * sret = attrkeyword(attr)
# ARGUMENTS
#   * code: int code of the keyword (>0) or global command (<0)
#   * module: int code of the module (<0 for the submodule alone)
#   * submodule: int code of the module (0 for the module alone)
#   * attr: int code of the attribute
# RESULT
#   str sret: trimmed value of the keyword or global command or module submodule
#         (null string if the code or module/submodule is not recognised)
# HISTORY
#   * getkeyword introduced in 1.4.2 (161010)
#   * modulekeyword and attrkeyword intoduced in 1.7.3 (170313)
#****
try:
    _getkeyword = _ganessa.keyword
except AttributeError:
    _getkeyword = lambda code : (0, '')
    _fn_undefined.append('getkeyword')
def getkeyword(code):
    nret, sret = _getkeyword(code)
    return sret[:nret]
try:
    _modulekeyword = _ganessa.modulekeyword
except AttributeError:
    _modulekeyword = lambda m, sm : (0, '')
    _fn_undefined.append('modulekeyword')
def modulekeyword(module, submodule):
    nret, sret = _modulekeyword(module, submodule)
    return sret[:nret]
try:
    attrkeyword = _ganessa.attrkeyword
except AttributeError:
    attrkeyword = lambda code : { 5:'NI', 6:'NF', 60:'ZN'}.get(code, '#')
    _fn_undefined.append('attrkeyword')

#****f* Functions/commit
# PURPOSE
#   Executes all the commands available on the stack (first in, first executed)
# SYNTAX
#   istat = commit()
# RESULT
#   int istat: error status (0 if OK)
# REMARK
#   If an error occurs, the remaining part of the stack is cleared
#****
def commit(*args):
    istat = _ganessa.commit(*args)
    _checkExceptions(2, istat, 'Command language execution error!')
    return istat

#****f* Functions/reset
# PURPOSE
#   Clears (removes) all model objects
# SYNTAX
#   istat = reset()
# RESULT
#   int istat: error status (0 if OK)
#****
def reset():
    if not _dll_version: init()
    nbn = _ganessa.nbobjects(NODE)
    _ganessa.addcmd(' /* before system reset: nb of nodes: ' + str(nbn))
    # COMM INIT
    _ganessa.gencmd(M.COM.ROOT, M.NONE)
    _ganessa.gencmd(M.GEN.ROOT, M.GEN.INIT, extmode= True)
    return _ganessa.commit(0)

#****f* Functions/loadbin
# PURPOSE
#   Clears (removes) all model objects and loads a binary file
# SYNTAX
#   istat = loadbin(fname)
# ARGUMENT
#   string fname: binary data/result file name to be loaded
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - The current model is discarded before the new one is loaded.
#   - If the file content is not a Piccolo binary file an error occurs.
#   - Binary result files also contain all data describing the model.
#****
def loadbin(fname):
    if not _dll_version: init()
    _ganessa.gencmd(M.GEN.ROOT, M.GEN.LOAD, scmd= winstr(quotefilename(fname)))
    istat = _ganessa.commit(0)
    _checkExceptions(16, istat, 'Error loading binfile: ')
    return istat

# Run the simulation
try:
    solveh = _ganessa.simulh
except AttributeError:
    solveh = _ganessa.solveh
#****f* Functions/full_solveH
# PURPOSE
#   Runs the full simulation and loads the result file for browsing results
# SYNTAX
#   istat = full_solveH([resultfile] [, silent] [, iverb] [, retry])
# ARGUMENT
#   * string resultfile: if provided, the results will be written in the file
#     instead of the default 'result.bin'. If the file exists it will be superseded.
#     If not it will be created.
#   * bool silent: if set to True, simulation runs without any output.
#     Optional - if False or not set, leaves 'iverb' unchanged.
#   * integer iverb: if provided, controls the amount of output during simulation
#     (SIM IVERB parameter). The defaults is -1.
#   * bool retry: if set to True, the simulation is run again if it fails
#     because of isolated nodes. Optional -  defaults to False
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - Unless explicitely disabled, results are saved to a binary file,
#     which defaults to the file 'result.bin' in the ganessa work directory.
#   - Binary result files also contain all data describing the model.
#   - silent=True overrides iverb setting if provided.
# HISTORY
#   optional argument 'retry' added in 1.5.1
#****
def full_solveH(resultfile= None, silent= False, iverb= -1, retry= False):
    # SIM IVERB
    if silent: sverb = '-9'
    elif iverb == -1: sverb = '-1'
    else: sverb = str(iverb)
    _ganessa.gencmd(M.SIM.ROOT, M.SIM.IVER, M.NONE, sverb)
    if resultfile:
        # SIM FILE xxx
        _ganessa.gencmd(-M.SIM.ROOT, M.SIM.FILE, M.NONE, winstr(quotefilename(resultfile)))
    #  EXEC FULL-PERIOD
    _ganessa.gencmd(-M.SIM.ROOT, M.SIM.EXEC, DICT.FULLPER)
    istat = _ganessa.commit(0)
    if retry and abs(istat) % SIMERR.SIMERR == SIMERR.ISOL:
        _ganessa.gencmd(-M.SIM.ROOT, M.SIM.EXEC, DICT.FULLPER)
        istat = _ganessa.commit(0)
    _checkExceptions(32, istat, 'Error running hydraulic simulation')
    return istat

#****f* Functions/solveH
# PURPOSE
#   Runs the simulation at a given instant
# SYNTAX
#   istat = solveH(time [, retry])
# ARGUMENT
#   * int or str time: instant to run the simulation - default to 0.
#     if int: time in seconds; if str: time in the format hh:mm[:ss]
#   * bool silent: if set to True, simulation runs without any output.
#     Optional - if False or not set, leaves 'iverb' unchanged.
#   * integer iverb: if provided, controls the amount of output during simulation
#     (SIM IVERB parameter). If not set, leaves 'iverb' unchanged.
#   * bool retry: if set to True, the simulation is run again if it fails
#     because of isolated nodes. Optional -  defaults to False
# RESULT
#   int istat: error status (0 if OK)
# HISTORY
#   added 2017.05.15 - version 1.7.5
#****
def solveH(time= 0, silent= False, iverb= None, retry= False):
    # SIM
    _ganessa.gencmd(M.SIM.ROOT, M.SIM.NONE, M.NONE)
    # IVERB
    if silent: 
        iverb = -9
    if iverb is not None: 
        _ganessa.gencmd(-M.SIM.ROOT, M.SIM.IVER, M.NONE, str(iverb))
    # Simulation time
    if isinstance(time, numbers.Number):
        if time == 0:
            stime = '0:0:0'
        else:
            stime = hhmmss(time, rounded=True)
    else:
        stime = time
    #  EXEC
    _ganessa.gencmd(-M.SIM.ROOT, M.SIM.EXEC, M.NONE, stime)
    istat = _ganessa.commit(0)
    if retry and abs(istat) % SIMERR.SIMERR == SIMERR.ISOL:
        _ganessa.gencmd(-M.SIM.ROOT, M.SIM.EXEC, M.NONE, stime)
        istat = _ganessa.commit(0)
    _checkExceptions(32, istat, 'Error running thermo-hydraulic simulation')
    return istat

def solveTH(silent= False, iverb= -1):
    # SIM IVERB
    if silent: sverb = '-9'
    elif iverb == -1: sverb = '-1'
    else: sverb = str(iverb)
    _ganessa.gencmd(M.SIM.ROOT, M.SIM.IVER, M.NONE, sverb)
    #  EXEC
    _ganessa.gencmd(-M.SIM.ROOT, M.SIM.EXEC, M.NONE)
    istat = _ganessa.commit(0)
    _checkExceptions(32, istat, 'Error running thermo-hydraulic simulation')
    return istat

#****f* Functions/loadres
# PURPOSE
#   Loads the default binary result file.
# SYNTAX
#   istat = loadres()
# RESULT
#   int istat: error status (0 if OK)
# REMARK
#   The current model is discarded before the data corresponding to
#   the last simulation making use of the default result file is loaded.
#****
def loadres():
    if _fresult:
        return loadbin(_fresult)
    else:
        print(' *** Result file not found !')
        return 1

#****f* Functions/setWQresultfile
# PURPOSE
#   Defines the binary result file(s) for WQ simulation.
# SYNTAX
#   setWQresultfile([fnode] , [flink])
# ARGUMENTS
#   * str fnode: name of the node WQ result file
#   * str flink: name of the link WQ result file (optional)
# REMARK
#   * if fnode is omitted, either use None or flink=filename
#   * this command can be used either before running the simulation, for writing
#     the file(s), or afterwards, in order to choose which result file(s) to browse.
#****
def setWQresultfile(fnode=None, flink=None):
    '''Added 150914'''
    if fnode is not None:
        # QUAL FILE xxx
        _ganessa.gencmd(M.QUA.ROOT, M.QUA.NODEFILE, M.NONE, winstr(quotefilename(fnode)))
    if flink is not None:
        # QUAL FILE xxx
        _ganessa.gencmd(M.QUA.ROOT, M.QUA.LINKFILE, M.NONE, winstr(quotefilename(flink)))
    istat = _ganessa.commit(0)

#****f* Functions/browseH, browseWQ
# PURPOSE
#   Retrieves and interpolate results from a given time step or instant:
#   * browseH retrieves hydraulic results
#   * browseWQ retrieves hydraulic
#   |html <b>and</b> water quality results
# SYNTAX
#   * istat = browseH(time_step)
#   * istat = browseH(instant)
# ARGUMENTS
#   * int time_step: time step to load
#   * string instant: instant to load, in the form hh:mm:ss
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   For hydraulic results, two set of results may be available at a given instant:
#   * at boudary of time steps, except beginning and end of the simulation,
#     results ending the previous time step and results starting the next time step.
#   * at internal time steps when a state transition occured (pump start/stop etc.).
#   In such a situation the results are those from the end of the previous interval.
#****
def browseH(time_or_str, wq= False):
    if isinstance(time_or_str, numbers.Number):
        stime = hhmmss(time_or_str, rounded= True)
    else:
        stime = time_or_str
    _ganessa.gencmd(M.GEN.ROOT, M.GEN.FIND, DICT.INSTANT, stime)
    if wq:
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.FIND)
        _ganessa.gencmd(M.QUA.ROOT, M.NONE, extmode= 1)
    istat = _ganessa.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(16*3, istat,
                'Error while retrieving simulation results at: ' + stime)
    return istat

def browseWQ(time_or_str):
    return browseH(time_or_str, True)

#****f* Functions/nbobjects
# PURPOSE
#   Returns the number of model elements in the given type
# SYNTAX
#   nb = nbobjects(typelt)
# ARGUMENT
#   int typelt: type of element (LINK, NODE, TANK)
# RESULT
#   int nb: number of element in that type
#****
nbobjects = _ganessa.nbobjects
#****f* Functions/selectlen, select
# PURPOSE
#   * selectlen returns the number and type of model elements in the given selection
#   * select: returns the index vector, number and type of elements in the selection
# SYNTAX
#   * nb, typelt = selectlen(sname)
#   * vect_idx, nb, typelt = select(sname)
# ARGUMENT
#   string sname: name of selection
# RESULT
#   * int nb: number of element in that selection
#   * int typelt: type of element of that selection
#   * int vect_idx[]: index vector of elements in the selection
#****
try:
    selectlen = _ganessa.getselectlen
    _select = _ganessa.getselect
except AttributeError:
    selectlen = _ganessa.selectlen
    _select = _ganessa.select
def select(sname):
    nb, typelt = selectlen(sname)
    return (_select(nb), nb, typelt)
#****k* Iterators/Selected
# SYNTAX
#   for id, typelt in Selected(sname):
# ARGUMENT
#   string sname: name of a selection
# RESULT
#   Returns the id and type of each element in the selection in turn:
#   * string id: id of the next element in the selection
#   * int type: element type (the same for all ids)
#****
# Iterators for browsing model elements
class Selected(object):
    def __init__(self, sname):
        self.nbmax, self.type = selectlen(sname)
        if self.nbmax > 0:
            self.select = _select(self.nbmax)
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if self.index >= self.nbmax:
            if self.nbmax > 0: 
                del self.select
                self.nbmax = 0
            raise StopIteration
        numelt = self.select[self.index]
        elem, ls = _ganessa.getid(self.type, numelt)
        self.index += 1
        return (elem[0:ls], self.type)
    def len(self):
        return self.nbmax

#****f* Functions/linkattr, nodeattr, tankattr, linkattrs, nodeattrs, tankattrs, attr, attrs, meanattr
# PURPOSE
#   * linkattr, nodeattr, rsvattr, attr: return numerical attributes
#     of a given element by id
#   * linkattrs, nodeattrs, attrs: return text attributes of a
#     given element by id
#   * meanattr: return mean attribute of from and to nodes given by branch id
# SYNTAX
#   * val = linkattr(id, attr)
#   * val = nodeattr(id, attr)
#   * val = tankattr(id, attr)
#   * txt = linkattrs(id, attr)
#   * txt = nodeattrs(id, attr)
#   * txt = tankattrs(id, attr)
#   * val = attr[typelt](id, attr)
#   * txt, sz = attrs(typelt, id, attr)
#   * val = meanattr(id, attr)
# ARGUMENTS
#   * string id: id of element
#   * string attr: attribute (data or result) for which value is requested
#   * int typelt: type of element
# RESULT
#   * float val: value of the numerical attribute (0. if not available)
#   * string txt: value of the text attribute (empty string '' if
#     undefined or not available)
#   * int sz: length of the returned string
# REMARKS
#   * Numerical attributes are returned converted in the actual unit system.
#   * Reservoir text attributes are identical to the underlying node id
#   * meanattr requires version 2016 or higher of Piccolo/Ganessa dll
#   * branchattr, rsvattr and branchattrs are synonyms for linkattr, tankattr and linkattrs
#****
nodeattr = _ganessa.nodeattr
linkattr = _ganessa.branchattr
tankattr = _ganessa.rsvattr
branchattr = _ganessa.branchattr
rsvattr = _ganessa.rsvattr
attr = {LINK: _ganessa.branchattr,
        NODE: _ganessa.nodeattr,
        TANK: _ganessa.rsvattr}
attrs = _ganessa.strattr

def linkattrs(eid, attr):
    sval, n = _ganessa.strattr(LINK, eid, attr)
    return sval[0:n] if n > 0 else ''
branchattrs = linkattrs

def nodeattrs(eid, attr):
    sval, n = _ganessa.strattr(NODE, eid, attr)
    return sval[0:n] if n > 0 else ''

def tankattrs(eid, attr):
    sval, n = _ganessa.strattr(TANK, eid, attr)
    return sval[0:n] if n > 0 else ''

try:
    meanattr = _ganessa.nodemeanattr
except AttributeError:
    meanattr = lambda sid, sattr : 0.0
    _fn_undefined.append('meanattr')

#****f* Functions/shearstr
# PURPOSE
#   Returns the shear stress associated with a velocity for the given pipe
# SYNTAX
#   val, grad = shearstr(id, v)
# ARGUMENTS
#   * string id: id of element
#   * float v: velocity for which value is requested
# RESULT
#   * float val: value of the shear stress
#   * float grad: value of ds/dv
# REMARKS
#   * val is not defined if id is not a pipe
#   * requires Piccolo 2017
# HISTORY
#   * 31.03.2017: function created (1.7.3)
#****
try:
    shearstr = _ganessa.shearstr
except AttributeError:
    shearstr = lambda sid, val : (0.0, 0.0)
    _fn_undefined.append('shearstr')

#****f* Functions/nlinkattr, nnodeattr, ntankattr, nlinkattrs, nnodeattrs, ntankattrs, nattr, nattrs
# PURPOSE
#   * nlinkattr, nnodeattr, nrsvattr, nattr: return numerical attributes
#     of a given element by index
#   * nlinkattrs, nnodeattrs, nattrs: return text attributes of a
#     given element by index
# SYNTAX
#   * val = nlinkattr(num, attr)
#   * val = nnodeattr(num, attr)
#   * val = ntankattr(num, attr)
#   * txt = nlinkattrs(num, attr)
#   * txt = nnodeattrs(num, attr)
#   * txt = ntankattrs(num, attr)
#   * val = nattr[typelt](num, attr)
#   * txt, sz = nattrs(typelt, num, attr)
# ARGUMENTS
#   * string num: index of element (stating at 1)
#   * string id_or_num: id or index of element
#   * string attr: attribute (data or result) for which value is requested
#   * int typelt: type of element
# RESULT
#   * float val: value of the numerical attribute (0. if not available)
#   * string txt: value of the text attribute (empty string '' if
#     undefined or not available)
#   * int sz: length of the returned string
# REMARKS
#   * Numerical attributes are returned converted in the actual unit system.
#   * Tank text attributes are identical to the underlying node id
#****
try:
    nnodeattr = _ganessa.nnodeattr
    nlinkattr = _ganessa.nlinkattr
    ntankattr = _ganessa.ntankattr
    nattrs = _ganessa.nstrattr
except AttributeError:
    _fn_undefined.extend(['nnodeattr', 'nlinkattr', 'ntankattr', 'nxxxattrs'])
    ntankattr = nlinkattr = nnodeattr = lambda num, attr : 0.0
    nattrs = lambda typ, num, attr : ''

nattr = {LINK: nlinkattr,
         NODE: nnodeattr,
         TANK: ntankattr}

def nlinkattrs(num, attr):
    sval, n = nattrs(LINK, num, attr)
    return sval[0:n] if n > 0 else ''
branchattrs = linkattrs

def nnodeattrs(num, attr):
    sval, n = nattrs(NODE, num, attr)
    return sval[0:n] if n > 0 else ''

def ntankattrs(num, attr):
    sval, n = nattrs(TANK, num, attr)
    return sval[0:n] if n > 0 else ''

#****f* Functions/getdemandbycode, getcodedemandinit, nextcodedemand
# PURPOSE
#   * getdemandbycode: returns demand for a given node and consumer code by id
#   * getcodedemandinit: initialises and returns the number of pairs
# SYNTAX
#   * demand, istat = getdemandbycode(id, code)
#   * nbpairs = getcodedemandinit(id)
#   * code, demand, codelen = nextcodedemand()
# ARGUMENTS
#   * string id: id of node
#   * string code: code for which demand value is requested
#   * int nbpairs: number of demand, csm pairs for the node
# RESULT
#   * float demand: value of the demand (0 if not available)
#   * int istat: return code (0= 0K -1= unknown code 1= unknown node 3= dll too old)
#   * int nbpairs: number of code, demand pairs for the node
#   * string code: demand code
#   * int codelen: length of code string
# REMARKS
#   * these functions require version 2016 or higher of the Piccolo/Ganessa dll
#   * If the GanSim Dll is too old those function will not return data
#   * See also the Demands(id) iterator
#****
try:
    getdemandbycode = _ganessa.getdemandnodebycode
    getcodedemandinit = _ganessa.getcodedemandinit
    nextcodedemand = _ganessa.nextcodedemand
except AttributeError:
    getcodedemandinit = _ret_errstat
    _fn_undefined.append('Demands')
    _fn_undefined.append('demand by node getter')

#getcodedemandall = _ganessa.getcodedemandall
#****k* Iterators/Demands
# SYNTAX
#   for code, csm in Demands(node_id):
# ARGUMENT
#   string node_id: id of node
# RESULT
#   Returns each demand code and nominal value for the node in turn:
#   * string code: demand code
#   * float csm: demand value for this code
# REMARK
#   * requires version 2016 or higher of Piccolo/Ganessa dll
#****
# Iterators for browsing demand codes and values for a given node
class Demands(object):
    def __init__(self, node_id):
        self.nb, self.szcod = getcodedemandinit(node_id)
        if self.nb < 0:
            raise GanessaError(8, 0, 'The version of ' + _dll_name +
                                ' does not support this feature')
    def __iter__(self):
        return self
    def next(self):
        if self.nb == 0:
            raise StopIteration
        self.nb -= 1
        code, csm, n = _ganessa.nextcodedemand()
        return (code[0:n], csm) if n > 0 else ('', 0.0)

#****f* Functions/getcodescount, nextcode
# PURPOSE
#   * getcodescount: returns count of used demand codes
#   * nextcode: returns the list of used codes with node count
# SYNTAX
#   * ncodes = getcodescount(used_only)
#   * code, demand, count, nbchar  = nextcode()
# ARGUMENTS
#   * bool used_only: if True, only codes associated with at least
#     one node will be returned
# RESULT
#   * int ncodes: number of codes to be returned
#   * str code: demand codes
#   * float demand: total nominal demand for the code
#   * int count: node count
#   * int nbchar: nb of chars in the demand code string
# REMARKS
#   * these functions require version 2016 or higher of Piccolo/Ganessa dll
#   * If the GanSim Dll is too old those function will not return data
#   * See also the Demands(id) iterator
#****
try:
    getcodescount = _ganessa.getcodescount
    nextcode = _ganessa.nextcodecsmnodecount
except AttributeError:
    _fn_undefined.append('DemandCodes')
    _fn_undefined.append('demand codes table getter')
    getcodescount = _ret_errstat

#****k* Iterators/DemandCodes
# SYNTAX
#   for code, demand, nodecount in DemandCodes():
# RESULT
#   Returns each demand code and node count in turn:
#   * string code: demand code
#   * float demand: total demand value for the code
#   * int count: node count associated with the code
# REMARK
#   * DemandCodes requires version 2016 or higher of Piccolo/Ganessa dll
# HISTORY
#   Added 11/09/2015
#****
# Iterators for browsing demand codes and values for a given node
class DemandCodes(object):
    '''Iterator for demand codes, total nominal demand and node count
    Added 150911'''
    def __init__(self, used_only=False):
        self.used_only = used_only
        self.nbc = getcodescount(used_only)
    def __iter__(self):
        return self
    def next(self):
        if self.nbc <= 0:
            raise StopIteration
        self.nbc -= 1
        code, csm, nbn, lnc = _ganessa.nextcodecsmnodecount()
        return (code[0:lnc], csm, nbn) if lnc > 0 else ('', 0.0, 0)

#****k* Iterators/Table
# SYNTAX
#   for item, objcount in Table(table, typelt):
# ARGUMENTS
#   * string table: requested table (2 char symbol or table name)
#   * int typelt: type of element (LINK or NODE), if table is ZN or ZP.
#     Defaults to LINK.
# RESULT
#   Returns each table entry and associated object count in turn:
#   * string item: table entry
#   * int objcount: node count associated with the code
# REMARK
#   * Table requires version 2015/12 or higher of Piccolo/Ganessa dll
#****
try:
    tablecount = _ganessa.tablecount
except AttributeError:
    _fn_undefined.append('Table')
    _fn_undefined.append('table entries getter')
    tablecount = _ret_errstat

class Table(object):
    '''Iterator for area, area2, material, nominald diameter etc. tables'''
    def __init__(self, table, typelt= LINK):
        self.table = table
        self.nbitems = tablecount(table, typelt)
    def __iter__(self):
        return self
    def next(self):
        if self.nbitems <= 0:
            raise StopIteration
        self.nbitems -= 1
        item, objcount, ln = _ganessa.nexttableentry()
        return (item[0:ln], objcount) if ln > 0 else ('', -1)

 #****f* Functions/tsdemand, tsdevice, tsdemandlen, tsdevicelen
# PURPOSE
#   * tsdemandlen: returns the number of values in the profile
#   * tsdevicelen: returns the number of values in the device state TS
#   * tsdemand: return the profile time series
#   * tsdevice: return the device state time series(boundary conditions)
# SYNTAX
#   * tslen = tsdemandlen(code)
#   * vec_tim, vec_val, len, mode = tsdemand(code)
#   * tslen = tsdevicelen(sid[, attr])
#   * vec_tim, vec_val, len, mode = tsdevice(sid [, attr] [, fixed_interval])
# ARGUMENTS
#   * string code: demand type of element
#   * string sid: device element ID
#   * string attr: pump attribute (speed or number of units) or ''
#   * float fixed_interval (optional): if present and > 0, return values at the give time step
# RESULT
#   * int tslen: number of values for the time serie (0 if none)
#   * float[] vec_tim: vector of instants in seconds
#   * float[] vec_val: vector of demand coefficients (not percentages) or settings
#    (for pumps: 0= off, 1 or higher= open/active)
#   * int mode: type of demand profile (<0 as time series, >0 based on time steps)
# REMARKS
#   * These functions require version 2016 or higher of Piccolo/Ganessa dll
#   * when the demand code or equipment does not exist or has no forcing TS associated,
#     the value (None, None, 0, 0) is returned.
#   * The demand coefficient for the demand type 'code' can be retrieved
#     as float(getvar('coefficient:' + code))
#   * A pump is shut off when the number of units running is 0, even if rotation speed is > 0.
# HISTORY
#   * 25.01.2017: added 'fixed_interval' parameter to tsdevide; changed return value to float
#
#****
try:
    tsdemandlen = _ganessa.demand_tslen
except AttributeError:
    _fn_undefined.append('tsdemand')
    tsdemandlen = _ret_errstat

def tsdemand(code):
    nbval = tsdemandlen(code)
    if nbval > 0:
        return _ganessa.demand_ts(code, nbval)
    else:
        return (None, None, 0, 0)

try:
    tsdevicelen = _ganessa.device_tslen
except AttributeError:
    _fn_undefined.append('tsdevice')
    tsdevicelen = _ret_errstat

def tsdevice(sid, attr= ' ', fixed_interval= 0.0):
    if fixed_interval > 0.0:
        tmin, tmax, nbval = _ganessa.tsinterv()
        nbval = int((tmax - tmin)/fixed_interval + 1.499999)
        del tmin, tmax
    else:
        nbval = tsdevicelen(sid, attr)
        fixed_interval = 0.0
    if nbval > 0:
        return _ganessa.device_ts(sid, nbval, fixed_interval, attr)
    else:
        return (None, None, 0, 0)

#****f* Functions/areas
# PURPOSE
#   * return areas associated with nodes/links
# SYNTAX
#   * area = areas(typelt, attr)
# ARGUMENTS
#   * int typelt: type of object (NODE or LINK)
#   * str attr (optional): area attribute to be returned (ZN or ZP). Default to 'ZN'
# RESULT
#   * counter area: dictionary of node/link counts by area
#   * str code: demand codes
# REMARKS
#   * The functions also return names
#   * See also the Demands(id) iterator
#****
def areas(typelt, attr= ''):
    areas = Counter()
    if typelt not in (NODE, LINK):
        return areas
    if not attr:
        attr = attrkeyword(60)      # ZN
    for i in range(1, _ganessa.nbobjects(typelt) + 1):
        item, n = _ganessa.nstrattr(typelt, i, attr)
        if n > 0:
            areas[item[0:n]] += 1
    return areas

#****f* Functions/getid
# PURPOSE
#   Returns the id of an element by type and index
# SYNTAX
#   id = getid(typelt, numelt)
# ARGUMENTS
#   * int typelt: type of element
#   * int numelt: index of element
# RESULT
#   string id: id of the element
# REMARKS
#   * Internal index starts with 1
#   * Internal index of an element may change after a simulation or
#     a modification of the model.
#****
def getid(typelt, numelt):
    eid, n = _ganessa.getid(typelt, numelt)
    return eid[0:n] if n > 0 else ''

#****f* Functions/getindex
# SYNTAX
#   num = getindex(typelt, id)
# ARGUMENT
#   int typelt: type of element
#   string id: ID of element
# RESULT
#   int num: index of element ID (starting at pos 1)
# HISTORY
#   new in 1.3.3
#****
try:
    getindex = _ganessa.geteltindex
except AttributeError:
    _fn_undefined.append('getindex')
    getindex = _ret_errstat

#****f* Functions/extrnodes
# PURPOSE
#   Returns the from and to node (indexes) form branch index
# SYNTAX
#   i_from, i_to = extrnodes(i_branch)
# ARGUMENTS
#   * int i_branch: index of the branch
# RESULT
#   * int i_from: index of from node
#   * int i_to:   index of to node
# REMARKS
#   * Internal indexes start with 1
#   * Internal index of an element may change after a simulation
#     or a modification of the model.
#****
extrnodes = _ganessa.extrnodes

# Get functions - time series (results and measurements)
try:
    hstepcount = _ganessa.hstepcount
except AttributeError:
    _fn_undefined.append('hstepcount')
    hstepcount = _ret_errstat
tslen = _ganessa.tslen
tsinterv = _ganessa.tsinterv
mslen = _ganessa.mslen
ms = _ganessa.ms
ts = _ganessa.ts

#****f* Functions/hstepcount, tslen, mslen, tsval, msval, tsvalbymts, tsinterv, refdate
# PURPOSE
#   * hstepcount: returns the number of user time steps
#   * tslen, mslen: return number of elements in the time serie
#   * tsval, msval: return the time series of results and measurements
#   * tsvalbymts: return the time series of results at measurement time steps
#     for a given element type, id and attribute
#   * refdate: return date corresponding to the beginning of simulation
# SYNTAX
#   * hsc = hstepcount()
#   * len = tslen()
#   * len = mslen(typelt, id, attr)
#   * vec_tim, vec_val, len = tsval(typelt, id, attr, [interval])
#   * vec_tim, vec_mes, len = msval(typelt, id, attr, [interval])
#   * vec_tim, vec_val, len = tsvalbymts(typelt, id, attr)
#   * tmin, tmax, len = tsinterv()
#   * sdate = refdate()
# ARGUMENTS
#   * int typelt: type of element
#   * string id: id of element
#   * string attr: attribute (data or result) for which value is requested
#   * float interval (optional): if present, requests the time serie
#     at given fixed interval in seconds
# RESULT
#   * int hsc: number of user time steps
#   * int len: number of values for the time serie
#   * float[] vec_tim: vector of instants in seconds
#   * float[] vec_val: vector of simulated results at the instants vec_tim
#   * float[] vec_mes: vector of measurements at the instants vec_tim
#   * float tmin and tmax: first (vec_tim[0]) and last (vec_tim[-1])
#     instants available in the result time series
#   * string sdate: date time at beginning of the simulation (iso format)
# REMARKS
#   * The time vector is identical for simulation results of all elements of all types ,
#     and can be much larger than the number of (user) time steps
#   * two consecutive instants in the time vector for simulation results may
#     be identical at time step boundaries, change status instants etc.
#   * Each element may have a different measurement time vector form the others
#   * Measurements time series may have different begin and end dates from results
#   * Add 'sdate' in order to get absolute date time
#   * hstepcount requires version 2016 or higher of Piccolo/Ganessa dll
# HISTOTY
#  12/12/2016 (1.5.1): bug fix when no simulation result available
#****
def tsval(typelt, sid, sattr, fixed_interval= 0.0):
    if fixed_interval > 0.0:
        tmin, tmax, nbval = _ganessa.tsinterv()
        nbval = int((tmax - tmin)/fixed_interval + 1.499999)
        del tmin, tmax
    else:
        nbval = _ganessa.tslen()
        fixed_interval = 0.0
    if nbval > 0:
        return _ganessa.ts(typelt, sid, sattr, nbval, fixed_interval)
    return (None, None, nbval)

def msval(typelt, sid, sattr, fixed_interval= 0.0):
    nbval = _ganessa.mslen(typelt, sid, sattr)
    if nbval <= 0:
        return (None, None, nbval)
    if fixed_interval > 0.0:
        t, v, nb = _ganessa.ms(typelt, sid, sattr, nbval)
        nbval = int((t[-1] - t[0])/fixed_interval + 1.499999)
        del t, v, nb
    else:
        fixed_interval = 0.0
    return _ganessa.ms(typelt, sid, sattr, nbval, fixed_interval)

def tsvalbymts(typelt, sid, sattr):
    nbval = _ganessa.mslen(typelt if _dll_version < 20141205 else -typelt, sid, sattr)
    if nbval > 0:
        return _ganessa.ts(-typelt, sid, sattr, nbval, 0.0)
    return (None, None, nbval)

def refdate():
    sdate, slen = _ganessa.refdate()
    return sdate[0:slen] if slen > 0 else ''

#****f* Functions/msmooth
# PURPOSE
#   Defines the smoothing constant for time series of measurements
# SYNTAX
#   msmooth(twidth)
# ARGUMENTS
#   twidth: characteristic time window for smoothing, in seconds
# REMARKS
#   * The smoothing algorithm is a convolution with exp(-(t/twidth)^2).
#   * Best results are expected when twidth is in the order of magnitude
#     or larger than the sampling interval.
#   * call msmooth(0.0) in order to cancel smoothing.
#****
def msmooth(twidth):
    # MESURE DT-LISSAGE xxx
    sval = str(twidth) if isinstance(twidth, numbers.Number) else twidth
    _ganessa.gencmd(M.MES.ROOT, M.MES.SMOOTH, M.NONE, sval)
    _ganessa.gencmd(M.COM.ROOT, M.NONE)
    _ganessa.commit(0)

#****f* Functions/linkXYZV, branchXYZV
# PURPOSE
#   Returns the XYZ polyline representing a link, and eventually
#   an additional node attribute
# SYNTAX
#   * vec_x, vec_y, vec_z, vec_v, len = linkXYZV(id, [attr], [include_depth])
# ARGUMENTS
#   * string id: id of element
#   * string attr: optional attribute for which value is requested
#   * bool include_depth: optional attribute, defaults to False
# RESULT
#   * int len: number of points for the polyline
#   * double[] vec_x, vec_y: vector of coordinates
#   * float[] vec_z: vector of interpolated elevations (minus depth if include_depth= True)
#   * float[] vec_v: vector of interpolated attribute
# HISTORY
#   optional argument include_depth introduced in 1.4.2 (160908)
# REMARKS
#   * Z and V are interpolated from initial and final nodes
#   * if attribute is missing or not recognised vec_v is null.
#   * if the link has no vertice, len=2 and the function returns values
#     from ending nodes
#   * if the id does not exists the return value is (None, None, None, None, 0)
#   * branchXYZV is a synonym of linkXYZV.
#****
try:
    _linkxyzdv = _ganessa.branchxyzdv
except AttributeError:
    _linkxyzdv = _ganessa.branchxyzv
    _fn_undefined.append('linkXYZV(use_depth= True)')

def linkXYZV(sid, sattr= '--', include_depth= False):
    nbval = _ganessa.branchxylen(sid)
    if nbval > 0:
        _func = _linkxyzdv if include_depth else _ganessa.branchxyzv
        return _func(sid, sattr, nbval)
    else:
        return (None, None, None, None, 0)
branchXYZV = linkXYZV

#****f* Functions/nodeXYZ
# PURPOSE
#   Returns the XYZ coordinates and depth of a node
# SYNTAX
#   * x, y, z, dz = nodeXYZ(id)
# ARGUMENTS
#   * string id: id of element
# RESULT
#   * double x, y: coordinates
#   * float z, dz: elevation and depth
# REMARKS
#   * nodeXYZ requires version 2016 or higher of Piccolo/Ganessa dll
#   * if the id does not exists the return value is (None, None, None, None)
#   * In most cases dz is 0.0
#****
try:
    nodeXYZ = _ganessa.nodexyz
except AttributeError:
    _fn_undefined.append('nodeXYZ')
    nodeXYZ = lambda sid : (0.0, 0.0, 0.0, 0.0)

#****f* Functions/dist2link
# PURPOSE
#   Returns the distance and curvilinear abcissae of a point from the given link
# SYNTAX
#   * d, s1, s2 = dist2link(id, x, y)
# ARGUMENTS
#   * string id: id of link element
#   * double x, y: coordinates of the point
# RESULT
#   * double d: distance of the point to the link polyline
#   * double s1, s2: curvilinear distance of the projection from each extremity
# HISTORY
#   introduced in 1.3.7 (160706)
# REMARKS
#   * dist2link requires version 2016b or higher of Piccolo/Ganessa dll;
#     if not a pure python calculation is made using linkXYZV
#   * the polyline length is s1 + s2;
#     s1= 0 or s2= 0 when the point projection is outside the polyline
#   * if the id does not exists the return value is (-1, -1, -1)
#****
try:
    dist2link = _ganessa.distlink
except AttributeError:
    # _fn_undefined.append('dist2link')
    def dist2link(sid, x, y):
        xs, ys, zs, vs, nseg = linkXYZV(sid)
        if nseg:
            return dist_to_poly(x, y, nseg, xs, ys)
        else:
            return -1, -1, -1

#****f* Functions/defcalind, getcalind
# PURPOSE
#   Compute and return calibration indicators
# SYNTAX
#   * defcalind(br_threshold, no_threshold, rsv_threshold)
#   * val, ival = getcalind(typelt, numelt)
# ARGUMENTS
#   * br_*** : thresholds for computing indicators
#   * int typelt: type of element
#   * string id: id of element
# RESULT
#   val:  percentage of values below threshold
#   ival: indicator rank, from 1 (best) to 4 (worse) (-1 if not defined)
# REMARK
#   defcalind actually compute all indicators; getcalind returns them.
#****
def defcalind(br_threshold= 0.1, no_threshold= 0.2, rsv_threshold= 0.5):
    _ganessa.defcalind(br_threshold, no_threshold, rsv_threshold)

getcalind = _ganessa.getcalind


#****f* Functions/getvar, getunitname
# PURPOSE
#   Returns the value of a Piccolo expression or variable
# SYNTAX
#   * str_val = getvar(expression)
#   * str_val = getunitname(attr)
# ARGUMENTS
#   * string expression: the expression or variable to be returned
#   * string attr: attribute
# RESULT
#   string str_val: a string containing the expected value
# REMARK
#   Unit coefficient of a given attribute can be returned with
#   the adequate getvar('unite.'+attr) .
#****
def getvar(varname):
    sval, slen = _ganessa.getvar(varname)
    return sval[:slen]

def getunitname(attr):
    sval, slen = _ganessa.getunit(attr)
    return sval[:slen]

#****f* Functions/getall, getallminmax
# PURPOSE
#   * getall returns the value for all objects of the given type
#   * getallminmax returns the min, max, average and mindate, maxdate
#     for all objects of the given type
# SYNTAX
#   * vect = getall(typelt, attr)
#   * vec_min, vec_max, vec_avg, vec_tmin, vec_tmax = getallminmax(typelt, attr)
# ARGUMENTS
#   * int typelt: type of element (LINK, NODE, TANK)
#   * string attr: attribute (result) for which value is requested
# RESULT
#   * float[] vec_min, vec_max, vec_avg: min, max and avg values for all elements
#   * float[] vec_tmin, vec_tmax: vector of instants where the min, max value is reached
# REMARKS
#   getall(typelt, attr): when typelt =1 (links), attr can be either a regular attribute
#   ('Q', 'V', 'D', etc.) or a node-based attribute such as 'P:M' for mean pressure,
#   'P:G' for geometric mean, 'P:N' for min and 'p:X' for max.
#****
def getall(typelt, sattr):
    nbval = _ganessa.nbobjects(typelt)
    if nbval > 0:
        return _ganessa.getall(typelt, sattr, nbval)
    else:
        return None

def getallminmax(typelt, sattr):
    nbval = _ganessa.nbobjects(typelt)
    if nbval > 0:
        return _ganessa.getallminmax(typelt, sattr, nbval)
    else:
        return (None, None, None, None, None)

#****k* Iterators/getMinMax
# PURPOSE
#   Returns the id, min, max, avg value reached by the attribute for each object
#   of the given type or selection in turn
# SYNTAX
#   for id, vmin, vmax, vavg in getMinMax(typelt or selection, sattr):
# ARGUMENT
#   * int typelt: type element constants BRANCH, NODE, RESERVOIR
#   * string selection: name of a selection
#   * string attr: attribute (result) for which value is requested
# RESULT
#   id, vmin, vmax, vavg: element id, minimum, maximum and average values
#   for the attribute over the simulation
#****
class getMinMax(object):
    def __init__(self, typelt_sel, sattr):
        self.attr = sattr
        if isinstance(typelt_sel, numbers.Number):
            self.type = typelt_sel
            self.nbmax = _ganessa.nbobjects(self.type)
            self.select = range(1, self.nbmax + 1)
        elif isinstance(typelt_sel, basestring):
            self.nbmax, self.type = selectlen(typelt_sel)
            if self.nbmax > 0:
                self.select = _select(self.nbmax)
        else:
            raise TypeError
        nbelem = _ganessa.nbobjects(self.type)
        if self.nbmax > 0:
            self.vmin, self.vmax, self.avg, tmin, tmax = _ganessa.getallminmax(self.type, sattr, nbelem)
            del tmin, tmax
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if self.index >= self.nbmax:
            if self.nbmax > 0:
                del self.vmin, self.vmax, self.avg, self.select
                self.nbmax = 0
            raise StopIteration
        # returns fortran index (from 1)
        numelt = self.select[self.index]
        (elem, ls) = _ganessa.getid(self.type, numelt)
        # np.array index
        numelt -= 1
        vmin, vmax, vmoy = self.vmin[numelt], self.vmax[numelt], self.avg[numelt]
        self.index += 1
        return (elem[0:ls], vmin, vmax, vmoy)

#****k* Iterators/Unstable
# PURPOSE
#   Provide access to the list of elements which status cannot be determined
#   thus causing a simulation not converge.
# SYNTAX
#   for item, typelt in Unstable():
# ARGUMENTS
#   none
# RESULT
#   Returns each unstable element in turn:
#   * string item: element ID
#   * int typelt: element type
# REMARK
#   * Unstable requires version 2016 (160118) or higher of Piccolo/Ganessa dll
# HISTORY
#   new in 1.3.2
#****
try:
    unstablecount = _ganessa.unstablecount
except AttributeError:
    _fn_undefined.append('Unstable')
    _fn_undefined.append('unstable getter')
    unstablecount = _ret_errstat

class Unstable(object):
    '''Iterator ustable items during a simulation'''
    def __init__(self):
        self.nbitems = unstablecount()
    def __iter__(self):
        return self
    def next(self):
        if self.nbitems <= 0:
            raise StopIteration
        self.nbitems -= 1
        item, typelt, ln = _ganessa.nextunstableentry()
        return (item[0:ln], typelt) if ln > 0 else ('', 0)

#****f* Functions/save, savemodel
# SYNTAX
#   * istat = save(fname [, version])
#   * istat = savemodel(fname [, version])
# ARGUMENTS
#   * string fname: file name to save to
#   * string version: optional version string "x.yz" for writing compatible file format,
#     for text file only.
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   * 'save' uses the same procedure as Piccolo MMI.
#   * 'savemodel' is pure python and produces the same hydraulic content;
#     exotic options and cost data are not saved.
#   * If filename ends with '.bin' then data is saved as binary. Otherwise data is
#     saved as text (.dat mode) file.
#   * If the useException mode is set, any error will raise GanessaError exception.
#****
def _save_kw_command():
    # SAVE TEXT COMM
    _ganessa.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.TEXT)
    _ganessa.gencmd(M.COM.ROOT, M.NONE, extmode= 1)

def save(fname, version= ''):
    return _ganessa.savefile(fname, version)

def savemodel(fname, version= None):
    # First close opened file if any
    _ganessa.gencmd(M.COM.ROOT, M.NONE)
    _ganessa.gencmd(M.GEN.ROOT, M.GEN.CLOSE)

    fwq = winstr(quotefilename(fname))
    if fname.lower().strip('"\'').endswith('.bin'):
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.OPEN, DICT.BINARY, fwq)
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.DATA)
    else:
        if version:
            _ganessa.gencmd(M.GEN.ROOT, M.GEN.COMPAT, M.NONE, version)
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.OPEN, DICT.DATA, fwq)
        for module in ('NOD', 'BRA', 'RSV', 'DYN', 'LAB', 'MES', 'SIM'):
            _ganessa.gencmd(M.GEN.ROOT, M.GEN.SAVE)
            _ganessa.gencmd(getattr(M.ROOT, module), M.NONE, extmode= 1)
        # singularities and wording
        _save_kw_command()
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _ganessa.gencmd(-M.BRA.ROOT, M.BRA.SING, extmode= 1)
        _save_kw_command()
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.WORDING, extmode= 1)
        _save_kw_command()
        # Quality at the end, in case option not available
        _ganessa.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _ganessa.gencmd(M.QUA.ROOT, M.NONE, extmode= 1)
        # _ganessa.gencmd(M.GEN.ROOT, M.GEN.EOF, extmode= 1)
    # Close and commit
    _ganessa.gencmd(M.GEN.ROOT, M.GEN.CLOSE)
    istat = _ganessa.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(9, istat, 'Error while saving model')
    return istat

#****f* Functions/addSHLtype, addSHL, updateSHL, delSHL
# PURPOSE
#   * addSHLtype: Add / modify a single head losses (SHL) from the SHL table
#   * addSHL, updateSHL, delSHL: Add / modify / delete single head losses (SHL)
#     objects for a given pipe
# SYNTAX
#   * istat = addSHLtype(shltype, values [, comment])
#   * istat = addSHL(id, shltype, nb)
#   * istat = updateSHL(id, shltype, nb)
#   * istat = delSHL(id [, shltype])
# ARGUMENTS
#   * string shltype: type of shl to be added/modified
#   * float values: direct and reverse SHL coefficients
#   * string comment: long name of the SHL type
#   * string id: id of pipe
#   * int nb: number of SHL of type shltype to be added / updated with
# RESULT
#   int istat: error status (0 if OK)
# COMMENTS
#   If shltype is not given or is '' for delSHL then all SHL are removed from pipe.
# REMARK
#   * these functions require version 2015/12 or higher of Piccolo/Ganessa dll
#****
try:
    setdensity = _ganessa.setdensity
    def addSHLtype(shltype, values, comment=' '):
        _ganessa.addshlentry(shltype, values, comment)
    addSHL = _ganessa.addsingleshl
    updateSHL = _ganessa.updatesingleshl
    def delSHL(sid, shlid=''):
        _ganessa.removeshl(sid, shlid)
except AttributeError:
    _fn_undefined.append('setdensity')
    _fn_undefined.append('SHL getter and setter')
    setdensity = _ret_errstat
    addSHLtype = _ret_errstat
    updateSHL = _ret_errstat
    delSHL = _ret_errstat

#****f* Functions/setlinkattr, setbranchattr
# SYNTAX
#   * istat = setlinkattr(id, attr, val)
#   * istat = setbranchattr(id, attr, val)
# ARGUMENTS
#   * string id: id of element
#   * string attr: attribute (data or result) to be set to val
#   * float val: new value for attr
# RESULT
#   int istat: error status:
#   * 0 if OK
#   * 1 if the attribute is not defined for the type of link
#   * -1 if the attribute is not recognised
#   * -2 if the link does not exist
# REMARKS
#   * setbranchattr requires version 2015/12 or higher of Piccolo/Ganessa dll
#   * setlinkattr is a synonym that has been introduced as 22/09/2016
#****
try:
    setbranchattr =  _ganessa.setbranchattrbyid
except AttributeError:
    _fn_undefined.append('setbranchattr')
    setbranchattr = _ret_errstat
setlinkattr = setbranchattr

#****f* Functions/inv_summary
# SYNTAX
#   * iter, iter100, fobjmin, fobj100, fobj0, flambda = inv_summary()
# ARGUMENTS
#   none
# RESULT
#   * int iter: number of iterations
#   * int iter100: number of iterations required to get 1.01 * min
#   * float fobjmin: minimum value of misfit function
#   * float fobj100: misfit function at iteration iter100
#   * float fobj0: misfit function before fitting
#   * float flambda: Levenberg-Marquardt multiplier
# REMARK
#   * inv_summary requires version 2016 (160309) or higher of Piccolo/Ganessa dll
# HISTORY
#   new in 1.3.4
#****
try:
    inv_summary = _ganessa.inv_summary
except AttributeError:
    _fn_undefined.append('inv_summary')
    inv_summary = _ret_errstat

#****f* Functions/symmetric_node
# SYNTAX
#   ids = symmetric_node(sid)
# ARGUMENTS
#   string sid: node ID for which the symmetric (counterpart node on the other circuit) is looked for
# RESULT
#   * string sid: id of the counterpart node. '' if not found.
# REMARKS
#   * always returns '' with Piccolo/Ganessa_SIM
#   * the counterpart can be found only if the hot and cold circuits are almost symmetric
#   * symmetric_node requires version 2016B (160511) or higher of Picalor/Ganessa TH dll
# HISTORY
#   new in 1.3.6
#****

try:
    _symmetric_node = _ganessa.symmetric_node
except AttributeError:
    _fn_undefined.append('symmetric_node')
    symmetric_node = lambda x: ''
else:
    del _symmetric_node
    def symmetric_node(sid):
        sids, ln = _ganessa.symmetric_node(sid)
        return sids[0:ln]

#****f* Functions/stat_quantiles, stat_duration
# PURPOSE
#   stat_quantiles and stat_duration returns stat info associated with result TS
#   of a given attribute for all elements in a selection.
# SYNTAX
#   * quantiles = stat_quantiles(sel, attr, qtl)
#   * duration = stat_duration(sel, attr, sop, threshold)
# ARGUMENTS
#   * string sel: selection of elements for which stats are expected
#   * string attr: attribute over which the stat is computed
#   * float iterable qtl: quantiles to be computed (0 <= qtl[i] <= 1)
#   * string sop: comparison operator '<' or '>'
#   * float threshold: comparison threshold (expressed in attribute unit)
# RESULT
#   * float[:,:] quantiles: 2-dim array of quantiles - shape (#sel, #qtl).
#     quantiles[i] is the array of quantiles for the element in position i;
#     quantiles[:, k] is the array of quantile qtl[k] for all elements
#   * float[:] duration: array of cumulated duration (att sop threshold) - shape (#sel, ).
#   The functions return an empty list if the selection or qtl is empty .
# EXAMPLE
#   * cd = stat_duration('branch (d > 500) end', 'V', '>', 0.7)
#   * qtl = stat_quantiles('branch (d > 500) end', 'V', [0.5, 0.95, 1.0])
#     will return median, 95% quantile and maximum for velocity.
# REMARK
#   Allowed attributes are:
#   * links: flow (Q), velocity (V), head loss (PC / HL), gradient (GR)
#   * nodes: Head (HH / CH), pressure (P) and pipe pressure (PP)
#   * tanks: level (NC / CL), height (H), volume (CV / VC), volume percentage (V%),
#     flow (Q), filling flow (IQ / QR), draught flow (OQ / QV),
#   * all: water quality attributes T, C0 ... C9.
#   See also: getallminmax, getMinMax, Dynamic_stats
# HISTORY
#   new in 1.5.0 (161124) - should be compatible with 2016b kernel.
#****

try:
    _tmp_ = _ganessa.stat_quantiles
except AttributeError:
    _fn_undefined.append('stat_quantiles')
    _fn_undefined.append('stat_duration')
    stat_quantiles = _ret_errstat
    stat_duration = _ret_errstat
else:
    del _tmp_
    def stat_squantiles(sel, attr, qtl):
        if len(qtl) > 0:
            nb, typelt = selectlen(sel)
            # vqtl = numpy.array(qtl).astype(numpy.float32, order='F')
            if nb > 0:
                ret = _ganessa.stat_squantiles(sel, attr, nb, qtl)
                return ret
        return []
    def stat_quantiles(sel, attr, qtl):
        if len(qtl) > 0:
            nb, typelt = selectlen(sel)
            if nb > 0:
                bufsel = _select(nb)
                ret = _ganessa.stat_quantiles(typelt, attr, qtl, bufsel, nb)
                # vqtl = numpy.array(qtl).astype(numpy.float32, order='F')
                return ret
        return []
    def stat_sduration(sel, attr, sop, threshold):
        nb, typelt = selectlen(sel)
        ret = _ganessa.stat_sduration(sel, attr, sop, threshold, nb) if nb > 0 else []
        return ret
    def stat_duration(sel, attr, sop, threshold):
        nb, typelt = selectlen(sel)
        if nb > 0:
            bufsel = _select(nb)
            ret = _ganessa.stat_duration(typelt, attr, sop, threshold, bufsel, nb)
            return ret
        return []

#****k* Iterators/Dynamic_Stats
# PURPOSE
#   Iterator which returns stat info associated with result TS
#   of a given attribute for all elements in a selection in turn.
# SYNTAX
#   for id, retval in Dynamic_Stats(sel, attr [, quantile= qtl] [, duration= (sop, threshold)]):
# ARGUMENT
#   * string sel: selection
#   * string attr: attribute
#   * float iterable qtl: quantiles to be computed (0 <= qtl[i] <= 1)
#   * string sop: comparison operator '<' or '>'
#   * float threshold: comparison threshold (expressed in attribute unit)
# RESULT
#   Returns the id and type of each element in the selection in turn:
#   * string id: id of the next element in the selection
#   * retval: result of the requested stat.
#   The return value depends on the input parameters:
#   * if duration= (sop, threshold) is present, returns the cumulated duration for which attribute (sop) threshold.
#   * if not, if quantile= qtl is present, returns a numpy array of the quantiles for the element id.
#   * without duration and quantile keywords, the return value is [minval, maxval, avg] over the result TS.
# REMARK
#   See also getallminmax, stat_quantiles, stat_duration, getMinMax
# HISTORY
#   new in 1.5.0 (161124) - should be compatible with 2016b kernel.
#****
# Iterators for browsing model elements
class Dynamic_Stats(object):
    def __init__(self, sel, attr, quantiles= None, duration= None):
        nb, typ = selectlen(sel)
        self.nbmax, self.type = nb, typ
        if self.nbmax > 0:
            sbuf = _select(self.nbmax)
            self.select = sbuf
            if duration is not None:
                sop, threshold = duration
                self.values = _ganessa.stat_duration(typ, attr, sop, threshold, sbuf, nb)
            elif quantiles is not None:
                self.values = _ganessa.stat_quantiles(typ, attr, quantiles, sbuf, nb)
            else:
                nobj = _ganessa.nbobjects(typ)
                vmin, vmax, avg, tmin, tmax = _ganessa.getallminmax(typ, attr, nobj)
                del tmin, tmax
                vbuf = sbuf - 1
                self.values = numpy.array([vmin[vbuf], vmax[vbuf], avg[vbuf]]).transpose()
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if self.index >= self.nbmax:
            if self.nbmax > 0:
                del self.select
                del self.values
                self.nbmax = 0
            raise StopIteration
        numelt = self.select[self.index]
        elem, ls = _ganessa.getid(self.type, numelt)
        value = self.values[self.index]
        self.index += 1
        return (elem[0:ls], value)
    def len(self):
        return self.nbmax

#****o* Classes/Graph, extrnodes, adjlinks, propagate
# SYNTAX
#   graph = Graph()
# METHODS
#   * from_n, to_n = graph.extrnodes(alink): returns the from and to nodes of a link
#   * linkset = graph.adjlinks(anode): returns a set of adjacent links
#   * links, nodes = graph.propagate(anode[, maxlen= -1]):
#     returns the sets of links and nodes connected to 'anode' by a path of max length 'maxlen'
# HISTORY
#   new in 1.3.7 (160706)
#   reviewed 1.7.6 (170620): use attrkeyword() for IN and FN
#****
class Graph(object):
    '''Dual node/link representation for in depth propagation'''  
    def __init__(self):
        KWNI = attrkeyword(5)   # initial node
        KWNF = attrkeyword(6)   # final node
        self.nodes = {n:set() for n in Nodes()}
        self.edges = {a:(linkattrs(a, KWNI), linkattrs(a, KWNF)) for a in Links()}
        for a, nn in self.edges.iteritems():
            for n in nn:
                self._addtonode(n, a)

    def extrnodes(self, alink):
        return self.edges[alink]

    def adjlinks(self, anode):
        return self.nodes[anode]

    def _addtonode(self, n, a):
        try:
            self.nodes[n].add(a)
        except KeyError:
            self.nodes[n] = {a}

    def add(self, link, nodes):
        if isinstance(link, basestring) and isinstance(nodes, tuple):
            self.edges[link] = nodes
            for n in nodes:
                self._addtonode(n, link)

    def remove(self, link):
        for n in self.edges[link]:
            self.nodes[n].remove(link)  # discard for error tolerance
        del self.edges[link]

    def propagate(self, rootnode, maxlen= -1):
        '''Finds links / nodes connected to the root up to the given depth'''
        edges = set()
        nodes = {rootnode}
        border_nodes = {rootnode}
        while maxlen and border_nodes:
            maxlen -= 1
            border_edges = set()
            for n in border_nodes:
                border_edges.update(self.nodes[n])
            edges.update(border_edges)
            border_nodes = {n for a in border_edges for n in self.edges[a] if n not in border_nodes}
            nodes.update(border_nodes)
        return edges, nodes

### Print functions not avaiable due to obsolete version of dll ###

if _fn_undefined:
    print('Warning: the following functions and iterators are not compatible with this version of', _dll_name, ':')
    nuf, duf = len(_fn_undefined), 5
    for k in range(0, nuf, duf):
        print('   ', ', '.join(_fn_undefined[k:min(k+duf,nuf)]))
    del nuf, duf

#**#**f* Functions/getcluster
# PURPOSE
#   Computes and returns the index of the nearest node in the selection,
#   as cumulated path relative to the given attribute.
# SYNTAX
#   vec_idx = getcluster(sname [, attr] [, copybuf])
# ARGUMENTS
#   * string sname: name of selection
#   * string attr (optional): attribute used for weighing links (expected L, XX, YY, ZZ, RH/HD).
#     Defaults to RH/HD
#   * string copybuf (optional): the result is also copied on node attribute copybuf.
#     Valid arguments are '', 'XX', 'YY' or 'ZZ'.
# RESULT
#   int vec_idx[]: vector of the nearest root node. 0 means that the node is not
#   connected to the root selection.
# HISTORY
#   introduced and aborted in 1.3.3
# REMARK
#   if sname is a link or tank selection, it is converted to a node selection.
#****
#try:
#    _tmp = _ganessa.getcluster
#except AttributeError:
#    print('getcluster function not defined in this version of', _dll_name)
#    getcluster = _ret_errstat
#else:
#    def getcluster(sname, attr= ' ', copybuf= ' '):
#        return _ganessa.getcluster(sname, attr, copybuf.upper(), _ganessa.nbobjects(NODE))

def help():
    print("""
 The import of ganessa module will automatically initialise Ganessa_SIM.dll
 The session should be properly terminated by calling "closepic()".
    """)

    print('\n The following functions allow to buid and/or execute commands\n')
    print(_ganessa.cmd.__doc__)
    print(_ganessa.gencmd.__doc__)
    print('\n "cmdfile(fname)"\n    allows to open a .pic or .dat file\n')
    print(_ganessa.cmdfile.__doc__)
    print("""
 "reset()"
    removes all model objects.
    Call 'reset()' before 'cmdfile(fname)' when reading a new model.

 "loadbin(fname)"
    loads a .bin file.

 "full_solveH()"
    runs the full EPS hydraulic simulation in a safe way, and
    automatically loads the result file - default or customised.

 "loadres()"
    loads the default 'result.bin' file from working dir.
    Loading a binary file implicitely resets before loading.

 "browseH(time_or_str)"
    loads the hydraulic results for all model objects at the given time.
    time may either be a number of seconds or a hh:mm:ss string

 "browseWQ(time_or_str)"
    loads the hydraulic and WQ results for all model objects at the given time.
    time may either be a number of seconds or a hh:mm:ss string
    """)

    print("""
 "Branches()", "Nodes()", and "Reservoirs()"
    are iterators on the three types of elements: "BRANCH", "NODE"
    and "RESERVOIR" (or "TANK").

 "branchattr", "nodeattr" and "rsvattr"
    allow to retrieve numerical attributes
 "branchattrs", "nodeattrs"
    allow to retrieve alphanumerical attributes.
 "getid" retrieves model object id by type and index
    """)
    print(_ganessa.branchattr.__doc__)
    print(_ganessa.nodeattr.__doc__)
    print(_ganessa.getid.__doc__)

    print("""
 The following functions allow to retrieve the length of result time series
 or measurement series from a given type of element, id, and attribute.
 Note that result time series are all the same length.
    """)
    print(_ganessa.tslen.__doc__)
    print(_ganessa.tsinterv.__doc__)
    print(_ganessa.mslen.__doc__)
    print("""
 The following functions 'ts', 'tsval', 'ms', 'msval' allow to retrieve
 time series from a given type of element, id, and attribute.
 The optional argument can be used to retrieve fixed-interval data.

 CAUTION: the argument 'nbval' for 'ts' and 'ms' must be greater or equal
 than the length of the series otherwise the output will be truncated to 'nbval'.

 "tsval" and "msval" are python wrapping functions that call 'tslen' and 'mslen'
 for hiding and retrieving 'nbval' before passing to 'ts' and 'ms'.
    """)
    print(_ganessa.ts.__doc__)
    print('  vec_tim,vec_val,vec_len = tsval(typelt,sid,sattr,[fixed_interval])\n')
    print(_ganessa.ms.__doc__)
    print('  vec_tim,vec_val,vec_len = msval(typelt,sid,sattr,[fixed_interval])\n')
docs = help




