import math

#Mod Exponential Function with binary

#b is a base of binary
#n is a exponential expressed in binary string
#m is a mod of the result of b^n
def modExp(b, n, m):
    #reverse binary
    n = str(n)
    n = n[::-1]
    k = len(n)
    b = int(b)
    m = int(m)
    x = 1
    p = b % m
    for i in range(0, k):
        if int(n[i]) == 1:
            x = x*p % m
        p = (p * p) % m
    return x