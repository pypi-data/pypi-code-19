def inverse(e,r,m):
    eInv = 1
    while(((eInv*e) % m) != (r % m)):
        eInv = eInv + 1
    return eInv