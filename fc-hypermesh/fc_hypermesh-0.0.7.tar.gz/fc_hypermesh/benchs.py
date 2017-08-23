import time
from . import OrthMesh

def bench_gen(d,ctype,Box,LN):
  #d=3
  #ctype='simplicial'
  #Box=[[-1,1],[-1,1],[-1,1]]
  #LN=range(20,170,20)
  Oh=OrthMesh(d,2,type=ctype,box=Box) # To force compilation
  print('# BENCH in dimension %d with %s mesh'%(d,ctype))
  print('#d: %d'%d)
  print('#type: %s'%ctype)
  print('#box: %s'%str(Box))
  print('#desc:  N        nq       nme    time(s)')
  for N in LN:
    tstart=time.time()
    Oh=OrthMesh(d,N,type=ctype,box=Box)
    t=time.time()-tstart
    print('     %4d  %8d  %8d     %2.3f'%(N,Oh.Mesh.nq,Oh.Mesh.nme,t))
    
def bench01():
  d=3
  ctype='simplicial'
  Box=[[-1,1],[-1,1],[-1,1]]
  LN=range(20,170,20)
  bench_gen(d,ctype,Box,LN)