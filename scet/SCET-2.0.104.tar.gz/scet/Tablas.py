267#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from tkinter import ttk, messagebox, Tk, Toplevel

from scet.bd_xml import Tabla
from scet import libsa
from scet.globales import *


log = logging.getLogger(__name__)


class Tabla_Estandar(libsa.Ventana, libsa.Tabla):
    archivo_gui = None
    nombre_tabla = ''
    msj_guardado = 'La tabla {nombre} ha sido guardada'

    def __init__(self, master, id_extranjero=None):
        self.master = master
        self.bd = Tabla(self.nombre_tabla, OBTENER_BD())
        libsa.Ventana.__init__(self, self.master, self.archivo_gui)
        libsa.Tabla.__init__(self, self.bd, id_extranjero)
        llave = self.gui.create_variable(self.bd.llaves_extranjeras[0]) if len(self.bd.llaves_extranjeras) > 0 else None
        llave.set(self.bd[0][self.bd.llaves_extranjeras[0]]) if llave else None


class Talleres(Tabla_Estandar):
    archivo_gui = 'T_Talleres'
    nombre_tabla = '_Talleres'

class Almasenes(Tabla_Estandar):
    archivo_gui = 'T_Almasenes'
    nombre_tabla = '_Almasenes'

class Tecnicos(Tabla_Estandar):
    archivo_gui = 'T_Tecnicos'
    nombre_tabla = '_Tecnicos'

class Herramientas(Tabla_Estandar):
    archivo_gui = 'T_Herramientas'
    nombre_tabla = '_Herramientas'

class Empresas(Tabla_Estandar):
    archivo_gui = 'T_Empresas'
    nombre_tabla = '_Empresas'

class Clientes(Tabla_Estandar):
    archivo_gui = 'T_Clientes'
    nombre_tabla = '_Clientes'

class Caracteristicas(Tabla_Estandar):
    archivo_gui = 'T_Caracteristicas'
    nombre_tabla = 'Caracteristicas'

class Contacto(Tabla_Estandar):
    archivo_gui = 'T_Contacto'
    nombre_tabla = 'Contacto'

class Especificaciones(Tabla_Estandar):
    archivo_gui = 'T_Caracteristicas'
    nombre_tabla = 'Especificaciones'

class Descripciones(Tabla_Estandar):
    archivo_gui = 'T_Caracteristicas'
    nombre_tabla = 'Descripciones'

class Entradas(Tabla_Estandar):
    archivo_gui = 'T_Entradas'
    nombre_tabla = '_Entradas'


class Equipos_Entrada(Tabla_Estandar):
    archivo_gui = 'T_EquiposEntrada'
    nombre_tabla = ''

    def __init__(self, master, id_extranjero=None):
        Tabla_Estandar.__init__(self, master, None)
        self.bd.agregar_columna(campo='Equipo', defecto='')
        self.bd.agregar_columna(campo='Marca', defecto='')
        self.bd.agregar_columna(campo='Modelo', defecto='')
        self.bd.agregar_columna(campo='Serial', defecto='')
        self.bd.agregar_columna(campo='Descripcion', defecto='')

    def agregarFila(self, evento=None):
        self.bd += self.datos
        self.actualisar_arbol()
