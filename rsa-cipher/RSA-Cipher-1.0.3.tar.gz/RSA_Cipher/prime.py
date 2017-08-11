def primeGenerator(lower,upper):
	lower = int(lower)
	upper = int(upper)
	for i in range(lower,upper+1):
		if i > 1:
			for j in range(2,i):
				if (i%j)==0:
					break
			else:
				print('[',i,']')

def primeListGenerator(lower,upper):
	lower = int(lower)
	upper = int(upper)
	returnList =[]
	for i in range(lower,upper+1):
		if i > 1:
			for j in range(2,i):
				if (i%j)==0:
					break
			else:
				returnList.append(i)
	return returnList

def check_prime(x):
    if x > 1:
        n = x // 2
        for i in range(2, n + 1):
            if x % i == 0:
                return False
        return True
    else:
        return False
