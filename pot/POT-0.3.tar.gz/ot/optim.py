# -*- coding: utf-8 -*-
"""
Optimization algorithms for OT
"""

import numpy as np
from scipy.optimize.linesearch import scalar_search_armijo
from .lp import emd
from .bregman import sinkhorn

# The corresponding scipy function does not work for matrices
def line_search_armijo(f,xk,pk,gfk,old_fval,args=(),c1=1e-4,alpha0=0.99):
    """
    Armijo linesearch function that works with matrices

    find an approximate minimum of f(xk+alpha*pk) that satifies the
    armijo conditions.

    Parameters
    ----------

    f : function
        loss function
    xk : np.ndarray
        initial position
    pk : np.ndarray
        descent direction
    gfk : np.ndarray
        gradient of f at xk
    old_fval : float
        loss value at xk
    args : tuple, optional
        arguments given to f
    c1 : float, optional
        c1 const in armijo rule (>0)
    alpha0 : float, optional
        initial step (>0)

    Returns
    -------
    alpha : float
        step that satisfy armijo conditions
    fc : int
        nb of function call
    fa : float
        loss value at step alpha

    """
    xk = np.atleast_1d(xk)
    fc = [0]

    def phi(alpha1):
        fc[0] += 1
        return f(xk + alpha1*pk, *args)

    if old_fval is None:
        phi0 = phi(0.)
    else:
        phi0 = old_fval

    derphi0 = np.sum(pk*gfk) # Quickfix for matrices
    alpha,phi1 = scalar_search_armijo(phi,phi0,derphi0,c1=c1,alpha0=alpha0)

    return alpha,fc[0],phi1


def cg(a,b,M,reg,f,df,G0=None,numItermax = 200,stopThr=1e-9,verbose=False,log=False):
    """
    Solve the general regularized OT problem with conditional gradient

        The function solves the following optimization problem:

    .. math::
        \gamma = arg\min_\gamma <\gamma,M>_F + reg*f(\gamma)

        s.t. \gamma 1 = a

             \gamma^T 1= b

             \gamma\geq 0
    where :

    - M is the (ns,nt) metric cost matrix
    - :math:`f` is the regularization term ( and df is its gradient)
    - a and b are source and target weights (sum to 1)

    The algorithm used for solving the problem is conditional gradient as discussed in  [1]_


    Parameters
    ----------
    a : np.ndarray (ns,)
        samples weights in the source domain
    b : np.ndarray (nt,)
        samples in the target domain
    M : np.ndarray (ns,nt)
        loss matrix
    reg : float
        Regularization term >0
    G0 :  np.ndarray (ns,nt), optional
        initial guess (default is indep joint density)
    numItermax : int, optional
        Max number of iterations
    stopThr : float, optional
        Stop threshol on error (>0)
    verbose : bool, optional
        Print information along iterations
    log : bool, optional
        record log if True

    Returns
    -------
    gamma : (ns x nt) ndarray
        Optimal transportation matrix for the given parameters
    log : dict
        log dictionary return only if log==True in parameters


    References
    ----------

    .. [1] Ferradans, S., Papadakis, N., Peyré, G., & Aujol, J. F. (2014). Regularized discrete optimal transport. SIAM Journal on Imaging Sciences, 7(3), 1853-1882.

    See Also
    --------
    ot.lp.emd : Unregularized optimal ransport
    ot.bregman.sinkhorn : Entropic regularized optimal transport

    """

    loop=1

    if log:
        log={'loss':[]}

    if G0 is None:
        G=np.outer(a,b)
    else:
        G=G0

    def cost(G):
        return np.sum(M*G)+reg*f(G)

    f_val=cost(G)
    if log:
        log['loss'].append(f_val)

    it=0

    if verbose:
        print('{:5s}|{:12s}|{:8s}'.format('It.','Loss','Delta loss')+'\n'+'-'*32)
        print('{:5d}|{:8e}|{:8e}'.format(it,f_val,0))

    while loop:

        it+=1
        old_fval=f_val


        # problem linearization
        Mi=M+reg*df(G)
        # set M positive
        Mi+=Mi.min()

        # solve linear program
        Gc=emd(a,b,Mi)

        deltaG=Gc-G

        # line search
        alpha,fc,f_val = line_search_armijo(cost,G,deltaG,Mi,f_val)

        G=G+alpha*deltaG

        # test convergence
        if it>=numItermax:
            loop=0

        delta_fval=(f_val-old_fval)/abs(f_val)
        if abs(delta_fval)<stopThr:
            loop=0


        if log:
            log['loss'].append(f_val)

        if verbose:
            if it%20 ==0:
                print('{:5s}|{:12s}|{:8s}'.format('It.','Loss','Delta loss')+'\n'+'-'*32)
            print('{:5d}|{:8e}|{:8e}'.format(it,f_val,delta_fval))


    if log:
        return G,log
    else:
        return G

