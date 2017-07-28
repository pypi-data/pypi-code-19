#!/usr/bin/env python3
# encoding:utf-8

import os
import shutil
from random import SystemRandom
from time import sleep

from fstab_reconfigure.programa.menu import Menu, Opciones
from fstab_reconfigure.programa.particiones import Particion
from fstab_reconfigure.utiles.utiles import es_sudo


class FSTab:
    TIMEOUT_OK = 2
    TIMEOUT_ERROR = 3

    def __init__(self):
        self.cabecera_programa = '--------------------------------------------\n Configurador simple del archivo /etc/fstab\n--------------------------------------------\n'
        os.umask(0)
        self.carpeta_temporal = str.format('/tmp/fstab-reconfigure-{0}/', SystemRandom().getrandbits(32))
        os.makedirs(self.carpeta_temporal, exist_ok=True)
        self.fichero_temporal = self.__crear_ruta_fichero_temporal()
        self.opciones = {
            0: {
                0: self.cabecera_programa,
                1: ('Configurar automontaje de particiones', self.fstab_reconfigure),
                2: ('Abrir fichero /etc/fstab [Solo lectura]', lambda: self.abrir_fstab(original=True, escritura=False), False),
                3: ('Abrir fichero /etc/fstab [Lectura y escritura]', lambda: self.abrir_fstab(original=True, escritura=True), False),
                4: ('Salir', self.salir, False),
            },
            1: {
                0: self.cabecera_programa,
                1: ('Configurar automontaje de particiones', self.fstab_reconfigure),
                2: ('Ver fichero fstab temporal generado', lambda: self.abrir_fstab(original=False), False),
                3: ('Sustituir el fichero /etc/fstab por el fichero fstab temporal generado', self.sustituir_fstab, False),
                4: ('Abrir fichero /etc/fstab [Solo lectura]', lambda: self.abrir_fstab(original=True, escritura=False), False),
                5: ('Abrir fichero /etc/fstab [Lectura y escritura]', lambda: self.abrir_fstab(original=True, escritura=True), False),
                6: ('Salir', self.salir, False),
            }
        }
        self.cabecera_fstab = '''# /etc/fstab: static file system information.
#
# Use 'blkid' to print the universally unique identifier for a
# device; this may be used with UUID= as a more robust way to name devices
# that works even if disks are added and removed. See fstab(5).
#
# <file system> <mount point>   <type>  <options>       <dump>  <pass>

'''
        self.fstab_completo = None
        self.menu = Menu(self.opciones, ancho=95, alto=30)
        self.__goto_menu_superior()

    def fstab_reconfigure(self):
        self.fstab_completo = self.cabecera_fstab
        principal_ya_asignada = False
        try:
            particiones = Particion.get_particiones()
            for i in range(len(particiones)):
                print(str.format('----------------------------------\n Información de la partición #{0}:\n----------------------------------', i + 1))
                particion = particiones[i]
                print(particion)
                if particion.formato == 'swap':
                    self.agregar_swap(particion)
                    continue
                if not principal_ya_asignada:
                    principal_ya_asignada = Menu.menu_booleano('¿Es ésta la partición principal del sistema operativo?', lambda: self.agregar_principal(particion), lambda: False, defecto=Opciones.NO)
                    if principal_ya_asignada:
                        continue
                Menu.menu_booleano('¿Le interesa que esta partición se monte automáticamente al iniciar el sistema?', lambda: self.agregar_particion(particion), defecto=Opciones.SI)
                print()
            self.fstab_completo = Particion.unificar_espacios(self.fstab_completo).strip()
            self.guardar_fstab_temporal()

        except KeyboardInterrupt:
            self.fstab_completo = None
            self.__print_msg('\n\n\tSaliendo de la configuración de automontaje...')

        finally:
            self.__goto_menu_superior()

    def agregar_swap(self, particion):
        swap = particion.linea_fstab()
        self.fstab_completo += swap
        print('Montando partición de intercambio automáticamente\n')

    def agregar_principal(self, particion):
        principal = particion.linea_fstab('/', True)
        self.fstab_completo += principal
        print()
        return True

    def agregar_particion(self, particion):
        ruta = input('Especifique la ruta absoluta del directorio donde debería montarse esta partición:\n\n>>> ')
        if ruta == '' or ruta.count(' '):
            print('Error: No se permiten nombres en blanco ni espacios en la ruta de montaje')
            return Opciones.REINICIAR
        print('\nLa ruta escogida es: ' + ruta)
        correcta = Menu.menu_booleano('¿Es correcta?', lambda: self.confirmar_ruta(particion, ruta), lambda: False)
        if not correcta:
            return Opciones.REINICIAR

    def confirmar_ruta(self, particion, ruta):
        self.fstab_completo += particion.linea_fstab(ruta)
        return True

    def guardar_fstab_temporal(self):
        """
        Guarda el archivo fstab generado por el programa en un archivo temporal.
        """
        escrito = self.__escribir_archivo(self.fichero_temporal)
        if escrito:
            os.chmod(self.fichero_temporal, 0o666)
            self.__print_msg('\n\tArchivo de automontaje de particiones generado correctamente...')

    def sustituir_fstab(self):
        """
        Sustituye el archivo /etc/fstab del sistema por el generado por el programa.
        """
        if es_sudo():
            seguro = Menu.menu_booleano('\n ¿Está seguro de querer sustituir el archivo /etc/fstab?', ejecutar_si=lambda: True, ejecutar_no=lambda: False)
            if seguro:
                escrito = self.__escribir_archivo('/etc/fstab')
                if escrito:
                    self.__print_msg('\n\tArchivo guardado correctamente...')
            else:
                self.__print_msg('\n\tCancelando sustitución del archivo /etc/fstab...')
        else:
            self.__print_msg('\n\tError: Es necesario ser root para poder escribir sobre el archivo /etc/fstab...', error=True)
        self.__goto_menu_superior()

    def abrir_fstab(self, original=False, escritura=False):
        """
        Ejecuta nano con permisos de solo lectura sobre una copia temporal del fichero fstab generado por el programa o del fichero original /etc/fstab
        Si están activadas tanto original como escritura, nano se ejecuta como sudo sobre el auténtico fichero /etc/fstab
        """
        fstab = '/etc/fstab' if original else self.fichero_temporal
        if original and escritura:
            os.system(str.format('sudo -Sk nano {0}', fstab))
        else:
            temporal = self.__copiar_a_fichero_temporal(fstab)
            os.system(str.format('nano -v {0}', temporal))
        self.__goto_menu_superior()

    def __crear_ruta_fichero_temporal(self):
        temporal = str.format(self.carpeta_temporal + 'tmp_fstab_{0}.txt', SystemRandom().getrandbits(32))
        return temporal

    def __copiar_a_fichero_temporal(self, origen):
        """
        Copia el archivo ubicado en la ruta origen a un archivo temporal con permisos 666, y devuelve la ubicación del archivo temporal creado. 
        """
        temporal = self.__crear_ruta_fichero_temporal()
        shutil.copy(origen, temporal)
        os.chmod(temporal, 0o666)
        return temporal

    def __escribir_archivo(self, destino):
        """
        Escribe el contenido de la variable fstab_completo en el destino especificado. 
        """
        try:
            file = open(destino, 'w')
            file.write(self.fstab_completo)
            file.close()
            return True
        except:
            self.__print_msg('Ha habido un error durante el guardado del archivo...', error=True)
            return False

    def __goto_menu_superior(self):
        if self.fstab_completo is None:
            self.menu.menu_superior(0)
        else:
            self.menu.menu_superior(1)

    def __print_msg(self, msg='', error=False):
        """
        Imprime un mensaje y paraliza la ejecución un tiempo determinado en función del parámetro error. 
        """
        print(msg)
        timeout = FSTab.TIMEOUT_ERROR if error else FSTab.TIMEOUT_OK
        sleep(timeout)

    def salir(self):
        shutil.rmtree(self.carpeta_temporal, ignore_errors=True)
        self.menu.salir('\n\tSaliendo del programa...', reset=True)
