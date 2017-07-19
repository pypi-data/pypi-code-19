'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 4, 2016
@author: Niels Lubbes

The polynomial ring is a object that extends PolynomialRing of Sage
in the sense that the base field can be extended by roots, by passing
the minimal polynomial of the root as argument.
'''

from class_ls_tools import LSTools

from sage_interface import sage_QQ
from sage_interface import sage__eval
from sage_interface import sage_PolynomialRing
from sage_interface import sage_diff
from sage_interface import sage_factor
from sage_interface import sage_gcd
from sage_interface import sage_expand
from sage_interface import sage_SR
from sage_interface import sage_NumberField
from sage_interface import sage_FractionField
from sage_interface import sage_proof


class PolyRing:
    '''
    Polynomial ring defined over an algebraic number field.
    The base field is a number field and is a static variable.
    Unless explicitly specified in the constructor, the number field
    will contain roots, that were previously added.     
    '''

    # Initially the number field is the rational numbers (static).
    #
    num_field = sage_QQ

    # List of roots in number field that are adjoined to QQ (static).
    # This list is used in "PolyRing.__str__()" for the human readable
    # output format. Its elements consist of 2-tuples:
    #     ( [name of root], [minimal polynomial for root] ).
    #
    root_lst = []

    def __init__( self, var_lst = 'x,y,z', reset_num_field = False ):
        '''
        Constructor.
        
        INPUT:
            - "var_lst"         -- A string of characters separated by comma's.
                                   The characters represent the generators of a 
                                   polynomial ring over "Poly_Ring.num_field".
            - "reset_num_field" -- If True then the base field is reset to QQ.
                                   Otherwise, the base field remembers previously
                                   added roots.
        '''

        # reset static num_field variable
        #
        if reset_num_field:
            PolyRing.reset_base_field()

        # Polynomial ring over an algebraic number field.
        #
        self.pol_ring = sage_PolynomialRing( PolyRing.num_field, var_lst )

        # Usage: sage__eval('<element in pol_ring>', ring_dct)
        #
        self.ring_dct = {}

        # update dictionary
        #
        self.ring_dct['t'] = sage_PolynomialRing( PolyRing.num_field, 't' ).gens()[0]
        self.__update_ring_dct()

        # Unlike in PARI/GP, class group computations in Sage do not by default
        # assume the Generalized Riemann Hypothesis. To do class groups computations
        # not provably correctly we set proof.number_field(False). It can easily take
        # 1000 times longer to do computations with proof (the default).
        #
        sage_proof.number_field( False )


    @staticmethod
    def reset_base_field():
        '''
        OUTPUT:
            - Resets base field of this polynomial ring to QQ.
        '''
        PolyRing.num_field = sage_QQ
        PolyRing.root_lst = []


    def __update_ring_dct( self ):
        '''
        This private method updates "PolyRing.num_field" 
        and "self.ring_dct" and should be called if attributes of 
        "self" are modified.
        '''
        PolyRing.num_field = self.get_num_field()
        if PolyRing.num_field != sage_QQ:  # do not add {'1':1}
            self.ring_dct.update( self.get_num_field().gens_dict() )
        self.ring_dct.update( self.pol_ring.gens_dict() )
        self.ring_dct['t'] = self.ring_dct['t'].parent().change_ring( self.get_num_field() ).gens()[0]


    def set_num_field( self, field, root, min_pol ):
        '''
        INPUT:
            - field   -- A Sage field object. For example QQ.
            - root    -- An element in field that has been adjoined to it 
                         most recently.
            - min_pol -- The minimal polynomial of root.
            
        OUTPUT:
            - Modifies "self.pol_ring" to be a PolynomialRing over the new
              base field.
        '''
        self.pol_ring = self.pol_ring.change_ring( field )
        PolyRing.num_field = self.get_num_field()
        PolyRing.root_lst += [ ( root, min_pol ) ]
        self.__update_ring_dct()


    def get_num_field( self ):
        return self.pol_ring.base_ring()


    def set_gens( self, new_gens ):
        '''
        INPUT:
            - "new_gens" -- set of generators of PolynomialRing.
        OUTPUT:
            - Modifies "self.pol_ring" to be a PolynomialRing with 
              generators "new_gens" over the same number field as before.
        '''
        self.pol_ring = sage_PolynomialRing( self.get_num_field(), new_gens )
        self.__update_ring_dct()


    def gens( self ):
        '''
        OUTPUT:
            - Returns generators of polynomial ring.
        '''
        return self.pol_ring.gens()


    def root_gens( self ):
        '''
        OUTPUT:
            - Returns roots of number field which were adjoined to QQ. 
        '''
        gen_lst = list( self.get_num_field().gens() )
        gen_lst.reverse()
        return gen_lst


    def coerce( self, elt ):
        '''
        INPUT:
            - "elt"  -- A string of a list of polynomials in "self.pol_ring". 
        OUTPUT:
            - Coerces the string "elt" to an element of "self.pol_ring".
        '''
        return sage__eval( str( elt ), self.ring_dct )


    def coerce_ff( self, elt ):
        '''
        Some symbolic methods in sage are not available in the polynomial 
        ring over a number field, but are available in the polynomial ring
        over a fraction field.
        
        INPUT:
            - "elt"  -- String of an symbolic expression 
                        with polynomials in "self.pol_ring".
        OUTPUT:
            - Elements in a polynomial ring R with generators "self.gens()".
              The ground field of R is the fraction field of a polynomial ring 
              whose generators corresponds to the roots in the 
              number field "PolyRing.num_field".
              For example R=FF[x,y,z] where FF=FractionField( QQ[a0,a1,a2,a3] ). 
        '''
        eval_dct = {}

        # construct fraction field FF
        FF = sage_QQ
        if PolyRing.num_field != sage_QQ:
            ngens = PolyRing.num_field.gens_dict().keys()  # (a0,a1,...)
            FF = sage_FractionField( sage_PolynomialRing( sage_QQ, ngens ) )
            eval_dct.update( FF.gens_dict() )

        # construct polynomial ring R over FF
        pgens = self.pol_ring.gens_dict().keys()
        R = sage_PolynomialRing( FF, pgens )
        eval_dct.update( R.gens_dict() )

        # coerce "elt" to R
        return sage__eval( str( elt ), eval_dct )


    def coerce_sr( self, elt ):
        '''
        Some symbolic methods in sage are not available in the 
        polynomial ring over a number field, but are available 
        in the "SymbolicRing" of Sage.
        
        INPUT:
            - "elt"  -- String of expression with 
                        polynomials in "self.pol_ring".
        OUTPUT:
            - Elements in the "SymbolicRing" of Sage. This can be seen
              as a polynomial ring over QQ where generators correspond to
              the roots in "PolyRing.num_field" and "self.gens()".
              For example: QQ[a0,a1,a2,x,y,z]. 
        '''
        # construct dictionary for "sage_eval"
        sym_dct = self.ring_dct.copy()
        for key in sym_dct.keys():
            sym_dct[key] = sage_SR( str( sym_dct[key] ) )  # SR = Symbolic Ring

        # coerce "elt" to symbolic ring
        return sage__eval( str( elt ), sym_dct )


    def diff( self, pol, gen, mult ):
        '''
        INPUT:
            - "pol"  -- A polynomial in "self.pol_ring".
            - "gen"  -- A generator of "self.pol_ring".
            - "mult" -- An integer.            
        OUTPUT:
            - Derivative of "pol" wrt. variable "gen", "mult" times.         
        '''
        # currently there is a bug in Sage for
        # computing the derivative of a polynomial
        # defined over a number field

        spol, sgen = self.coerce_sr( [pol, gen] )
        dpol = sage_diff( spol, sgen, mult )
        dpol = self.coerce( dpol )

        return dpol


    def quo( self, pol1, pol2 ):
        '''
        INPUT:
            - "pol1" -- A polynomial in "self.pol_ring".
            - "pol2" -- A polynomial in "self.pol_ring".            
        OUTPUT:
            - Polynomial quotient of "pol1" and "pol2" in "self.pol_ring".         
        '''
        # currently there is a bug in Sage for
        # computing the polynomial quotient over a number field.

        spol1, spol2 = self.coerce_ff( [pol1, pol2] )
        squo = spol1.quo_rem( spol2 )[0]
        quo = self.coerce( squo )
        # LSTools.p( ( pol1, pol2, squo, quo ) )
        return quo


    def resultant( self, pol1, pol2, var ):
        '''
        INPUT:
            - "pol1" -- A polynomial in "self.pol_ring".
            - "pol2" -- A polynomial in "self.pol_ring".
            - "var"  -- A generator of "self.pol_ring".
        OUTPUT:
            - Resultant of "pol1" and "pol2" w.r.t. "var" in "self.pol_ring". 
        '''
        # currently there is a bug in Sage for computing
        # the resultant over a number field. So we coerce
        # the arguments first to a fraction field, then
        # we compute the resultant, after which we coerce
        # the resultant to be an element in PolyRing.

        spol1, spol2, svar = self.coerce_ff( [pol1, pol2, var] )

        if spol1 in sage_QQ or spol2 in sage_QQ:
            sres = -1
        else:
            sres = spol1.resultant( spol2, svar )

        res = self.coerce( sres )

        return res


    def aux_gcd( self, pol_lst ):
        '''
        INPUT:
            - "pol_lst" -- A (string of a) list of polynomials in "self.pol_ring"
        
        OUTPUT: 
            - Returns the following two lists:
                * A list of non-constant factors of the 
                  gcd over QQ of the polynomials:  
                    [( factor in "self.pol_ring", multiplicity ),...].
                * A list of polynomials in "self.pol_ring" such 
                  that the gcd is factored out.
        '''

        # In Sage it is currently not possible to compute gcd and to
        # factor a multivariate polynomial over a number field.

        # convert to symbolic ring
        spol_lst = self.coerce_sr( pol_lst )

        # compute gcd and factor in symbolic ring
        sgcd = sage_gcd( spol_lst )
        sfct_lst = sgcd.factor_list()

        # factor out gcd in polynomials
        spol_lst = [ sage_expand( spol / sgcd ) for spol in spol_lst]

        # coerce back
        fct_lst, npol_lst = self.coerce( [sfct_lst, spol_lst] )

        # ignore the factors that are constants
        nfct_lst = []
        for fct in fct_lst:
            if fct[0] not in PolyRing.num_field:
                nfct_lst += [ fct ]

        return nfct_lst, npol_lst


    def factor( self, pol ):
        '''
        INPUT:
            - "pol" -- A univariate polynomial in "self.pol_ring".
        OUTPUT
            - A list of factors of "pol" in "PolyRing.pol_ring":
              
              [  ( <polynomial-factor>, <multiplicity> ), ... ]               
              
              If "pol" is a constant then the empty list is returned.
        '''
        LSTools.p( 'factoring ', pol, ' in ', self )
        if pol in self.get_num_field():
            return []
        else:
            fct_lst = sage_factor( pol )
            LSTools.p( '\t', fct_lst )
            return fct_lst

        #
        # The call "sage_factor(pol)" sometimes raises the following warning:
        # "
        # local/lib/python2.7/site-packages/sage/rings/number_field/number_field.py:1526:
        # UserWarning: interpreting PARI polynomial 1 relative to the
        # defining polynomial x^2 + 1 of the PARI number field % (x, self.pari_polynomial()))
        # "
        #
        # If "pol" in "self.ring.get_num_field()" then "sage_factor( ypol )" raises
        # "
        # ArithmeticError: non-principal ideal in factorization
        # "
        #


    def ext_num_field( self, pol ):
        '''
        INPUT: 
            - "pol" --A (string of a) univariate polynomial over 
              "self.get_num_field()" in 't'.        
        METHOD:
            - Adjoins roots of "pol" to the number field of "self.ring". 
        '''

        # factor
        pol = self.coerce( pol )
        if pol in self.get_num_field():
            return  # nothing to do here
        fct_lst = self.factor( pol )
        first_pol = fct_lst[0][0]


        if first_pol.degree() == 1:
            fct_lst = fct_lst[1:]
        else:

            # obtain extended number field with first factor
            gen_str = 'a' + str( len( self.root_lst ) )
            NF = sage_NumberField( [first_pol], gen_str )

            # set the new number field
            self.set_num_field( NF, NF.gens()[0], first_pol )


        # continue recursively with remaining factors until all factors are linear
        for fct in fct_lst:
            self.ext_num_field( fct[0] )


    def __str__( self ):
        '''
        OUTPUT:
          - A human readable string representation of object.
            The roots of the number field, that are adjoined 
            to the rational numbers QQ are depicted with their
            minimal polynomial.
            
        EXAMPLES:
          - sage: ring = PolyRing( 'x,y,z', True )
            sage: ring.ext_num_field( 't^2 + 1' )
            sage: ring.ext_num_field( 't^3 + a0' )
            sage: print( ring )
            out : QQ( <a0|t^2 + 1>, <a1|t^2 + a0*t - 1> )[x, y, z]
        '''
        s = 'QQ'
        if len( PolyRing.root_lst ) > 0:
            rs = ''
            for root in PolyRing.root_lst:
                rs += '<' + str( root[0] ) + '|' + str( root[1] ) + '>, '
            s += '( ' + rs[:-2] + ' )'
        s += str( self.gens() ).replace( '(', '[' ).replace( ')', ']' )
        return s



