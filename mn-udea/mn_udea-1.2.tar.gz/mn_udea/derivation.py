x = [0,0.25,0.5,0.75,1]
y = [1.2,1.103516,0.925,0.6363281,0.2]

import numpy as np
def dif(x,y,p,h,HP='1'):
    """
    Diferencia Dividida Finita
    
    Esta función entrega la derivada de los datos (x,y) evaluados en el 
    punto P dado. Las formulas empleadas para calcular la derivada corresponden
    a la diferencia dividida finita centrada, con lo cual es necesario que el
    punto P tenga al menos un valor hacia atrás y otro hacia adelante para la
    versión simplificada (HP=0) o 2 valores hacia atrás y 2 hacia adelante para
    la versión de alta presición (HP=1)
    
    NOTAS: 
        Para definir el punto p, se utiliza la posición del dato en la cual
        se desea evaluar la derivada.
        El la diferencia entre X[i+1]-X[i] debe ser constante
    
    Ejemplo: Evaluar la derivada en x=3 de los siguientes datos
        x = [2,3,4], y=[8,12,16]
        - Posición de interés para evaluar la derivada en 1 porque x[1]=3.
        - Dado que a aprtir de la posición en la que se evaluará la derivada 
          solo tengo un dato hacia atrás y uno hacia adelante, se debe 
          selecionar baja presición (HP=0).
        - El paso (h) es x[1]-x[0]=1 para este caso
        
        
                              x = [2,3,4]
                              y=[8,12,16]
                              dif(x,y,1,1,0)
                              >> 4.0
        
    """
    x = np.array(x)
    y = np.array(y)
    l = len(y)
    p = np.int(p)
    HP = np.int(HP)
    if(HP==1):
        if(p>=2):
            D = (-y[p+2]+8*y[p+1]-8*y[p-1]+y[p-2])/(12*h)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela o trabaje con fórmula '
                  'menos precisa (HP=0)')
    else:
        if(p>=1):
            D = (y[p+1]-y[p-1])/(2*h)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela')
    return(D)
def dif2(x,y,p,h,HP='1'):
    """
    Diferencia Dividida Finita
    
    Esta función entrega la segunda derivada de los datos (x,y) evaluados en el 
    punto P dado. Las formulas empleadas para calcular la derivada corresponden
    a la diferencia dividida finita centrada, con lo cual es necesario que el
    punto P tenga al menos un valor hacia atrás y otro hacia adelante para la
    versión simplificada (HP=0) o 2 valores hacia atrás y 2 hacia adelante para
    la versión de alta presición (HP=1)
    
    NOTAS: 
        Para definir el punto p, se utiliza la posición del dato en la cual
        se desea evaluar la derivada.
        El la diferencia entre X[i+1]-X[i] debe ser constante
    
    Ejemplo: Remítase a la ayuda de la función "dif"
    
    """
    x = np.array(x)
    y = np.array(y)
    l = len(y)
    p = np.int(p)
    HP = np.int(HP)
    if(HP==1):
        if(p>=2):
            D=(-y[p+2]+16*y[p+1]-30*y[p]+16*y[p-1]-y[p-2])/(12*h**2)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela o trabaje con fórmula '
                  'menos precisa (HP=0)')
    else:
        if(p>=1):
            D=(y[p+1]-2*y[p]+y[p-1])/(h**2)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela')
    return(D)
def dif3(x,y,p,h,HP='1'):
    """
    Diferencia Dividida Finita
    
    Esta función entrega la tercera derivada de los datos (x,y) evaluados en el 
    punto P dado. Las formulas empleadas para calcular la derivada corresponden
    a la diferencia dividida finita centrada, con lo cual es necesario que el
    punto P tenga al menos 2 valores hacia atrás y 2 hacia adelante para la
    versión simplificada (HP=0) o 3 valores hacia atrás y 3 hacia adelante para
    la versión de alta presición (HP=1)
    
    NOTAS: 
        Para definir el punto p, se utiliza la posición del dato en la cual
        se desea evaluar la derivada.
        El la diferencia entre X[i+1]-X[i] debe ser constante
    
    Ejemplo: Remítase a la ayuda de la función "dif"
    
    """
    x = np.array(x)
    y = np.array(y)
    l = len(y)
    p = np.int(p)
    HP = np.int(HP)
    if(HP==1):
        if(p>=3):
            D=(-y[p+3]+8*y[p+2]-13*y[p+1]+13*y[p-1]-8*y[p-2]+y[p-3])/(8*h**3)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela o trabaje con fórmula '
                  'menos precisa (HP=0)')
    else:
        if(p>=2):
            D=(y[p+2]-2*y[p+1]+2*y[p-1]-y[p-2])/(2*h**3)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela')
    return(D)
def dif4(x,y,p,h,HP='1'):
    """
    Diferencia Dividida Finita
    
    Esta función entrega la tercera derivada de los datos (x,y) evaluados en el 
    punto P dado. Las formulas empleadas para calcular la derivada corresponden
    a la diferencia dividida finita centrada, con lo cual es necesario que el
    punto P tenga al menos 2 valores hacia atrás y 2 hacia adelante para la
    versión simplificada (HP=0) o 3 valores hacia atrás y 3 hacia adelante para
    la versión de alta presición (HP=1)
    
    NOTAS: 
        Para definir el punto p, se utiliza la posición del dato en la cual
        se desea evaluar la derivada.
        El la diferencia entre X[i+1]-X[i] debe ser constante
    
    Ejemplo: Remítase a la ayuda de la función "dif"
    
    """
    x = np.array(x)
    y = np.array(y)
    l = len(y)
    p = np.int(p)
    HP = np.int(HP)
    if(HP==1):
        if(p>=3):
            D=(-y[p+3]+12*y[p+2]+39*y[p+1]+56*y[p]-39*y[p-1]+12*y[p-2]+y[p-3])/(6*h**4)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela o trabaje con fórmula '
                  'menos precisa (HP=0)')
    else:
        if(p>=2):
            D=(y[p+2]-4*y[p+1]+6*y[p]-4*y[p-1]+y[p-2])/(h**4)
        else:
            print('NO es posible evaluar la derivada en la posición '
                  'seleccionada, por favor verifíquela')
    return(D)
        
    
            
        
