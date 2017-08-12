import sys

def _makeCyclingRunParser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('exp', type=str, help='experiment name')
    parser.add_argument('cfg', type=str, help='config file')
    return parser

def makeCyclingRun(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = _makeCyclingRunParser()

    args = parser.parse_args()

    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(args.cfg)

    import frappedata.dataset as frappe
    ds      = frappe.ExtractsDataset()
    ds_args = { 'tag': config.get('Global', 'case') }

    import tuv
    tuvdb = tuv.DB()

    import chemspectranslator
    translator  = chemspectranslator.Translator()

    from . import cycling as c
    exp_path = c.run( ds, ds_args, tuvdb, translator, args.exp , args.cfg )

    from . import helpers as h
    h.archive(exp_path, args.exp)


def _plotAssimDiagsParser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('exp', type=str, help='experiment name')
    parser.add_argument('cycle', type=str, help='cycle number')
    return parser


def plotAssimDiags(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = _plotAssimDiagsParser()

    args = parser.parse_args()

    import os
    import matplotlib.pyplot as plt

    try:
        from . import plotting as p
    except:
        import warnings
        warnings.warn("Plotting disabled - is matplotlib installed?")
        return

    beatbox_result_path = os.path.join(os.environ["BEATBOX_ARCHIVE_PATH"], args.exp, 'fcst_' + args.cycle, 'BEATBOX.p')

    p.scatter( beatbox_result_path )
    p.relative_to_NR( beatbox_result_path )
    p.skill_across_state( beatbox_result_path )

    plt.show()


def _plotTimeSeriesDiagsParser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('exp', type=str, help='experiment name')
    parser.add_argument('spec', type=str, help='chemical compound')
    return parser

def plotTimeSeries(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = _plotTimeSeriesDiagsParser()

    args = parser.parse_args()

    import os
    import matplotlib.pyplot as plt

    try:
        from . import plotting as p
    except:
        print("Plotting disabled - is matplotlib installed?")
        return

    exp_path = os.path.join(os.environ["BEATBOX_ARCHIVE_PATH"], args.exp)

    import chemspectranslator
    translator = chemspectranslator.Translator()

    p.cycling( translator, exp_path, args.spec )
    p.sensitivities ( exp_path )

    plt.show()

