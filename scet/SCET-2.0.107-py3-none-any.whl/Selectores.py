#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from tkinter import ttk, messagebox, Tk, Toplevel

from scet.bd_xml import Tabla
from scet import libsa
from scet.globales import *


log = logging.getLogger(__name__)
fila_defecto = 0


class Selector_Estandar(libsa.Ventana, libsa.Selector):
    nombre_objeto_lista = 'lista'

    archivo_gui = None
    nombre_tabla = ''
    nombre_columna = 'nombre'

    def __init__(self, master, id=None):
        self.master = master
        self.bd = Tabla(self.nombre_tabla, OBTENER_BD())
        libsa.Ventana.__init__(self, self.master, self.archivo_gui)
        libsa.Selector.__init__(self, tabla=self.bd, id_extranjero=id)
        self.lista = self.gui.get_object(self.nombre_objeto_lista)
        self.lista['values'] = [fila[self.nombre_columna] for fila in self.bd]
        self.lista.current(fila_defecto) if len(self.lista['values']) > 0 else None


class Empresas(Selector_Estandar):
    archivo_gui = 'S_Empresas'
    nombre_tabla = '_Empresas'
    nombre_columna = 'nombre'

    def __init__(self, master, id=None):
        Selector_Estandar.__init__(self, master, None)
