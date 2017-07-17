# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 20:23:00 2016

@author: SRINIVAS
"""

from random_words import RandomWords
rw = RandomWords()
word = rw.random_word()
word=list(word)
blank=[]
for elem in word:
    blank.append('_')
tries=0
loop=-1
print(' '.join(blank))
while tries<7:
    
    
    a=input('Letter or guess\n')
    if len(a)==1:
        if a in word:
            print('Yay')
            for elem in word:
                loop=loop+1
                if elem==a:
                    blank[loop]=a
            loop=-1
        else:
            tries=tries+1
            print('\a')
    else:
        if a==''.join(word):
            print('You Won')
            tries=10
        else:
         
         print('\a')
        
    print(' '.join(blank))
    if ''.join(blank)==''.join(word):
        print('You Won')
        tries=10
    
print('The answer was '+''.join(word))