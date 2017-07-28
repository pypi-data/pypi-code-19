#!/usr/bin/env python3
# encoding:utf-8

import os
import subprocess
import sys
from subprocess import CalledProcessError


def es_sudo():
    return os.geteuid() == 0


def salida_consola(instruccion, root=False):
    if root:
        instruccion = str.format('sudo -S {0}', instruccion)
    try:
        res = subprocess.check_output(instruccion, shell=True).decode('UTF-8')
        return res
    except CalledProcessError as error:
        sys.exit('Se ha producido un error al intentar ejecutar la siguiente instrucción: ' + error.cmd)


def getChar():
    try:
        # Para sistemas basados en POSIX (con soporte para termios y tty)
        import tty, sys, termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            answer = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return answer

    except ImportError:
        # Para sistemas basados en Windows
        import msvcrt  # Si se importa, es que estamos en Windows

        return msvcrt.getch()
