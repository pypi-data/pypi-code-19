#!/usr/bin/env python3
# encoding:utf-8

import os
import re
import sys

from fstab_reconfigure.programa.fstab import FSTab
from fstab_reconfigure.programa.menu import Menu, Opciones
from fstab_reconfigure.utiles.utiles import es_sudo

CURRENT_PATH = os.path.realpath(__file__)
ZIP_FILE = False if os.path.isfile(CURRENT_PATH) else True
CURRENT_PATH = os.path.dirname(CURRENT_PATH) if ZIP_FILE else CURRENT_PATH


def entrar_como_root():
    os.system('sudo python3 ' + re.escape(CURRENT_PATH))
    sys.exit(0)


def main():
    if not es_sudo():
        print('Es necesario ser root para poder hacer funcionar la aplicación al 100%. De lo contrario, pueden ocurrir errores durante la ejecución.')
        Menu.menu_booleano('\n¿Desea reiniciar la ejecución como sudo?', ejecutar_si=entrar_como_root, ejecutar_no=FSTab, defecto=Opciones.SI)
    else:
        FSTab()


if __name__ == '__main__':
    main()
