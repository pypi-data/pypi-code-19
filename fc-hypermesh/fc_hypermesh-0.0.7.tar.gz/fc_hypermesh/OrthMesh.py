import numpy as np
from fc_tools.others import isModuleFound,LabelBaseName

class OrthMesh:
  """ Meshing with d-simplices or d-orthotopes elements of a d-orthotope
  
  Let [a_1,b_1]x...x[a_d,b_d] be the d-orthotope to mesh.
  
  Attributes:
      d (int): space dimension.
      N (int): number of discretization in each space dimension. Can also be a list of d intergers: 
               one value by space dimension.
      type (str):  type of the mesh elements, 'simplicial'(default) or 'orthotope'.
      box (d-by-2 numpy array): a_i=box[i-1][0] and b_i=box[i-1][1].
      Mesh (EltMesh object): EltMesh object with Mesh.m==d
      Faces (2d-list of EltMesh): ...
  """
  
  def __init__(self,d,N,**kwargs):
    import fc_hypermesh.CartesianGrid as CG
    from fc_hypermesh.EltMesh import EltMesh
    from fc_tools.colors import selectColors

    ctype=kwargs.get('type', 'simplicial' )
    box=kwargs.get('box',np.ones((d,1))*np.array([0,1]))
    m_min=kwargs.get('m_min',0)
    mapping=kwargs.get('mapping',None)

    N=np.atleast_1d(N)
    assert len(N)==1 or len(N)==d
    if len(N)==1:
      N=N[0]*np.ones(d)
    if (ctype=='orthotope'):
      funMesh = lambda N: CG.TessHyp(N)
      funFaces = lambda N,m: CG.TessFaces(N,m)
      ntype=1
    else: # default 'simplicial'
      funMesh = lambda N: CG.Triangulation(N)
      funFaces = lambda N,m: CG.TriFaces(N,m)
      ntype=0
    self.d=d
    self.box=np.array(box)
    assert self.box.shape==(d,2)
    self.type=ctype
    [q,me]=funMesh(N)
    trans=lambda Q: MappingBox(Q,N,box)
    if mapping is not None:
      my_mapp=lambda Q: mapping(trans(Q))
    else:
      my_mapp=trans
    self.Mesh=EltMesh(d,d,my_mapp(q),me,None,label=1,type=ntype)
    self.set_box()
    self.Faces=[]
    for m in np.arange(d-1,m_min-1,-1):
      sTh=funFaces(N,m)
      nsTh=len(sTh)
      colors = selectColors(nsTh)
      Fh=[]
      for j in np.arange(nsTh):
        Fh.append(EltMesh(d,m,my_mapp(sTh[j].q),sTh[j].me,sTh[j].toGlobal,label=j+1,color=colors[j],type=ntype))
      self.Faces.append(Fh)
      
  def __repr__(self):
    strret = ' %s object \n'%self.__class__.__name__ 
    strret += '      d : %d\n'%self.d 
    strret += '  Mesh  : %s\n'%str(self.Mesh)
    for F in self.Faces:
      strret += ' Number of %d-faces : %d\n'%(F[0].m,len(F))
      i=0
      for f in F:
        strret += '   [%2d] (type,nq,nme) : (%s,%d,%d)\n'%(i,f.strtype(),f.nq,f.nme)
        i+=1
      
    #strret += '    nme : %d\n'%self.get_nme()
    #strret += '    sTh : %s of %d %s\n'%(self.sTh.__class__.__name__,len(self.sTh),self.sTh[0].__class__.__name__)
    #strret += '   nsTh : %d\n'%self.nsTh
    #strret += 'sThsimp : %s %s\n'%(str(self.sThsimp.shape),self.sThsimp.__class__.__name__)
    #strret += '   '+np.array_str(self.sThsimp).replace('\n','\n          ')+'\n'
    #strret += ' sThlab : %s %s\n'%(str(self.sThlab.shape),self.sThlab.__class__.__name__)
    #strret += '   '+np.array_str(self.sThlab).replace('\n','\n          ')+'\n'
    return strret         
   
  def getFacesIndex(self,m): # must be improved
    A=np.array(np.arange(self.d-1,-1,-1))
    return np.where(A==m)[0][0]
  
  def set_box(self):
    for i in range(self.d):
      self.box[i,0]=np.min(self.Mesh.q[i])
      self.box[i,1]=np.max(self.Mesh.q[i])
   
  def plotmesh(self,**kwargs):
    if not isModuleFound('matplotlib'):
      print('plotmesh needs matplotlib package!')
      return
    import matplotlib.pyplot as plt
    #from fc_tools.graphics import set_axes_equal
    if self.d > 3:
      print('Unable to plot in dimension %d > 3!'%self.d)
      return
    #m=kwargs.get('m', self.d );kwargs.pop('m',None)
    #legend=kwargs.get('legend', False);kwargs.pop('legend',None)
    m=kwargs.pop('m',self.d)
    assert m in range(self.d+1)
    legend=kwargs.pop('legend', False);
    fig=plt.gcf()
    if m==self.d:
      Legend_handle,Labels=self.Mesh.plotmesh(**kwargs)
      Legend_handle=[Legend_handle]
      Labels=[Labels]
    else:
      Legend_handle=[];Labels=[]
      idx=self.getFacesIndex(m)
      F=self.Faces[idx]
      nF=len(F);
      for i in range(nF):
        Leg,Lab=F[i].plotmesh(**kwargs)
        Legend_handle.append(Leg)
        Labels.append(Lab)
    fig = plt.gcf()
    ax=fig.axes[0]
    if self.d==3:
      ax.set_zlim(self.box[2,0],self.box[2,1])
    ax.set_xlim(self.box[0,0],self.box[0,1])
    ax.set_ylim(self.box[1,0],self.box[1,1]) 
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    if self.d==3:
      ax.set_zlabel('z')
    #-> No background
    ax.patch.set_facecolor('None')
    fig.patch.set_visible(False) 
    #<-
    if legend:
      plt.legend(Legend_handle,Labels,loc='best', ncol=int(len(Legend_handle)/10)+1).draggable()
      
def MappingBox(q,N,box):
  box=np.array(box)
  d=len(N)
  for i in range(d):
    q[i]=box[i,0]+(box[i,1]-box[i,0])/N[i]*q[i]
  return q