#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import platform
from pathlib import Path
from os.path import join, abspath, dirname, expanduser
from shutil import copyfile
from os import makedirs
from datetime import date
from time import strftime
from io import StringIO
from configparser import ConfigParser
from logging import basicConfig, getLogger, StreamHandler, FileHandler,\
    DEBUG, INFO

# Fecha
FORMATO_FECHA_ISO = "%Y-%m-%d %H:%M:%S"
FORMATO_FECHA = "%d-%m-%Y"
FORMATO_HORA = "%H:%M:%S"
FORMATO_FECHA_HORA = FORMATO_FECHA  + ' ' + FORMATO_HORA

# Carpetas
CARPETA_MADRE = abspath(dirname(__file__))
CARPETA_GUIS = join(CARPETA_MADRE, 'InterfacesGraficas')
CARPETA_RECURSOS = join(CARPETA_MADRE, 'Recursos')
CARPETA_BD = join(CARPETA_MADRE, 'BaseDeDatos')
CARPETA_REPORTES = join(CARPETA_MADRE, 'Reportes')
# Escoger una carpeta del usuario para poder escribir
if platform.startswith('win'):
    from ctypes import wintypes, windll, create_unicode_buffer
    CSIDL_APPDATA = 26
    SHGFP_TYPE_CURRENT = 0
    buf = create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(0, CSIDL_APPDATA, 0, SHGFP_TYPE_CURRENT, buf)
    CARPETA_TRABAJO = join(buf.value, 'SCET')
else:
    CARPETA_TRABAJO = expanduser(join('~','.scet'))
# si no existe crearla
if not Path(CARPETA_TRABAJO).exists():
    makedirs(CARPETA_TRABAJO)
# copiar archivos de estilo
for i in ('entradas.xsl', 'estandar.css'):
    copyfile(join(CARPETA_REPORTES, i), join(CARPETA_TRABAJO, i))
IMAGEN_LOGO = join(CARPETA_TRABAJO, 'logo.png')

# Metadata
metadata = ConfigParser()
metadata.read(join(CARPETA_MADRE, 'metadata.cfg'))
NOMBRE = metadata['metadata']['name']
VERSION = metadata['metadata']['version']
TITULO = metadata['metadata']['title']
FECHA = date(*[int(i) for i in metadata['metadata']['date'].split('-')])
AUTOR = metadata['metadata']['author']
CONTACTO = metadata['metadata']['author_email']

# Logger
LOG_0 = getLogger()
LOG_0.setLevel(DEBUG)
LOG_SCET = getLogger(__name__.split('.')[0])
LOG_SCET.setLevel(DEBUG)
LOG_SCET.info('Iniciando SCET vercion <{}>'.format(VERSION))

# Crear loging del sistema
REGISTRO = StringIO('SCET - Registro {}'.format(strftime(FORMATO_FECHA_ISO)))
_rh = StreamHandler(REGISTRO)
_rh.setLevel(DEBUG)
LOG_0.addHandler(_rh)
# configurar logging para SCET
_fh = FileHandler(join(CARPETA_TRABAJO, 'scet.log'), mode='w')
_fh.setLevel(DEBUG)
LOG_SCET.addHandler(_fh)

# Base de Datos
NOMBRE_SQL_SQLITE = "SCET_SQLite.sql"
ARCHIVO_SQL_SQLITE = join(CARPETA_BD, NOMBRE_SQL_SQLITE)
NOMBRE_SQLITE = "scet.sqlite"
ARCHIVO_SQLITE = join(CARPETA_TRABAJO, NOMBRE_SQLITE)
_BD = None
def DEFINIR_BD(coneccion):
    global _BD
    LOG_SCET.debug('Definiendo la bases de datos como {}'.format(coneccion))
    _BD = coneccion
def OBTENER_BD():
    return _BD

# Interface Principal
_ROOT = None
def OBTENER_ROOT():
    global _ROOT
    from tkinter import Tk
    if _ROOT is None:
        _ROOT = Tk()
    return _ROOT
