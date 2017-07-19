'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 4, 2016
@author: Niels Lubbes

The method "get_bp_tree()" should be called from "LinearSeries.get_bp_tree()"
'''

from class_ls_tools import LSTools
from class_poly_ring import PolyRing
from class_base_points import BasePointTree
from class_base_points import BasePoint


def in_previous_chart( sol, chart ):
    '''
    We consider the following charts.
    
    * P^2(x:y:z) (projective plane). 
      There are 3 charts: x!=0, y!=0 and z!=0, 
      denoted by 'x', 'y' and 'z' resp.
      
    * P^1xP^1(x:y; v:w) (fiber product of projective line with itself).
      There are 4 charts: (x,v)!=(0,0), (x,w)!=(0,0), (y,v)!=(0,0) and (y,w)!=0,
      denoted by 'xv', 'xw', 'yv' and 'yw' respectively.      
    
    * A^2xP^1 (u,v; s:t) (fiber product of affine plane with projective line)
      There are 2 charts: s!=0 and t!=0, denoted by 's' and 't' resp.
      
    
    INPUT:
        - "sol"   -- Solution represented as a 2-tuple of elements 
                     in number field "PolyRing.num_field".
        - "chart" -- Chart over which solution is considered.
        
    OUTPUT:
        - Returns False if solution is already analyzed in a previous chart 
          and True otherwise.
    '''

    # sol = (a,b,mult)
    # Us --> Ut: (a,b)|-->(1/b,a*b)
    # Ut --> Us: (a,b)|-->(a*b,1/a)

    if chart == 't':
        return False
    elif chart == 's':
        return sol[1] != 0
    elif chart == 'z':  # sol=(x,y)
        return False
    elif chart == 'y':  # sol=(x,z)
        return sol[1] != 0
    elif chart == 'x':  # sol=(y,z)
        return sol[0] != 0 or sol[1] != 0
    elif chart == 'xv':  # sol=(y,w)
        return False
    elif chart == 'xw':  # sol=(y,v)
        return sol[1] != 0
    elif chart == 'yv':  # sol=(x,w)
        return sol[0] != 0
    elif chart == 'yw':  # sol=(x,v)
        return sol[0] != 0 or sol[1] != 0
    else:
        raise ValueError( 'chart =' + chart )


def get_bp_lst_chart( ls, chart, depth = 0 ):
    '''
    INPUT:
        - "ls"    -- LinearSeries.
        - "chart" -- A String representing the current chart 
                     of linear series "ls".  
        - "depth" -- Integer representing the recursive depth 
                     of this function call.
    OUTPUT:
        - Returns a list of BasePoint objects representing base points
          of linear series "ls".
    '''

    LSTools.p( 'input =', ( depth, chart, str( ls ) ) )

    nls = ls.copy()
    if chart == 's':
        nls.pol_lst = [ nls.ring.gens()[0] ] + nls.pol_lst
    elif chart == 't':
        nls.pol_lst = [ nls.ring.gens()[1] ] + nls.pol_lst

    sol_lst = nls.get_solution_set()

    bp_lst = []

    # if no solutions, add empty base point with BasePoint.mult=0.
    if sol_lst == []:
        bp_lst += [ BasePoint( depth, chart, ls ) ]

    for sol in sol_lst:

        bp = BasePoint( depth, chart, ls )
        bp.sol = sol

        if in_previous_chart( sol, chart ):

            bp.mult = -1  # this indicates that base point was already considered.

        else:

            ls_t, bp.mult = ls.copy().translate_to_origin( sol ).blow_up_origin( 't' )
            bp.bp_lst_t = get_bp_lst_chart( ls_t, 't', depth + 1 )

            ls_s, mult_s = ls.copy().translate_to_origin( sol ).blow_up_origin( 's' )
            bp.bp_lst_s = get_bp_lst_chart( ls_s, 's', depth + 1 )

            if bp.mult != mult_s:
                raise Exception( 'Unexpected multiplicities: (bp.mult, mult_s) =', ( bp.mult, mult_s ) )

        bp_lst += [ bp ]

    return bp_lst


def get_bp_tree( ls ):
    '''
    INPUT:
        - "ls" -- A LinearSeries. Its polynomials are 
                  either 
                      homogenous in (x:y:z) 
                  or
                      bi-homogenous in (x:y) and (v:w).
    OUPUT:
        - A BasePointTree representing the simple base points 
          and infinitely near base points of "ls".
    '''

    # create BasePointTree object
    g_set = set( [str( g ) for g in ls.gens()] )
    if g_set == set( ['x', 'y', 'v', 'w'] ):
        bp_tree = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    elif g_set == set( ['x', 'y', 'z'] ):
        bp_tree = BasePointTree( ['z', 'x', 'y'] )
    else:
        ValueError( 'Expect "ls.gens()" to be a subset of:', ['z', 'x', 'y', 'v', 'w'] )
    bp_tree.ls = ls

    # get base points for each affine plane chart of linear series
    for c in bp_tree.chart_lst:
        ls_c = ls.copy().chart( c )
        bp_tree[c] = get_bp_lst_chart( ls_c, c )

    return bp_tree





