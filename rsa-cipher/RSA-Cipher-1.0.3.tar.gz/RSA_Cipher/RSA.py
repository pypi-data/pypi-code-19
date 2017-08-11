import math
from RSA_Cipher.encryptRSA import encryptRSA
from RSA_Cipher.decryptRSA import decryptRSAPrivate
from RSA_Cipher.modExp import modExp
from RSA_Cipher.congruence import inverse
from RSA_Cipher.prime import primeGenerator
from RSA_Cipher.prime import primeListGenerator
from RSA_Cipher.prime import check_prime
from RSA_Cipher.gcd import gcd
from RSA_Cipher.gcd import lcm
import pyperclip

def main():
    end = False
    global choice
    choice = 7
    while(end!=True):
        print('################################')
        print('#   1.) Encrypt                #')
        print('#   2.) Decrypt                #')
        print('#   3.) Generate Prime Numbers #')
        print('#   4.) Check Prime Number     #')
        print('#   5.) Notes                  #')
        print('#   6.) End Program            #')
        print('################################')
        try:
            choice = int(input('--->'))
        except:
            print('Invalid Input')
        if(choice == 1):
            encryptRSA()
        elif(choice == 2):
            decryptRSAPrivate()
        elif(choice == 3):
            try:
                lower = int(input('Enter lower bound: '))
                upper = int(input('Enter upper bound: '))
                print(primeListGenerator(lower,upper))
            except:
                print('Invalid Input')
        elif(choice == 4):
            try:
                n = int(input('Enter a number: '))
                print('Is ',n,' a prime number?')
                print(check_prime(n))
            except:
                print('Invalid Input')
        elif(choice == 5):
            print('\nNotes:\n'
                '+To make encryption stronger, choose higher encryption key\n'
                '+Recipient only needs a decryption key to translate the message\n'
                '+The message can be intercepted if the encryption key and decryption'
                ' key has been compromised by an attacker\n'
                '+There is more chance the message to be intercepted if sender and'
                ' receiver of the message use the same encryption/decryption keys to'
                ' communicate. Make sure to have different encryption/decryption keys\n\n'
                '--Important--\n'
                '+The encryption/decryption only works for English alphabet and white space.'
                ' Any other character will break the program\n')
        elif(choice == 6):
            print()
            end = True
        else:
            print('Invalid input')


if __name__ == '__main__':
    main()