def factor(n):
    result = []
    for num in range(1, int(n**(0.5))+1):
        if n % num == 0 and num**2 != n:
            result.append(num)
            result.append(n//num)
        elif num**2 == n:
            result.append(num)

    return result