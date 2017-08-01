import msvcrt
import os


def get_character():
    return msvcrt.getch()


def clear():
    os.system('cls')
