""" demos of the OrthMesh class (see fc_hypermesh.OrthMesh module)

Usage information
=================
There are seven available functions:

    1. demo01: [-1,1]x[-1,1]x[-1,1] meshing by orthotopes
    2. demo02: [-1,1]x[-1,1] meshing by orthotopes
    3. demo03: [-1,1]x[0,1]x[0,2] meshing by orthotopes
    4. demo04: [-1,1]x[0,1] meshing by simplices
    5. demo05: [0,1]x[0,1] mapped by (x,y)->(2*x,y) and meshed by simplices
    6. demo06: [0,1]x[0,1] mapped by (x,y)->(20*x,2*(2*y-1+cos(2*pi*x))) 
       and meshed by simplices
    7. demo07: [0,1]x[0,1]x[0,1] mapped by 
       (x,y,z)->(x+sin(4*pi*y),10*y-1,z+cos(4*pi*y)) 
       and meshed by simplices
    
Example 1
---------
>>>   import fc_hypermesh.demos
>>>   demos.demo03()

"""
from fc_tools.colors import str2rgb
from fc_tools.others import isModuleFound
from .OrthMesh import OrthMesh

if isModuleFound('matplotlib'):
  import matplotlib.pyplot as plt
  from fc_tools.graphics import DisplayFigures,set_axes_equal


def demo01():
  """ OrthMesh  """
  print('------ demo01 --------')
  print("oTh=OrthMesh(3,5,type='orthotope',box=[[-1,1],[-1,1],[-1,1]])")
  print('----------------------')
  oTh=OrthMesh(3,5,type='orthotope',box=[[-1,1],[-1,1],[-1,1]])
  print(oTh)
  
  if isModuleFound('matplotlib'):
    plt.ion()
    plt.figure(1)
    plt.clf()
    oTh.plotmesh(legend=True)
    set_axes_equal()

    plt.figure(2)
    plt.clf()
    oTh.plotmesh(m=2,legend=True,edgecolor=[0,0,0])
    set_axes_equal()
    plt.axis('off')

    plt.figure(3)
    plt.clf()
    oTh.plotmesh(m=2,facecolor=None,edgecolor=str2rgb('LightGray'))
    oTh.plotmesh(m=1,legend=True,linewidth=2)
    set_axes_equal()
    plt.axis('off')

    plt.figure(4)
    plt.clf()
    oTh.plotmesh(m=1,color='black')
    oTh.plotmesh(m=0,legend=True,s=55) # see matplotlib.pyplot.scatter options
    set_axes_equal()
    plt.axis('off')

    DisplayFigures(screen=1)
  
  
def demo02():
  print('------ demo02 --------')
  print("oTh=OrthMesh(2,5,type='orthotope',box=[[-1,1],[-1,1]])")
  print('----------------------')
  oTh=OrthMesh(2,5,type='orthotope',box=[[-1,1],[-1,1]])
  print(oTh)
  
  if isModuleFound('matplotlib'):
    plt.close('all')
    plt.ion()
    plt.figure(1)
    plt.clf()
    oTh.plotmesh(legend=True)
    set_axes_equal()

    plt.figure(2)
    plt.clf()
    oTh.plotmesh(m=1,legend=True,linewidth=3)
    set_axes_equal()
    plt.axis('off')


    plt.figure(3)
    plt.clf()
    oTh.plotmesh(m=1,color='black')
    oTh.plotmesh(m=0,legend=True,s=105) # see matplotlib.pyplot.scatter options
    set_axes_equal()
    plt.axis('off')
    DisplayFigures(screen=1)
  
  
def demo03():
  print('------ demo03 --------')
  print("oTh=OrthMesh(3,[10,5,10],box=[[-1,1],[0,1],[0,2]])")
  print('----------------------')
  oTh=OrthMesh(3,[10,5,10],box=[[-1,1],[0,1],[0,2]])
  print(oTh)
  
  if isModuleFound('matplotlib'):
    plt.close('all')
    plt.ion()
    plt.figure(1)
    plt.clf()
    oTh.plotmesh(legend=True,linewidth=0.5)
    set_axes_equal()

    plt.figure(2)
    plt.clf()
    oTh.plotmesh(m=2,legend=True,edgecolor=[0,0,0])
    set_axes_equal()
    plt.axis('off')

    plt.figure(3)
    plt.clf()
    oTh.plotmesh(m=2,edgecolor=[0,0,0],color='none')
    oTh.plotmesh(m=1,legend=True,linewidth=2,alpha=0.3)
    set_axes_equal()
    plt.axis('off')

    plt.figure(4)
    plt.clf()
    oTh.plotmesh(m=1,color='black',alpha=0.3)
    oTh.plotmesh(m=0,legend=True,s=55)
    set_axes_equal()
    plt.axis('off')

    DisplayFigures(screen=1)
  
