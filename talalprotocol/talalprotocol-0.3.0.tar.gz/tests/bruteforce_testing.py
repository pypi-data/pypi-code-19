from talalprotocol.talalprotocol import *
import string, random

# Caesar Cipher Brute Force

raw_message='GoodLuckTryingToCrackThis'
shift_value=random.randrange(25)
message = caesar_cipher(raw_message, shift_value)

letters = string.ascii_lowercase

# loop through every possible key
for key in range(len(letters)):
    translated = ''

    for symbol in message:
        if symbol in letters:
            num = letters.find(symbol)
            num = num - key
            if num < 0:
                num = num + len(letters)
            translated = translated + letters[num]
        else:
            translated = translated + symbol
    if translated==raw_message.lower():
        print('Key #%s: %s' % (key, translated))
