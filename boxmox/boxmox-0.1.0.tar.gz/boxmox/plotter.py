class ExperimentPlotter:
    '''
    Plotting routines for BOXMOX experiments.
    '''
    def _plottingTimes(self):
        ptimes = self.__times
        punit  = 'h'
        if (ptimes[-1] - ptimes[0]) < 1.0:
            ptimes *= 3600.0
            punit   = 's'
        return ptimes, punit

    def concentrations(self, specs, scaleFactors = 1e3, colorMap=None, tmin=None, tmax=None):
        '''
        Plot time series of concentrations.
        '''
        import numpy as np
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()

        if isinstance(specs, (str, unicode)):
            specs = [ specs ]

        nspecs = len(specs)

        if isinstance(scaleFactors, float):
            scaleFactors = [ scaleFactors for x in range(nspecs) ]

        ptimes, punit = self._plottingTimes()
        if tmin is None:
            tmin=ptimes[0]
        if tmax is None:
            tmax=ptimes[-1]

        if colorMap is None:
            colorMap = plt.cm.brg
        color=iter(colorMap(np.linspace(0,1,nspecs)))

        for scale, spec in zip(scaleFactors, specs):
            c=next(color)
            ax.plot(ptimes, self.__conc[spec] * scale, color=c, label=spec, linewidth=2)
        ax.set_xlabel('Time in '+punit)
        ax.set_xlim( tmin, tmax )

        ax.legend()

    def fluxes(self, spec, fig=None, ax=None, plot_legend=True,
               xlabel='Time in h', ylabel=r'Flux in ppbv h$^{-1}$', plabel=None):
        '''
        Plot time series of fluxes through a species.
        '''
        import numpy as np
        import matplotlib.pyplot as plt

        if fig is None:
            fig, ax = plt.subplots()

        flxs = self.__flxs.get(spec)

        times   = flxs['time']
        flx     = { x: flxs['values'][x] for x in flxs['values'].keys() if not x == 'time' }

        netflux = np.zeros(len(times))

        for xkey, xvalue in flx.iteritems():
            ax.plot(times, xvalue, label=xkey)
            netflux += np.array(xvalue)

        ax.plot(times, netflux, label="Net flux", lw=2, c='k')
        ax.plot(times, np.zeros(len(times)), lw=1, c='gray')

        ax.grid( alpha=0.5 )
        ax.set( xlim=(times[0],times[-1]), xlabel=xlabel, ylabel=ylabel)

        if not plabel is None:
            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()
            ax.text( xmin + 0.05 * (xmax - xmin), ymin + 0.95 * (ymax - ymin), plabel,
                     horizontalalignment='center', verticalalignment='center')

        if plot_legend:
            ax.legend(loc='top', fontsize="xx-small")

        return fig

    def __init__(self, output, fluxes):
        self.__conc = output['Concentrations']
        self.__flxs = fluxes
        self.__times = self.__conc['time']
