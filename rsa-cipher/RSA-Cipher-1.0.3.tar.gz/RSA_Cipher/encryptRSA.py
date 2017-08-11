import math
from RSA_Cipher.modExp import modExp
from RSA_Cipher.gcd import gcd
from RSA_Cipher.congruence import inverse
from RSA_Cipher.gcd import lcm
from RSA_Cipher.prime import check_prime
import pyperclip
# s is string
# n is a public key
# e is a prime public key
def encryptRSA():
    try:
        #initialising variables
        candidates = []
        lowerBound=-1
        upperBound=-1
        p = q = 1

        message = input('Message: ')
        while(not check_prime(p) or not check_prime(q)):
            print('-------------------------')
            p = int(input('Enter prime p: '))
            q = int(input('Enter prime q: '))
            print('-------------------------')
        n = p*q
        r = (p-1)*(q-1)
        while(lowerBound<1 or upperBound<1):
            print('Pick two positive integers range for your encryption key')
            lowerBound = int(input('Lower Bound: '))
            upperBound = int(input('Upper Bound: '))
        global eKey, dKey
        eKeyList = []
        dKeyList = []
        privKey = {}
        for i in range(lowerBound,upperBound):
            if((r*i)+1) != largest_prime_factor((r*i)+1):
                # candidates.append((r*i)+1)
                eKeyList.append(i)
                dKeyList.append((r*i)+1)
                privKey[i] = (r*i)+1
        k=-1
        print('Encryption Keys Available:\n',
            eKeyList)
        print('-------------------------')
        eKey = int(input('Choose Encryption Key: '))
        print('-------------------------')

        print('Encrypted Private Key: ',eKey)
        print('Decrypted Privaye Key: ',privKey[eKey])
        
        print('Public Key: ', p*q)
        e = int(k/largest_prime_factor(k))
        conversion = {"A": "65", "B": "66", "C": "67", "D": "68", "E": "69",
                      "F": "70", "G": "71", "H": "72", "I": "73", "J": "74",
                      "K": "75", "L": "76", "M": "77", "N": "78", "O": "79",
                      "P": "80", "Q": "81", "R": "82", "S": "83", "T": "84",
                      "U": "85", "V": "86", "W": "87", "X": "88", "Y": "89",
                      "Z": "90", " ": "91"}
        digits=""
        for c in message:
            digits = digits + conversion[c.upper()]
        i=False
        cap = '25'
        while (i!=True):
            if (len(cap)<len(str(p*q)) and int(cap)<(p*q)):
                cap = str(cap)+'25'
            else:
                i=True
        padded = False
        while (padded!=True):
            if(int((len(digits)))%2!=0):
                digits = digits + conversion['X']
            else:
                padded = True
        tmpTuple = ()
        tmpString = ''
        for x in range(1,len(digits)+1):
            if(int(x%2)!=0):
                tmpString = tmpString+digits[x-1]
            else:
                tmpString = tmpString+digits[x-1]
                tmpTuple = tmpTuple + (tmpString,)
                tmpString = ''
        returnTuple = ()
        for j in tmpTuple:
            returnTuple = returnTuple + (modExp(j,"{0:b}".format(e),(p*q)),)
        returnString = ''
        for k in returnTuple:
            k = str(k)
            while(len(str(k))<len(cap)):
                k = '0'+k
            returnString = returnString+k

        print('Encrypted Cipher: ',returnString)
        print('-------------------------')
        pyperclip.copy(returnString)
    except:
        print('Invalid Input')
    return 0


def largest_prime_factor(n):
    i = 2
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
    return n