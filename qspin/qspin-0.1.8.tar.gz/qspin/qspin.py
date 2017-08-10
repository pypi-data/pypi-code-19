"""create pauli spin matrices and
manipulate quantum entangled states
"""

import numpy as np
import copy

__version__ = '0.1.8'

i = 1j
debug = False
sign = lambda a: '+' if a>0 else '-' if a<0 else '+'

class state_base(object):
    """Base class of all states
    """
    def __init__(self):
        self.bra = False # its a ket by default
        self.kind = 'ket' # by default
    
    def _old_repr(self):
        phi = self.phi
        first_one = True
        s = '0'
        for k in range(self.n):
            phi_k = phi.item(k)
            if phi_k != 0:
                if first_one:
                    s = str(phi_k) + ' ' + self.basis[k] + ' '
                    first_one = False
                else:
                    if isinstance(phi_k,float):
                        if phi_k < 0:
                            coef = ' - ' + str(abs(phi_k))
                        else:
                            coef = ' + ' + str(phi_k)
                    else: # complex
                        coef = ' + ' + str(phi_k)
                    s += coef + ' ' + self.basis[k] + ' '
        return s
    
    def __repr__(self):
        phi = self.phi
        first_one = True
        s = '0'
        for k in range(self.n):
            phi_k = phi.item(k)
            if phi_k != 0:
                
                if first_one:
                    s = ''
                    if isinstance(phi_k,(float,int)):
                        if phi_k == 1:
                            coef = ''
                        else:
                            coef = '%g '%phi_k
                    else: # complex
                        if phi_k.imag == 0:
                            if phi_k.real == 1:
                                coef = ''
                            elif phi_k.real == -1:
                                coef = '- '
                            else:
                                coef = '%g '%phi_k.real
                        elif phi_k.real == 0:
                            if phi_k.imag == 1:
                                coef = ' i '
                            else:
                                coef = '%g i '%phi_k.imag
                        else:
                            coef = '( %g %s %g i )'%(phi_k.real,sign(phi_k.imag),abs(phi_k.imag))
                    first_one = False
                    
                else:
                    if isinstance(phi_k,(float,int)):
                        if phi_k == 1:
                            coef = ''
                        else:
                            if phi_k == -1:
                                coef = '- '
                            else:
                                coef = '%s %g '%(sign(phi_k),abs(phi_k))
                    else: # complex
                        if phi_k.imag == 0:
                            if phi_k.real == 1:
                                coef = ' + '
                            elif phi_k.real == -1:
                                coef = ' - '
                            else:
                                coef = '%s %g '%(sign(phi_k.real),abs(phi_k.real))
                        elif phi_k.real == 0:
                            if phi_k.imag == 1:
                                coef = ' + i '
                            elif phi_k.imag == -1:
                                coef = ' - i '
                            else:
                                coef = '%s %g i '%(sign(phi_k.imag),abs(phi_k.imag))
                        else:
                            coef = '+ ( %g %s %g i )'%(phi_k.real,sign(phi_k.imag),abs(phi_k.imag))

                s += '%s%s '%(coef, self.basis[k])
        return s
    
    def __add__(self,another):
        """|a> + |b>
        """
        assert isinstance(another,self.__class__)
        assert self.bra == another.bra
        return self.__class__(self.phi + another.phi)
        
    def __sub__(self,another):
        """|a> - |b>
        """
        assert isinstance(another,self.__class__)
        assert self.bra == another.bra
        return self.__class__(self.phi - another.phi)
    
    def __mul__(self,another):
        """
        inner product: <a|b>
        operation on bra: <a|A
        scalar product: <a| alpha or <a| alpha
        outer product: |a><b|
        """
        if debug: print ('state_base.__mul__')
        assert isinstance(another,(int,float,complex,self.__class__,self.operator_class,str))
        if isinstance(another,self.__class__): # either inner or outer product
            if self.bra: # <a|b>
                assert not another.bra,'cannot multiply two bras'
                r = (self.phi.T*another.phi).item(0)
                if isinstance(r,complex):
                    if r.imag == 0:
                        r = r.real
                return r
            else: # |a><b|
                assert another.bra,'cannot multiply two kets'
                return self.operator_class(self.phi*another.phi.T)
        elif isinstance(another,self.operator_class): #  <a|A
            assert self.bra
            phi = (self.phi.T * another.op).T
            return bra(phi)
        elif isinstance(another,str): # '<a|'*A
            another = self.__class__(another)
            return self*another
        elif isinstance(another,(int,float,complex)):
            if self.bra:
                r = bra(self.phi*another) #  <a| alpha
            else:
                r = ket(self.phi*another) #  |a> alpha
            return r

    def __rmul__(self,num):
        """scalar product alpha |a> or alpha <a|
        """
        if debug: print ('state_base.__rmul__')
        assert isinstance(num,(int,float,complex))
        if self.bra:
            r = bra(self.phi*num) #  <a| alpha
        else:
            r = ket(self.phi*num) #  |a> alpha
        return r

    def __div__(self,num):
        """scalar product |a> / alpha
        """
        assert isinstance(num,(int,float,complex))
        if self.bra:
            r = bra(self.phi/num) #  <a| alpha
        else:
            r = ket(self.phi/num) #  |a> alpha
        return r
    
    def __truediv__(self,num):
        """scalar product |a> / alpha
        """
        assert isinstance(num,(int,float,complex))
        if self.bra:
            r = bra(self.phi/num) #  <a| alpha
        else:
            r = ket(self.phi/num) #  |a> alpha
        return r

    def __neg__(self):
        return (-1)*self #   - |a>
    
    def __getattr__(self,dot_op):
        if dot_op == 'H':
            assert not self.bra
            return bra(self)
        else:
            raise AttributeError(self.__repr__(),' object has no attribute ',dot_op)
    
    def copy(self):
        """deep copy of self
        """
        return copy.deepcopy(self)
    
    def normalize(self):
        """normalizes the wave function
        """
        norm = (self.phi.H*self.phi).item(0)
        self.phi /= np.sqrt(norm)
    
    def normalized(self):
        """returns the normalized version
        """
        norm = (self.phi.H*self.phi).item(0)
        return self/np.sqrt(norm)
    
    def density(self):
        """generate the density matrix
        """
        n = self.phi.size
        rho = np.matrix(np.zeros((n,n)))
        Phi = np.array(self.phi).flatten().tolist()
        for a in range(n):
            for a_prime in range(n):
                rho[a,a_prime] = (Phi[a]*np.conj(Phi[a_prime])).real
        return rho
    
    def prob(self,A):
        """determine the probability of being in
        a given basis state after the measurement A
        """
        p = []
        for basis in self.basis:
            p.append( (basis*A*self)**2 )
        return p

