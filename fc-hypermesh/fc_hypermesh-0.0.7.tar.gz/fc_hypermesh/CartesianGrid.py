import numpy as np
import itertools
from math import factorial

def perms(L):
  # perms(range(3))
  #return np.array([x for x in itertools.permutations(np.flipud(L),len(L))])
  return np.array([x for x in itertools.permutations(L,len(L))])

def comb(n,k):
  return np.array([x for x  in itertools.combinations(np.arange(n),k)])

def betafunc(N):
  N=np.array(N,dtype=int)
  d=len(N)
  beta=np.insert(np.cumprod(N[:-1]+1),0,1)
  return beta

def points(N):
  N=np.array(N,dtype=int)
  d=len(N)
  beta=betafunc(N)
  q=np.zeros((d,np.prod(N+1)))
  for r in range(d):
    A=np.tile(np.arange(N[r]+1),(beta[r],1)).flatten(1)
    q[r,:]=np.tile(A,(1,np.prod(N[r+1:]+1)))
  return q

def TessHyp(N):
  N=np.array(N,dtype=int)
  d=len(N)
  beta=betafunc(N)
  q=points(N)
  Hinv=points(N-1)
  qhat=points(np.ones(d))
  ibase=beta.dot(Hinv)
  me=np.zeros((2**d,len(ibase)),dtype=np.int)
  for l in range(2**d):
    me[l,:]=ibase+beta.dot(qhat[:,l])
  return q,me

def Triangulation(N):
  from fc_hypermesh.Hypercube import KuhnTriangulation
  N=np.array(N)
  d=len(N)
  q=points(N)
  Hinv=points(N-1)
  Nh=Hinv.shape[1]
  beta=betafunc(N)
  ibase=beta.dot(Hinv)
  qK,meK=KuhnTriangulation(d)
  fd=factorial(d)
  me=np.zeros((d+1,fd*Nh),dtype=int)
  Idx=fd*np.arange(Nh)
  for j in range(d+1):
    for l in range(fd):
      me[j,Idx+l]=ibase+beta.dot(qK[:,meK[j,l]])
  return q,me

class smallTh:
  def __init__(self,q,me,ind):
    self.q=q
    self.me=np.array(me,dtype=int)
    self.dim=q.shape[0]
    self.d=me.shape[0]-1
    #self.toGlobal=np.array(ind).astype(int)
    self.toGlobal=np.array(ind,dtype=int)
    
  def __repr__(self):
    strret = ' %s object \n'%self.__class__.__name__ 
    strret += '       d : %d\n'%self.d 
    strret += '     dim : %d\n'%self.dim 
    strret += '       q : (%d,%d)\n'%self.q.shape
    strret += '      me : (%d,%d)\n'%self.me.shape
    strret += 'toGlobal : (%d,)\n'%self.toGlobal.shape
    return strret  
    
def TriFaces(N,m):
  N=np.array(N,dtype=int)
  d=len(N)
  level=d-m
  beta=betafunc(N)
  sTh=[]
  if m==0:
    Q=np.diag(N).dot(points(np.ones(d)))
    ind=beta.dot(Q).astype(int)
    for k in range(Q.shape[1]):
      #sTh.append(smallTh(np.array([Q[:,k]]).T,np.array([[0]]),[int(ind[k])]))
      sTh.append(smallTh(np.array([Q[:,k]]).T,np.array([[0]]),ind[k]))
    return sTh
  S=points(np.ones(level))
  L=comb(d,d-m)
  nc=L.shape[0]
  R=np.flipud(comb(d,m))
  for l in range(nc):
    qw,mew=Triangulation(N[R[l,:]])
    nq=qw.shape[1]
    for r in range(2**level):
      q=np.zeros((d,nq))
      q[R[l],:]=qw
      tmp=np.matrix(N[L[l,:]].T*S[:,r]).T
      q[L[l],:]=tmp*np.ones(nq)
      sTh.append(smallTh(q,mew,beta.dot(q)))
  return sTh

def TessFaces(N,m):
  N=np.array(N,dtype=int)
  d=len(N)
  level=d-m
  beta=betafunc(N)
  sTh=[]
  if m==0:
    Q=np.diag(N).dot(points(np.ones(d)))
    ind=beta.dot(Q)
    for k in range(Q.shape[1]):
      sTh.append(smallTh(np.array([Q[:,k]]).T,np.array([[0]]),[int(ind[k])]))
    return sTh
  S=points(np.ones(level))
  L=comb(d,d-m)
  nc=L.shape[0]
  R=np.flipud(comb(d,m))
  for l in range(nc):
    qw,mew=TessHyp(N[R[l,:]])
    nq=qw.shape[1]
    for r in range(2**level):
      q=np.zeros((d,nq))
      q[R[l],:]=qw
      tmp=np.matrix(N[L[l,:]].T*S[:,r]).T
      q[L[l],:]=tmp*np.ones(nq)
      sTh.append(smallTh(q,mew,beta.dot(q)))
  return sTh