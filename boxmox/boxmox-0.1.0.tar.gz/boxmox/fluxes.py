#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyparsing as pp
import numpy as np

class FluxParser:

    def _init_reac_parser(self):

        #--------------------------------------------------
        # Format of reaction equation:
        # (factor) species + ... --> (factor) species + ...
        #--------------------------------------------------

        plus   = pp.Literal('+')  .suppress()
        arrow  = pp.Literal('-->').suppress()
        spec   = pp.Word( pp.alphanums+'_' ).setParseAction(lambda f: f[0].upper())
        factor = pp.Word( pp.nums+'.' ).setParseAction(lambda f: float(f[0]))

        spec_mem = pp.Optional(factor, default=1.0) + spec + pp.Optional(plus)

        self.reac_parser = pp.Group( pp.OneOrMore(spec_mem) ) + \
                           arrow                              + \
                           pp.Group( pp.OneOrMore(spec_mem) )

    def get (self, spec, min_flux_percentage=0.1, CFACTOR=2.596379e13):

        # Extract sink and source reactions:
        sinks, sources  = {}, {}
        reactants       = []
        for xkey,xvalue in self.rates.iteritems():

            xreac = self.reac_parser.parseString(xkey).asList()

            if spec in xreac[0]:
                sinks[xkey] = xreac
                for xspec in xreac[0]:
                    if type(xspec)==str:
                        reactants.append( xspec )

            elif spec in xreac[1]:
                sources[xkey] = xreac
                for xspec in xreac[0]:
                    if type(xspec)==str:
                        reactants.append( xspec )

            else:
                pass

        # Involved reactants of which concentration is needed:
        reactants = list( set( reactants ) )

        # Example for how to calculate chemical fluxes:
        #      Searched is the flux of species C in the following reaction:
        #      Reaction:  A + B -> 0.3C + 0.7D + 0.6E
        #      Flux    :  [A] * [B] * r * 0.3 = flux_C = 0.3*[C] * 0.7*[D] * 0.6*[E] * r
        #
        #      Where [x] denotes the concentration of x and r is the rate constant of the
        #      present reaction.
        #
        def calc_flux ( spec, reac, conc, rates ):

            flux = {}

            for xkey,xvalue in reac.iteritems():
                xflux = np.ones_like( rates[xkey], dtype=float ) * rates[xkey]

                for ispec in range(1,len(xvalue[0]),2):
                    # The concentrations in the files are ppmv
                    # CFACTOR -> concentrations in mlc/cm3.
                    # The rates are in e.g. cm3/mlc/s -> convert concentrations in
                    # mlc/cm3
                    xconc = conc[xvalue[0][ispec]][:] * CFACTOR
                    # Every species has its own factor (mostly 1.0):
                    xfac  = xvalue[0][ispec-1]

                    xflux *= (xconc**xfac)

                flux[xkey] =  xflux / CFACTOR

                # Divide by the CFACTOR to get the flux in ppmv/s instead of mlc/cm3/s:
                if spec in xvalue[0]:
                    flux[xkey] = -1.0 * xflux / CFACTOR   # sinks are negative
                elif spec in xvalue[1]:
                    # If the reaction is a source reaction the factor of the investigated
                    # species may not be 1.0 ...
                    flux[xkey] =  1.0 * xflux / CFACTOR * xvalue[1][xvalue[1].index(spec)-1]
                else:
                    raise IOError('species <{0:s}> not contained in reaction "{1:s}"'\
                                  .format(spec,xkey))

            return flux

        fluxes = calc_flux(spec,sinks,self.conc,self.rates)
        fluxes.update( calc_flux(spec,sources,self.conc,self.rates) )

        # Remove fluxes that account for less then <min_flux_percentage> of total net flux
        #print fluxes.values()
        netFlux_pos=0.0
        netFlux_neg=0.0

        for indx,val in enumerate(np.array(fluxes.values())[:,0]):
            netFlux_pos += np.sum( [x for x in np.array(fluxes.values())[indx,1:-1] if x>0.0]  )
            netFlux_neg += np.sum( [x for x in np.array(fluxes.values())[indx,1:-1] if x<0.0]  )

        without_negligible_fluxes = {}
        for xkey,xvalue in fluxes.iteritems():
            if np.sum(xvalue[1:-1]) < min_flux_percentage * netFlux_pos and np.sum(xvalue[1:-1]) > min_flux_percentage * netFlux_neg :
                pass
            else:
                without_negligible_fluxes[xkey] = xvalue

        return { 'species': spec, 'time': self.time, 'values': without_negligible_fluxes }

    def __init__(self, output):
        self.valid = False

        self.output = output

        self._init_reac_parser()

        # Output of single BOXMOX run:
        ratesObj    = self.output['Rates']
        self.time   = ratesObj.time
        self.rates  = ratesObj.rates

        self.conc   = self.output['Concentrations']