class operator_base(object):
    """Base class of all operators
    """
    def __init__(self):
        return

    def __repr__(self):
        return str(self.op)
    
    def __add__(self,another):
        """ A+B
        """
        assert isinstance(another,self.__class__)
        return self.__class__(self.op+another.op) # A + B
    
    def __sub__(self,another):
        """ A-B
        """
        assert isinstance(another,self.__class__)
        return self.__class__(self.op-another.op) #  A - B
    
    def __mul__(self,another):
        """
        scalar multiplication: alpha A
        operation on ket: A |a>
        operator x operator: A*B
        """
        if debug: print ('operator_base.__mul__')
        assert isinstance(another,(str,self.state_class,self.__class__,np.matrix,int,float,complex))
        if isinstance(another,(int,float,complex)): # alpha A
            return self.__class__(self.op*another)
        elif isinstance(another,self.state_class): # A |a>
            assert not another.bra
            return self.state_class(self.op*another.phi)
        elif isinstance(another,self.__class__):  # A*B
            return self.__class__(self.op*another.op)
        elif isinstance(another,np.matrix): # assume this operator*density_matrix
            return self.op*another
        elif isinstance(another,str): # convert the string to a basis state
            another = self.state_class(another)
            return self*another
    
    def __rmul__(self,ls):
        """
        multiply by a scalar : A*alpha
        """
        if debug: print ('operator_base.__rmul__')
        assert isinstance(ls,(int,float,complex,str))
        if isinstance(ls,(int,float,complex)):
            return self.__class__(self.op*ls) #  # A*alpha
        elif isinstance(ls,str):
            ls = bra(ls)
            return ls*self
    
    def __div__(self,num):
        """
        divide by a scalar A/alpha
        """
        assert isinstance(num,(int,float,complex))
        return self.__class__(self.op/num)
        
    def __truediv__(self,num):
        """
        divide by a scalar A/alpha
        """
        assert isinstance(num,(int,float,complex))
        return self.__class__(self.op/num)
        
    def __neg__(self): # -A
        """
        scalar negation -A
        """
        return (-1)*self
    
