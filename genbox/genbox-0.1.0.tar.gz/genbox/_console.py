import sys

def _makeEnvironmentParser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('tag'     , type=str  , help='FRAPPE_extract tag')
    parser.add_argument('--scaleFac', type=float, default=1.0,
                        help='scaling factor; default is 1.0')
    parser.add_argument('--diurnalCycle', action='store_true',
                        help='get an idealized diurnal temperature cycle')
    return parser

def makeEnvironment(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = _makeEnvironmentParser()

    args = parser.parse_args()

    import genbox.wrappers as b
    import frappedata.dataset as ds

    ds = ds.ExtractsDataset()
    ds_args = { 'tag' : args.tag }

    with open("Environment.csv", "w") as f:
        b.createEnvironment(ds, ds_args, args.scaleFac, args.diurnalCycle, f=f)

def _makeInitialConditionsParser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('tag'       , type=str  , help='FRAPPE_extract tag')
    parser.add_argument('mechanism' , type=str  , help='mechanism name'    )
    parser.add_argument('--scaleFac', type=float, default=1.0,
                        help='scaling factor; default is 1.0')
    parser.add_argument('--scaleSpec', type=str, default="none",
                        help='scaling species (comma-separated if several); default is none')
    return parser

def makeInitialConditions(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = _makeInitialConditionsParser()

    args = parser.parse_args()

    import genbox.wrappers as b
    import frappedata.dataset as ds
    import chemspectranslator

    ds = ds.ExtractsDataset()
    ds_args = { 'tag' : args.tag }

    # translator database
    translator  = chemspectranslator.Translator()

    with open("InitialConditions.csv", "w") as f:
        b.createInitialConditions(ds, ds_args, translator, args.mechanism, args.scaleFac, args.scaleSpec, f=f)

def _makePhotolysisRatesParser():
    from argparse import ArgumentParser
    parser = ArgumentParser('Generate "PhotolysisRates.csv" out of FRAPPE_extracts-files')
    parser.add_argument('tag'     , type=str  , help='FRAPPE_extract tag')
    parser.add_argument('--diurnalCycle', action='store_true',
                        help='get an idealized diurnal photolysis rates cycle'             )
    parser.add_argument('--scaleFac', type=float, default=1.0,
                        help='scaling factor for photolysis rates; default is 1.0'          )
    return parser

def makePhotolysisRates(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = _makePhotolysisRatesParser()

    args = parser.parse_args()

    import genbox.wrappers as b
    import frappedata.dataset as ds

    import tuv
    tuvdb = tuv.DB()

    ds = ds.ExtractsDataset()
    ds_args = { 'tag' : args.tag }

    with open("PhotolysisRates.csv", "w") as f:
        b.createPhotolysisRates(ds, ds_args, tuvdb, args.scaleFac, args.diurnalCycle, f=f)

