'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 4, 2016
@author: Niels Lubbes
'''

from class_poly_ring import PolyRing
from get_base_point_tree import get_bp_tree
from get_solution_set import get_solution_set
from get_linear_series import get_linear_series
from get_implicit import get_implicit_projection
from get_implicit import get_implicit_image


class LinearSeries:
    '''
    A linear series in the plane is represented 
    as a list of polynomials in "PolyRing". 
    '''

    def __init__( self, pol_lst = [], ring = PolyRing() ):
        '''
        INPUT:
            - "pol_lst" -- A list of (strings of) polynomials in "ring".
            - "ring"    -- A "PolyRing" representing a polynomial ring.   
        OUTPUT:
            - "self.pol_lst"
            - "self.ring"
        '''
        self.ring = ring
        self.pol_lst = [self.ring.coerce( pol ) for pol in pol_lst]


    def get_bp_tree( self ):
        return get_bp_tree( self )


    def get_solution_set( self ):
        return get_solution_set( self )


    @staticmethod
    def get( deg, bp_tree ):
        return get_linear_series( deg, bp_tree )


    def get_implicit_projection( self, deg ):
        return get_implicit_projection( self, deg )


    def get_implicit_image( self ):
        return get_implicit_image( self )


    def copy( self ):
        cp_ring = PolyRing( self.gens() )
        cp_pol_lst = cp_ring.coerce( self.pol_lst )
        return LinearSeries( cp_pol_lst, cp_ring )


    def gens( self ):
        return self.ring.gens()


    def subs( self, sub_dct ):
        '''
        INPUT:
            - "self"     -- "self.ring" is a PolyRing and "self.polyring" is a list
                            of polynomials in PolyRing.
            - "sub_dct"  --  A dictionary with [key] and [value] elements in PolyRing.
        OUTPUT:
            - Sets "self.pol_lst" to the list of polynomials in PolyRing where
              each occurrence of [key] is substituted with [value].   
        '''
        self.pol_lst = [ self.ring.coerce( pol ) for pol in self.pol_lst ]
        self.pol_lst = [ pol.subs( sub_dct ) for pol in self.pol_lst ]
        return self


    def chart( self, c_lst ):
        '''        
        INPUT:
            - "self"  -- The polynomials in "self.pol_lst" are assumed 
                         to be (bi-) homogeneous in PolyRing.
            - "c_lst" -- A list of characters where each character  
                         denotes a generator of the polynomial ring "self.ring" 
                         of type PolyRing. For bi-homogeneous polynomials, 
                         we expect "c_lst" to be a string of length two,
                         since we can consider a string as a list of characters.                                                    
        OUTPUT:
            - Substitutes {c:1} in polynomials in "self.pol_lst" 
              for all c in "c_lst". 
              The generators of the polynomial ring "self.ring" 
              are modified accordingly. 
              Thus "self" now represents a linear series 
              in the affine plane.
            
            - Returns "self". 
        '''
        for c in c_lst:
            var = self.ring.coerce( c )
            self.subs( { var:1} )
            new_gens = [ gen for gen in self.gens() if gen != var ]
            self.ring.set_gens( new_gens )
            self.pol_lst = self.ring.coerce( self.pol_lst )

        return self


    def diff( self, mu, mv ):
        '''
        INPUT:
            - "self" -- "self.pol_lst" are bivariate polynomials in PolyRing in say u and v.
            - "mu"   -- An integer. 
            - "mv"   -- An integer.
        OUTPUT:
            - "self.pol_lst" is set to
             
                [ d_u^{mu}d_v^{mv}(f) for f in "pol_lst"  ] 
              
              where d_u(.)=diff(.,u) denotes differentiation w.r.t. u.
              
              Thus we consider the (multiple) partial derivatives of each polynomial 
              in "self.pol_lst" wrt the variable u and v.
            
            - Returns "self".
        '''
        u, v = self.ring.gens()
        self.pol_lst = [ self.ring.diff( pol, u, mu ) for pol in self.pol_lst ]
        self.pol_lst = [ self.ring.diff( pol, v, mv ) for pol in self.pol_lst ]
        return self


    def translate_to_origin( self, sol ):
        '''
        INPUT:
            - "sol" -- A 2-tuple of elements in "self.ring.get_num_field()".
            
        METHOD:
            - Composes each polynomial F in "self.pol_lst" with a
              translation T such that F(p)=(FoT)(0,0) 
              where p=(sol[0],sol[1]).               
        '''
        u, v = self.gens()
        self.subs( {u:u + sol[0], v:v + sol[1]} )
        return self


    def blow_up_origin( self, chart ):
        '''
        INPUT:
            - "self"  -- Polynomials in PolyRing in the list "self.pol_lst" 
                         should be bi-variate and co-prime.
            - "chart" -- Either 's' or 't'.
            
        OUTPUT:
            - Returns the following 2 values:
                      * "self" 
                      * multiplicity of origin in "self.pol_lst".
        
            - Additionally "self" is modified as follows.   
            
              Let (g_i(u,v))_i denote the list of polynomials in "self.pol_lst" 
              indexed by i and in the variables u an v. These polynomials are elements
              in PolyRing.
              
              Let "mul" denote the multiplicity of the linear series at the origin: 
                  mul = deg( gcd( (g_i(u*v,v)_i) ) )
                           
              If "chart" equals 't' then "self.pol_lst" is modified to
                  ( g_i(u*v,v)*v^{-mul} )_i
              
              If "chart" equals 's' then "self.pol_lst" is modified to
                  ( g_i(u,v*u)*u^{-mul} )_i

              The linear series represented by "self.pol_lst" is after this
              modification isomorphic to a chart of the blow up of a linear series 
              at the origin. 
              
              The mathematical reason is as follows: 
              
              Let g(u,v) = c0*g0(u,v)+...+c5*g5(u,v) for some general coefficients ci in a 
              number field.
              
              In the chart z!=0, the blow up at the origin (0,0) is in coordinates:
                  
                U_z = { (u,v)x(s:t) | u*t=v*s and g(u,v)=0 } in A^2xP^1,
              
              and thus contained in the fiber product of the affine plane 
              with the projective line.  
                
              If also t!=0 then we obtain the chart
              
                U_t = { (u,v)x(s/t) | u=v*(s/t) and g(u,v)=0  } in A^2xA^1.
              
              The chart U_t has a component coming from the 
              multiplicity of g(u,v) at the origin (this is known
              in the algebraic geometry literature as 
              the exceptional component). This multiplicity is equal 
              to "mul" as above.
              
              The chart U_t is isomorphic to 
                  
                U'_t = { (s/t, v) | g( v*(s/t), v)=0 } in A^2.
              
              where u is recovered from (s/t, v) since u=v*(s/t).
              So we can subsequently repeat this blow up procedure,
              by setting the new u as u:=s/t, and factoring out
              the exceptional component.
        '''
        u, v = self.gens()
        if chart == 't':
            self.subs( {u:u * v} )
            f = v
        elif chart == 's':
            self.subs( {v:v * u} )
            f = u
        else:
            raise ValueError( 'Chart should be either "t" or "s"', chart )

        gcd_fct_lst, self.pol_lst = self.ring.aux_gcd( self.pol_lst )

        if len( gcd_fct_lst ) > 1:
            raise Exception( 'Linear series has a fixed component.' )

        for fct in gcd_fct_lst:
            if fct[0] != f:
                raise Exception( 'Expect factor: ' + str( f ) + '^mult.', gcd_fct_lst )
            return self, fct[1]

        return self, 0


    def quo( self, pol2 ):
        '''
        INPUT:
            - "pol2" -- A (string of a) polynomial "pol" in PolyRing "self.ring".
             
        OUTPUT:
            - Polynomials in "self.pol_lst" are replaced with their quotient with "pol2".            
            - Return "self"
        '''
        pol2 = self.ring.coerce( pol2 )
        self.pol_lst = [ self.ring.quo( pol1, pol2 ) for pol1 in self.pol_lst ]

        return self


    def __str__( self ):
        '''                
        OUTPUT:
          - Human readable string representation of object. The String
            has the following format:
                { N, <<F0,...,FN>>, R }
            where
                * N         = Number of polynomials defining the linear series.
                * F0,...,FN = The N polynomials that define the linear series.
                * R         = The PolyRing over which the linear series is defined 
                
        EXAMPLES:
          - sage: print( LinearSeries( ['x^2', 'x*z + y^2'], PolyRing( 'x,y,z', True ) ) )                          
            out : { 2, <<x^2, y^2 + x*z>>, QQ[x, y, z] }
              
          - sage: ring = PolyRing( 'x,y,z', True )
            sage: ring.ext_num_field( 't^2 + 1' )              
            sage: print( LinearSeries( ['x^2+a0*y*z','y^2+x*z'], ring ) )
            out : { 2, <<x^2 + (a0)*y*z, y^2 + x*z>>, QQ( <a0|t^2 + 1> )[x, y, z] }                   
        '''

        s = '{ '
        s += str( len( self.pol_lst ) ) + ', '
        s += '<<' + str( self.pol_lst )[1:-1] + '>>, '
        s += str( self.ring )
        s += ' }'
        return s