def demo04():
  print('------ demo04 --------')
  print("oTh=OrthMesh(2,10,type='simplicial',box=[[-1,1],[0,1]])")
  print('----------------------')
  oTh=OrthMesh(2,10,type='simplicial',box=[[-1,1],[0,1]])
  print(oTh)
  
  if isModuleFound('matplotlib'):
    plt.close('all')
    plt.ion()
    
    plt.figure(1)
    plt.clf()
    oTh.plotmesh(legend=True)
    set_axes_equal()

    plt.figure(2)
    plt.clf()
    oTh.plotmesh(m=1,legend=True,linewidth=3)
    plt.axis('off')
    set_axes_equal()

    plt.figure(3)
    plt.clf()
    oTh.plotmesh(m=1,color='black')
    oTh.plotmesh(m=0,legend=True,s=105) # see matplotlib.pyplot.scatter options
    plt.axis('off')
    set_axes_equal()

    DisplayFigures(screen=1)
  
def demo05():
  print('------ demo05 --------')
  print('trans=lambda q: np.array([2*q[0],q[1]])')
  print("oTh=OrthMesh(2,5,type='simplicial',mapping=trans)")
  print('----------------------')
  trans=lambda q: np.array([2*q[0],q[1]])
  oTh=OrthMesh(2,5,type='simplicial',mapping=trans)
  print(oTh)
  
  if isModuleFound('matplotlib'):
    plt.close('all')
    plt.ion()
    plt.figure(1)
    plt.clf()
    oTh.plotmesh(legend=True)
    set_axes_equal()

    plt.figure(2)
    plt.clf()
    oTh.plotmesh(color='lightgray')
    oTh.plotmesh(m=1,legend=True,linewidth=3)
    plt.axis('equal')
    plt.axis('off')

    plt.figure(3)
    plt.clf()
    oTh.plotmesh(color='lightgray')
    oTh.plotmesh(m=1,color='black')
    oTh.plotmesh(m=0,legend=True,s=105) # see matplotlib.pyplot.scatter options
    plt.axis('equal')
    plt.axis('off')

    DisplayFigures(screen=1)  
  
def demo06():
  print('------ demo06 --------')
  print('trans=lambda q: np.array([20*q[0],2*(2*q[1]-1+np.cos(2*np.pi*q[0]))])')
  print("oTh=OrthMesh(2,[100,20],type='simplicial',mapping=trans")
  print('----------------------')
  trans=lambda q: np.array([20*q[0],2*(2*q[1]-1+np.cos(2*np.pi*q[0]))])
  oTh=OrthMesh(2,[100,20],type='simplicial',mapping=trans)
  print(oTh)

  if isModuleFound('matplotlib'):
    plt.close('all')
    plt.ion()
    plt.figure(1)
    plt.clf()
    oTh.plotmesh(legend=True)
    plt.axis('equal')

    plt.figure(2)
    plt.clf()
    oTh.plotmesh(color='lightgray')
    oTh.plotmesh(m=1,legend=True,linewidth=3)
    plt.axis('equal')
    plt.axis('off')

    plt.figure(3)
    plt.clf()
    oTh.plotmesh(color='lightgray')
    oTh.plotmesh(m=1,color='black')
    oTh.plotmesh(m=0,legend=True,s=105) # see matplotlib.pyplot.scatter options
    plt.axis('equal')
    plt.axis('off')

    DisplayFigures(screen=1)
  
def demo07():
  print('------ demo05 --------')
  print('trans=lambda q: np.array([q[0]+np.sin(4*np.pi*q[1]), 10*q[1]-1, q[2]+np.cos(4*np.pi*q[1])])')
  print("oTh=OrthMesh(3,[3,25,3],type='simplicial',mapping=trans)")
  print('----------------------')
  trans=lambda q: np.array([q[0]+np.sin(4*np.pi*q[1]), 10*q[1]-1, q[2]+np.cos(4*np.pi*q[1])])
  oTh=OrthMesh(3,[3,25,3],type='simplicial',mapping=trans)
  print(oTh)
  
  if isModuleFound('matplotlib'):
    plt.close('all')
    plt.ion()
    plt.figure(1)
    plt.clf()
    oTh.plotmesh(legend=True)
    set_axes_equal()

    plt.figure(2)
    plt.clf()
    oTh.plotmesh(m=2,legend=True,edgecolor=[0,0,0])
    set_axes_equal()

    plt.figure(3)
    plt.clf()
    oTh.plotmesh(m=2,edgecolor='lightgray',facecolor=None,alpha=0.3)
    oTh.plotmesh(m=1,legend=True,linewidth=2)
    set_axes_equal()

    plt.figure(4)
    plt.clf()
    oTh.plotmesh(m=1,color='black')
    oTh.plotmesh(m=0,legend=True,s=55)
    set_axes_equal()

    DisplayFigures(screen=1)