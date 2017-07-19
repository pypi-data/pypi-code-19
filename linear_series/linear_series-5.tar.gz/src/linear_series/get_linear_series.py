'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 6, 2016
@author: Niels Lubbes

The method "get_linear_series()" should be called from "LinearSeries.get()".
'''

from class_ls_tools import LSTools
from class_poly_ring import PolyRing
import class_linear_series

from sage_interface import sage__eval
from sage_interface import sage_Compositions
from sage_interface import sage_matrix
from sage_interface import sage_vector


def get_ls_lst( ls, bp_lst ):
    '''
    Helper for "get_linear_series" method. 
    '''
    ind_str = None

    ls_lst = []
    for bp in bp_lst:

        if ind_str == None:
            ind_str = bp.depth * '\t'
            LSTools.p( ind_str + 'input  = len( bp_lst ):' + str( len( bp_lst ) ) + ',' + str( ls ) )

        # base points which do not have multiplicity at least
        # can be ignored
        #
        if bp.mult <= 0: continue
        LSTools.p( 'basepoint  = ' + str( bp )[1:].replace( '\n', '\n' + ind_str ) )

        # translate the base point to the origin
        #
        nls = ls.copy().translate_to_origin( bp.sol )
        LSTools.p( ind_str + 'translated =', nls )

        #
        # Loop through (a,b) s.t.
        # (a-1)+(b-1)=bp.mult-1 and (a-1)>=(b-1)>=0
        #
        for m in range( 1, bp.mult + 1 ):
            for a, b in sage_Compositions( m - 1 + 2, length = 2 ):
                ls_lst += [ nls.copy().diff( a - 1, b - 1 ) ]
                LSTools.p( ind_str + str( a - 1 ) + ',' + str( b - 1 ) + ',' + str( ls_lst[-1] ) )

        #
        # Continue recursively.
        #
        u, v = nls.gens()
        ls_lst += get_ls_lst( nls.copy().subs( {u:u * v} ).quo( v ** bp.mult ), bp.bp_lst_t )
        ls_lst += get_ls_lst( nls.copy().subs( {v:v * u} ).quo( u ** bp.mult ), bp.bp_lst_s )

    if ind_str != None:
        LSTools.p( ind_str + 'output =', [str( ls ) for ls in ls_lst] )

    return ls_lst


def get_mon_lst( deg, g_lst ):
    '''
    INPUT:
        - "deg"   -- An integer.
        - "g_lst" -- List of either 3 or 4 generators of a ring. 
    OUTPUT:
        - If "gens" consist of 3 generators then returns
          a list of all monomials in "gens" of degree "deg".
        - If "gens" consist of 4 generators then returns
          a list of all monomials in "gens" of bi-degree ("deg","deg").
    EXAMPLE:
        - get_mon_lst( 2, PolyRing('x,y,z').gens() )==[z^2, y*z, x*z, y^2, x*y, x^2]
        
        - get_mon_lst( 2, PolyRing('x,y,v,w').gens() )== [x^2*v^2, x^2*v*w, x^2*w^2, 
                                                          x*y*v^2, x*y*v*w, x*y*w^2, 
                                                          y^2*v^2, y^2*v*w, y^2*w^2] 
    '''

    mon_lst = []
    if len( g_lst ) == 4:
        x, y, v, w = g_lst
        for a, b, c, d in sage_Compositions( 2 * deg + 4, length = 4 ):
            if a + b == deg + 2 and c + d == deg + 2:
                mon_lst += [ x ** ( a - 1 ) * y ** ( b - 1 ) * v ** ( c - 1 ) * w ** ( d - 1 ) ]
    elif len( g_lst ) == 3:
        x, y, z = g_lst
        for a, b, c  in sage_Compositions( deg + 3, length = 3 ):
            mon_lst += [ x ** ( a - 1 ) * y ** ( b - 1 ) * z ** ( c - 1 ) ]
    else:
        raise ValueError( 'Expect either 3 or 4 generators:', g_lst )

    return mon_lst


def get_linear_series( deg, bp_tree ):
    '''
    INPUT:
        - "deg"     -- Integer representing the degree of polynomials.
        - "bp_tree" -- BasePointTree where base points might be in 
                       overlapping charts.
                       We require that "bp_tree.chart_lst" equals either 
                       ['z', 'x', 'y'] or ['xv', 'xw', 'yv', 'yw'].                       
    OUTPUT:
        - Return A LinearSeries "ls" with base points defined by "bp_tree".
          The polynomials in "ls.pol_lst" are either 
                  * homogeneous in (x:y:z) and of degree "deg" or          
                  * bi-homogenous in (x:y)(v:w) and of bi-degree ("deg","deg")
          Note that there might unassigned base points. 
    '''

    #
    # Obtain generators of polynomial ring from "bp_tree.chart_lst"
    # Note that for initializing PolyRing, it is important that the
    # base field is not reset to the rationals QQ. The input "bp_tree"
    # could already be defined over some extension field.
    #
    if bp_tree.chart_lst == ['z', 'x', 'y']:
        ring = PolyRing( 'x,y,z', False )
    elif bp_tree.chart_lst == ['xv', 'xw', 'yv', 'yw']:
        ring = PolyRing( 'x,y,v,w', False )
    else:
        raise ValueError( 'Expect "bp_tree.chart_lst" in ', ( ['z', 'x', 'y'], ['xv', 'xw', 'yv', 'yw'] ) )

    #
    # Obtain linear series defined by
    # monomials of degree "deg" or bidegree ("deg","deg").
    #
    mon_lst = get_mon_lst( deg, ring.gens() )
    LSTools.p( 'mon_lst =', mon_lst )
    ls = class_linear_series.LinearSeries( mon_lst, ring )

    #
    # For each chart "c" we obtain a list of linear series.
    #
    ls_lst = []
    for c in bp_tree.chart_lst:
        ls_lst += get_ls_lst( ls.copy().chart( c ), bp_tree[c] )

    #
    # Create matrix whose coefficients are obtained
    # by evaluating each polynomial in linear series
    # in "ls_lst" at (0,0).
    #
    row_lst = []
    for ls in ls_lst:
        LSTools.p( ls )
        for g in ls.ring.gens():
            ls.subs( {g:0} )
        row = sage__eval( str( ls.pol_lst ), PolyRing.num_field.gens_dict() )
        row_lst += [row]
    LSTools.p( 'matrix =', row_lst )

    #
    # Compute kernel.
    #
    kern = list( sage_matrix( row_lst ).right_kernel().matrix() )
    LSTools.p( 'kernel =', kern )
    LSTools.p( mon_lst )

    #
    # Obtain linear series from linear conditions on "mon_lst".
    #
    mon_lst = ring.coerce( mon_lst )  # update w.r.t. PolyRing.num_field
    kern = ring.coerce( kern )
    pol_lst = sage_matrix( kern ) * sage_vector( mon_lst )
    LSTools.p( pol_lst )

    return class_linear_series.LinearSeries( pol_lst, ring )


