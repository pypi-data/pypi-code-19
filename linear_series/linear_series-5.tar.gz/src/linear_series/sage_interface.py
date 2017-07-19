'''
Use of this source code is governed by a 
MIT-style license that can be found in the 
LICENSE file.
Created on Jul 12, 2017
@author: Niels Lubbes

Sage has a complicated import structure and it 
is not possible to simply import each need 
module. It seems that "from sage.all import *" 
is the only option. Therefore we introduce an 
interface to Sage so that in the code, it is 
clear, which libraries of Sage we use. Moreover, 
we specify below from which modules in the Sage 
library we import. 

We explain the naming scheme with the following 
two examples. The interface method for 
"PolynomialRing()" is called 
"sage_PolynomialRing()". However the interface 
method for "sage_eval()" is not called 
"sage_sage_eval()" but instead "sage__eval()". 
The variable "ZZ" is called "sage_ZZ".
'''

from sage.all import *


#################################################
# sage.structure                                #
#################################################

# from sage.structure.proof.proof import proof
sage_proof = proof

# from sage.structure.sage_object import save
def sage_save( *args, **kwargs ):
    return save( *args, **kwargs )

# from sage.structure.sage_object import load
def sage_load( *args, **kwargs ):
    return load( *args, **kwargs )


#################################################
# sage.misc                                     #
#################################################

# from sage.misc.sage_eval import sage_eval
def sage__eval( *args, **kwargs ):
    return sage_eval( *args, **kwargs )


#################################################
# sage.symbolic                                 #
#################################################

# from sage.symbolic.ring import SR
sage_SR = SR

# from sage.symbolic.relation import solve
def sage_solve( *args, **kwargs ):
    return solve( *args, **kwargs )


#################################################
# sage.rings                                    #
#################################################

# from sage.rings.integer_ring import ZZ
sage_ZZ = ZZ

# from sage.rings.rational_field import QQ
sage_QQ = QQ

# import sage.rings.invariant_theory
sage_invariant_theory = invariant_theory

# from sage.rings.fraction_field import FractionField
def sage_FractionField( *args, **kwargs ):
    return FractionField( *args, **kwargs )

# from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
# http://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/polynomial_ring_constructor.html
def sage_PolynomialRing( *args, **kwargs ):
    return PolynomialRing( *args, **kwargs )

# from sage.rings.number_field.number_field import NumberField
def sage_NumberField( *args, **kwargs ):
    return NumberField( *args, **kwargs )


#################################################
# sage.matrix                                   #
#################################################

# from sage.matrix.constructor import matrix
def sage_matrix( *args, **kwargs ):
    return matrix( *args, **kwargs )

# from sage.matrix.constructor import diagonal_matrix
def sage_diagonal_matrix( *args, **kwargs ):
    return diagonal_matrix( *args, **kwargs )

# from sage.matrix.constructor import vector
def sage_vector( *args, **kwargs ):
    return vector( *args, **kwargs )


#################################################
# sage.arith                                    #
#################################################

# from sage.arith.misc import factor
def sage_factor( *args, **kwargs ):
    return factor( *args, **kwargs )

# from sage.arith.misc import gcd
def sage_gcd( *args, **kwargs ):
    return gcd( *args, **kwargs )


#################################################
# sage.calculus                                 #
#################################################

# from sage.calculus.functional import diff
def sage_diff( *args, **kwargs ):
    return diff( *args, **kwargs )

# from sage.calculus.functional import expand
def sage_expand( *args, **kwargs ):
    return expand( *args, **kwargs )

# from sage.calculus.var import var
def sage_var( *args, **kwargs ):
    return var( *args, **kwargs )


#################################################
# sage.combinat                                 #
#################################################

# from sage.combinat.composition import Compositions
def sage_Compositions( *args, **kwargs ):
    return Compositions( *args, **kwargs )

# from sage.combinat.combination import Combinations
def sage_Combinations( *args, **kwargs ):
    return Combinations( *args, **kwargs )




