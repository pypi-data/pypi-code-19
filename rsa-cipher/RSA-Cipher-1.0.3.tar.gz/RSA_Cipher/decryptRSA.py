import math
from RSA_Cipher.modExp import modExp
from RSA_Cipher.gcd import gcd
from RSA_Cipher.congruence import inverse
import pyperclip

def decryptRSAPrivate():
    try:
        deconversion = {"65":"A", "66":"B", "67": "C" , "68":"D","69":"E",
                      "70":"F", "71": "G",  "72":"H", "73":"I", "74":"J",
                      "75":"K", "76":"L",  "77":"M", "78":"N", "79":"O",
                      "80":"P", "81": "Q", "82":"R", "83":"S", "84":"T",
                      "85":"U", "86":"V", "87":"W", "88":"X", "89": "Y",
                      "90":"Z", "91":" "}

        code = input('Enter Encrypted Message: ')
        eInv = int(input('Enter Decryption Key: '))
        n = int(input('Enter Public Key: '))

        eInv = int("{0:b}".format(eInv))

        matchCap=False
        cap = '25'
        while (matchCap!=True):
            if (len(cap)<len(str(n)) and int(cap)<(n)):
                cap = str(cap)+'25'
            else:
                matchCap=True

        code = [code[i:i+len(cap)] for i in range(0,len(code),len(cap))]

        returnString = ''
        for d in code:
            tmpDecrypt = str(modExp(int(d),eInv,n))
            returnString = returnString + deconversion[tmpDecrypt] 
        print('-------------------------')
        print('Decrypted Message: ',returnString)
        print('-------------------------')
        pyperclip.copy(returnString)
    except:
        print('Invalid Input')
    return 0