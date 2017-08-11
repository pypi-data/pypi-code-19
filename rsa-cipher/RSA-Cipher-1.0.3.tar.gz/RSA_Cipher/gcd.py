#This source code is for educational purposes only!
#Any plagiarism or reuse of this source code
#   will be at your own risk

#x is a positive integer
#y is a positive integer
def gcd(x,y):
    a = max(x,y)
    b = min(x,y)
    r = a % b
    while r != 0:
        a = b
        b = r
        r = a % b
    return b

# define lcm function
def lcm(x, y):
   lcm = (x*y)//gcd(x,y)
   return lcm