class state1(state_base):
    """Single particle
    """
    basis = ['|u>','|d>']
    
    def __init__(self,s):
        """initialize with either a basis ket, or a wave function
        """
        assert isinstance(s,(str,np.matrix))
        state_base.__init__(self)
        self.operator_class = operator1 # this state can be operated on by single particle operators
        self.n = 2
        self.basis = self.__class__.basis
        if isinstance(s,str):
            if s.startswith('<'): # it's a bra
                self.bra = True
                self.kind = 'bra'
                s = '|'+s[1:-1]+'>'
            assert s in self.basis
            self.name = s
            k = self.basis.index(s)
            self.phi = np.matrix([0.]*self.n).T # the wave function
            self.phi[k] = 1.
        else:
            assert s.shape == (2,1)
            self.phi = s
    
    def __pow__(self,other):
        """tensor product to create the next higher dimensional multiplet
        "a**b" = |a>|b> --> |ab>
        """
        assert isinstance(other,self.__class__)
        # r = (a |u> + b |d>) x (c |u> + d |d> )
        #   = ac |uu> +  ad |ud> + bc |du> + bd |dd>
        phi = (self.phi*other.phi.T).flatten().T
        return state2(phi)

class operator1(operator_base):
    ops = ['s0','sx','sy','sz']
    sig_0 = np.matrix([[1,0],[0,1]])
    sig_x = np.matrix([[0,1],[1,0]])
    sig_y = np.matrix([[0,-i],[i,0]])
    sig_z = np.matrix([[1,0],[0,-1]])
    op_mats = [sig_0,sig_x,sig_y,sig_z]

    def __init__(self,op):
        """initialize either with one of the Pauli spin operators
        or some arbirary matrix operator
        """
        assert isinstance(op,(str,np.matrix))
        self.basis = state1.basis
        self.state_class = state1 # this operator operates on single particle states
        if isinstance(op,str):
            assert op in self.ops
            self.name = op
            k = self.ops.index(op)
            self.op = self.__class__.op_mats[k]
        else:
            assert op.shape == (2,2)
            self.op = op
    
    def __pow__(self,another):
        """tensor product of operators to create an operator on the next higher dimensional multiplet
        "A**B" --> A(x)B
        """
        assert isinstance(another,self.__class__)
        op = []
        for k in range(2):
            row = []
            for l in range(2):
                row.append(self.op[k,l]*another.op)
            op.append(row)
        op = np.bmat(op)
        return operator2(op)

# entanglement
#  states are n-vectors, where n is the number of orthogonal states
#  For 2 particles, there are 4 orthogonal states. States are represented by a 4-vector

class state2(state_base):
    basis = ['|uu>','|ud>','|du>','|dd>']
    def __init__(self,s):
        assert isinstance(s,(str,np.matrix))
        state_base.__init__(self)
        self.n = 4
        self.basis = self.__class__.basis
        self.operator_class = operator2 # this 2 particle state can be operated on by 2-particle operators
        if isinstance(s,str):
            if s.startswith('<'): # it's a bra
                self.bra = True
                self.kind = 'bra'
                s = '|'+s[1:-1]+'>'
            assert s in self.basis
            self.name = s
            k = self.basis.index(s)
            self.phi = np.matrix([0.]*self.n).T
            self.phi[k] = 1.
        else:
            assert s.shape == (4,1)
            self.phi = s
    
    def density1(self):
        """density matrix for a single particle given the state of a pair
        """
        rho4 = self.density()
        rho_a = np.matrix(np.zeros((2,2)))
        rho_b = np.matrix(np.zeros((2,2)))
        for k in range(2):
            rho_a += rho4[k::2,k::2]
            rho_b += rho4[2*k:2*k+2,2*k:2*k+2]
        return [rho_a,rho_b]
    
    def correlation(self,A=None,B=None):
        """test if the two particles are entangled
        return the correlation.
        A non-zero correlation means the particles are entangled.
        """
        s = self
        assert s.kind == 'ket'
        if A is None:
            A = sz
        if B is None:
            B = sz
        c = bra(s)*((A**s0)*(s0**B))*s - (bra(s)*(A**s0)*s) * (bra(s)*(s0**B)*s)
        return c
    
    def entropy(self):
        """calculate the total Von Neumann entropy in
        the two particle system.
        A non zero entropy means the particles are entangled.
        """
        rho_a,rho_b = self.density1()
        return entropy(rho_a)+entropy(rho_b)
    
    def entangled(self,method='entropy'):
        """Test if entnagled.
        Return True or False
        method can be 'entropy' (default) or 'correlation'
        """
        if method == 'entropy':
            S = self.entropy()
            if np.isclose(S,0.):
                return False
            else:
                return True
        elif method == 'correlation':
            c = self.correlation()
            if np.isclose(c,0.):
                return False
            else:
                return True
    
