import numpy as np

def RegLin(t,y):
    """
    Regresión Lineal
    
    Ajusta los puntos ingresados (t,y) a una línea recta bajo el críterio de 
    mínimos cuadrados
    
    Donde:
        t: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada
    
    y = m*x +b
    
    La función entrega 2 valores, los cuales son m y b de la ecuación anterior
    respectivamente.
    """
    t = np.array(t);
    y = np.array(y);
    l = len(t);
    sum1 = np.sum(t*y);
    sum2 = np.sum(t**2);
    tmed = np.sum(t)/l;
    ymed = np.sum(y)/l;
    a1 = ((l*sum1)-(np.sum(t)*np.sum(y)))/((l*sum2)-(np.sum(t))**2)
    a0 = ymed - a1*tmed
    return(a1,a0)

def RegPol(t,y,grado):  # se resuelve con n ecuaciones para n incognitas
    """
    Regresión Polinomial
    
    Ajusta los puntos ingresados (t,y) a un polinomio de un grado cualquiera,
    siempre y cuando la cantidad de datos sea mayor al grado + 1 deseado.
    
    Donde:
        t: es el vector de datos de la absisa
        y: es el vector de datos de la ordenada
        grado: es el grado del polinomio al que se quiere ajustar los datos
        
    La función entrega n valores, los cuales son los coeficientes del polinomio
    solicitado. tenga en cuenta que el orden de los coeficientes es desde el
    valor independiente hacia el coeficiente de la variable de mayor grado.
    
    y = a0 + a1*x + a2*x^2 + ... + an*x^n
    
    """
    t = np.array(t);
    y = np.array(y);
    l = len(t);
    grado = grado +1;
    if(l<=grado):
        print('no es posible realizar regresión.')
        print('Revise el la cantidad de datos y el orden del polinomio deseado')
    else:
        mat = np.zeros([grado,grado])
        for i in range(grado):
            for j in range(grado):
                mat[i,j]=np.sum(t**(j+i))
        mat[0,0]=l
    vec = np.zeros([grado,1])
    for i in range(grado):
        vec[i,0]=np.sum((t**i)*(y))
           
    A = np.matrix(np.linalg.inv(mat))*np.matrix(vec);
    return(A)
  
def RegLinMul(t,y):
    """
    Regresión Lineal Multiple
    
    Ajusta los datos ingresados a un polinomio de igual cantidad de variables
    a la cantidad de vectores de datos que posea t.
    
    Donde:
        t: es una matriz con los datos experimentales
        y: vector de datos depentientes de t
    
    Ejemplo:
        Ajuste los siguientes datos:
                x1   X2    y
                0    0     5
                2    1     10
                2.5  2     9
                1    3     0
                4    6     3
                7    2     27
        dado que los datos dependen de 2 variables, el algoritmo tendrá que 
        encontrar valores para los coeficientes de una ecuación que depende de
        2 variables. Esto se hace por defecto.
        
        Ingreso de datos:
            t = [[0,2,2.5,1,4,7],
                 [0,1,2,3,6,2]]
            y = [5,10,9,0,3,27],
            
        Salida del algoritmo:
            La función entregará un vector con los coeficientes de la ecuación
            que tiene la forma siguiente:
            
                    y = a0 + a1*x1 + a2*x2 + ... + an*xn
        
    
    """
    t = np.array(t);
    y = np.array(y);
    l = len(t)+1;
    mat = np.zeros([l,l]);
    for i in range(l-1):
        for j in range(l-1):
            if(i==j):
                mat[i+1,j+1]=np.sum(t[i]**2);
            else:
                mat[i+1,j+1]=np.sum(t[i]*t[j]);
            if(i==0 and j==0):
                mat[i,j]=len(t[0]);
            if(i==0):
                mat[i,j+1]=np.sum(t[j]);
            if(j==0):
                mat[i+1,j]=np.sum(t[i]);
    vec=np.zeros([l,1]);
    for i in range(l-1):
        vec[i+1,0]=np.sum(t[i]*y);
    vec[0,0] = np.sum(y);
    x = np.matrix(np.linalg.inv(mat))*np.matrix(vec)
    return(x)
    
    

           