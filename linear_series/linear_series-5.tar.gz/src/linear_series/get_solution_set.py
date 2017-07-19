'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 6, 2016
@author: Niels Lubbes

The method "get_solution_set()" should be called 
from "LinearSeries.get_solution_set()".
'''

from class_ls_tools import LSTools

from sage_interface import sage_Combinations
from sage_interface import sage_gcd


def get_solution_set( ls ):
    '''
    INPUT:
        - "ls" -- Assumes that "ls.pol_lst" is a list of polynomials 
                  in two variables and that its zero-set is 0-dimensional.
        
    OUTPUT:
        - The number field of "ls.ring" is extended with roots in the zero-set. 
        - Returns zero-set of "ls.pol_lst". Thus the set of points on which 
          all polynomials in "ls.pol_lst" vanish.
    '''

    LSTools.p( 'input =', ls )

    if  len( ls.gens() ) != 2:
        raise Exception( 'Not implemented for polynomials in', ls.gens() )

    # Try all possible pairs of polynomials in pol_lst
    # until their resultant wrt. y is nonzero.
    xres = 0
    x, y = ls.gens()
    interval = range( len( ls.pol_lst ) )
    for i, j in sage_Combinations( interval, 2 ):
        xres = ls.ring.resultant( ls.pol_lst[i], ls.pol_lst[j], y )
        if xres != 0:
            break
    if xres == 0:
        if sage_gcd( ls.pol_lst ) != 1:
            raise ValueError( 'Expect gcd of "pol_lst" to be 1:', sage_gcd( ls.pol_lst ) )
        # TODO: handle this case as well.
        raise Exception( 'All pairs of polynomials in "pol_lst" have a common factor: ', ls.pol_lst )

    # extend number field with roots of resultant
    tres = str( xres ).replace( str( x ), 't' )
    ls.ring.ext_num_field( tres )
    ls.pol_lst = ls.ring.coerce( ls.pol_lst )
    xres = ls.ring.coerce( xres )
    x, y = ls.ring.gens()

    # factor resultant in linear factors
    fct_lst = ls.ring.factor( xres )

    # obtain candidates for x-coordinates of solutions
    xsol_lst = []
    for fct in fct_lst:
        xsol_lst += [ -fct[0].subs( {xres.variables()[0]:0} ) ]
    xsol_lst = list( set( xsol_lst ) )
    LSTools.p( xsol_lst )

    # find y-coordinate for each x-coordinate
    xysol_lst = []
    for xsol in xsol_lst:

        # substitute x-coord
        xsol = ls.ring.coerce( xsol )  # ring.num_field is changed during while loop
        ypol_lst = [ pol.subs( {x:xsol} ) for pol in ls.pol_lst]
        ypol_lst = [ ypol for ypol in ypol_lst if ypol != 0 ]
        ypol = ypol_lst[0]

        # extend number field with roots of polynomial in y
        tpol = str( ypol ).replace( str( y ), 't' )
        ls.ring.ext_num_field( tpol )
        ls.pol_lst = ls.ring.coerce( ls.pol_lst )
        ypol = ls.ring.coerce( ypol )
        ypol_lst = ls.ring.coerce( ypol_lst )
        x, y = ls.ring.gens()

        # obtain candidates for y-coordinates
        ysol_lst = []
        if ypol not in ls.ring.get_num_field():
            for fct in ls.ring.factor( ypol ):
                ysol_lst += [ -fct[0].subs( {ypol.variables()[0]:0} ) ]

        # check whether (xsol, ysol) is in the zero-set of "ls.pol_lst"
        for ysol in ysol_lst:
            lst = [ ypol.subs( {y:ysol} ) for ypol in ypol_lst ]
            if set( lst ) == {0}:
                xysol_lst += [( xsol, ysol )]

    xysol_lst = list( set( xysol_lst ) )
    LSTools.p( 'output =', xysol_lst )

    return xysol_lst