class operator2(operator_base):
    ops = ['sigma_x','sigma_y','sigma_z','tau_x','tau_y','tau_z']
    def __init__(self,op):
        assert isinstance(op,(str,np.matrix))
        self.basis = state2.basis
        self.state_class = state2 # this operator operates on 2-particle states
        if isinstance(op,str):
            assert op in self.__class__.ops
            self.name = op
            if   op == 'sigma_x': op = sx**s0
            elif op == 'sigma_y': op = sy**s0
            elif op == 'sigma_z': op = sz**s0
            elif op == 'tau_x': op = s0**sx
            elif op == 'tau_y': op = s0**sy
            elif op == 'tau_z': op = s0**sz
            else:
                raise Exception('no op assigned for '+op)
            self.op = op.op
        elif isinstance(op,np.matrix):
            assert op.shape == (4,4)
            self.op = op

def ket(s):
    """generate a state vector given the state as a string or a wave function
    or generate the ket version of a bra vector
    """
    assert isinstance(s,(str,np.matrix,state_base))
    classes = [state1,state2]
    if isinstance(s,str):
        for clas in classes:
            if s in clas.basis:
                return clas(s)
    elif isinstance(s,np.matrix):
        for clas in classes:
            n = len(clas.basis)
            if s.shape == (n,1):
                return clas(s)
    elif isinstance(s,state_base):
        if not s.bra:
            return s
        s = s.__class__(s.phi.conj())
        s.bra = False
        s.kind = 'ket'
        s.basis = map(lambda ss: '|'+ss[1:-1]+'>',s.basis)
        return s
    raise Exception(s.__repr__()+' is not a valid state')

def bra(s):
    """generate a state vector given the state as a string or wave function
    or generate the bra version of a ket vector
    """
    assert isinstance(s,(str,np.matrix,state_base))
    classes = [state1,state2]
    if isinstance(s,str):
        s = '|'+s[1:-1]+'>' # turn it into a ket string
        s = ket(s)
        s.bra = True
        s.kind = 'bra'
        s.basis = map(lambda ss: '<'+ss[1:-1]+'|',s.basis)
        return s
    elif isinstance(s,np.matrix):
        s = ket(s)
        s.bra = True
        s.kind = 'bra'
        s.basis = map(lambda ss: '<'+ss[1:-1]+'|',s.basis)
        return s
    elif isinstance(s,state_base):
        if s.bra:
            return s
        s = s.__class__(s.phi.conj())
        s.bra = True
        s.kind = 'bra'
        s.basis = map(lambda ss: '<'+ss[1:-1]+'|',s.basis)
        return s        
    else:
        raise Exception(s.__repr__()+' is not a valid state')

def entropy(rho,frac=False,decohere=False):
    """calculate the Von Neumann entropy given the density matrix
    S = sum(p log(p)) where p are the density matrix eigenvalues
    If frac=True, return S/S_max where S_max = log(n) the max entropy.
    If decohere=True then assume decoherent population (off-diagonal elements are zero)
    """
    if decohere:
        w = np.diag(rho)
    else:
        w,v = np.linalg.eig(rho)
    n = w.size
    S = 0
    for k in range(n):
        if w[k] > 0 and not np.isclose(w[k],1.0):
            S -= w[k]*np.log(w[k])
    if frac:
        S_max = np.log(float(n))
        return S/S_max
    else:
        return S

#================ examples ==============

s0 = operator1('s0')
sx = operator1('sx')
sy = operator1('sy')
sz = operator1('sz')
u = state1('|u>')
d = state1('|d>')

