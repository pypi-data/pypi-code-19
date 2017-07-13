#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from tkinter import ttk, messagebox, Tk, Toplevel

from scet.bd_xml import Tabla
from scet import libsa
from scet.globales import *


log = logging.getLogger(__name__)


class Formulario_Estandar(libsa.Ventana, libsa.Formulario):
    condicion = False
    columnas = ('*',)
    msj_guardado = 'El Formulario {nombre} fue guardado'

    def __init__(self, master, id=None):
        self.master = master
        self.bd = Tabla(self.nombre_tabla, OBTENER_BD())
        libsa.Ventana.__init__(self, self.master, self.archivo_gui)
        libsa.Formulario.__init__(self, tabla=self.bd, id_primario=id)
        # escribir datos a la gui
        self._sincronisar('formulario', None, self.bd, 'none_a_str')

    @libsa.Formulario._guardar
    def guardar(self):
        if self.master:
            self.bd.truncar()
            self.bd += self.datos

class Informacion_Fiscal(libsa.Ventana, libsa.Formulario):
    nombre_tabla = 'Informacion_Fiscal'
    nombre = 'La Informacion Fiscal'
    archivo_gui = 'F_Informacion_Fiscal'
    condicion = False
    columnas = ('*',)
    msj_guardado = 'La Informacion fiscal ha sido guardada'

    def __init__(self, master, id=None):
        self.master = master
        self.bd = Tabla(self.nombre_tabla, OBTENER_BD())
        libsa.Ventana.__init__(self, self.master, self.archivo_gui)
        libsa.Formulario.__init__(self, tabla=self.bd, id_extranjero=id)
        # escribir datos a la gui
        self._sincronisar('formulario', None, self.bd, 'none_a_str')
        tipo = self.bd[0]['rif_tipo'] if self.bd[0]['rif_tipo'] else ''
        numero = str(int(self.bd[0]['rif_numero'])) if self.bd[0]['rif_numero'] else ''
        final = str(int(self.bd[0]['rif_final'])) if self.bd[0]['rif_final'] else ''
        rif = tipo + numero + final
        self.gui.get_variable('rif').set(rif) if self.master else False

    @libsa.Formulario._guardar
    def guardar(self):
        self.bd.truncar()
        self.bd += self.datos
        self.bd[0]['rif_tipo'] = self.datos['rif'][0]
        self.bd[0]['rif_numero'] = self.datos['rif'][1:9]
        if self.datos['rif'][0].upper() in ('J', 'G') or len(self.datos['rif']) == 10:
            self.bd[0]['rif_final'] = self.datos['rif'][9]
        else:
            self.bd[0]['rif_final'] = None

class Entidad(Formulario_Estandar):
    nombre_tabla = 'Entidades'
    nombre = 'La Entidad'
    archivo_gui = 'F_Entidad'

class Objetos(Formulario_Estandar):
    nombre_tabla = 'Objetos'
    nombre = 'El Objeto'
    archivo_gui = 'F_Objetos'

class Ubicaciones(Formulario_Estandar):
    nombre_tabla = 'Ubicaciones'
    nombre = 'La Ubicacion'
    archivo_gui = 'F_Ubicaciones'

class Cliente(Formulario_Estandar):
    nombre_tabla = 'Clientes'
    nombre = 'El Cliente'
    archivo_gui = None

class Equipos(Formulario_Estandar):
    nombre_tabla = 'Equipos'
    nombre = 'El Equipo'
    archivo_gui = None

class Tecnicos(Formulario_Estandar):
    nombre_tabla = 'Tecnicos'
    nombre = 'El Tecnico'
    archivo_gui = None

class Talleres(Formulario_Estandar):
    nombre_tabla = 'Talleres'
    nombre = 'El Talleres'
    archivo_gui = None

class Herramientas(Formulario_Estandar):
    nombre_tabla = 'Herramientas'
    nombre = 'La Herraminta'
    archivo_gui = None

class Almasenes(Formulario_Estandar):
    nombre_tabla = 'Almasenes'
    nombre = 'El Almasen'
    archivo_gui = None

class Empresas(Formulario_Estandar):
    nombre_tabla = 'Empresas'
    nombre = 'La Empresa'
    archivo_gui = None

class Entradas(Formulario_Estandar):
    nombre_tabla = 'Entradas'
    nombre = 'La Entrada'
    archivo_gui = None

class Trabajos(Formulario_Estandar):
    nombre_tabla = 'Trabajos'
    nombre = 'El Trabajo'
    archivo_gui = None
