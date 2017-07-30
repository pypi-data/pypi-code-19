from talalprotocol.talalprotocol import *

'''
This is just a test file used for
1. testing functionality
2. debugging
'''

#<---------- Caesar testing cases ---------->#

#test case 1
original_message = 'Nadim is a faggot bitch ####!'
shift_val = 5
x = str(caesar_cipher(original_message,shift_val))
print('The original message is: ' + original_message)
print('The encrypted text is: ' + x)
y = str(caesar_decipher(x, shift_val))
print("Th decrypted text is: " + y)








