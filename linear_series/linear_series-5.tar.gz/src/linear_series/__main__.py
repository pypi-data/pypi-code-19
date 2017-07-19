'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.

Created on Aug 6, 2016
@author: Niels Lubbes
'''

from class_ls_tools import LSTools
from class_poly_ring import PolyRing
from class_linear_series import LinearSeries
from class_base_points import BasePointTree

from sage_interface import sage_ZZ
from sage_interface import sage_QQ
from sage_interface import sage_invariant_theory
from sage_interface import sage__eval
from sage_interface import sage_PolynomialRing
from sage_interface import sage_matrix
from sage_interface import sage_diagonal_matrix
from sage_interface import sage_vector
from sage_interface import sage_SR
from sage_interface import sage_var
from sage_interface import sage_diff


def usecase__get_base_points__P2():
    '''
    We obtain (infinitely near) base points of a 
    linear series defined over a number field.
    '''
    ring = PolyRing( 'x,y,z', True )
    ring.ext_num_field( 't^2 + 1' )
    ring.ext_num_field( 't^3 + a0' )

    a0, a1 = ring.root_gens()
    x, y, z = ring.gens()

    pol_lst = [x ** 2 + a0 * y * z, y + a1 * z + x ]

    ls = LinearSeries( pol_lst, ring )
    LSTools.p( ls )

    bp_tree = ls.get_bp_tree()
    LSTools.p( bp_tree )


def usecase__get_base_points__P1P1():
    '''
    We obtain (infinitely near) base points of a 
    linear series defined by bi-homogeneous polynomials.
    Such polynomials are defined on P^1xP^1 (the fiber product 
    of the projective line with itself). 
    The coordinate functions of P^1xP^1 are (x:y)(v:w).
    '''

    pol_lst = [ '17/5*v^2*x^2 + 6/5*v*w*x^2 + w^2*x^2 + 17/5*v^2*y^2 + 6/5*v*w*y^2 + w^2*y^2',
                '6/5*v^2*x^2 + 8/5*v*w*x^2 + 6/5*v^2*y^2 + 8/5*v*w*y^2',
                '7/5*v^2*x^2 + 6/5*v*w*x^2 + w^2*x^2 + 7/5*v^2*y^2 + 6/5*v*w*y^2 + w^2*y^2',
                '4*v^2*x*y',
                '-2*v^2*x^2 + 2*v^2*y^2',
                '2/5*v^2*x^2 + 6/5*v*w*x^2 - 4*v^2*x*y - 2/5*v^2*y^2 - 6/5*v*w*y^2',
                '2*v^2*x^2 + 4/5*v^2*x*y + 12/5*v*w*x*y - 2*v^2*y^2' ]

    ls = LinearSeries( pol_lst, PolyRing( 'x,y,v,w' ) )
    LSTools.p( ls )

    bp_tree = ls.get_bp_tree()
    LSTools.p( bp_tree )


def usecase__get_base_points__examples():
    '''
    We obtain (infinitely near) base points of several 
    examples of linear series in order to test
    "get_base_point_tree.get_bp_tree()".
    '''
    pol_lst_lst = []

    # 0
    pol_lst_lst += [['x^2*z + y^2*z', 'y^3 + z^3']]

    # 1
    pol_lst_lst += [['x^3*z^2 + y^5', 'x^5']]

    # 2 (example from PhD thesis)
    pol_lst_lst += [['x^2', 'x*z + y^2']]

    # 3
    pol_lst_lst += [['x^2 + y^2', 'x*z + y^2']]

    # 4
    pol_lst_lst += [['x*z', 'y^2', 'y*z', 'z^2']]

    # 5
    pol_lst_lst += [['x^5', 'y^2*z^3']]

    # 6
    pol_lst_lst += [['x^2*y', 'x*y^2', 'x*y*z', '( x^2 + y^2 + z^2 )*z' ]]

    # 7 (weighted projective plane P(2:1:1))
    pol_lst_lst += [['z^6'    , 'y*z^5'    , 'y^2*z^4'    ,
                     'y^3*z^3', 'y^4*z^2'  , 'y^5*z'      , 'y^6',
                     'x^2*z^4', 'x^2*y*z^3', 'x^2*y^2*z^2', 'x^3*z^3']]

    # 8 (provided by Martin Weimann)
    pol_lst_lst += [['y^2*(x^3+x^2*z+2*x*z^2+z^3)+y*(2*x^3+2*x*z^2)*z+z^2*(x^3-x^2*z+x*z^2)',
                    'z^5' ]]

    # 9
    pol_lst_lst += [['x^3*y^4+x*y^4*z^2+3*x^2*y^3*z^2+3*x*y^2*z^4+y',
                    'z^7']]

    # 10 (degree 6 del Pezzo in S^5, which is the orbital product of 2 circles)
    pol_lst_lst += [[
        'x^2*y^2 + 6/5*x^2*y*z + 17/5*x^2*z^2 + y^2*z^2 + 6/5*y*z^3 + 17/5*z^4',
        '8/5*x^2*y*z + 6/5*x^2*z^2 + 8/5*y*z^3 + 6/5*z^4',
        'x^2*y^2 + 6/5*x^2*y*z + 7/5*x^2*z^2 + y^2*z^2 + 6/5*y*z^3 + 7/5*z^4',
        '4*x*z^3',
        '2*x^2*z^2 - 2*z^4',
        '-6/5*x^2*y*z - 2/5*x^2*z^2 - 4*x*z^3 + 6/5*y*z^3 + 2/5*z^4',
        '-2*x^2*z^2 + 12/5*x*y*z^2 + 4/5*x*z^3 + 2*z^4'
       ]]


    BasePointTree.short = True

    idx = 0
    for pol_lst in pol_lst_lst:

        ls = LinearSeries( pol_lst, PolyRing( 'x,y,z', True ) )

        LSTools.p( 3 * ( '\n' + 50 * '=' ) )
        LSTools.p( 'index for example =', idx )
        LSTools.p( ls )

        bp_tree = ls.get_bp_tree()
        LSTools.p( bp_tree )

        idx += 1


def usecase__get_linear_series__P2():
    '''
    Construct linear series of curves in the plane P^2, 
    with a given tree of (infinitely near) base points.
    '''

    # Example from PhD thesis (page 159).
    PolyRing.reset_base_field()
    bp_tree = BasePointTree()
    bp = bp_tree.add( 'z', ( 0, 0 ), 1 )
    bp = bp.add( 't', ( 0, 0 ), 1 )
    bp = bp.add( 't', ( -1, 0 ), 1 )
    bp = bp.add( 't', ( 0, 0 ), 1 )
    LSTools.p( bp_tree )

    ls = LinearSeries.get( 2, bp_tree )
    LSTools.p( ls.get_bp_tree() )


def usecase__get_linear_series__P1P1_DP6():
    '''
    Construct linear series of curves in P^1xP^1, 
    with a given tree of (infinitely near) base points.
    '''

    # construct ring over Gaussian rationals
    #
    ring = PolyRing( 'x,y,v,w', True )
    ring.ext_num_field( 't^2 + 1' )
    a0 = ring.root_gens()[0]

    # setup base point tree for 2 simple complex conjugate base points.
    #
    bp_tree = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bp = bp_tree.add( 'xv', ( -a0, a0 ), 1 )
    bp = bp_tree.add( 'xv', ( a0, -a0 ), 1 )
    LSTools.p( 'We consider linear series of curves in P^1xP^1 with the following base point tree:' )
    LSTools.p( bp_tree )

    #
    # Construct linear series is defined by a list of polynomials
    # in (x:y)(v:w) of bi-degree (2,2) with base points as in "bp_tree".
    # The defining polynomials of this linear series, correspond to a parametric map
    # of an anticanonical model of a Del Pezzo surface of degree 6 in P^6.
    #
    # We expect that the linear series is defined by the following set of polynomials:
    #
    # [ 'x^2*v^2 - y^2*w^2', 'x^2*v*w + y^2*v*w', 'x^2*w^2 + y^2*w^2', 'x*y*v^2 - y^2*v*w',
    #   'x*y*v*w - y^2*w^2', 'y^2*v*w + x*y*w^2', 'y^2*v^2 + y^2*w^2' ]
    #
    ls = LinearSeries.get( 2, bp_tree )
    LSTools.p( 'The linear series of bi-degree (2,2) corresponding to this base point tree is as follows:' )
    LSTools.p( ls.get_bp_tree() )

    #
    # construct corresponding linear series of bi-degree (1,1)
    # and 2 simple complex conjugate base points
    #
    # We expect that the linear series is defined by the following set of polynomials:
    #
    # ['x * v - y * w', 'y * v + x * w' ]
    #
    #
    ls = LinearSeries.get( 1, bp_tree )
    LSTools.p( 'The linear series of bi-degree (1,1) corresponding to this base point tree is as follows:' )
    LSTools.p( ls.get_bp_tree() )


def usecase__get_implicit__DP6():
    '''
    Construct linear series of curves in P^1xP^1, 
    with a given tree of (infinitely near) base points.
    The defining polynomials of this linear series, correspond to a parametric map
    of an anticanonical model of a Del Pezzo surface of degree 6 in P^6.
    Its ideal is generated by quadratic forms. We search for a quadratic form in
    this ideal of signature (1,6). This quadratic form corresponds to a hyperquadric 
    in P^6, such that the sextic Del Pezzo surface is contained in this hyperquadric.         
    We construct a real projective isomorphism from this hyperquadric to the projectivization
    of the unit 5-sphere in P^6. 
    '''

    #
    # parametrization of degree 6 del Pezzo surface in projective 6-space.
    # See ".usecase__get_linear_series__P1P1_DP6()" for the construction of
    # this linear series.
    #
    pmz_lst = [
         'x^2*v^2 - y^2*w^2',
         'x^2*v*w + y^2*v*w',
         'x^2*w^2 + y^2*w^2',
         'x*y*v^2 - y^2*v*w',
         'x*y*v*w - y^2*w^2',
         'y^2*v*w + x*y*w^2',
         'y^2*v^2 + y^2*w^2'
         ]
    ls = LinearSeries( pmz_lst, PolyRing( 'x,y,v,w', True ) )

    #
    # base points of linear series
    #
    bp_tree = ls.get_bp_tree()
    LSTools.p( 'parametrization    =', ls.pol_lst )
    LSTools.p( 'base points        =' + str( bp_tree ) )

    #
    # implicit image in projective 6-space
    # of map associated to linear series
    #
    imp_lst = ls.get_implicit_image()
    LSTools.p( 'implicit equations =', imp_lst )

    #
    # compute Hilbert polynomial in QQ[x0,...,x6]
    #
    ring = sage_PolynomialRing( sage_QQ, [ 'x' + str( i ) for i in range( 7 )] )
    x_lst = ring.gens()
    imp_lst = sage__eval( str( imp_lst ), ring.gens_dict() )
    hpol = ring.ideal( imp_lst ).hilbert_polynomial()
    hdeg = hpol.diff().diff()
    LSTools.p( 'Hilbert polynomial =', hpol )
    LSTools.p( 'implicit degree    =', hdeg )

    #
    # equation of unit sphere is not in the ideal
    #
    s_pol = sum( [-x_lst[0] ** 2] + [x ** 2 for x in x_lst[1:]] )
    LSTools.p( 'Inside sphere?: ', s_pol in ring.ideal( imp_lst ) )

    #
    # compute random quadrics containing del Pezzo surface
    # until a quadric with signature (1,6) is found
    # or set a precomputed quadric with given "c_lst"
    #
    LSTools.p( 'Look for quadric in ideal of signature (1,6)...(may take a while)...' )
    sig = []
    while sorted( sig ) != [0, 1, 6]:

        # set coefficient list
        c_lst = []
        c_lst = [-1, -1, 0, 0, 0, -1, 1, 0, -1, -1, -1]  # uncomment to speed up execution
        if c_lst == []:
            lst = [-1, 0, 1]
            for imp in imp_lst:
                idx = int( sage_ZZ.random_element( 0, len( lst ) ) )
                c_lst += [ lst[idx] ]

        # obtain quadric in ideal from "c_lst"
        i_lst = range( len( imp_lst ) )
        M_pol = [ c_lst[i] * imp_lst[i] for i in i_lst if imp_lst[i].total_degree() == 2 ]
        M_pol = sum( M_pol )

        # eigendecomposition
        M = sage_invariant_theory.quadratic_form( M_pol, x_lst ).as_QuadraticForm().matrix()
        M = sage_matrix( sage_QQ, M )
        vx = sage_vector( x_lst )
        D, V = M.eigenmatrix_right()

        # determine signature of quadric
        num_pos = len( [ d for d in D.diagonal() if d > 0 ] )
        num_neg = len( [ d for d in D.diagonal() if d < 0 ] )
        num_zer = len( [ d for d in D.diagonal() if d == 0 ] )
        sig = [ num_pos, num_neg, num_zer ]
        LSTools.p( '\t sig =', sig, c_lst )

    #
    # output of M.eigenmatrix_right() ensures that
    # D has signature either (--- --- +) or (- +++ +++)
    #
    if num_pos < num_neg:  # (--- --- +) ---> (+ --- ---)
        V.swap_columns( 0, 6 )
        D.swap_columns( 0, 6 )
        D.swap_rows( 0, 6 )

    #
    # diagonal orthonormalization
    # note: M == W.T*D*W == W.T*L.T*J*L*W = U.T*J*U
    #
    W = sage_matrix( [col / col.norm() for col in V.columns()] )
    J = []
    for d in D.diagonal():
        if d > 0:
            J += [1]
        elif d < 0:
            J += [-1]
    J = sage_diagonal_matrix( J )
    L = sage_diagonal_matrix( [ d.abs().sqrt() for d in D.diagonal()] )
    U = L * W

    #
    # Do some tests
    #
    assert M_pol in ring.ideal( imp_lst )
    assert vx * M * vx == M_pol
    assert M * V == V * D

    #
    # output values
    #
    LSTools.p( 'quadratic form of signature (1,6) in ideal =', M_pol )
    LSTools.p( 'matrix M associated to quadratic form      =', list( M ) )
    LSTools.p( 'M == U.T*J*U                               =', list( U.T * J * U ) )
    LSTools.p( 'U                                          =', list( U ) )
    LSTools.p( 'J                                          =', list( J ) )


def usecase__get_base_points__and__get_linear_series():
    '''
    We obtain (infinitely near) base points of a 
    linear series defined over QQ. The base points
    are defined over a number field.
    '''
    ring = PolyRing( 'x,y,z', True )
    ls = LinearSeries( ['x^2+y^2', 'y^2+x*z'], ring )
    bp_tree = ls.get_bp_tree()
    LSTools.p( bp_tree )

    ls = LinearSeries.get( 2, bp_tree )
    LSTools.p( ls )
    LSTools.p( ls.get_bp_tree() )


def usecase__linear_normalization__and__adjoint():
    '''
    In this usecase are some applications of the 
    "linear_series" library.  we show by example 
    how to compute a linear normalization X of a surface Y, 
    or equivalently, how to compute the completion of a 
    linear series. Also we contruct an example of a surface Z 
    such that X is its adjoint surface.     
    '''
    #
    # Linear series corresponding to the parametrization
    # of a cubic surface X in P^4 that is the projection
    # of the Veronese embedding of P^2 into P^5.
    #
    ring = PolyRing( 'x,y,z', True )
    bp_tree = BasePointTree()
    bp = bp_tree.add( 'z', ( 0, 0 ), 1 )
    ls = LinearSeries.get( 2, bp_tree )
    imp_lst = ls.get_implicit_image()
    LSTools.p( 'linear series      =', ls.get_bp_tree() )
    LSTools.p( 'implicit image     =', imp_lst )

    #
    # compute Hilbert polynomial of X in QQ[x0,...,x6]
    #
    R = sage_PolynomialRing( sage_QQ, [ 'x' + str( i ) for i in range( len( ls.pol_lst ) )] )
    x_lst = R.gens()
    imp_lst = sage__eval( str( imp_lst ), R.gens_dict() )
    hpol = R.ideal( imp_lst ).hilbert_polynomial()
    hdeg = hpol.diff().diff()
    LSTools.p( 'Hilbert polynomial =', hpol )
    LSTools.p( 'implicit degree    =', hdeg )

    #
    # projection of X in P^4 to Y in P^3, where Y is singular.
    #
    ls = LinearSeries( ['x^2-x*y', 'x*z', 'y^2', 'y*z'], PolyRing( 'x,y,z', True ) )
    bp_tree = ls.get_bp_tree()
    LSTools.p( 'basepoint tree of projection =', bp_tree )
    eqn = ls.get_implicit_image()
    assert len( eqn ) == 1
    eqn = sage_SR( eqn[0] )
    x0, x1, x2, x3 = sage_var( 'x0,x1,x2,x3' )
    LSTools.p( 'eqn       =', eqn )
    LSTools.p( 'D(eqn,x0) =', sage_diff( eqn, x0 ) )
    LSTools.p( 'D(eqn,x1) =', sage_diff( eqn, x1 ) )
    LSTools.p( 'D(eqn,x2) =', sage_diff( eqn, x2 ) )
    LSTools.p( 'D(eqn,x3) =', sage_diff( eqn, x3 ) )

    #
    # compute normalization X of Y
    #
    ls_norm = LinearSeries.get( 2, bp_tree )
    LSTools.p( 'normalization = ', ls_norm )
    LSTools.p( '              = ', ls_norm.get_implicit_image() )

    #
    # define pre-adjoint surface Z
    #
    ring = PolyRing( 'x,y,z', True )
    bp_tree = BasePointTree()
    bp_tree.add( 'z', ( 0, 0 ), 2 )
    bp_tree.add( 'z', ( 0, 1 ), 1 )
    ls = LinearSeries.get( 5, bp_tree )
    LSTools.p( ls.get_bp_tree() )


if __name__ == '__main__':

    LSTools.start_timer()
    mod_lst = []
    mod_lst += ['__main__.py']
    # mod_lst += ['get_linear_series.py']
    LSTools.filter( mod_lst )  # output only from specified modules

    ################################################
    #                                              #
    # (Un)comment usecases for this package below. #
    #                                              #
    ################################################

    usecase__get_base_points__P2()  # shows how to obtain base points of linear series in the projective plane P^2
    usecase__get_base_points__P1P1()  # shows how to obtain base points of linear series in P^1xP^1
    usecase__get_base_points__examples()  # several examples of linear series and their base point
    usecase__get_linear_series__P2()  # shows how to construct a linear series in P^2 from given base points
    usecase__get_linear_series__P1P1_DP6()  # shows how to construct a linear series in P^1xP^1 from given base points
    usecase__get_implicit__DP6()  # shows how to compute the ideal of the surface parametrized by the linear series
    usecase__get_base_points__and__get_linear_series()  # another easy example for getting base points and linear series
    usecase__linear_normalization__and__adjoint()  # shows how to compute linear normalization and adjoint of surface

    ###############################################
    #                                             #
    # End of list of usecase methods.             #
    #                                             #
    ###############################################

    LSTools.stop_timer()
    print
    print( 'The End' )

