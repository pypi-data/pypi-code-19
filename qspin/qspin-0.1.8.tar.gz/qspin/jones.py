import numpy as np
import matplotlib.pyplot as plt

plt.ion()
pi = np.pi
exp = np.exp
cos = np.cos
sin = np.sin
i = 1j
sx = np.matrix([[0,1],[1,0]])
sy = np.matrix([[0,-i],[i,0]])
sz = np.matrix([[1,0],[0,-1]])
s0 = np.matrix([[1,0],[0,1]])

def jones(th,phi,color='blue'):
    J = [cos(th/2.),sin(th/2.)*exp(i*phi)]
    #norm = np.sqrt(J[0]**2 + J[1]**2)
    #J = [J[0]/norm,J[1]*exp(i*phi)/norm]
    t = np.linspace(0,2*pi,100)
    Ex,Ey = (J[0]*exp(i*t),J[1]*exp(i*t))
    x0 = Ex[0].real
    y0 = Ey[0].real
    x1 = Ex[1].real
    y1 = Ey[1].real
    dx = x1-x0
    dy = y1-y0
    first_one = True
    for x,y in zip(Ex.real,Ey.real):
        plt.plot([x0,x],[y0,y],color=color)
        x0,y0 = x,y
        if first_one:
            plt.arrow(x0,y0,dx,dy)
            first_one = False
        #plt.pause(.003)
    #plt.plot(Ex.real,Ey.real)
    plt.pause(.1)
    J = np.matrix([J[0],J[1]]).T
    a = [sin(th)*cos(phi),sin(th)*sin(phi),cos(th)]
    rho = 0.5*(s0 + a[0]*sx + a[1]*sy + a[2]*sz)
    return(J,a,rho)

def clr():
    plt.close('all')
    plt.figure()
    plt.plot([-1],[-1])
    plt.plot([1],[1])
    plt.xlim(-1,1)
    plt.ylim(-1,1)
    plt.axes().set_aspect('equal')
    plt.grid('on')

def vsphi():
    for phi in np.linspace(0,pi,9):
        jones(pi/4,phi)
    for phi in np.linspace(0,pi,9):
        jones(pi/8,phi)
    for phi in np.linspace(0,pi,9):
        jones(pi*3./8,phi)

def vsth():
    for th in np.linspace(0,pi/2,9):
        jones(th,pi/2.)
    for th in np.linspace(0,pi/2,9):
        jones(th,pi/4.)
    for th in np.linspace(0,pi/2,9):
        jones(th,pi*3./4.)

# This is the observable that measures the photon spin
# (eigenvalue +1 for |L>, -1 for |R>)
# It happens to be the same as Pauli sy
szc = 0.5*np.matrix([[1,-i],[i,1]]) - 0.5*np.matrix([[1,i],[-i,1]])

def photon():
    print '----------------'
    print '|H>'
    J,a,rho = jones(0,0,'blue')
    print 'J = ',J.T
    print 'a = ',a
    print 'rho = '
    print rho
    print 'spins'
    print np.trace(sx*rho),np.trace(sy*rho),np.trace(sz*rho)
    print '----------------'
    print '|V>'
    J,a,rho = jones(pi,0,'blue')
    print 'J = ',J.T
    print 'a = ',a
    print 'rho = '
    print rho
    print 'spins'
    print np.trace(sx*rho),np.trace(sy*rho),np.trace(sz*rho)
    print '----------------'
    print '|D> = |H>+|V>'
    J,a,rho = jones(pi/2,0,'green')
    print 'J = ',J.T
    print 'a = ',a
    print 'rho = '
    print rho
    print 'spins'
    print np.trace(sx*rho),np.trace(sy*rho),np.trace(sz*rho)
    print '----------------'
    print '|A> = |H>-|V>'
    J,a,rho = jones(pi/2,pi,'green')
    print 'J = ',J.T
    print 'a = ',a
    print 'rho = '
    print rho
    print 'spins'
    print np.trace(sx*rho),np.trace(sy*rho),np.trace(sz*rho)
    print '----------------'
    print '|L> = |H>+i|V>'
    J,a,rho = jones(pi/2,pi/2,'red')
    print 'J = ',J.T
    print 'a = ',a
    print 'rho = '
    print rho
    print 'spins'
    print np.trace(sx*rho),np.trace(sy*rho),np.trace(sz*rho)
    print '----------------'
    print '|R> = |H>-i|V>'
    J,a,rho = jones(pi/2,-pi/2,'red')
    print 'J = ',J.T
    print 'a = ',a
    print 'rho = '
    print rho
    print 'spins'
    print np.trace(sx*rho),np.trace(sy*rho),np.trace(sz*rho)
    print '----------------'

V = np.matrix([1,0]).T
H = np.matrix([0,1]).T
D = np.matrix([1,1]).T/np.sqrt(2.)
A = np.matrix([1,-1]).T/np.sqrt(2.)
L = np.matrix([1,i]).T/np.sqrt(2.)
R = np.matrix([1,-i]).T/np.sqrt(2.)

