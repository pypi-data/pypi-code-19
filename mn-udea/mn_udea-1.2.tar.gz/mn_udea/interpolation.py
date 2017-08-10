import numpy as np

def InterLin(x,y,p):
    """ 
    Interpolación Lineal.
    Esta función entrega el f(p) a partir de los datos de entrada.
    
    Donde:
        x: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada
        p: es el punto sobre el cual quiero conocer el valor f(p)
    """
    x = np.array(x);
    y = np.array(y);
    fp = y[0]+ ((y[1]-y[0])*(p-x[0])/(x[1]-x[0]));
    return(fp)
def Inter2(x,y,p):
    """
    Interpolación Cuadrática.
    Esta función entrega el f(p) a partir de los datos de entrada y adoptando
    polinomio de segundo grado.
    
    IMPORTANTE: para poder realizar la interpolación, el tamaño de x y y debe
    ser de 3 datos
    
    Donde:
        x: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada
        p: es el punto sobre el cual quiero conocer el valor f(p)
    
    
    """
    x = np.array(x);
    y = np.array(y);
    b0 = y[0];
    b1 = (y[1]-y[0])/(x[1]-x[0]);
    b2 = (((y[2]-y[1])/(x[2]-x[1]))-b1)/(x[2]-x[0]);
    fp = b0 + b1*(p-x[0]) + b2*(p-x[0])*(p-x[1]);
    return(fp)
def DifDiv(x,y,p):
    """
    Polinomios de Interpolación de Newton: Diferencias divididas.
    
    Esta función entrega el f(p) a partir de los datos de entrada y se asume 
    como grado de la función interpolante, el que corresponda a n-1 datos de
    entrada.
    
    Donde:
        x: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada
        p: es el punto sobre el cual quiero conocer el valor f(p) 
    
    """
    x = np.array(x);
    y = np.array(y);
    l = len(x);
    mat = np.zeros([l-1,l-1]);
    vec = [];
    for j in range(0,l-1):
        i=j+1;
        vec.append((y[i]-y[j])/(x[i]-x[j]))
    mat[:,0]=np.transpose(vec);             
         
    c = 2;                       
    for j in range(1,l-1):
        for i in range(l-1-j):
            mat[i,j]=(mat[i+1,j-1]-mat[i,j-1])/(x[i+c]-x[i]);
        c=c+1;
    coef = mat[0,:];
    mat2 = np.ones([len(coef),len(coef)])
    for j in range(len(coef)):
        for i in range(len(coef)-j):
            mat2[i,j] = p-x[i]
    coe=np.prod(mat2,axis=0);
    ccoe = np.zeros([len(coe)])
    for i in range(len(coe)):
        ccoe[i]= coe[len(coe)-1-i]
    fp = np.sum(ccoe*coef)
    fp = fp + y[0];
    return(fp)
def Lagrange(x,y,p,grado):
    """
    Polinomio de Interpolación de Lagrange
    
    Esta función entrega el f(p) a partir de los datos de entrada y el grado
    de la función interpolante.
    
    Donde:
        x: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada
        p: es el punto sobre el cual quiero conocer el valor f(p)
        grado: grado del polinomio interpolante
    
    """
    x = np.array(x)
    y = np.array(y)
    if(grado>= len(x)):
        print('no se puede obtener polinomio, revise grado de polinomio')
    else:
        mat= np.zeros([grado+1,grado+1])
        for j in range(grado+1):
            for i in range(grado+1):
                if(i==j):
                    mat[i,j] = 1
                else:
                    mat[i,j] = (p-x[i])/(x[j]-x[i])
        coef = np.prod(mat, axis=0)
        ffp = []
        for i in range(grado+1):
           ffp.append(coef[i]*y[i])
        fp = np.sum(ffp)
        return(fp)
def cpoly(x,y,grado):
    """
    Coeficientes de Polinomio interpolante
    
    Esta función entrega los coeficientes en orden ascendente de un polinomio 
    de grado n. (desde a0 hasta an).
    
    y = a0 + a1*x + ... + an*xn
    
    Donde: 
        x: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada
        grado: grado del polinomio interpolante
        
    NOTA: Debe tener cuidado al usar la función para polinomios de orden 
    superior, pues puede resultar inexactitudes considerables.
        
    """
    x = np.array(x)
    y = np.array(y)
    if(grado>= len(x)):
        print('no se puede obtener polinomio, revise grado de polinomio')
    else:
        mat = np.zeros([grado+1,grado+1])
        for i in range(grado+1):
            for j in range(grado+1):
                mat[i,j] = x[i]**j
        fp = np.matrix(np.linalg.inv(mat))*np.transpose(np.matrix(y))
        return(fp)
