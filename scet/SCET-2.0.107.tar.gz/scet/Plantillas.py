#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from tkinter import ttk, messagebox, Tk, Toplevel

from scet.bd_xml import Tabla
from scet import libsa
from scet.globales import *


log = logging.getLogger(__name__)


class Plantilla_Estandar(libsa.Ventana, libsa.Formulario):
    condicion = False

    def __init__(self, master, id=None):
        self.master = master
        self.bd = Tabla(self.nombre_tabla, OBTENER_BD())
        libsa.Ventana.__init__(self, master, self.archivo_gui)
        libsa.Formulario.__init__(self, self.bd, id_extranjero=id)
        # escribir datos a la gui
        for tipo, valor in [(fil['tipo'], fil['valor']) for fil in self.bd]:
            self.gui.create_variable(tipo).set(valor)
        self.colocar_text_variable()

    @libsa.Formulario._guardar
    def guardar(self):
        for variable, valor in self.datos.items():
            if not valor is None:
                for val in [v for v in valor.split('\n') if not v is '']:
                    self.bd += {'tipo':variable, 'valor':val}


class Contacto(Plantilla_Estandar):
    archivo_gui = 'P_Contacto'
    nombre_tabla = 'Contacto'
    columnas = ['tipo','valor']
    referencia = 'idEntidades'
    msj_guardado= 'La informacion de contacto fue guardada correctamente'

class Descripciones(Plantilla_Estandar):
    archivo_gui = None
    nombre_tabla = 'Descripciones'
    columnas = ['tipo','valor']
    referencia = 'idUbicaciones'
    msj_guardado= 'La informacion de ubicacion fue guardada correctamente'

class Especificaciones(Plantilla_Estandar):
    archivo_gui = None
    nombre_tabla = 'Especificaciones'
    columnas = ['tipo','valor']
    referencia = 'idObjetos'
    msj_guardado= 'Las Especificaciones fueron guardadas correctamentes'

    @libsa.Formulario._guardar
    def guardar(self):
        for variable, valor in self.datos.items():
            if variable == 'descripcion':
                for val in [v for v in valor.split('\n') if not v is ''] if (not valor is None) else ():
                    var, val = val.split(' ', 1) if ' ' in val else (val, '')
                    self.bd += {'tipo':var, 'valor':val}
            else:
                self.bd += {'tipo':variable, 'valor':valor}

class Caracteristicas(Plantilla_Estandar):
    archivo_gui = None
    nombre_tabla = 'Caracteristicas'
    columnas = ['tipo','valor']
    referencia = 'idEntidades'
    msj_guardado= 'Las Caracteristicasfueron guardadas correctamentes'
