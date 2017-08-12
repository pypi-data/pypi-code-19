import sys

def _plotExperimentParser():
    from argparse import ArgumentParser

    parser = ArgumentParser(description='BOXMOX experiment plotter.')
    parser.add_argument('species', type=str,
                       help='One or several (comma separated) species names to be plotted')
    parser.add_argument('-e', '--experimentPath', type=str, default="./",
                       help='Path to the experiment to be used. Defaults to current directory.')
    parser.add_argument('-f', '--outputFile', type=str, default='plot.png',
                       help='Name (or full path) of the output (png) file')
    parser.add_argument('--timeLimits', type=str, default=None,
                       help='Time axis limits (as "min,max") in time units.')

    return parser

def plotExperiment(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = _plotExperimentParser()

    args = parser.parse_args()

    import boxmox

    try:
        from . import ExperimentPlotter as ep
    except:
        import warnings
        warnings.warn("Plotting disabled - is matplotlib installed?")
        return

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    exp = boxmox.ExperimentFromExistingRun(args.experimentPath)
    tmin = tmax = None
    if not args.timeLimits is None:
        tmin = float(args.timeLimits.split(",")[0])
        tmax = float(args.timeLimits.split(",")[1])
    exp.plot(args.species.split(","), tmin=tmin, tmax=tmax)
    plt.savefig(args.outputFile)

