# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 17:59:35 2017

@author: kabya94
"""

import random

def isprime(n):
    '''Checks if the number n is prime or not
        - returns True if prime
        - returns False if composite'''
    try:
        assert type(n) == int and n > 1
    
        for i in range(2, n):
            if n%i == 0:
                return False
        return True
    
    except AssertionError:
        print("Invalid Input! Enter a positive integer greater than 1.")
        
def find_primes(start, stop):
    '''Returns a list of prime numbers between the integer 'start'
       and the integer 'stop', including the end values, is they are prime. Returns 'None'
       if no such primes exists.'''
    try:
        assert type(start) == int and type(stop) == int
        assert start >= 1 and stop >= 1 and start <= stop
           
        prime_list = []
        if start == 1:
            start = start + 1
        for i in range(start, stop + 1):
            if isprime(i):
                prime_list.append(i)
        if len(prime_list) != 0:
            return prime_list
        else:
            return 'None'
        
    except AssertionError:
        print("Invalid Input!! Make sure you enter positive integers as parameters.")
        print("Also note that the 'start' must be less than equal to the 'stop' value.")
       

def rand_prime(start, stop):
    '''Returns a random prime number between the values 'start' and 'stop'.
       Returns 'None' if no prime exists in that interval'''
    try:
        prime_list = find_primes(start, stop)
        rand_index = random.randint(0, len(prime_list) - 1)
        #print(prime_list)
        if type(prime_list) == list:
            return prime_list[rand_index]
        else:
            return 'None'
            
    except ValueError:
        print("Invalid Input!! Make sure you enter positive integers as parameters.")
        print("Also note that the 'start' must be less than equal to the 'stop' value.")
       
def inter_primes(start, stop, interval = 0):
    '''Returns a list of tuples of primes separated by a magnitude of 'interval' (optional argument).
       In case 'interval' parameter is not specified, or is specified as '0', it is similar to function 'find_primes'.
       Returns 'None' is no such primes exist
       For example: >>> import primelib
                    >>> inter_primes(1, 20, 2)
                    >>> [(3, 5), (5, 7), (11, 13), (17, 19)]
                    >>> inter_primess(1, 20, 6)
                    >>> [(5, 11), (7, 13), (11, 17), (13, 19)]
                    >>> inter_prime(1, 20)
                    >>> [2, 3, 5, 7, 11, 13, 17, 19]
                    >>> inter_primes(3,20,1)
                    >>> 'None'
    '''
    try:
        assert type(interval) == int and interval >= 0
        
        prime_list = find_primes(start, stop)
        inter_prime_list = []
        
        if interval == 0:
            return prime_list
        elif interval % 2 == 1 and type(prime_list) == list:
            if start <= 2 and stop >= 2 + interval and isprime(2+interval):
                inter_prime_list.append((2, 2+interval))                
                return inter_prime_list
            else:
                return 'None'
        elif type(prime_list) != list:
            return 'None'
        else:
            for i in prime_list:
                if isprime(i) and isprime(i+interval) and i + interval <= stop:
                    inter_prime_list.append((i, i + interval))
            if len(inter_prime_list) > 0:
                return inter_prime_list
            else:
                return 'None'
    
    except ValueError:
        print("Invalid Input!! Make sure you enter positive integers as parameters.")
        print("Also note that the 'start' must be less than equal to the 'stop' value.")
    
    except AssertionError:
        print("Enter a positive integer as the value of the interval.")