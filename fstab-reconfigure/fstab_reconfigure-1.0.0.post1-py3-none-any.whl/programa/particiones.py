#!/usr/bin/env python3
# encoding:utf-8

import re

from fstab_reconfigure.utiles.utiles import salida_consola


class Particion:
    def __init__(self, linea: str):
        self.unidad = linea[:linea.find(':')]
        self.uuid = re.search(r'UUID="(.+?)"', linea).group(1)
        self.formato = re.search(r'TYPE="(.+?)"', linea).group(1)
        self.punto_montaje = None
        try:
            self.etiqueta = re.search(r'LABEL="(.+?)"', linea).group(1)
        except AttributeError:
            self.etiqueta = ''

    def linea_fstab(self, punto_montaje=None, es_principal=False):
        comentario = ''
        instruccion = ''
        self.punto_montaje = punto_montaje
        if self.etiqueta == '':
            comentario = str.format('# {0}', self.unidad)
        else:
            comentario = str.format('# {0} ({1})', self.etiqueta, self.unidad)
        if self.formato == 'swap':
            instruccion = str.format('UUID={0}\tnone\tswap\tsw\t0\t0', self.uuid)
        elif es_principal:
            instruccion = str.format('UUID={0}\t/\text4\terrors=remount-ro\t0\t1', self.uuid)
        else:
            instruccion = str.format('UUID={0}\t{1}\t{2}\tdefaults\t0\t0', self.uuid, self.punto_montaje, self.formato)
        instruccion = instruccion.replace('\t', '    ').strip()
        return comentario + '\n' + instruccion + '\n\n'

    @staticmethod
    def unificar_espacios(fstab):
        """
        Dado el contenido del fichero fstab, devuelve dicho contenido formateado de tal forma que cada opción de cada partición está en la misma columna.
        """
        regex = re.compile(r'^(?:(UUID=.+?)|^(/dev/sd.+?))[\s]+(.+?)[\s]+(.+?)[\s]+(.+?)[\s]+(.+?)[\s]+(.+?)$')
        particiones = Particion.__get_particiones_fstab(fstab, regex)
        Particion.__suma_espacios_por_columna(particiones)
        espaciadas = Particion.__join_lista_particiones(particiones)
        fstab = fstab.split('\n')
        nueva = 0
        for i in range(len(fstab)):
            linea = re.search(regex, fstab[i])
            if linea is not None:
                fstab[i] = espaciadas[nueva]
                nueva += 1
        fstab = str.join('\n', fstab)
        return fstab

    @staticmethod
    def __get_particiones_fstab(fstab, regex):
        """
        Dado el contenido del fichero fstab, devuelve una lista de las particiones que contiene con todas sus opciones (6 en total) separadas
        como elementos de otra lista.
        """
        fstab = fstab.split('\n')
        particiones = []
        for linea in fstab:
            linea = re.search(regex, linea)
            if linea is not None:
                identificador = linea.group(1) if linea.group(2) is None else linea.group(2)
                particiones.append([identificador, linea.group(3), linea.group(4), linea.group(5), linea.group(6), linea.group(7)])
        return particiones

    @staticmethod
    def __suma_espacios_por_columna(particiones):
        """
        Dada la lista de listas de particiones representadas con todas sus opciones, modifica cada opción añadiendo espacios a su derecha para que, al final,
        todas ocupen exactamente el mismo número de caracteres.
        """
        num_particiones = len(particiones)
        for j in range(6):
            maximo = 0
            for i in range(num_particiones):
                maximo = len(particiones[i][j]) if len(particiones[i][j]) > maximo else maximo
            for i in range(num_particiones):
                longitud = len(particiones[i][j])
                diferencia = maximo - longitud
                espacios = ''
                for dif in range(diferencia):
                    espacios += ' '
                particiones[i][j] = particiones[i][j] + espacios

    @staticmethod
    def __join_lista_particiones(particiones):
        """
        Dada la lista de listas de particiones representadas con todas sus opciones, devuelve una lista con las particiones representadas como cadenas ya unidas.
        """
        res = []
        for i in range(len(particiones)):
            linea = str.format('{0}\t{1}\t{2}\t{3}\t{4}\t{5}', particiones[i][0], particiones[i][1], particiones[i][2], particiones[i][3], particiones[i][4], particiones[i][5])
            linea = linea.replace('\t', '    ')
            res.append(linea)
        return res

    @staticmethod
    def get_particiones():
        """
        Devuelve una lista de objetos de tipo Particion, generada a partir del contenido de la salida de la instrucción blkid.
        """
        salida_blkid = salida_consola('blkid', root=True)
        return [Particion(x.strip()) for x in salida_blkid.split('\n') if x.strip() != '']

    def __str__(self):
        return str.format("Unidad: {0}\nEtiqueta: {1}\nUUID: {2}\nTipo: {3}", self.unidad, self.etiqueta, self.uuid, self.formato)

    def __repr__(self):
        return str.format("Partición {0}", self.unidad)
