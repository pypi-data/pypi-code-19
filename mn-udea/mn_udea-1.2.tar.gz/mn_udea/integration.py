import numpy as np

def Trap(x,y,h='0'):
    """
    Regla del Trapecio
    
    Esta función permite calcular la integral numérica de los datos (x,y). El 
    valor de h es opcional y si se usa, no es necesario tener los datos de x.
    
    la función retorna el valor de la integral por la regla del trapecio.
    
    NOTA: Si se poseen los datos (x,y), estos no necesitan estar igualmente
          para calcular la integral
    
    """
    x = np.array(x)
    y = np.array(y)
    l = len(y)
    II=[]
    h = np.double(h)
    if(h==0):
        for i in range(l-1):
            II.append((x[i+1]-x[i])*(y[i]+y[i+1])/2)
        I = np.sum(II)            
    else:
        suma = 0
        for i in range(1,l-1):
            suma = suma + y[i]
            suma = 2*suma
        I = h*(y[0]+ suma + y[-1])/2
    return(I)
def Simpson(x,y):
    """
    Regla Simpson 1/3
    
    Esta función permite calcular la integral numérica de los datos (x,y).
    
    la función retorna el valor de la integral por la regla de simpson 1/3.
    
    """
    x = np.array(x)
    y = np.array(y)
    l = len(y)
    h = (x[-1]-x[0])
    suma1 =0
    suma2=0
    for i in range(1,l-1,2):
        suma1 = suma1+ 4*y[i]
    for i in range(2,l-1,2):
        suma2 = suma2+ 2*y[i]
    I = h*(y[0]+suma1+suma2+y[-1])/(3*(l-1))
    return(I)
def Simpson3(x,y):
    """
    Regla Simpson 3/8
    
    Esta función permite calcular la integral numérica de los datos (x,y). La 
    función retorna el valor de la integral por la regla de simpson 1/3.
    
    NOTA: esta función solo calcula la integral bajo la curva denotada por los
    4 puntos, es decir no realiza el cálculo de la integral definida por mas 
    puntos.
    
    
    """
    x = np.array(x)
    y = np.array(y)
    l = len(y)
    h = x[-1]-x[0]
    I = h*(y[0]+3*(y[1]+y[2])+y[3])/8
    return(I)
    
    
    