'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 6, 2016
@author: Niels Lubbes
'''
from sage.all import *

from class_ls_tools import LSTools
from class_poly_ring import *
from get_linear_series import *



def get_implicit_image( ls ):
    '''
    INPUT:
        - "ls" -- LinearSeries object. Elements in "ls.pol_lst"
                  should be homogeneous polynomials over QQ. 
                  These polynomials represent a map F between 
                  projective spaces. We assume that the polynomials 
                  are co-prime.
    OUTPUT
        - A list of polynomials in QQ[x0,...,xn]. 
          These polynomials represent the ideal of the image
          of the map F in projective n-space, where n is 
          "len(ls.pol_lst)-1".
          
          
          This method might not terminate within reasonable time.
    '''

    # QQ[x0,...,xn]
    vx_lst = [ 'x' + str( i ) for i in range( len( ls.pol_lst ) )]
    ring = PolynomialRing( QQ, vx_lst + list( ls.ring.gens() ) )
    x_lst = ring.gens()[0:len( vx_lst )]
    v_lst = ring.gens()[len( vx_lst ):]

    # coerce "ls.pol_lst""
    p_lst = [ sage_eval( str( pol ), ring.gens_dict() ) for pol in ls.pol_lst ]

    # construct ideal
    s_lst = [ x_lst[i] - p_lst[i] for i in range( len( p_lst ) )]
    s_ideal = ring.ideal( s_lst )
    LSTools.p( len( s_lst ), s_lst )

    # eliminate all variables except for the xi's
    e_lst = list( s_ideal.elimination_ideal( v_lst ).gens() )
    LSTools.p( len( e_lst ), e_lst )

    # test
    dct = { x_lst[i]:p_lst[i] for i in range( len( p_lst ) ) }
    r_lst = [ e.subs( dct ) for e in e_lst ]
    LSTools.p( 'test:', sum( r_lst ) == 0 )

    return e_lst


def get_implicit_projection( ls, deg ):
    '''
    This function does not work properly, since the output polynomial still contains
    undeterminate variables. These need to be solved.
    
    INPUT:
        - "ls"  -- LinearSeries s.t. "ls.pol_lst" consist of polynomials in x,y,z 
                   and of the same degree. Note that the polynomials in "ls.pol_lst"
                   define a birational map from the projective plane to a surface S in
                   projective n-space where n equals "len(ls.pol_lst)-1".
        - "deg" -- An integer representing the degree of the parametrized surface S.
    OUTPUT:
        - A polynomial F(x0:x1:x2:x3) of degree at most "deg" and 
          undetermined coefficients in (r0,r1,...). 
          The ".parent()" of the polynomial is "SymbolicRing".
          The zero-set V(F) is a projection of the surface S by the map
          (x0:x1:...:xn) |-> (x0:x1:x2:x3) 
    '''
    p0, p1, p2, p3 = ls.pol_lst[0:4]

    # construct a polynomial ring
    c_len = len( Compositions( deg + 4, length = 4 ).list() )
    c_str_lst = [ 'c' + str( i ) for i in range( c_len )]

    R = PolynomialRing( PolyRing.num_field, ['x0', 'x1', 'x2', 'x3'] + c_str_lst + ['x', 'y', 'z'], order = 'lex' )
    x0, x1, x2, x3 = R.gens()[0:4]
    c_lst = R.gens()[4:4 + c_len]
    x, y, z = R.gens()[4 + c_len:]
    m_lst = get_mon_lst( deg, ( x0, x1, x2, x3 ) )
    R_dict = R.gens_dict()
    R_dict.update( PolyRing.num_field.gens_dict() )

    p0, p1, p2, p3 = sage_eval( str( [p0, p1, p2, p3] ), R_dict )

    LSTools.p( R )
    LSTools.p( 'm_lst =', m_lst )
    LSTools.p( '(p0, p1, p2, p3) =', ( p0, p1, p2, p3 ) )

    # construct polynomial in x0, x1, x2 with coefficients in c_lst
    F = 0
    for i in range( len( m_lst ) ):
        F += c_lst[i] * m_lst[i]
    LSTools.p( 'F =', F )

    # compute F( p0(x,y,z):...: p3(x,y,z) )
    FP = expand( F.subs( {x0:p0, x1:p1, x2:p2, x3:p3} ) )  # expand to prevent a bug in sage.
    LSTools.p( 'FP =', FP )

    # obtain coefficients w.r.t. x, y and z
    coef_lst = []
    pmzdeg = p0.total_degree()
    comp_lst = Compositions( deg * pmzdeg + 3 , length = 3 ).list()  # e.g. [1,1,2]=[0,0,1]
    LSTools.p( 'comp_lst =', comp_lst )
    for comp in comp_lst:
        coef = FP.coefficient( {x: comp[0] - 1, y: comp[1] - 1, z:comp[2] - 1} )
        coef_lst += [coef]
    LSTools.p( 'coef_lst =', coef_lst )

    # compute groebner basis and reduce F w.r.t. the GB
    #
    # alternative code
    # ----------------
    # GB = list( ideal( coef_lst ).groebner_basis() )
    # LSTools.p( 'GB =', GB )
    # red_F = F.reduce( ideal( GB ) )
    # for g in GB:
    #    red_F = red_F.quo_rem( g )[1]
    # LSTools.p( 'red_F =', red_F )
    # ----------------
    #
    scoef_lst = [ SR( coef ) for coef in coef_lst]
    sc_lst = [ SR( c ) for c in c_lst]
    sol_lst = solve( scoef_lst, sc_lst, solution_dict = True )
    LSTools.p( sol_lst )
    red_F = expand( SR( F ).subs( sol_lst[0] ) )
    LSTools.p( 'red_F =', red_F )

    # check the solutions
    sp0, sp1, sp2, sp3 = SR( p0 ), SR( p1 ), SR( p2 ), SR( p3 )
    sx0, sx1, sx2, sx3 = SR( x0 ), SR( x1 ), SR( x2 ), SR( x3 )
    chk_F = expand( red_F.subs( {sx0:sp0, sx1:sp1, sx2:sp2, sx3:sp3} ) )
    LSTools.p( 'chk_F =', chk_F )
    if chk_F != 0:
        raise Exception( 'The polynomial red_F(p0:p1:p2:p3) does not vanish:', red_F, ( p0, p1, p2, p3 ), chk_F )

    return red_F
