def factor(n, param1="default"):  
    result = []
    for num in range(1, int(n**(0.5))+1):
        if n % num == 0 and num**2 != n:
            result.append(num)
            result.append(n//num)
        elif num**2 == n:
            result.append(num)
    return sorted(result)


def gcd(n1, n2):
    # Simple cases
    if n1 == n2:
        return n1
    if n1 == 0:
        return n2
    if n2 == 0:
        return n1
    # Look for factors of 2
    if ~n1 & 1: # n1 is even
        if n2 & 1: # n2 is odd
            return gcd(n1 >> 1, n2)
        else: # n1 and n2 are even
            return gcd(n1 >> 1, n2 >> 1) << 1
    if ~n2 & 1: # n1 is odd; n2 is even
        return gcd(n1, n2 >> 1)
    # Reduce if both odd
    if n1 > n2:
        return gcd((n1-n2) >> 1, n2)
    return gcd((n2-n1) >> 1, n1)


def iscoprime(n1, n2):
    if gcd(n1, n2) != 1:
        return False
    return True


def ispalindrome(n):
    for i in range((len(str(n))+1) // 2):
        if str(n)[i] != str(n)[-i-1]:
            return False
    return True


def isprime(n):
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True