def TrazLin(x,y):
    """
    Trazador Lineal
    
    Esta función entrega un conjunto de n ecuaciones de rectas donde n+1 es la
    cantidad de datos ingresados denominadas también trazadores lineales. Los
    datos se entregan en forma de vectores así:
        
        
                        [m0 m1 m2 ... mn], [b0 b1 b2 ... bn]
    
    Donde:
        x: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada       
    
    
    f(x)= m0*x + b0          x0<=x<=x1
    f(x)= m1*x + b1          x1<=x<=x2
    f(x)= m2*x + b2          x1<=x<=x2
    f(x)= mn*x + bn          x(n-1)<=x<=x(n)
    
    NOTA: Cada función sólo es válida en la región comprendida como se ilustra 
    en el conjunto de ecuaciones anteriormente.
    
    """
    x = np.array(x)
    y = np.array(y)
    l=len(x)
    m = []
    b = []
    for i in range(l-1):
        m.append((y[i+1]-y[i])/(x[i+1]-x[i]))
        b.append(y[i]-m[i]*x[i])
    return(m,b)
def Traz2(x,y):
    """
    Trazador cuadrático
    
    Esta función entrega un conjunto de n ecuaciones cuadráticas donde n+1 es 
    la cantidad de datos ingresados denominadas también trazadores cuadráticos. 
    Los datos se entregan en forma de vectores así:
        
             [a0 a1 a2 ... an], [b0 b1 b2 ... bn], [c0 c1 c2 ... cn]
             
    Siendo las constantes a,b,c las constantes de las n-ecuaciones de la forma:
        
        
                f(x)= a*x^2 + b*x + c      xi <= x <= xi+1
                
                
    NOTA: Cada función sólo es válida en la región comprendida como se ilustra 
    anteriormente.                
    
    """
    x = np.array(x)
    y = np.array(y)
    l=len(x)-1
    mat = np.zeros([3*l,3*l])
    vec = np.zeros([3*l-1,1])
    bandera = 1
    ii=0
    jj = 0
    # condición de igualdas en polinomios adyacentes
    for i in range(2*l-2):
        for j in range(3*l):
            bandera = bandera*np.complex(0,1)
            if(np.isreal(bandera)):
                ii = ii
                jj = jj +3
            else:
                ii=ii+1
                jj = jj
            mat[i,jj]=x[ii]**2
            mat[i,jj+1]=x[ii]
            mat[i,jj+2]=1
            vec[i,0]=y[ii]
            break
    #condiciones de bordes externos          
    mat[2*l-2,0]=x[0]**2
    mat[2*l-2,1]=x[0]
    mat[2*l-2,2]=1
    vec[2*l-2,0]=y[0]
    mat[2*l-1,-3]=x[-1]**2
    mat[2*l-1,-2]=x[-1]
    mat[2*l-1,-1]=1
    vec[2*l-1,0]=y[-1]
    #condición de igualdad en primeras derivadas de polinomios adyacentes
    bandera = 1
    ii=0
    jj = 0   
    for i in range(l-1):
        for j in range(3*l):
            ii = range(2*l,3*l-1)
            bandera=  bandera*np.complex(0,1)
            if(np.isreal(bandera)):
                jj = jj +3
            else:
                jj = jj
            mat[ii[i],jj]=2*x[i+1]
            mat[ii[i],jj+1]=1
            mat[ii[i],jj+3]=-2*x[i+1]
            mat[ii[i],jj+4]=-1
            break
    #condición de segunda derivada igual a 0 en punto inicial
    mat[3*l-1,0]=1
    mat2=np.zeros([3*l-1,3*l-1])  
    for i in range(3*l-1):
        for j in range(3*l-1):
            mat2[i,j]=mat[i,j+1]
          
    #encontrando los valores para los an's
    X = np.matrix(np.linalg.inv(mat2))*np.matrix(vec)
    a = [0]
    b=[]
    c=[]
    co=0
    for i in range(3):
        a.append(np.double(X[i*3-co]))
        b.append(np.double(X[i*3]))
        c.append(np.double(X[i*3+1]))
        co=1
    return(a,b,c)
    
            
                    