def gcg(a,b,M,reg1,reg2,f,df,G0=None,numItermax = 10,numInnerItermax = 200,stopThr=1e-9,verbose=False,log=False):
    """
    Solve the general regularized OT problem with the generalized conditional gradient

        The function solves the following optimization problem:

    .. math::
        \gamma = arg\min_\gamma <\gamma,M>_F + reg1\cdot\Omega(\gamma) + reg2\cdot f(\gamma)

        s.t. \gamma 1 = a

             \gamma^T 1= b

             \gamma\geq 0
    where :

    - M is the (ns,nt) metric cost matrix
    - :math:`\Omega` is the entropic regularization term :math:`\Omega(\gamma)=\sum_{i,j} \gamma_{i,j}\log(\gamma_{i,j})`
    - :math:`f` is the regularization term ( and df is its gradient)
    - a and b are source and target weights (sum to 1)

    The algorithm used for solving the problem is the generalized conditional gradient as discussed in  [5,7]_


    Parameters
    ----------
    a : np.ndarray (ns,)
        samples weights in the source domain
    b : np.ndarray (nt,)
        samples in the target domain
    M : np.ndarray (ns,nt)
        loss matrix
    reg1 : float
        Entropic Regularization term >0
    reg2 : float
        Second Regularization term >0
    G0 :  np.ndarray (ns,nt), optional
        initial guess (default is indep joint density)
    numItermax : int, optional
        Max number of iterations
    numInnerItermax : int, optional
        Max number of iterations of Sinkhorn
    stopThr : float, optional
        Stop threshol on error (>0)
    verbose : bool, optional
        Print information along iterations
    log : bool, optional
        record log if True

    Returns
    -------
    gamma : (ns x nt) ndarray
        Optimal transportation matrix for the given parameters
    log : dict
        log dictionary return only if log==True in parameters


    References
    ----------

    .. [5] N. Courty; R. Flamary; D. Tuia; A. Rakotomamonjy, "Optimal Transport for Domain Adaptation," in IEEE Transactions on Pattern Analysis and Machine Intelligence , vol.PP, no.99, pp.1-1
    .. [7] Rakotomamonjy, A., Flamary, R., & Courty, N. (2015). Generalized conditional gradient: analysis of convergence and applications. arXiv preprint arXiv:1510.06567.

    See Also
    --------
    ot.optim.cg : conditional gradient

    """

    loop=1

    if log:
        log={'loss':[]}

    if G0 is None:
        G=np.outer(a,b)
    else:
        G=G0

    def cost(G):
        return np.sum(M*G)+ reg1*np.sum(G*np.log(G)) + reg2*f(G)

    f_val=cost(G)
    if log:
        log['loss'].append(f_val)

    it=0

    if verbose:
        print('{:5s}|{:12s}|{:8s}'.format('It.','Loss','Delta loss')+'\n'+'-'*32)
        print('{:5d}|{:8e}|{:8e}'.format(it,f_val,0))

    while loop:

        it+=1
        old_fval=f_val


        # problem linearization
        Mi=M+reg2*df(G)

        # solve linear program with Sinkhorn
        #Gc = sinkhorn_stabilized(a,b, Mi, reg1, numItermax = numInnerItermax)
        Gc = sinkhorn(a,b, Mi, reg1, numItermax = numInnerItermax)

        deltaG=Gc-G

        # line search
        dcost=Mi+reg1*(1+np.log(G)) #??
        alpha,fc,f_val = line_search_armijo(cost,G,deltaG,dcost,f_val)

        G=G+alpha*deltaG

        # test convergence
        if it>=numItermax:
            loop=0

        delta_fval=(f_val-old_fval)/abs(f_val)
        if abs(delta_fval)<stopThr:
            loop=0


        if log:
            log['loss'].append(f_val)

        if verbose:
            if it%20 ==0:
                print('{:5s}|{:12s}|{:8s}'.format('It.','Loss','Delta loss')+'\n'+'-'*32)
            print('{:5d}|{:8e}|{:8e}'.format(it,f_val,delta_fval))


    if log:
        return G,log
    else:
        return G

