import numpy as np
def cramer(A,B):
    """
    Esta función permite resolver sistemas lineales de n ecuaciones 
    con n incognitas utilizando la regla de cramer.
    
                        [A]*[X]=[B]
    
    donde:
        A: es la matriz de coeficientes
        B: es el vector de términos independientes
    
    La función entrega el vector de soluciones para X
    
    """
    B=np.matrix(B)
    D = np.linalg.det(A)
    X = []
    for i in range(len(A)):
        AA = np.matrix(A)
        for j in range(len(A)):
            AA[j,i] = B[j,0]
        DD = np.linalg.det(AA)
        X.append(DD/D)
    return(X)
def desc_LU(A):
    """
    Descomposición LU -> matrices "L" "U"
    
    Esta función devuelve las matrices "L" y "U" a partir de una matriz de 
    coeficientes A.
    """
    mat=np.matrix(A)
    n = len(mat)
    L = np.matrix(np.zeros([n,n]))
    for j in range(0,n-1):
        for i in range(1+j,n):
            fac = (-mat[i,j]/mat[j,j])
            L[i,j]=-fac
            for q in range(0,n):
                mat[i,q]= (fac*mat[j,q]+mat[i,q])
    U = mat
    for i in range(n):
        for j in range(n):
            if i == j:
                L[i,j]=1
    return(L,U)
def desc_D(L,b):
    """
    descomposición LU -> matriz "D"
    
    Esta función devuelve la matriz "D" a partir de la matriz "L" (que se puede
    obtener con la función "desc_LU") y el vector de términos independientes.
    
    
    """
    L = np.matrix(L)
    b = np.matrix(b)
    D = (np.linalg.inv(L)*b)
    return(D)