uu = u**u
ud = u**d
du = d**u
dd = d**d
# singlet state
s = (ud - du).normalized()
# triplet states
t1 = uu
t2 = (ud + du).normalized()
t3 = dd

# spin of an electron
sx_e = sx/2.
sy_e = sy/2.
sz_e = sz/2.
spinx = (sx_e**s0) + (s0**sx_e)
spiny = (sy_e**s0) + (s0**sy_e)
spinz = (sz_e**s0) + (s0**sz_e)
spinx2 = spinx*spinx
spiny2 = spiny*spiny
spinz2 = spinz*spinz
spin2 = spinx2 + spiny2 + spinz2

def test_spin():
    """ calculate the spin of an electron and pairs of electrons
    """
    print ('spin of the electron along z axis is 1/2:')
    print (u.H*sz_e*u)
    print ('magnitude of the spin is sqrt(3)/2:')
    print ('  quantum number is J=1/2 so')
    print ('  spin = sqrt( J*(J+1) ) = sqrt( (1/2)*(3/2) ) = 0.866')
    print (np.sqrt( u.H*(sx_e*sx_e + sy_e*sy_e + sz_e*sz_e)*u ))
    print ('magnitude of spin of the singlet state is zero:')
    print (np.sqrt( s.H*spin2*s ))
    print ('magnitudes of spins of the triplet states are sqrt(2):')
    print ('  quantum number of paired triplet state is J=1 so')
    print ('  spin = sqrt( J*(J+1) ) = sqrt(2) = 1.414')
    print (np.sqrt( t1.H*spin2*t1 ))
    print (np.sqrt( t2.H*spin2*t2 ))
    print (np.sqrt( t3.H*spin2*t3 ))
    print ('spins of triplet states projected onto z axis:')
    print ('  these are the m quantum nummbers and should be +1, 0, -1')
    print (t1.H*spinz*t1)
    print (t2.H*spinz*t2)
    print (t3.H*spinz*t3)
    

def test_entangled(s = s):
    """ the argument can be any mixed state of two particles.
    the singlet state is the default argument.
    """
    print ('(perhaps) entangled state:')
    print (s)
    print ('Alice and Bob:')
    print (s.density())
    print ("Alice's view:")
    rhoA,rhoB = s.density1()
    print (rhoA)
    print ("Bob's view:")
    print (rhoB)
    print ("entropy of Alices's view")
    S = entropy(rhoA)
    S_frac = entropy(rhoA,frac=True)
    print ('S = %.3f which is %.1f%% of max entropy'%(S,S_frac*100))
    print ("entropy of Bob's view")
    S = entropy(rhoB)
    S_frac = entropy(rhoB,frac=True)
    print ('S = %.3f which is %.1f%% of max entropy'%(S,S_frac*100))
    print ('tests for entanglement')
    rho = s.density()
    rhoA = s.density1()[0]
    print ('density matrix trace test:')
    print ('trace(rho_Alice^2) =',np.trace(rhoA*rhoA))
    print ('(if it is < 1, the particles are entangled)')
    print ('correlation tests <AB> - <A><B>')
    cor = []
    scor = []
    for a,sa in zip([sx,sy,sz],['x','y','z']):
        cor_row = []
        scor_row = []
        for b,sb in zip([sx,sy,sz],['x','y','z']):
            scor_row.append('c'+sa+sb)
            sigma = (a**s0) # measures first particle without affecting 2nd
            tau = (s0**b) # measures second particle without affecting first
            c = s.H*(sigma*tau)*s - (s.H*sigma*s)*(s.H*tau*s)
            cor_row.append(c)
        scor.append(scor_row)
        cor.append(cor_row)
    cor = np.matrix(cor).real
    scor = np.matrix(scor)
    print ('correlation ')
    print (scor)
    print (cor)
    #         
    # cxx = s.H*((sx**s0)*(s0**sx))*s - (s.H*((sx**s0))*s)*(s.H*((s0**sx))*s)
    # cyy = s.H*((sy**s0)*(s0**sy))*s - (s.H*((sy**s0))*s)*(s.H*((s0**sy))*s)
    # czz = s.H*((sz**s0)*(s0**sz))*s - (s.H*((sz**s0))*s)*(s.H*((s0**sz))*s)
    # print 'correlation x,y,z = ',cxx,cyy,czz
    print ('(if any correlation != 0, the particles are entangled)')
