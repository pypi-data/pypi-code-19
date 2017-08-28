# During my recent encounter on an article about the vulnerability of weak passwords, I was enlightened on the dangers of weak passwords, which includes single-handedly serving as the "weakest link" to a web server. In details, if my weak password is guessed by an hacker, the whole web server of the site is vulnerable.

# Olu Gbadebo
# Aug 21st 2017
# Password Generator: generates specifically rendom passwords.

# Each password generated as a format (this helps me to remember the password):
# 1: a digit, a randomized-case word, a special character, another word, another special character, a third word, a third special character, one last word, second digit
# 2: a special character, a randomized-case word, a digit, another word, another digit, third word, third digit, last word, special character
# 3: a randomized-case word, a digit, another word, another digit, third word, third digit, last word
# 4: a randomized-case word, a special character, another word, another special character, third word, third special character, last word

# imports
import os
import random
import linecache

# range of four digit numbers
NUMBER = range(2)
# range of digits
DIGITS = range(2)
# range of special characters (ascii)
CHARACTERS = range(2)

# randomizers
# returns a four digit number
def randomizeNumber(num_range):
    if num_range[0] > 999 and num_range[1] > 1000:
        return random.randint(num_range[0], num_range[1])
    else:
        raise ValueError('Invalid special character range')

# returns a digit
def randomizeDigit(dig_range):
    return random.randint(dig_range[0], dig_range[1])

# retuns a word with varied cases
def randomizeCase():
    gen_word = getWord()
    result_word = ''
    for letter in gen_word:
        # frequency of capitalizing a letter
        if (random.randint(0,4) == 1):
            result_word += str(letter).upper()
        else:
            result_word += letter
    return result_word

# returns a special character
def randomizeCharacter(char_range):
    if (char_range[0] >= 33 and char_range[1] <= 47):
        return chr(random.randint(char_range[0], char_range[1]))
    else:
        raise ValueError('Invalid special character range')

# get a random word from list of most common words
def getWord():
    return linecache.getline('dictionary.txt', random.randint(1, 8829)).split()[0]

def getNumRange():
    try:
        NUMBER[0] = int(raw_input('NUMBER start (int only): '))
    except ValueError:
        print('You failed to enter an integer. \nProgram ended')
        return
    else:
        try:
            NUMBER[1] = int(raw_input('NUMBER stop (int only): '))
        except ValueError:
            print('You failed to enter an integer. \nProgram ended')
            return

def getDigRange():
    try:
        DIGITS[0] = int(raw_input('DIGITS start (int only): '))
    except ValueError:
        print('You failed to enter an integer. \nProgram ended')
        return
    else:
        try:
            DIGITS[1] = int(raw_input('DIGITS stop (int only): '))
        except ValueError:
            print('You failed to enter an integer. \nProgram ended')
            return

def getCharRange():
    try:
        CHARACTERS[0] = int(raw_input('CHARACTERS start (*ASCII* int only): '))
    except ValueError:
        print('You failed to enter an integer. \nProgram ended')
        return
    else:
        try:
            CHARACTERS[1] = int(raw_input('CHARACTERS stop (*ASCII* int only): '))
        except ValueError:
            print('You failed to enter an integer. \nProgram ended')
            return

# let's user define range
def freedomRange():
    getNumRange()
    getDigRange()
    getCharRange()
    createPW()

# populate with default ranges
def populator():
    NUMBER[0] = int(os.environ['NUM_START'])
    NUMBER[1] = int(os.environ['NUM_STOP'])
    DIGITS[0] = int(os.environ['DIG_START'])
    DIGITS[1] = int(os.environ['DIG_STOP'])
    CHARACTERS[0] = int(os.environ['CHAR_START'])
    CHARACTERS[1] = int(os.environ['CHAR_STOP'])
    createPW()

def createPW():
    # randomly select a format
    pw_type = random.randint(1, 4)
    if pw_type == 1:
        return PW1()
    elif pw_type == 2:
        return PW2()
    elif pw_type == 3:
        return PW3()
    else:
        return PW4()

# create password
def PW1():
    # 1: a digit, a randomized-case word, a special character, another word, another special character, a third word, a third special character, one last word, second digit
    print '\n'
    print ' '.join([str(randomizeDigit(DIGITS)), randomizeCase(), randomizeCharacter(CHARACTERS), randomizeCase(), randomizeCharacter(CHARACTERS), randomizeCase(), randomizeCharacter(CHARACTERS), randomizeCase(), str(randomizeDigit(DIGITS))])

def PW2():
    # 2: a special character, a randomized-case word, a digit, another word, another digit, third word, third digit, last word, special character
    print '\n'
    print ' '.join([randomizeCharacter(CHARACTERS), randomizeCase(), str(randomizeDigit(DIGITS)), randomizeCase(), str(randomizeDigit(DIGITS)), randomizeCase(), str(randomizeDigit(DIGITS)), randomizeCase(), randomizeCharacter(CHARACTERS)])

def PW3():
    # 3: a randomized-case word, a digit, another word, another digit, third word, third digit, last word
    print '\n'
    print ' '.join([randomizeCase(), str(randomizeDigit(DIGITS)), randomizeCase(), str(randomizeDigit(DIGITS)), randomizeCase(), str(randomizeDigit(DIGITS)), randomizeCase()])

def PW4():
    # 4: a randomized-case word, a special character, another word, another special character, third word, third special character, last word
    print '\n'
    print ' '.join([randomizeCase(), randomizeCharacter(CHARACTERS), randomizeCase(), randomizeCharacter(CHARACTERS), randomizeCase(), randomizeCharacter(CHARACTERS), randomizeCase()])

while raw_input('\nRun: [r]\n') == 'r':
    if raw_input('Do you want to specify ranges? [y/any other input]\n') == 'y':
        freedomRange()
    else:
        populator()
